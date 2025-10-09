from datetime import timedelta

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from compliance.models import ComplianceCheckResult
from invoices.models import Invoice

from .models import Task, TaskStatusHistory


@receiver(post_save, sender=Invoice)
def create_task_on_invoice_status_change(sender, instance, created, **kwargs):
    """
    Créer automatiquement des tâches selon le statut de la facture
    """
    # Éviter de créer des tâches si c'est une nouvelle facture en brouillon
    if created and instance.status == "draft":
        return

    # Facture rejetée → Créer une tâche de correction
    if instance.status == "rejected":
        Task.objects.get_or_create(
            invoice=instance,
            task_type="invoice_rejected",
            status="pending",
            defaults={
                "company": instance.company,
                "client": instance.client,
                "title": f"Facture rejetée : {instance.invoice_number}",
                "description": f"La facture {instance.invoice_number} a été rejetée. "
                f"Veuillez vérifier les motifs et apporter les corrections nécessaires.",
                "priority": 2,  # Haute priorité
                "due_date": timezone.now() + timedelta(days=3),
                "created_by": instance.created_by,
            },
        )

    # Facture en litige → Créer une tâche de suivi
    elif instance.status == "disputed":
        Task.objects.get_or_create(
            invoice=instance,
            task_type="client_followup",
            status="pending",
            defaults={
                "company": instance.company,
                "client": instance.client,
                "title": f"Litige sur facture : {instance.invoice_number}",
                "description": f"La facture {instance.invoice_number} est en litige. "
                f"Contacter le client pour résoudre le problème.",
                "priority": 2,
                "due_date": timezone.now() + timedelta(days=2),
                "created_by": instance.created_by,
            },
        )

    # Facture en retard de paiement
    elif instance.status == "accepted" and instance.days_overdue > 0:
        # Créer une tâche de relance uniquement si retard > 7 jours
        if instance.days_overdue >= 7:
            # Vérifier qu'une tâche de relance n'existe pas déjà
            existing_task = Task.objects.filter(
                invoice=instance,
                task_type="payment_overdue",
                status__in=["pending", "in_progress"],
            ).exists()

            if not existing_task:
                # Priorité augmente avec le retard
                priority = 3  # Normal
                if instance.days_overdue >= 30:
                    priority = 1  # Très haute
                elif instance.days_overdue >= 15:
                    priority = 2  # Haute

                Task.objects.create(
                    invoice=instance,
                    company=instance.company,
                    client=instance.client,
                    task_type="payment_overdue",
                    title=f"Relance paiement : {instance.invoice_number} ({instance.days_overdue}j de retard)",
                    description=f"La facture {instance.invoice_number} est en retard de {instance.days_overdue} jours. "
                    f"Montant : {instance.amount_ttc} {instance.currency.code}. "
                    f'Échéance initiale : {instance.due_date.strftime("%d/%m/%Y")}.',
                    priority=priority,
                    status="pending",
                    due_date=timezone.now() + timedelta(days=2),
                    created_by=instance.created_by,
                )


@receiver(post_save, sender=ComplianceCheckResult)
def create_task_on_compliance_failure(sender, instance, created, **kwargs):
    """
    Créer une tâche lorsqu'une vérification de conformité échoue
    """
    if not created:
        return

    # Seulement pour les échecs et avertissements
    if instance.status not in ["fail", "warning"]:
        return

    invoice = instance.invoice

    # Déterminer la priorité selon la sévérité
    priority = 3 if instance.status == "warning" else 2

    Task.objects.get_or_create(
        invoice=invoice,
        task_type="compliance_check",
        status="pending",
        defaults={
            "company": invoice.company,
            "client": invoice.client,
            "title": f"Non-conformité : {invoice.invoice_number}",
            "description": f"La facture {invoice.invoice_number} présente un problème de conformité.\n"
            f"Règle : {instance.rule.name}\n"
            f"Statut : {instance.get_status_display()}\n"
            f'Détails : {instance.details or "Aucun détail"}',
            "priority": priority,
            "due_date": timezone.now() + timedelta(days=5),
            "metadata": {
                "compliance_check_id": instance.id,
                "rule_id": instance.rule.id,
                "rule_name": instance.rule.name,
            },
        },
    )


