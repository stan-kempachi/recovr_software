"""
Settings spécifiques pour l'environnement production.
"""

import os
from pathlib import Path

from .settings import *  # noqa: F403

# Désactiver le debug en production
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
SESSION_COOKIE_SECURE = True
