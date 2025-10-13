from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from invoices.models import Invoice

from .models import (
    Client,
    RecurrenceRule,
    Task,
    TaskCategory,
    TaskComment,
    TaskStatusHistory,
)

User = get_user_model()


@login_required
def task_list(request):
    """Affiche la liste des tâches filtrables de l'entreprise"""
    user = request.user
    user_company_link = (
        user.companies.filter(is_primary=True).first() or user.companies.first()
    )

    if not user_company_link:
        return HttpResponse("Aucune entreprise associée à cet utilisateur.", status=400)

    company = user_company_link.company

    # Récupération de toutes les tâches de cette entreprise + préchargement des commentaires
    tasks = (
        Task.objects.filter(company=company)
        .select_related("client", "category", "assigned_to")
        .prefetch_related(
            "comments__user"
        )  # Précharge les commentaires et leurs auteurs
    )

    # --- Filtres ---
    status_filter = request.GET.get("status", "")
    client_filter = request.GET.get("client", "")
    sort = request.GET.get(
        "sort", "priority"
    )  # Modifier la valeur par défaut pour correspondre au comportement

    if status_filter:
        tasks = tasks.filter(status=status_filter)

    if client_filter:
        tasks = tasks.filter(client_id=client_filter)

    # --- Tri ---
    if sort == "due_date":
        tasks = tasks.order_by("due_date")
    elif sort == "priority":
        tasks = tasks.order_by("priority")
    elif sort == "created_at":
        tasks = tasks.order_by("-created_at")
    else:
        # Tri par urgence personnalisée (priorité + échéance)
        tasks = tasks.order_by("priority", "due_date")

    # --- Clients pour le menu déroulant ---
    clients = Client.objects.filter(company=company)

    # --- Statistiques ---
    # Optimisation pour éviter les requêtes multiples en utilisant des annotations et des agrégations
    # Mais gardons l'approche simple pour l'instant
    total_tasks = tasks.count()
    pending_tasks = tasks.filter(status="pending").count()
    completed_tasks = tasks.filter(status="completed").count()
    overdue_tasks = tasks.filter(
        due_date__lt=timezone.now(), status__in=["pending", "in_progress"]
    ).count()

    # Détermination du template de base en fonction de l'URL
    base_template = "core/base.html" if request.path == "/tasks/" else "dashboard.html"

    context = {
        "tasks": tasks,
        "clients": clients,
        "status_filter": status_filter,
        "client_filter": client_filter,
        "sort": sort,
        "stats": {
            "total": total_tasks,
            "pending": pending_tasks,
            "completed": completed_tasks,
            "overdue": overdue_tasks,
        },
        "base_template": base_template,
    }

    return render(request, "tasks/task_list.html", context)


@login_required
def get_tasks(request):
    """Endpoint AJAX qui renvoie les tâches triées selon un critère"""
    user = request.user
    sort = request.GET.get("sort", "urgency")

    tasks = Task.objects.filter(
        assigned_to=user, status__in=["pending", "in_progress"]
    ).select_related("company", "client")

    if sort == "due_date":
        tasks = tasks.order_by("due_date")
    elif sort == "status":
        tasks = tasks.order_by("status")
    elif sort == "client":
        tasks = tasks.order_by("client__name")
    elif sort == "project":
        tasks = tasks.order_by("company__name")
    else:
        tasks = tasks.order_by("-urgency_score")

    data = [
        {
            "id": t.id,
            "title": t.title,
            "due_date": t.due_date.strftime("%d/%m/%Y") if t.due_date else "-",
            "urgency": t.urgency_score or "-",
            "company": t.company.name if t.company else "-",
            "client": t.client.name if t.client else "-",
            "status": t.get_status_display(),
        }
        for t in tasks
    ]
    return JsonResponse({"tasks": data})


