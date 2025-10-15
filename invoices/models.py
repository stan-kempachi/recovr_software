# invoices/models.py
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import Company


class Client(models.Model):
    """Modèle pour les clients"""

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="clients"
    )
    name = models.CharField(_("Nom"), max_length=200)
    identifier = models.CharField(_("SIRET/SIREN"), max_length=20)
    contact_name = models.CharField(_("Nom du contact"), max_length=100, blank=True)
    contact_email = models.EmailField(_("Email du contact"), blank=True)
    contact_phone = models.CharField(
        _("Téléphone du contact"), max_length=20, blank=True
    )
    address = models.TextField(_("Adresse"))
    postal_code = models.CharField(_("Code postal"), max_length=10)
    city = models.CharField(_("Ville"), max_length=100)
    country = models.CharField(_("Pays"), max_length=100, default="France")
    notes = models.TextField(_("Notes"), blank=True)
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

    class Meta:
        verbose_name = _("Client")
        verbose_name_plural = _("Clients")
        unique_together = [["company", "identifier"]]

    def __str__(self):
        return self.name


class Invoice(models.Model):
    """Modèle pour les factures"""

    STATUS_CHOICES = (
        ("draft", _("Brouillon")),
        ("submitted", _("Soumise")),
        ("accepted", _("Acceptée")),
        ("rejected", _("Rejetée")),
        ("disputed", _("En litige")),
        ("partially_paid", _("Partiellement payée")),
        ("paid", _("Payée")),
    )

    PLATFORM_CHOICES = (
        ("chorus_pro", "Chorus Pro"),
        ("ariba", "Ariba"),
        ("sap", "SAP Business Network"),
        ("tradeshift", "Tradeshift"),
        ("manual", _("Manuel")),
    )

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="invoices"
    )
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="invoices"
    )
    invoice_number = models.CharField(_("Numéro de facture"), max_length=50)
    external_reference = models.CharField(
        _("Référence externe"), max_length=100, blank=True
    )
    platform = models.CharField(
        _("Plateforme"), max_length=20, choices=PLATFORM_CHOICES
    )
    platform_id = models.CharField(
        _("ID sur la plateforme"), max_length=100, blank=True
    )
    amount_ht = models.DecimalField(_("Montant HT"), max_digits=15, decimal_places=2)
    amount_ttc = models.DecimalField(_("Montant TTC"), max_digits=15, decimal_places=2)
    vat_amount = models.DecimalField(_("Montant TVA"), max_digits=15, decimal_places=2)
    currency = models.ForeignKey(
        "core.Currency", on_delete=models.PROTECT, related_name="invoices"
    )
    issue_date = models.DateField(_("Date d'émission"))
    due_date = models.DateField(_("Date d'échéance"))
    payment_date = models.DateField(_("Date de paiement"), null=True, blank=True)
    status = models.CharField(
        _("Statut"), max_length=20, choices=STATUS_CHOICES, default="draft"
    )
    payment_method = models.CharField(
        _("Méthode de paiement"), max_length=50, blank=True
    )
    notes = models.TextField(_("Notes"), blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_invoices",
    )
    created_at = models.DateTimeField(_("Créée le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mise à jour le"), auto_now=True)
    is_compliant = models.BooleanField(_("Conforme"), default=False)
    days_overdue = models.IntegerField(_("Jours de retard"), default=0)

    def update_compliance_status(self):
        """Vérifier si tous les documents requis sont présents et valides"""
        required_docs = ["FACTURE", "PO", "BL"]  # Liste des types de documents requis

        # Vérifier si tous les types de documents requis sont présents
        existing_doc_types = self.invoicedocument_set.values_list(
            "document_type", flat=True
        )
        all_required_present = all(
            doc_type in existing_doc_types for doc_type in required_docs
        )

        self.is_compliant = all_required_present
        self.save(update_fields=["is_compliant"])
        return self.is_compliant

    class Meta:
        verbose_name = _("Facture")
        verbose_name_plural = _("Factures")
        unique_together = [["company", "invoice_number"]]

    def __str__(self):
        return f"{self.invoice_number} - {self.client.name}"


class InvoiceDocument(models.Model):
    """Documents associés aux factures"""

    DOC_TYPE_CHOICES = (
        ("invoice", _("Facture")),
        ("po", _("Bon de commande")),
        ("bl", _("Bon de livraison")),
        ("pv", _("Procès-verbal")),
        ("cra", _("Compte-rendu d'activité")),
        ("other", _("Autre")),
    )

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents",
    )

    document_type = models.CharField(
        _("Type de document"), max_length=20, choices=DOC_TYPE_CHOICES
    )
    file = models.FileField(_("Fichier"), upload_to="invoice_documents/")
    reference = models.CharField(_("Référence"), max_length=100, blank=True)
    description = models.TextField(_("Description"), blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    uploaded_at = models.DateTimeField(_("Téléchargé le"), auto_now_add=True)

    class Meta:
        verbose_name = _("Document de facture")
        verbose_name_plural = _("Documents de facture")

    def __str__(self):
        return f"{self.get_document_type_display()} - {self.invoice.invoice_number}"


class InvoiceStatusHistory(models.Model):
    """Historique des changements de statut des factures"""

    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="status_history"
    )
    previous_status = models.CharField(_("Statut précédent"), max_length=20, blank=True)
    new_status = models.CharField(_("Nouveau statut"), max_length=20)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    changed_at = models.DateTimeField(_("Modifié le"), auto_now_add=True)
    notes = models.TextField(_("Notes"), blank=True)

    class Meta:
        verbose_name = _("Historique de statut")
        verbose_name_plural = _("Historiques de statut")
        ordering = ["-changed_at"]
