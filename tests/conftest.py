import os

# Définir le module de paramètres Django avant d'importer
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings_test",
)

import django

django.setup()
