"""Création de notifications in-app (et email si un backend SMTP est configuré)."""

import logging

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import EmailLog, Notification, NotificationPreference, NotificationType

logger = logging.getLogger(__name__)

DEFAULT_TYPES = {
    "invoice_overdue": "Facture en retard",
    "invoice_non_compliant": "Facture non conforme",
    "invoice_status_changed": "Changement de statut",
    "system": "Information système",
}


def get_type(code):
    ntype, _ = NotificationType.objects.get_or_create(
        code=code, defaults={"name": DEFAULT_TYPES.get(code, code)}
    )
    return ntype


def _prefs(user, ntype):
    pref = NotificationPreference.objects.filter(
        user=user, notification_type=ntype
    ).first()
    app_enabled = pref.app_enabled if pref else True
    email_enabled = pref.email_enabled if pref else user.notification_email
    return app_enabled and user.notification_app, email_enabled


def notify(user, code, title, message, link="", priority="normal", send_email=False):
    """Crée une notification pour `user`. Retourne la Notification ou None."""
    ntype = get_type(code)
    if not ntype.is_active:
        return None
    app_enabled, email_enabled = _prefs(user, ntype)
    if not app_enabled:
        return None
    notification = Notification.objects.create(
        user=user,
        notification_type=ntype,
        title=title,
        message=message,
        link=link,
        priority=priority,
    )
    if send_email and email_enabled and user.email:
        _send_email(notification)
    return notification


def _send_email(notification):
    log = EmailLog.objects.create(
        notification=notification,
        recipient=notification.user.email,
        subject=f"[RecovR] {notification.title}",
        body=notification.message,
    )
    try:
        send_mail(
            log.subject,
            log.body,
            getattr(settings, "DEFAULT_FROM_EMAIL", None),
            [log.recipient],
            fail_silently=False,
        )
        log.status = "sent"
        log.sent_at = timezone.now()
    except Exception as exc:  # noqa: BLE001 - on journalise, on ne casse pas le flux
        logger.warning("Envoi email impossible : %s", exc)
        log.status = "failed"
        log.error_message = str(exc)
    log.save(update_fields=["status", "sent_at", "error_message"])


def already_notified_today(user, code, link):
    """Évite de renvoyer la même alerte plusieurs fois par jour."""
    return Notification.objects.filter(
        user=user,
        notification_type__code=code,
        link=link,
        created_at__date=timezone.localdate(),
    ).exists()


def unread_count(user):
    if not user.is_authenticated:
        return 0
    return Notification.objects.filter(user=user, is_read=False).count()