@receiver(post_save, sender=Invoice)
def create_task_for_missing_documents(sender, instance, created, **kwargs):
    """
    Vérifier les documents manquants et créer des tâches
    """
    # Seulement pour les factures soumises
    if instance.status not in ["submitted", "accepted"]:
        return

    # Documents requis selon le type de client/plateforme
    required_docs = ["po", "bl"]  # Exemple : PO et BL toujours requis

    # Vérifier quels documents sont présents
    present_docs = set(instance.documents.values_list("document_type", flat=True))

    missing_docs = [doc for doc in required_docs if doc not in present_docs]

    if missing_docs:
        # Créer une tâche si elle n'existe pas déjà
        Task.objects.get_or_create(
            invoice=instance,
            task_type="document_missing",
            status__in=["pending", "in_progress"],
            defaults={
                "company": instance.company,
                "client": instance.client,
                "title": f"Documents manquants : {instance.invoice_number}",
                "description": f"Les documents suivants sont manquants pour la facture {instance.invoice_number}:\n"
                + "\n".join([f"- {doc.upper()}" for doc in missing_docs]),
                "priority": 2,
                "due_date": timezone.now() + timedelta(days=3),
                "created_by": instance.created_by,
                "metadata": {
                    "missing_documents": missing_docs,
                },
            },
        )


@receiver(post_save, sender=Task)
def auto_assign_task_from_template(sender, instance, created, **kwargs):
    """
    Assigner automatiquement une tâche selon des règles prédéfinies
    """
    if not created or instance.assigned_to:
        return

    # Exemple : Assigner automatiquement certains types de tâches
    # selon des règles métier

    # Tâches de conformité → assigner au responsable qualité de l'entreprise
    if instance.task_type == "compliance_check":
        from accounts.models import UserCompany

        # Chercher un utilisateur avec rôle admin dans l'entreprise
        admin_user = UserCompany.objects.filter(
            company=instance.company, user__role="admin"
        ).first()

        if admin_user:
            instance.assigned_to = admin_user.user
            instance.save(update_fields=["assigned_to"])


@receiver(post_save, sender=TaskStatusHistory)
def log_task_completion(sender, instance, created, **kwargs):
    """
    Logger la complétion d'une tâche dans les audit logs
    """
    if not created:
        return

    if instance.new_status == "completed":
        from core.models import AuditLog

        AuditLog.objects.create(
            user=instance.changed_by,
            action="other",
            content_type="task_completion",
            object_id=str(instance.task.id),
            details={
                "task_title": instance.task.title,
                "task_type": instance.task.task_type,
                "completed_at": instance.changed_at.isoformat(),
                "notes": instance.notes,
            },
        )


def check_overdue_tasks_daily():
    """
    Fonction à appeler via cron/celery pour vérifier les tâches en retard
    et augmenter leur priorité
    """
    from django.utils import timezone

    now = timezone.now()

    # Trouver toutes les tâches en retard non terminées
    overdue_tasks = Task.objects.filter(
        due_date__lt=now,
        status__in=["pending", "in_progress"],
        is_overdue=False,  # Pas encore marquées comme en retard
    )

    for task in overdue_tasks:
        # Marquer comme en retard
        task.is_overdue = True

        # Augmenter la priorité si ce n'est pas déjà au maximum
        if task.priority > 1:
            task.priority = max(1, task.priority - 1)

        task.save()

        # Créer une notification pour l'utilisateur assigné
        if task.assigned_to:
            from notifications.models import Notification, NotificationType

            notif_type = NotificationType.objects.filter(code="task_overdue").first()

            if notif_type:
                Notification.objects.create(
                    user=task.assigned_to,
                    notification_type=notif_type,
                    title=f"Tâche en retard : {task.title}",
                    message=f'La tâche "{task.title}" est en retard depuis le {task.due_date.strftime("%d/%m/%Y")}.',
                    link=f"/tasks/{task.id}/",
                    priority="high",
                )
