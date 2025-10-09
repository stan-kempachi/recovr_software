from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import Company
from invoices.models import Client, Invoice


class TaskCategory(models.Model):
    """Catégories de tâches pour classification"""

    code = models.CharField(_("Code"), max_length=50, unique=True)
    name = models.CharField(_("Nom"), max_length=100)
    description = models.TextField(_("Description"), blank=True)
    color = models.CharField(
        _("Couleur"), max_length=7, default="#3B82F6"
    )  # Format hex
    icon = models.CharField(_("Icône"), max_length=50, blank=True)
    is_active = models.BooleanField(_("Active"), default=True)

    class Meta:
        verbose_name = _("Catégorie de tâche")
        verbose_name_plural = _("Catégories de tâche")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Task(models.Model):
    """Modèle principal pour les tâches"""

    TYPE_CHOICES = (
        ("compliance_check", _("Vérification de conformité")),
        ("document_missing", _("Document manquant")),
        ("payment_overdue", _("Retard de paiement")),
        ("platform_sync", _("Synchronisation plateforme")),
        ("invoice_rejected", _("Facture rejetée")),
        ("client_followup", _("Suivi client")),
        ("manual", _("Tâche manuelle")),
        ("other", _("Autre")),
    )

    STATUS_CHOICES = (
        ("pending", _("En attente")),
        ("in_progress", _("En cours")),
        ("completed", _("Terminée")),
        ("cancelled", _("Annulée")),
        ("blocked", _("Bloquée")),
    )

    PRIORITY_CHOICES = (
        (1, _("Très haute")),
        (2, _("Haute")),
        (3, _("Normale")),
        (4, _("Basse")),
        (5, _("Très basse")),
    )

    # Relations
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="tasks",
        verbose_name=_("Entreprise"),
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
        verbose_name=_("Assigné à"),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_tasks",
        verbose_name=_("Créé par"),
    )
    category = models.ForeignKey(
        TaskCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
        verbose_name=_("Catégorie"),
    )

    # Relations optionnelles (contexte)
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="tasks",
        verbose_name=_("Facture associée"),
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="tasks",
        verbose_name=_("Client associé"),
    )

    # Informations de la tâche
    title = models.CharField(_("Titre"), max_length=200)
    description = models.TextField(_("Description"), blank=True)
    task_type = models.CharField(
        _("Type de tâche"), max_length=30, choices=TYPE_CHOICES, default="manual"
    )
    status = models.CharField(
        _("Statut"), max_length=15, choices=STATUS_CHOICES, default="pending"
    )
    priority = models.IntegerField(_("Priorité"), choices=PRIORITY_CHOICES, default=3)

    # Gestion temporelle
    due_date = models.DateTimeField(_("Date d'échéance"), null=True, blank=True)
    reminder_date = models.DateTimeField(_("Date de rappel"), null=True, blank=True)
    completed_at = models.DateTimeField(_("Terminée le"), null=True, blank=True)
    created_at = models.DateTimeField(_("Créée le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mise à jour le"), auto_now=True)

    # Métadonnées
    is_recurring = models.BooleanField(_("Récurrente"), default=False)
    recurrence_rule = models.JSONField(
        _("Règle de récurrence"),
        blank=True,
        null=True,
        help_text=_("Format: {frequency: 'daily/weekly/monthly', interval: 1}"),
    )
    metadata = models.JSONField(
        _("Métadonnées"),
        blank=True,
        null=True,
        help_text=_("Données supplémentaires contextuelles"),
    )

    # Champs calculés
    is_overdue = models.BooleanField(_("En retard"), default=False, editable=False)
    urgency_score = models.IntegerField(
        _("Score d'urgence"),
        default=0,
        editable=False,
        help_text=_("Score calculé basé sur priorité + échéance"),
    )

    class Meta:
        verbose_name = _("Tâche")
        verbose_name_plural = _("Tâches")
        ordering = ["urgency_score", "priority", "due_date"]
        indexes = [
            models.Index(fields=["status", "assigned_to"]),
            models.Index(fields=["due_date", "priority"]),
            models.Index(fields=["company", "status"]),
            models.Index(fields=["urgency_score"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        """Calcul automatique du score d'urgence avant sauvegarde"""
        from django.utils import timezone

        # Calcul de l'overdue
        if self.due_date and self.status not in ["completed", "cancelled"]:
            self.is_overdue = self.due_date < timezone.now()

        # Calcul du score d'urgence (plus le score est élevé, plus c'est urgent)
        score = 0

        # Priorité (inverse car 1 = très haute)
        score += (6 - self.priority) * 20

        # Urgence temporelle
        if self.due_date:
            days_until_due = (self.due_date - timezone.now()).days
            if days_until_due < 0:  # En retard
                score += 100 + abs(days_until_due) * 5
            elif days_until_due <= 1:  # Aujourd'hui ou demain
                score += 50
            elif days_until_due <= 3:
                score += 30
            elif days_until_due <= 7:
                score += 15

        # Bonus pour certains types critiques
        if self.task_type in ["payment_overdue", "invoice_rejected"]:
            score += 25

        self.urgency_score = score

        super().save(*args, **kwargs)


class TaskComment(models.Model):
    """Commentaires sur les tâches"""

    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="comments", verbose_name=_("Tâche")
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Utilisateur"),
    )
    comment = models.TextField(_("Commentaire"))
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)
    is_internal = models.BooleanField(
        _("Interne"),
        default=True,
        help_text=_("Commentaire visible uniquement en interne"),
    )

    class Meta:
        verbose_name = _("Commentaire de tâche")
        verbose_name_plural = _("Commentaires de tâche")
        ordering = ["created_at"]

    def __str__(self):
        return f"Commentaire de {self.user} sur {self.task}"


class TaskAttachment(models.Model):
    """Pièces jointes associées aux tâches"""

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name=_("Tâche"),
    )
    file = models.FileField(_("Fichier"), upload_to="task_attachments/%Y/%m/")
    filename = models.CharField(_("Nom du fichier"), max_length=255)
    file_size = models.IntegerField(_("Taille (octets)"), default=0)
    mime_type = models.CharField(_("Type MIME"), max_length=100, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Téléchargé par"),
    )
    uploaded_at = models.DateTimeField(_("Téléchargé le"), auto_now_add=True)
    description = models.TextField(_("Description"), blank=True)

    class Meta:
        verbose_name = _("Pièce jointe")
        verbose_name_plural = _("Pièces jointes")
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.filename