@login_required
def create_or_edit_task(request, task_id=None):
    """Création ou édition d'une tâche (même template)"""

    user = request.user
    user_company_link = (
        user.companies.filter(is_primary=True).first() or user.companies.first()
    )
    if not user_company_link:
        return HttpResponse("Aucune entreprise associée à cet utilisateur.", status=400)

    company = user_company_link.company

    # Si un ID est fourni → édition, sinon création
    task = None
    if task_id:
        task = get_object_or_404(Task, id=task_id)
        # sécurité : vérifier l'accès
        user_companies = user.companies.values_list("company_id", flat=True)
        if task.company_id not in user_companies and task.created_by != user:
            return JsonResponse({"error": "Permission denied"}, status=403)

    categories = TaskCategory.objects.filter(is_active=True)
    clients = Client.objects.filter(company=company)
    users = [uc.user for uc in company.users.all()]
    # Récupération des factures disponibles
    invoices = Invoice.objects.filter(company=company)

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        category_id = request.POST.get("category")
        client_id = request.POST.get("client")
        assigned_to_id = request.POST.get("assigned_to")
        due_date_str = request.POST.get("due_date")
        priority = request.POST.get("priority", 3)
        invoice_id = request.POST.get("invoice")
        task_type = request.POST.get("task_type", "manual")
        status = request.POST.get("status", "pending")
        is_recurring = request.POST.get("is_recurring") == "on"
        reminder_date_str = request.POST.get("reminder_date")

        category = (
            TaskCategory.objects.filter(id=category_id).first() if category_id else None
        )
        client = Client.objects.filter(id=client_id).first() if client_id else None
        assigned_to = (
            next((u for u in users if str(u.id) == assigned_to_id), None)
            if assigned_to_id
            else None
        )
        invoice = Invoice.objects.filter(id=invoice_id).first() if invoice_id else None

        due_date = None
        if due_date_str:
            try:
                naive_date = datetime.strptime(due_date_str, "%Y-%m-%d")
                due_date = timezone.make_aware(
                    naive_date, timezone.get_current_timezone()
                )
            except ValueError:
                pass

        reminder_date = None
        if reminder_date_str:
            try:
                naive_date = datetime.strptime(reminder_date_str, "%Y-%m-%d")
                reminder_date = timezone.make_aware(
                    naive_date, timezone.get_current_timezone()
                )
            except ValueError:
                pass

        # Gestion des règles de récurrence
        recurrence_frequency = request.POST.get("recurrence_frequency", "monthly")
        recurrence_interval = int(request.POST.get("recurrence_interval", 1))
        recurrence_rule = None

        if is_recurring:
            # Création/mise à jour d'une règle de récurrence
            if task and hasattr(task, "recurrence_rule") and task.recurrence_rule:
                recurrence_rule = task.recurrence_rule
                recurrence_rule.frequency = recurrence_frequency
                recurrence_rule.interval = recurrence_interval
                recurrence_rule.save()
            else:
                recurrence_rule = RecurrenceRule.objects.create(
                    frequency=recurrence_frequency, interval=recurrence_interval
                )
        elif task and hasattr(task, "recurrence_rule") and task.recurrence_rule:
            # Suppression de la règle de récurrence si elle existe et que la case n'est plus cochée
            old_rule = task.recurrence_rule
            task.recurrence_rule = None
            task.save()
            old_rule.delete()

        # Création ou mise à jour
        if task:
            task.title = title
            task.description = description
            task.category = category
            task.client = client
            task.assigned_to = assigned_to or task.assigned_to
            task.priority = int(priority)
            task.due_date = due_date
            task.invoice = invoice
            task.task_type = task_type
            task.status = status
            task.is_recurring = is_recurring
            task.reminder_date = reminder_date

            if is_recurring and recurrence_rule:
                task.recurrence_rule = recurrence_rule

            task.save()
        else:
            task = Task.objects.create(
                title=title,
                description=description,
                company=company,
                category=category,
                client=client,
                created_by=user,
                assigned_to=assigned_to or user,
                priority=int(priority),
                due_date=due_date,
                invoice=invoice,
                task_type=task_type,
                status=status,
                is_recurring=is_recurring,
                recurrence_rule=recurrence_rule if is_recurring else None,
                reminder_date=reminder_date,
            )

        return redirect("tasks:task_detail", task_id=task.id)

    context = {
        "task": task,
        "categories": categories,
        "clients": clients,
        "users": users,
        "invoices": invoices,
        "is_edit": bool(task),
    }
    return render(request, "tasks/task_create.html", context)


