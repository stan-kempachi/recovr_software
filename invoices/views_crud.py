"""Vues CRUD factures / clients (liste, création, édition, statut)."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.utils import get_user_company

from .forms import ClientForm, InvoiceForm, InvoiceStatusForm
from .models import Client, Invoice

NO_COMPANY_MESSAGE = (
    "Aucune entreprise n'est associée à votre compte. "
    "Demandez à un administrateur de vous rattacher à une entreprise."
)


def _require_company(request):
    company = get_user_company(request.user)
    if company is None:
        messages.error(request, NO_COMPANY_MESSAGE)
    return company


def _readonly(user):
    return getattr(user, "role", "") == "readonly"


def filtered_invoices(company, params):
    """Applique les filtres GET (status, client, platform, q, overdue) aux factures."""
    qs = Invoice.objects.filter(company=company).select_related("client", "currency")
    status = params.get("status", "")
    client = params.get("client", "")
    platform = params.get("platform", "")
    q = params.get("q", "").strip()
    if status == "open":
        qs = qs.filter(status__in=Invoice.OPEN_STATUSES)
    elif status:
        qs = qs.filter(status=status)
    if client:
        qs = qs.filter(client_id=client)
    if platform:
        qs = qs.filter(platform=platform)
    if params.get("overdue"):
        qs = qs.filter(due_date__lt=timezone.localdate()).exclude(status="paid")
    if params.get("non_compliant"):
        qs = qs.filter(is_compliant=False)
    if q:
        qs = qs.filter(
            Q(invoice_number__icontains=q)
            | Q(external_reference__icontains=q)
            | Q(client__name__icontains=q)
        )
    sort = params.get("sort", "-issue_date")
    allowed = {"issue_date", "due_date", "amount_ttc", "status", "invoice_number"}
    if sort.lstrip("-") in allowed:
        qs = qs.order_by(sort, "-id")
    else:
        qs = qs.order_by("-issue_date", "-id")
    return qs


@login_required
def invoice_list(request):
    company = _require_company(request)
    if company is None:
        return render(request, "invoices/invoice_list.html", {"invoices": []})
    invoices = filtered_invoices(company, request.GET)
    today = timezone.localdate()
    paginator = Paginator(invoices, 25)
    page_obj = paginator.get_page(request.GET.get("page"))
    context = {
        "page_obj": page_obj,
        "invoices": page_obj.object_list,
        "clients": Client.objects.filter(company=company).order_by("name"),
        "status_choices": Invoice.STATUS_CHOICES,
        "platform_choices": Invoice.PLATFORM_CHOICES,
        "filters": request.GET,
        "query_string": request.GET.urlencode(),
        "today": today,
        "total_count": paginator.count,
        "readonly": _readonly(request.user),
    }
    return render(request, "invoices/invoice_list.html", context)


@login_required
def invoice_create(request):
    company = _require_company(request)
    if company is None:
        return redirect("invoices:invoice_list")
    if _readonly(request.user):
        return HttpResponseForbidden("Lecture seule.")
    form = InvoiceForm(request.POST or None, company=company)
    if request.method == "POST" and form.is_valid():
        invoice = form.save(commit=False)
        invoice.company = company
        invoice.created_by = request.user
        invoice.save()
        invoice.compute_days_overdue()
        messages.success(request, f"Facture {invoice.invoice_number} créée.")
        return redirect("invoices:invoice_detail", invoice_id=invoice.id)
    return render(
        request,
        "invoices/invoice_form.html",
        {"form": form, "title": "Nouvelle facture", "company": company},
    )


@login_required
def invoice_edit(request, invoice_id):
    company = _require_company(request)
    if company is None:
        return redirect("invoices:invoice_list")
    if _readonly(request.user):
        return HttpResponseForbidden("Lecture seule.")
    invoice = get_object_or_404(Invoice, id=invoice_id, company=company)
    form = InvoiceForm(request.POST or None, instance=invoice, company=company)
    if request.method == "POST" and form.is_valid():
        invoice = form.save()
        invoice.compute_days_overdue()
        messages.success(request, f"Facture {invoice.invoice_number} mise à jour.")
        return redirect("invoices:invoice_detail", invoice_id=invoice.id)
    return render(
        request,
        "invoices/invoice_form.html",
        {
            "form": form,
            "title": f"Modifier {invoice.invoice_number}",
            "invoice": invoice,
            "company": company,
        },
    )


@login_required
@require_POST
def invoice_change_status(request, invoice_id):
    company = _require_company(request)
    if company is None:
        return redirect("invoices:invoice_list")
    if _readonly(request.user):
        return HttpResponseForbidden("Lecture seule.")
    invoice = get_object_or_404(Invoice, id=invoice_id, company=company)
    form = InvoiceStatusForm(request.POST)
    if form.is_valid():
        changed = invoice.change_status(
            form.cleaned_data["status"],
            user=request.user,
            notes=form.cleaned_data["notes"],
        )
        invoice.compute_days_overdue()
        if changed:
            messages.success(
                request, f"Statut passé à « {invoice.get_status_display()} »."
            )
        else:
            messages.info(request, "Le statut est inchangé.")
    else:
        messages.error(request, "Statut invalide.")
    return redirect("invoices:invoice_detail", invoice_id=invoice.id)


@login_required
def client_list(request):
    company = _require_company(request)
    clients = Client.objects.filter(company=company).order_by("name") if company else []
    return render(
        request,
        "invoices/client_list.html",
        {"clients": clients, "readonly": _readonly(request.user)},
    )


@login_required
def client_create(request):
    company = _require_company(request)
    if company is None:
        return redirect("invoices:client_list")
    if _readonly(request.user):
        return HttpResponseForbidden("Lecture seule.")
    form = ClientForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        client = form.save(commit=False)
        client.company = company
        if Client.objects.filter(
            company=company, identifier=client.identifier
        ).exists():
            form.add_error("identifier", "Ce SIRET/SIREN existe déjà pour ce client.")
        else:
            client.save()
            messages.success(request, f"Client {client.name} créé.")
            if request.GET.get("next") == "invoice":
                return redirect("invoices:invoice_create")
            return redirect("invoices:client_list")
    return render(
        request,
        "invoices/client_form.html",
        {"form": form, "title": "Nouveau client"},
    )


@login_required
def client_edit(request, client_id):
    company = _require_company(request)
    if company is None:
        return redirect("invoices:client_list")
    if _readonly(request.user):
        return HttpResponseForbidden("Lecture seule.")
    client = get_object_or_404(Client, id=client_id, company=company)
    form = ClientForm(request.POST or None, instance=client)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Client {client.name} mis à jour.")
        return redirect("invoices:client_list")
    return render(
        request,
        "invoices/client_form.html",
        {"form": form, "title": f"Modifier {client.name}", "client": client},
    )
