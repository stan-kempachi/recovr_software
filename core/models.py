# core/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _


class Currency(models.Model):
    """Modèle pour les devises"""
    code = models.CharField(_("Code"), max_length=3, unique=True)
    name = models.CharField(_("Nom"), max_length=100)
    symbol = models.CharField(_("Symbole"), max_length=5)

    class Meta:
        verbose_name = _("Devise")
        verbose_name_plural = _("Devises")

    def __str__(self):
        return f"{self.code} - {self.name}"


class Country(models.Model):
    """Modèle pour les pays"""
    code = models.CharField(_("Code"), max_length=2, unique=True)
    name = models.CharField(_("Nom"), max_length=100)

    class Meta:
        verbose_name = _("Pays")
        verbose_name_plural = _("Pays")

    def __str__(self):
        return self.name


class SystemSetting(models.Model):
    """Paramètres système globaux"""
    key = models.CharField(_("Clé"), max_length=100, unique=True)
    value = models.JSONField(_("Valeur"))
    description = models.TextField(_("Description"), blank=True)
    is_public = models.BooleanField(_("Public"), default=False)

    class Meta:
        verbose_name = _("Paramètre système")
        verbose_name_plural = _("Paramètres système")

    def __str__(self):
        return self.key


class AuditLog(models.Model):
    """Journal d'audit pour traçabilité des actions"""
    ACTION_CHOICES = (
        ('create', _('Création')),
        ('update', _('Modification')),
        ('delete', _('Suppression')),
        ('login', _('Connexion')),
        ('logout', _('Déconnexion')),
        ('export', _('Export')),
        ('import', _('Import')),
        ('other', _('Autre')),
    )

    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs"
    )
    action = models.CharField(_("Action"), max_length=10, choices=ACTION_CHOICES)
    content_type = models.CharField(_("Type de contenu"), max_length=100)
    object_id = models.CharField(_("ID de l'objet"), max_length=50, blank=True)
    timestamp = models.DateTimeField(_("Horodatage"), auto_now_add=True)
    ip_address = models.GenericIPAddressField(_("Adresse IP"), blank=True, null=True)
    user_agent = models.TextField(_("Agent utilisateur"), blank=True)
    details = models.JSONField(_("Détails"), blank=True, null=True)

    class Meta:
        verbose_name = _("Journal d'audit")
        verbose_name_plural = _("Journaux d'audit")
        ordering = ['-timestamp']