@login_required
def create_task(request):
    """Création d'une tâche"""

    user = request.user
    # Récupérer l'entreprise principale ou la première associée
    user_company_link = (
        user.companies.filter(is_primary=True).first() or user.companies.first()
    )

    if not user_company_link:
        return HttpResponse("Aucune entreprise associée à cet utilisateur.", status=400)

    company = user_company_link.company

    # Liste des catégories et clients pour le formulaire
    categories = TaskCategory.objects.filter(is_active=True)
    clients = Client.objects.filter(company=company)
    users = [uc.user for uc in company.users.all()]  # Utilisateurs liés à l'entreprise

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        category_id = request.POST.get("category")
        client_id = request.POST.get("client")
        assigned_to_id = request.POST.get("assigned_to")
        due_date_str = request.POST.get("due_date")
        priority = request.POST.get("priority", 3)

        # Récupérer objets liés
        category = (
            TaskCategory.objects.filter(id=category_id).first() if category_id else None
        )
        client = Client.objects.filter(id=client_id).first() if client_id else None
        assigned_to = None
        if assigned_to_id:
            assigned_to = next((u for u in users if str(u.id) == assigned_to_id), None)

        # Conversion de la date
        due_date = None
        if due_date_str:
            try:
                naive_date = datetime.strptime(due_date_str, "%Y-%m-%d")
                # rendre aware avec timezone par défaut
                due_date = timezone.make_aware(
                    naive_date, timezone.get_current_timezone()
                )
            except ValueError:
                due_date = None

        # Création de la tâche
        task = Task.objects.create(
            title=title,
            description=description,
            company=company,
            category=category,
            client=client,
            created_by=user,
            assigned_to=assigned_to or user,  # Si rien sélectionné, s'auto-assigner
            priority=int(priority),
            due_date=due_date,
        )

        return redirect("tasks:task_detail", task_id=task.id)

    context = {
        "categories": categories,
        "clients": clients,
        "users": users,
    }
    return render(request, "tasks/task_create.html", context)


@login_required
def task_edit(request, task_id):
    """Édition d’une tâche"""
    task = get_object_or_404(Task, id=task_id)
    user = request.user

    # Vérification permissions
    user_companies = user.companies.values_list("company_id", flat=True)
    if task.company_id not in user_companies and task.created_by != user:
        return JsonResponse({"error": "Permission denied"}, status=403)

    # Données nécessaires pour le template
    user_company_link = (
        user.companies.filter(is_primary=True).first() or user.companies.first()
    )
    company = user_company_link.company if user_company_link else task.company
    if task.company != company:
        return HttpResponseForbidden("Vous n'avez pas accès à cette tâche.")

    categories = TaskCategory.objects.filter(is_active=True)
    clients = Client.objects.filter(company=company)
    users = [uc.user for uc in company.users.all()]

    if request.method == "POST":
        task.title = request.POST.get("title")
        task.description = request.POST.get("description")
        task.priority = int(request.POST.get("priority", 3))
        task.category_id = request.POST.get("category") or None
        task.client_id = request.POST.get("client") or None
        task.assigned_to_id = request.POST.get("assigned_to") or None

        due_date_str = request.POST.get("due_date")
        if due_date_str:
            try:
                task.due_date = timezone.make_aware(
                    datetime.strptime(due_date_str, "%Y-%m-%d")
                )
            except ValueError:
                task.due_date = None

        task.save()
        return redirect("tasks:task_detail", task_id=task.id)

    context = {
        "task": task,
        "categories": categories,
        "clients": clients,
        "users": users,
    }
    return render(request, "tasks/task_edit.html", context)


@login_required
def task_detail(request, task_id):
    """Détail d'une tâche avec commentaires et historique"""
    task = get_object_or_404(  # type: ignore
        Task.objects.select_related(
            "invoice", "client", "category", "assigned_to", "created_by", "company"
        ),
        id=task_id,
    )

    # Vérifier les permissions
    user_companies = request.user.companies.values_list("company_id", flat=True)
    if task.company_id not in user_companies and task.assigned_to != request.user:
        return JsonResponse({"error": "Permission denied"}, status=403)

    # Commentaires
    comments = task.comments.select_related("user").order_by("-created_at")

    # Historique
    history = task.status_history.select_related("changed_by").order_by("-changed_at")[
        :10
    ]

    # Pièces jointes
    attachments = task.attachments.select_related("uploaded_by").order_by(
        "-uploaded_at"
    )

    context = {
        "task": task,
        "comments": comments,
        "history": history,
        "attachments": attachments,
    }

    return render(request, "tasks/task_detail.html", context)


