"""
Settings spécifiques pour l'environnement staging.
"""

import os
from pathlib import Path

from .settings import *  # noqa: F403

# Désactiver le debug en staging
DEBUG = False

# Hosts staging
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

# Base de données staging
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("STAGING_DB_NAME"),
        "USER": os.getenv("STAGING_DB_USER"),
        "PASSWORD": os.getenv("STAGING_DB_PASSWORD"),
        "HOST": os.getenv("STAGING_DB_HOST"),
        "PORT": os.getenv("STAGING_DB_PORT"),
    }
}

# Emails (console pour staging)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Static
STATIC_ROOT = os.path.join(Path(__file__).resolve().parent.parent, "staticfiles")

# SSL / HTTPS (optionnel selon le proxy)
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Exceptions pour healthchecks
SECURE_REDIRECT_EXEMPT = [r"^health/$", r"^nginx-health/$"]

LOGIN_REDIRECT_URL = "/staging/"
