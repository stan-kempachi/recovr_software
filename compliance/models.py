from django.db import models
from django.utils.translation import gettext_lazy as _


class DocumentType(models.Model):
    """Types de documents requis pour la conformité des factures"""

    code = models.CharField(_("Code"), max_length=10, unique=True)
    name = models.CharField(_("Nom"), max_length=100)
    description = models.TextField(_("Description"), blank=True)
    is_mandatory = models.BooleanField(_("Obligatoire"), default=True)

    class Meta:
        verbose_name = _("Type de document")
        verbose_name_plural = _("Types de document")

    def __str__(self):
        return self.name


class ComplianceRule(models.Model):
    """Règles de conformité pour les factures"""

    name = models.CharField(_("Nom"), max_length=100)
    description = models.TextField(_("Description"), blank=True)
    rule_type = models.CharField(_("Type de règle"), max_length=50)
    rule_definition = models.JSONField(_("Définition de la règle"))
    is_active = models.BooleanField(_("Active"), default=True)
    priority = models.IntegerField(_("Priorité"), default=0)
    created_at = models.DateTimeField(_("Créée le"), auto_now_add=True)

    class Meta:
        verbose_name = _("Règle de conformité")
        verbose_name_plural = _("Règles de conformité")
        ordering = ["priority", "name"]

    def __str__(self):
        return self.name


class ComplianceCheckResult(models.Model):
    """Résultats des vérifications de conformité"""

    STATUS_CHOICES = (
        ("pass", _("Conforme")),
        ("fail", _("Non conforme")),
        ("warning", _("Avertissement")),
        ("pending", _("En attente")),
    )

    invoice = models.ForeignKey(
        "invoices.Invoice", on_delete=models.CASCADE, related_name="compliance_checks"
    )
    rule = models.ForeignKey(
        ComplianceRule, on_delete=models.CASCADE, related_name="check_results"
    )
    status = models.CharField(_("Statut"), max_length=10, choices=STATUS_CHOICES)
    details = models.JSONField(_("Détails"), blank=True, null=True)
    checked_at = models.DateTimeField(_("Vérifié le"), auto_now=True)

    class Meta:
        verbose_name = _("Résultat de vérification de conformité")
        verbose_name_plural = _("Résultats de vérification de conformité")
        unique_together = [["invoice", "rule"]]
