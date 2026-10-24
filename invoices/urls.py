from django.urls import path

from . import views, views_crud

app_name = "invoices"

urlpatterns = [
    # URLs pour la gestion des documents
    path("", views_crud.invoice_list, name="invoice_list"),
    path("new/", views_crud.invoice_create, name="invoice_create"),
    path(
        "invoice/<int:invoice_id>/edit/", views_crud.invoice_edit, name="invoice_edit"
    ),
    path(
        "invoice/<int:invoice_id>/status/",
        views_crud.invoice_change_status,
        name="invoice_change_status",
    ),
    path("clients/", views_crud.client_list, name="client_list"),
    path("clients/new/", views_crud.client_create, name="client_create"),
    path("clients/<int:client_id>/edit/", views_crud.client_edit, name="client_edit"),
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
