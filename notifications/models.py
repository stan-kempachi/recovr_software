# notifications/models.py
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class NotificationType(models.Model):
    """Types de notifications configurables"""
    code = models.CharField(_("Code"), max_length=50, unique=True)
    name = models.CharField(_("Nom"), max_length=100)
    description = models.TextField(_("Description"), blank=True)
    is_active = models.BooleanField(_("Actif"), default=True)
    email_template = models.CharField(_("Template email"), max_length=100, blank=True)
    app_template = models.CharField(_("Template application"), max_length=100, blank=True)

    class Meta:
        verbose_name = _("Type de notification")
        verbose_name_plural = _("Types de notification")

    def __str__(self):
        return self.name


class NotificationPreference(models.Model):
    """Préférences de notification par utilisateur"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name="notification_preferences")
    notification_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE, related_name="user_preferences")
    email_enabled = models.BooleanField(_("Email activé"), default=True)
    app_enabled = models.BooleanField(_("Notification in-app activée"), default=True)

    class Meta:
        verbose_name = _("Préférence de notification")
        verbose_name_plural = _("Préférences de notification")
        unique_together = [['user', 'notification_type']]


class Notification(models.Model):
    """Notifications envoyées aux utilisateurs"""
    PRIORITY_CHOICES = (
        ('low', _('Basse')),
        ('normal', _('Normale')),
        ('high', _('Haute')),
        ('urgent', _('Urgente')),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    notification_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(_("Titre"), max_length=200)
    message = models.TextField(_("Message"))
    link = models.CharField(_("Lien"), max_length=255, blank=True)
    priority = models.CharField(_("Priorité"), max_length=10, choices=PRIORITY_CHOICES, default='normal')
    is_read = models.BooleanField(_("Lu"), default=False)
    read_at = models.DateTimeField(_("Lu le"), null=True, blank=True)
    created_at = models.DateTimeField(_("Créée le"), auto_now_add=True)

    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class EmailLog(models.Model):
    """Journal des emails envoyés"""
    STATUS_CHOICES = (
        ('queued', _('En file d\'attente')),
        ('sent', _('Envoyé')),
        ('delivered', _('Livré')),
        ('opened', _('Ouvert')),
        ('clicked', _('Cliqué')),
        ('bounced', _('Rejeté')),
        ('failed', _('Échoué')),
    )

    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name="email_logs", null=True,
                                     blank=True)
    recipient = models.EmailField(_("Destinataire"))
    subject = models.CharField(_("Sujet"), max_length=255)
    body = models.TextField(_("Corps"))
    status = models.CharField(_("Statut"), max_length=10, choices=STATUS_CHOICES, default='queued')
    sent_at = models.DateTimeField(_("Envoyé le"), null=True, blank=True)
    error_message = models.TextField(_("Message d'erreur"), blank=True)

    class Meta:
        verbose_name = _("Journal d'email")
        verbose_name_plural = _("Journaux d'email")
        ordering = ['-sent_at']