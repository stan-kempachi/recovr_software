from django.urls import path

from . import views

app_name = "invoices"

urlpatterns = [
    # URLs pour la gestion des documents
    path("documents/", views.document_list, name="document_list"),
    path("document/upload/", views.upload_document, name="upload_document"),
    path(
        "document/upload/<int:invoice_id>/",
        views.upload_document,
        name="upload_document",
    ),
    path(
        "document/download/<int:document_id>/",
        views.download_document,
        name="download_document",
    ),
    path(
        "document/delete/<int:document_id>/",
        views.delete_document,
        name="delete_document",
    ),
    path("invoice/<int:invoice_id>/", views.invoice_detail, name="invoice_detail"),
    # API pour le téléchargement rapide
    path("api/invoices/", views.api_invoice_list, name="api_invoice_list"),
    path("api/document-types/", views.api_document_types, name="api_document_types"),
]
