from django import forms

from .models import InvoiceDocument


class InvoiceDocumentUploadForm(forms.ModelForm):
    class Meta:
        model = InvoiceDocument
        fields = ["invoice", "document_type", "file", "reference", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        invoice_id = kwargs.pop("invoice_id", None)
        is_quick_upload = kwargs.pop("is_quick_upload", False)
        super().__init__(*args, **kwargs)

        if invoice_id:
            self.fields["invoice"].initial = invoice_id
            self.fields["invoice"].widget = forms.HiddenInput()

        # Rendre le champ invoice optionnel pour les uploads rapides
        if is_quick_upload:
            self.fields["invoice"].required = False
