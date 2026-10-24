from django.urls import path

from . import views

app_name = "reporting"

urlpatterns = [
    path("export/invoices/", views.export_invoices, name="export_invoices"),
]
