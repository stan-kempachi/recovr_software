import os

from dotenv import load_dotenv

# Charger les variables du fichier .env
load_dotenv()

# Debug désactivé en staging
DEBUG = False

# Permettre l'accès depuis différentes sources
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS").split(",")


# Base de données PostgreSQL pour l'environnement staging
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

# Configuration des emails (peut utiliser un backend de développement en staging)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Configuration des fichiers statiques
STATIC_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "staticfiles"
)

# IMPORTANT: SSL/HTTPS settings différents selon l'accès
# Via HTTPS (port 443) : SSL activé
# Via HTTP (port 8080) : SSL désactivé
if os.getenv("HTTP_X_FORWARDED_PROTO") == "https":
    # Paramètres de sécurité pour HTTPS
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
else:
    # Paramètres pour HTTP (port 8080 direct)
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

# Exemptions pour les healthchecks
SECURE_REDIRECT_EXEMPT = [r"^health/$", r"^nginx-health/$"]

# Configuration du sous-chemin pour staging via HTTPS
FORCE_SCRIPT_NAME = "/staging"
