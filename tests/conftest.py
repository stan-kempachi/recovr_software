import os

import django

# Définir le module de paramètres Django avant d'importer les modèles
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "recovr_software.config.settings")
django.setup()
