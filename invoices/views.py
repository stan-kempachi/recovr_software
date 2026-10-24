import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import FileResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import InvoiceDocumentUploadForm
from .models import Invoice, InvoiceDocument
from .validators import validate_invoice_document


@login_required
def upload_document(request, invoice_id=None):
    """View to handle document uploads, both from dedicated page and quick upload modal"""
    invoice = None
    if invoice_id:
        invoice = get_object_or_404(Invoice, id=invoice_id)

    # Vérifier si c'est un upload rapide
    is_quick_upload = "is_quick_upload" in request.POST

    if request.method == "POST":
        # Créer le formulaire avec l'option is_quick_upload
        form = InvoiceDocumentUploadForm(
            request.POST,
            request.FILES,
            invoice_id=invoice_id,
            is_quick_upload=is_quick_upload,
        )

        if form.is_valid():
            document = form.save(commit=False)
            document.uploaded_by = request.user
            document.save()

            # Valider le document en fonction de son type
            validation_result = validate_invoice_document(document)

            # Si c'est une requête AJAX, retourner une réponse JSON
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "success": True,
                        "message": f"Document '{document.get_document_type_display()}' téléchargé avec succès.",
                    }
                )

            if validation_result["is_valid"]:
                messages.success(
                    request,
                    f"Document '{document.get_document_type_display()}' téléchargé avec succès.",
                )

                # Mise à jour du statut de conformité de la facture si nécessaire
                invoice = document.invoice
                if invoice:  # Vérifier que invoice n'est pas None
                    invoice.update_compliance_status()
            else:
                messages.warning(
                    request,
                    f"Document téléchargé mais avec des avertissements: {validation_result['message']}",
                )

            # Redirection - si depuis dashboard, retour au dashboard
            if request.POST.get("source") == "dashboard":
                return redirect("dashboard:dashboard")
            # Si c'est un upload rapide sans facture associée
            elif is_quick_upload and not document.invoice:
                return redirect("dashboard")  # Ou une autre vue appropriée
            # Sinon, redirection vers la page de détail de la facture
            elif document.invoice:
                return redirect("invoices:invoice_detail", invoice_id=invoice_id)
            else:
                return redirect("invoices:document_list")

    else:
        form = InvoiceDocumentUploadForm(invoice_id=invoice_id)

    context = {"form": form, "invoice": invoice, "is_quick_upload": is_quick_upload}

    # Si c'est une requête AJAX pour le modal
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return render(request, "upload_document_partial.html", context)

    # Pour la page complète
    return render(request, "upload_document.html", context)


@login_required
def download_document(request, document_id):
    document = get_object_or_404(InvoiceDocument, id=document_id)
    response = FileResponse(document.file, as_attachment=True)
    return response


@login_required
def delete_document(request, document_id):
    document = get_object_or_404(InvoiceDocument, id=document_id)

    # Vérifier si le document est associé à une facture
    invoice_id = None
    if document.invoice:
        invoice_id = document.invoice.id

    # Suppression du fichier physique si nécessaire
    if document.file:
        if os.path.isfile(document.file.path):
            os.remove(document.file.path)

    # Suppression de l'entrée en base de données
    invoice_obj = document.invoice
    document.delete()
    if invoice_obj:
        invoice_obj.update_compliance_status()

    # Redirection vers la liste des documents ou la facture associée
    if invoice_id:
        return redirect("invoices:invoice_detail", invoice_id=invoice_id)
    else:
        return redirect("invoices:document_list")


@login_required
def api_invoice_list(request):
    """API endpoint to get invoices for quick upload"""
    # Récupérer les IDs des entreprises associées à l'utilisateur
    company_ids = request.user.companies.values_list("company_id", flat=True)

    # Filtrer les factures
    invoices = Invoice.objects.filter(company_id__in=company_ids)

    data = [
        {
            "id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "client": {"id": invoice.client.id, "name": invoice.client.name},
        }
        for invoice in invoices
    ]
    return JsonResponse(data, safe=False)


def api_invoices(request):
    """API pour récupérer la liste des factures"""
    invoices = Invoice.objects.all()
    data = [
        {
            "id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "client": {
                "name": invoice.client.name if invoice.client else "Sans client"
            },
        }
        for invoice in invoices
    ]
    return JsonResponse(data, safe=False)


def api_document_types(request):
    """API pour récupérer les types de documents"""
    document_types = [
        {"id": key, "name": value} for key, value in InvoiceDocument.DOC_TYPE_CHOICES
    ]

    return JsonResponse(document_types, safe=False)


def document_list(request):
    """
    Affiche la liste de tous les documents.
    """
    documents = InvoiceDocument.objects.all().order_by("-uploaded_at")

    if not request.user.is_staff:
        documents = documents.filter(uploaded_by=request.user)

    paginator = Paginator(documents, 20)  # 20 documents par page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "documents": documents,
        "document_types": dict(InvoiceDocument.DOC_TYPE_CHOICES),
    }

    return render(request, "document_list.html", context)


def invoice_detail(request, invoice_id):
    """
    Affiche les détails d'une facture et ses documents associés.
    """
    from .forms import InvoiceStatusForm

    company_ids = request.user.companies.values_list("company_id", flat=True)
    invoice = get_object_or_404(Invoice, id=invoice_id, company_id__in=company_ids)
    invoice.compute_days_overdue()
    documents = invoice.documents.all().order_by("document_type")

    context = {
        "invoice": invoice,
        "documents": documents,
        "missing_documents": invoice.missing_documents(),
        "status_history": invoice.status_history.select_related("changed_by")[:20],
        "status_form": InvoiceStatusForm(initial={"status": invoice.status}),
        "readonly": getattr(request.user, "role", "") == "readonly",
    }
    return render(request, "invoices/invoice_detail.html", context)
