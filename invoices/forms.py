from django import forms

from core.models import Currency

from .models import Client, Invoice, InvoiceDocument


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


INPUT_CLASS = (
    "w-full rounded-lg border border-gray-300 px-3 py-2 text-sm "
    "focus:border-blue-500 focus:ring-blue-500"
)


class TailwindFormMixin:
    """Applique les classes Tailwind aux widgets."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = field.widget.attrs.get("class", "")
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = f"{css} h-4 w-4 rounded".strip()
            else:
                field.widget.attrs["class"] = f"{css} {INPUT_CLASS}".strip()


class ClientForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            "name",
            "identifier",
            "contact_name",
            "contact_email",
            "contact_phone",
            "address",
            "postal_code",
            "city",
            "country",
            "notes",
        ]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 2}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class InvoiceForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            "client",
            "invoice_number",
            "external_reference",
            "platform",
            "platform_id",
            "amount_ht",
            "vat_amount",
            "amount_ttc",
            "currency",
            "issue_date",
            "due_date",
            "payment_method",
            "notes",
        ]
        widgets = {
            "issue_date": forms.DateInput(attrs={"type": "date"}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company = company
        if company is not None:
            self.fields["client"].queryset = Client.objects.filter(company=company)
        self.fields["vat_amount"].required = False
        self.fields["vat_amount"].help_text = "Calculé (TTC − HT) si laissé vide."
        if not self.instance.pk:
            default_currency = Currency.objects.filter(code="EUR").first()
            if default_currency:
                self.fields["currency"].initial = default_currency.pk

    def clean(self):
        cleaned = super().clean()
        ht, ttc = cleaned.get("amount_ht"), cleaned.get("amount_ttc")
        if ht is not None and ttc is not None:
            if ttc < ht:
                self.add_error("amount_ttc", "Le TTC ne peut pas être inférieur au HT.")
            elif cleaned.get("vat_amount") in (None, ""):
                cleaned["vat_amount"] = ttc - ht
        issue, due = cleaned.get("issue_date"), cleaned.get("due_date")
        if issue and due and due < issue:
            self.add_error("due_date", "L'échéance doit être postérieure à l'émission.")
        number = cleaned.get("invoice_number")
        if number and self.company is not None:
            qs = Invoice.objects.filter(company=self.company, invoice_number=number)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error("invoice_number", "Ce numéro existe déjà.")
        return cleaned


class InvoiceStatusForm(forms.Form):
    status = forms.ChoiceField(
        choices=Invoice.STATUS_CHOICES,
        widget=forms.Select(attrs={"class": INPUT_CLASS}),
    )
    notes = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": INPUT_CLASS, "placeholder": "Commentaire (optionnel)"}
        ),
    )
