import json

from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, F, Q, Sum
from django.db.models.functions import TruncDay, TruncMonth, TruncWeek
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from accounts.models import Company
from invoices.models import Invoice
from tasks.models import Client, Task

from .models import Dashboard, Widget


@login_required
def dashboard_view(request):
    """Vue principale du tableau de bord"""

    company = Company.objects.filter(
        users__user=request.user, users__is_primary=True
    ).first()

    # Charger le tableau de bord de l'utilisateur ou créer un par défaut
    try:
        dashboard = Dashboard.objects.filter(user=request.user, is_default=True).first()
    except Dashboard.DoesNotExist:
        dashboard = Dashboard.objects.create(
            user=request.user, name="Tableau de bord principal", is_default=True
        )

    # Récupérer les widgets associés au tableau de bord
    widgets = Widget.objects.filter(dashboard=dashboard).order_by(
        "position_y", "position_x"
    )

    # Préparer les données pour les KPIs
    kpis = get_kpi_data(company)

    # Statistiques financières
    financial_stats = get_financial_statistics(company)

    # Données pour les graphiques
    chart_data = get_chart_data(company)

    # Récupérer les tâches (similaire à votre vue task_list)
    tasks = Task.objects.all()

    context = {
        "dashboard": dashboard,
        "widgets": widgets,
        "kpis": kpis,
        "financial_stats": financial_stats,
        "chart_data": chart_data,
        "tasks": tasks,
        "clients": Client.objects.all(),
    }

    return render(request, "dashboard.html", context)


def get_kpi_data(company):
    """Récupère les données pour les KPIs du tableau de bord"""

    today = timezone.now().date()
    thirty_days_ago = today - timezone.timedelta(days=30)

    # Total des factures non payées
    unpaid_invoices = Invoice.objects.filter(
        company=company,
        status__in=["submitted", "accepted", "disputed", "partially_paid"],
    ).aggregate(
        total=Sum("amount_ttc"),  # Utilisez amount_ttc au lieu de total_amount
        count=Count("id"),
    )

    # Factures en retard
    overdue_invoices = Invoice.objects.filter(
        company=company,
        status__in=["submitted", "accepted", "disputed", "partially_paid"],
        due_date__lt=today,
    ).aggregate(
        total=Sum("amount_ttc"),  # Utilisez amount_ttc au lieu de total_amount
        count=Count("id"),
        avg_days=Avg("days_overdue"),
    )

    # Factures récemment payées
    recent_paid = Invoice.objects.filter(
        company=company, status="paid", payment_date__gte=thirty_days_ago
    ).aggregate(
        total=Sum("amount_ttc"),  # Utilisez amount_ttc au lieu de total_amount
        count=Count("id"),
    )

    # Tâches à faire
    pending_tasks = Task.objects.filter(
        company=company, status__in=["pending", "in_progress"]
    ).count()

    return {
        "unpaid_invoices": unpaid_invoices,
        "overdue_invoices": overdue_invoices,
        "recent_paid": recent_paid,
        "pending_tasks": pending_tasks,
    }


def get_financial_statistics(company):
    """Récupère les statistiques financières pour le tableau de bord"""

    today = timezone.now().date()
    current_year = today.year

    # Chiffre d'affaires par mois pour l'année en cours
    monthly_revenue = (
        Invoice.objects.filter(company=company, issue_date__year=current_year)
        .annotate(month=TruncMonth("issue_date"))
        .values("month")
        .annotate(
            total=Sum("amount_ttc")  # Utilisez amount_ttc au lieu de total_amount
        )
        .order_by("month")
    )

    # Taux de recouvrement (montant payé / montant total)
    total_billed = Invoice.objects.filter(
        company=company, issue_date__year=current_year
    ).aggregate(
        total=Sum("amount_ttc")
    )  # Utilisez amount_ttc au lieu de total_amount

    total_paid = Invoice.objects.filter(
        company=company, status="paid", issue_date__year=current_year
    ).aggregate(
        total=Sum("amount_ttc")
    )  # Utilisez amount_ttc au lieu de total_amount

    recovery_rate = 0
    if total_billed["total"] and total_billed["total"] > 0:
        recovery_rate = (total_paid["total"] or 0) / total_billed["total"] * 100

    # Délai moyen de paiement
    avg_payment_time = (
        Invoice.objects.filter(
            company=company, status="paid", payment_date__year=current_year
        )
        .exclude(payment_date=None)
        .annotate(days_to_pay=F("payment_date") - F("issue_date"))
        .aggregate(avg_days=Avg("days_to_pay"))
    )

    return {
        "monthly_revenue": list(monthly_revenue),
        "recovery_rate": round(recovery_rate, 2),
        "avg_payment_time": avg_payment_time,
    }