@login_required
def task_update_status(request, task_id):
    """Mise à jour du statut d'une tâche (AJAX)"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    task = get_object_or_404(Task, id=task_id)

    # Vérifier les permissions
    user_companies = request.user.companies.values_list("company_id", flat=True)
    if task.company_id not in user_companies and task.assigned_to != request.user:
        return JsonResponse({"error": "Permission denied"}, status=403)

    new_status = request.POST.get("status")
    notes = request.POST.get("notes", "")

    if new_status not in dict(Task.STATUS_CHOICES):
        return JsonResponse({"error": "Invalid status"}, status=400)

    # Enregistrer l'historique
    TaskStatusHistory.objects.create(
        task=task,
        previous_status=task.status,
        new_status=new_status,
        changed_by=request.user,
        notes=notes,
    )

    # Mettre à jour la tâche
    old_status = task.status
    task.status = new_status
    if new_status == "completed":
        task.completed_at = timezone.now()
    task.save()

    return JsonResponse(
        {
            "success": True,
            "old_status": old_status,
            "new_status": new_status,
            "completed_at": (
                task.completed_at.isoformat() if task.completed_at else None
            ),
        }
    )


@login_required
def task_add_comment(request, task_id):
    """Ajouter un commentaire à une tâche (AJAX)"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    task = get_object_or_404(Task, id=task_id)

    # Vérifier les permissions
    user_companies = request.user.companies.values_list("company_id", flat=True)
    if task.company_id not in user_companies and task.assigned_to != request.user:
        return JsonResponse({"error": "Permission denied"}, status=403)

    comment_text = request.POST.get("comment", "").strip()
    is_internal = request.POST.get("is_internal", "true") == "true"

    if not comment_text:
        return JsonResponse({"error": "Comment cannot be empty"}, status=400)

    comment = TaskComment.objects.create(
        task=task, user=request.user, comment=comment_text, is_internal=is_internal
    )

    return JsonResponse(
        {
            "success": True,
            "comment_id": comment.id,
            "user": request.user.get_full_name() or request.user.username,
            "created_at": comment.created_at.isoformat(),
            "comment": comment.comment,
        }
    )


@login_required
def task_assign(request, task_id):
    """Assigner une tâche à un utilisateur (AJAX)"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    task = get_object_or_404(Task, id=task_id)

    # Vérifier les permissions (seuls les admins peuvent assigner)
    if not request.user.is_admin():
        return JsonResponse({"error": "Permission denied"}, status=403)

    user_id = request.POST.get("user_id")

    from accounts.models import User

    if user_id:
        assigned_user = get_object_or_404(User, id=user_id)
        task.assigned_to = assigned_user
    else:
        task.assigned_to = None

    task.save()

    return JsonResponse(
        {
            "success": True,
            "assigned_to": (
                task.assigned_to.get_full_name() if task.assigned_to else None
            ),
        }
    )


@login_required
def api_tasks_summary(request):
    """API pour obtenir un résumé des tâches (pour widgets)"""
    user = request.user
    user_companies = user.companies.values_list("company_id", flat=True)

    now = timezone.now()

    summary = {
        "my_tasks": {
            "total": Task.objects.filter(
                assigned_to=user, status__in=["pending", "in_progress"]
            ).count(),
            "urgent": Task.objects.filter(
                assigned_to=user,
                status__in=["pending", "in_progress"],
                urgency_score__gte=70,
            ).count(),
            "overdue": Task.objects.filter(
                assigned_to=user, is_overdue=True, status__in=["pending", "in_progress"]
            ).count(),
            "today": Task.objects.filter(
                assigned_to=user,
                due_date__date=now.date(),
                status__in=["pending", "in_progress"],
            ).count(),
        },
        "team_tasks": {
            "unassigned": Task.objects.filter(
                company_id__in=user_companies,
                assigned_to__isnull=True,
                status="pending",
            ).count(),
            "total_pending": Task.objects.filter(
                company_id__in=user_companies, status="pending"
            ).count(),
        },
        "by_type": list(
            Task.objects.filter(assigned_to=user, status__in=["pending", "in_progress"])
            .values("task_type")
            .annotate(count=Count("id"))
        ),
    }

    return JsonResponse(summary)