class TaskStatusHistory(models.Model):
    """Historique des changements de statut des tâches"""

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="status_history",
        verbose_name=_("Tâche"),
    )
    previous_status = models.CharField(_("Statut précédent"), max_length=15, blank=True)
    new_status = models.CharField(_("Nouveau statut"), max_length=15)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Modifié par"),
    )
    changed_at = models.DateTimeField(_("Modifié le"), auto_now_add=True)
    notes = models.TextField(_("Notes"), blank=True)

    class Meta:
        verbose_name = _("Historique de statut de tâche")
        verbose_name_plural = _("Historiques de statut de tâche")
        ordering = ["-changed_at"]

    def __str__(self):
        return f"{self.task.title}: {self.previous_status} → {self.new_status}"


class TaskTemplate(models.Model):
    """Templates de tâches pour automatisation"""

    name = models.CharField(_("Nom"), max_length=100)
    description = models.TextField(_("Description"), blank=True)
    task_type = models.CharField(
        _("Type de tâche"), max_length=30, choices=Task.TYPE_CHOICES
    )
    category = models.ForeignKey(
        TaskCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="templates",
        verbose_name=_("Catégorie"),
    )
    default_priority = models.IntegerField(
        _("Priorité par défaut"), choices=Task.PRIORITY_CHOICES, default=3
    )
    default_title = models.CharField(_("Titre par défaut"), max_length=200)
    default_description = models.TextField(_("Description par défaut"), blank=True)
    default_due_days = models.IntegerField(
        _("Échéance (jours)"), default=7, help_text=_("Nombre de jours après création")
    )
    trigger_conditions = models.JSONField(
        _("Conditions de déclenchement"),
        blank=True,
        null=True,
        help_text=_("Conditions pour créer automatiquement cette tâche"),
    )
    is_active = models.BooleanField(_("Actif"), default=True)
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

    class Meta:
        verbose_name = _("Template de tâche")
        verbose_name_plural = _("Templates de tâche")
        ordering = ["name"]

    def __str__(self):
        return self.name
