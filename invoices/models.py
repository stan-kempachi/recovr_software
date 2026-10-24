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

    REQUIRED_DOCUMENT_TYPES = ("invoice", "po", "bl")
    OPEN_STATUSES = ("submitted", "accepted", "disputed", "partially_paid")

    def missing_documents(self):
        """Liste des types de documents requis absents (libellés lisibles)."""
        existing = set(self.documents.values_list("document_type", flat=True))
        labels = dict(InvoiceDocument.DOC_TYPE_CHOICES)
        return [
            str(labels[code])
            for code in self.REQUIRED_DOCUMENT_TYPES
            if code not in existing
        ]

    def update_compliance_status(self):
        """Vérifie si tous les documents requis sont présents"""
        self.is_compliant = not self.missing_documents()
        self.save(update_fields=["is_compliant"])
        return self.is_compliant

    def compute_days_overdue(self, today=None):
        """Jours de retard : échéance dépassée et facture non payée."""
        from django.utils import timezone

        today = today or timezone.localdate()
        if self.status == "paid" or self.due_date >= today:
            days = 0
        else:
            days = (today - self.due_date).days
        if days != self.days_overdue:
            self.days_overdue = days
            self.save(update_fields=["days_overdue"])
        return days

    @property
    def is_overdue(self):
        return self.days_overdue > 0

    def change_status(self, new_status, user=None, notes=""):
        """Change le statut en traçant l'historique ; renseigne payment_date si payée."""
        from django.utils import timezone

        if new_status == self.status:
            return False
        previous = self.status
        self.status = new_status
        update_fields = ["status", "updated_at"]
        if new_status == "paid":
            if not self.payment_date:
                self.payment_date = timezone.localdate()
                update_fields.append("payment_date")
            self.days_overdue = 0
            update_fields.append("days_overdue")
        self.save(update_fields=update_fields)
        InvoiceStatusHistory.objects.create(
            invoice=self,
            previous_status=previous,
            new_status=new_status,
            changed_by=user,
            notes=notes,
        )
        return True

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
