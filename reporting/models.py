# reporting/models.py
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import Company


class Report(models.Model):
    """Définition des rapports"""

    TYPE_CHOICES = (
        ("invoice_status", _("Statut des factures")),
        ("payment_delays", _("Délais de paiement")),
        ("compliance", _("Conformité")),
        ("platform_performance", _("Performance des plateformes")),
        ("custom", _("Personnalisé")),
    )

    FORMAT_CHOICES = (
        ("excel", "Excel"),
        ("csv", "CSV"),
        ("pdf", "PDF"),
        ("json", "JSON"),
    )

    name = models.CharField(_("Nom"), max_length=100)
    description = models.TextField(_("Description"), blank=True)
    report_type = models.CharField(
        _("Type de rapport"), max_length=20, choices=TYPE_CHOICES
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="reports"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_reports",
    )
    query_parameters = models.JSONField(
        _("Paramètres de requête"), blank=True, null=True
    )
    default_format = models.CharField(
        _("Format par défaut"), max_length=10, choices=FORMAT_CHOICES, default="excel"
    )
    is_public = models.BooleanField(_("Public"), default=False)
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

    class Meta:
        verbose_name = _("Rapport")
        verbose_name_plural = _("Rapports")

    def __str__(self):
        return self.name


class ReportSchedule(models.Model):
    """Planification des rapports automatiques"""

    FREQUENCY_CHOICES = (
        ("daily", _("Quotidien")),
        ("weekly", _("Hebdomadaire")),
        ("monthly", _("Mensuel")),
        ("quarterly", _("Trimestriel")),
    )

    report = models.ForeignKey(
        Report, on_delete=models.CASCADE, related_name="schedules"
    )
    frequency = models.CharField(
        _("Fréquence"), max_length=10, choices=FREQUENCY_CHOICES
    )
    day_of_week = models.IntegerField(
        _("Jour de la semaine"), null=True, blank=True
    )  # 0=Lundi, 6=Dimanche
    day_of_month = models.IntegerField(_("Jour du mois"), null=True, blank=True)
    recipients = models.JSONField(_("Destinataires"))
    format = models.CharField(_("Format"), max_length=10, choices=Report.FORMAT_CHOICES)
    is_active = models.BooleanField(_("Actif"), default=True)
    last_sent = models.DateTimeField(_("Dernier envoi"), null=True, blank=True)
    next_scheduled = models.DateTimeField(
        _("Prochain envoi planifié"), null=True, blank=True
    )

    class Meta:
        verbose_name = _("Planification de rapport")
        verbose_name_plural = _("Planifications de rapport")


class ReportExecution(models.Model):
    """Historique des exécutions de rapports"""

    STATUS_CHOICES = (
        ("pending", _("En attente")),
        ("running", _("En cours")),
        ("completed", _("Terminé")),
        ("failed", _("Échoué")),
    )

    report = models.ForeignKey(
        Report, on_delete=models.CASCADE, related_name="executions"
    )
    schedule = models.ForeignKey(
        ReportSchedule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="executions",
    )
    executed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    status = models.CharField(
        _("Statut"), max_length=10, choices=STATUS_CHOICES, default="pending"
    )
    started_at = models.DateTimeField(_("Démarré le"), auto_now_add=True)
    completed_at = models.DateTimeField(_("Terminé le"), null=True, blank=True)
    parameters_used = models.JSONField(_("Paramètres utilisés"), blank=True, null=True)
    error_message = models.TextField(_("Message d'erreur"), blank=True)
    result_file = models.FileField(
        _("Fichier résultat"), upload_to="report_results/", null=True, blank=True
    )

    class Meta:
        verbose_name = _("Exécution de rapport")
        verbose_name_plural = _("Exécutions de rapport")
        ordering = ["-started_at"]
