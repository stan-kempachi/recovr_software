from django.contrib import admin

from .models import Invoice, InvoiceDocument, InvoiceStatusHistory


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number",
        "client",
        "company",
        "status",
        "amount_ttc",
        "due_date",
    )
    search_fields = ("invoice_number", "client__name")
    list_filter = ("status", "company", "client")
    autocomplete_fields = ("currency",)


@admin.register(InvoiceDocument)
class InvoiceDocumentAdmin(admin.ModelAdmin):
    list_display = ("invoice", "document_type", "uploaded_by", "uploaded_at")
    search_fields = ("invoice__invoice_number", "uploaded_by__username")
    list_filter = ("document_type",)
    readonly_fields = ("uploaded_at",)
    autocomplete_fields = ("uploaded_by", "invoice")


@admin.register(InvoiceStatusHistory)
class InvoiceStatusHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "invoice",
        "previous_status",
        "new_status",
        "changed_by",
        "changed_at",
    )
    search_fields = ("invoice__invoice_number", "changed_by__username")
    list_filter = ("previous_status", "new_status")
    readonly_fields = ("changed_at",)
    autocomplete_fields = ("changed_by",)
