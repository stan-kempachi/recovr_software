"""
Settings spécifiques pour l'environnement production.
"""

import os
from pathlib import Path

from . import settings  # noqa: F401

MIDDLEWARE = settings.MIDDLEWARE

DEBUG = False
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

# Base de données production
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("PRODUCTION_DB_NAME"),
        "USER": os.getenv("PRODUCTION_DB_USER"),
        "PASSWORD": os.getenv("PRODUCTION_DB_PASSWORD"),
        "HOST": os.getenv("PRODUCTION_DB_HOST"),
        "PORT": os.getenv("PRODUCTION_DB_PORT"),
    }
}

# Static
STATIC_ROOT = os.path.join(Path(__file__).resolve().parent.parent, "staticfiles")

# SSL / sécurité
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Exceptions pour healthchecks
SECURE_REDIRECT_EXEMPT = [r"^health/$", r"^nginx-health/$"]
