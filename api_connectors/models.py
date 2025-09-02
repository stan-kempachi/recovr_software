from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from accounts.models import Company


class APICredential(models.Model):
    """Stockage sécurisé des identifiants API pour les différentes plateformes"""
    PLATFORM_CHOICES = (
        ('chorus_pro', 'Chorus Pro'),
        ('ariba', 'Ariba'),
        ('sap', 'SAP Business Network'),
        ('tradeshift', 'Tradeshift'),
    )

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="api_credentials")
    platform = models.CharField(_("Plateforme"), max_length=20, choices=PLATFORM_CHOICES)
    api_key = models.CharField(_("Clé API"), max_length=255)
    api_secret = models.CharField(_("Secret API"), max_length=255)
    additional_data = models.JSONField(_("Données additionnelles"), blank=True, null=True)
    is_active = models.BooleanField(_("Actif"), default=True)
    last_sync = models.DateTimeField(_("Dernière synchronisation"), null=True, blank=True)
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

    class Meta:
        verbose_name = _("Identifiant API")
        verbose_name_plural = _("Identifiants API")
        unique_together = [['company', 'platform']]

    def __str__(self):
        return f"{self.company.name} - {self.get_platform_display()}"


class APILog(models.Model):
    """Journalisation des appels API"""
    STATUS_CHOICES = (
        ('success', _('Succès')),
        ('error', _('Erreur')),
        ('warning', _('Avertissement')),
    )

    credential = models.ForeignKey(APICredential, on_delete=models.CASCADE, related_name="logs")
    endpoint = models.CharField(_("Point d'accès"), max_length=255)
    request_data = models.JSONField(_("Données de requête"), blank=True, null=True)
    response_data = models.JSONField(_("Données de réponse"), blank=True, null=True)
    status = models.CharField(_("Statut"), max_length=10, choices=STATUS_CHOICES)
    error_message = models.TextField(_("Message d'erreur"), blank=True)
    execution_time = models.FloatField(_("Temps d'exécution (s)"), null=True, blank=True)
    timestamp = models.DateTimeField(_("Horodatage"), auto_now_add=True)

    class Meta:
        verbose_name = _("Log API")
        verbose_name_plural = _("Logs API")
        ordering = ['-timestamp']


class SyncSchedule(models.Model):
    """Planification des synchronisations API"""
    FREQUENCY_CHOICES = (
        ('hourly', _('Toutes les heures')),
        ('daily', _('Quotidien')),
        ('weekly', _('Hebdomadaire')),
        ('monthly', _('Mensuel')),
        ('custom', _('Personnalisé')),
    )

    credential = models.ForeignKey(APICredential, on_delete=models.CASCADE, related_name="sync_schedules")
    frequency = models.CharField(_("Fréquence"), max_length=10, choices=FREQUENCY_CHOICES)
    cron_expression = models.CharField(_("Expression cron"), max_length=100, blank=True)
    last_run = models.DateTimeField(_("Dernière exécution"), null=True, blank=True)
    next_run = models.DateTimeField(_("Prochaine exécution"), null=True, blank=True)
    is_active = models.BooleanField(_("Actif"), default=True)

    class Meta:
        verbose_name = _("Planification de synchronisation")
        verbose_name_plural = _("Planifications de synchronisation")