def get_chart_data(company):
    """Récupère les données pour les graphiques du tableau de bord"""

    today = timezone.now().date()
    ninety_days_ago = today - timezone.timedelta(days=90)

    # Flux de trésorerie (entrées vs sorties)
    cash_flow = (
        Invoice.objects.filter(company=company, issue_date__gte=ninety_days_ago)
        .annotate(week=TruncWeek("issue_date"))
        .values("week")
        .annotate(
            billed=Sum("amount_ttc"),  # Utilisez amount_ttc au lieu de total_amount
            paid=Sum(
                "amount_ttc", filter=Q(status="paid")
            ),  # Utilisez amount_ttc au lieu de total_amount
        )
        .order_by("week")
    )

    # Répartition par statut
    status_distribution = (
        Invoice.objects.filter(company=company, issue_date__gte=ninety_days_ago)
        .values("status")
        .annotate(
            count=Count("id"),
            amount=Sum("amount_ttc"),  # Utilisez amount_ttc au lieu de total_amount
        )
        .order_by("status")
    )

    # Activité quotidienne
    daily_activity = (
        Invoice.objects.filter(company=company, created_at__date__gte=ninety_days_ago)
        .annotate(day=TruncDay("created_at"))
        .values("day")
        .annotate(new_invoices=Count("id"))
        .order_by("day")
    )

    return {
        "cash_flow": list(cash_flow),
        "status_distribution": list(status_distribution),
        "daily_activity": list(daily_activity),
    }


@login_required
def save_dashboard_layout(request):
    """Enregistre la disposition du tableau de bord"""

    if request.method == "POST" and request.is_ajax():
        layout_data = json.loads(request.body)  # Modifié pour utiliser json.loads
        dashboard_id = layout_data.get("dashboard_id")

        try:
            dashboard = Dashboard.objects.get(id=dashboard_id, user=request.user)

            # Mettre à jour la position des widgets
            for widget_data in layout_data.get("widgets", []):
                widget_id = widget_data.get("id")
                position_x = widget_data.get("position_x")
                position_y = widget_data.get("position_y")
                width = widget_data.get("width", 1)
                height = widget_data.get("height", 1)

                Widget.objects.filter(id=widget_id, dashboard=dashboard).update(
                    position_x=position_x,
                    position_y=position_y,
                    width=width,
                    height=height,
                )

            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "Requête invalide"})


@login_required
def toggle_widget(request, widget_id):
    """Active ou désactive un widget"""

    if request.method == "POST" and request.is_ajax():
        try:
            widget = Widget.objects.get(id=widget_id, dashboard__user=request.user)
            widget.is_active = not widget.is_active
            widget.save()

            return JsonResponse({"status": "success", "is_active": widget.is_active})
        except Widget.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Widget non trouvé"})

    return JsonResponse({"status": "error", "message": "Requête invalide"})


@login_required
def add_widget(request):
    """Ajoute un nouveau widget au tableau de bord"""

    if request.method == "POST" and request.is_ajax():
        data = json.loads(request.body)  # Modifié pour utiliser json.loads
        dashboard_id = data.get("dashboard_id")
        widget_type = data.get("widget_type")
        title = data.get("title")
        data_source = data.get("data_source", "")
        filter_criteria = data.get("filter_criteria", {})
        position_x = data.get("position_x", 0)
        position_y = data.get("position_y", 0)
        width = data.get("width", 1)
        height = data.get("height", 1)
        refresh_rate = data.get("refresh_rate", 60)

        try:
            dashboard = Dashboard.objects.get(id=dashboard_id, user=request.user)

            # Si aucune position n'est spécifiée, placer le widget à la fin
            if position_x is None and position_y is None:
                # Trouver la dernière position Y
                last_widget = (
                    Widget.objects.filter(dashboard=dashboard)
                    .order_by("-position_y", "-position_x")
                    .first()
                )
                if last_widget:
                    position_y = last_widget.position_y
                    position_x = last_widget.position_x + 1
                    # Si on atteint le bord, passer à la ligne suivante
                    if position_x > 3:  # Supposons que la grille a 4 colonnes max
                        position_x = 0
                        position_y += 1
                else:
                    position_x = 0
                    position_y = 0

            # Créer le nouveau widget
            widget = Widget.objects.create(
                dashboard=dashboard,
                widget_type=widget_type,
                title=title,
                data_source=data_source,
                filter_criteria=filter_criteria,
                position_x=position_x,
                position_y=position_y,
                width=width,
                height=height,
                refresh_rate=refresh_rate,
            )

            return JsonResponse(
                {
                    "status": "success",
                    "widget": {
                        "id": widget.id,
                        "title": widget.title,
                        "type": widget.widget_type,
                        "position_x": widget.position_x,
                        "position_y": widget.position_y,
                        "width": widget.width,
                        "height": widget.height,
                    },
                }
            )
        except Dashboard.DoesNotExist:
            return JsonResponse(
                {"status": "error", "message": "Tableau de bord non trouvé"}
            )
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "Requête invalide"})
