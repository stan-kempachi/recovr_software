"""
Settings de déploiement sur le Pi (recovr.stan-aria.dev).
Objectif : version fonctionnelle rapidement — login email/mot de passe,
Google OAuth2 activé seulement si les credentials sont présents.
"""

import os

from .settings import *  # noqa: F403
from .settings import INSTALLED_APPS, MIDDLEWARE

DEBUG = False

PUBLIC_HOST = os.getenv("PUBLIC_HOST", "recovr.stan-aria.dev")
ALLOWED_HOSTS = [PUBLIC_HOST, "localhost", "127.0.0.1"]
CSRF_TRUSTED_ORIGINS = [f"https://{PUBLIC_HOST}"]

# Static servi par whitenoise (pas de nginx devant, juste le proxy ARIA)
MIDDLEWARE = (
    MIDDLEWARE[:1] + ["whitenoise.middleware.WhiteNoiseMiddleware"] + MIDDLEWARE[1:]
)
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

# Auth : login email/mdp sans vérification email (pas de SMTP pour l'instant)
ACCOUNT_EMAIL_VERIFICATION = "none"
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Google OAuth2 : bypass tant que les credentials ne sont pas fournis
if not (
    os.getenv("GOOGLE_OAUTH2_CLIENT_ID") and os.getenv("GOOGLE_OAUTH2_CLIENT_SECRET")
):
    INSTALLED_APPS = [
        a for a in INSTALLED_APPS if a != "allauth.socialaccount.providers.google"
    ]
    SOCIALACCOUNT_PROVIDERS = {}

# Pas de redirection SSL côté Django : TLS terminé par Cloudflare
SECURE_SSL_REDIRECT = False

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
