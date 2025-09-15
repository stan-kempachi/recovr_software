import os

# Désactiver le debug en staging (comme en production)
DEBUG = False

# Permettre l'accès depuis le sous-domaine de staging
ALLOWED_HOSTS = ["157.230.21.181", "staging.recovr.com", "localhost", "127.0.0.1"]

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

# Paramètres de sécurité pour le staging (similaires à la production)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_REDIRECT_EXEMPT = [r"^health/$"]


# Configuration des emails pour le staging
# EMAIL_BACKEND = os.getenv("EMAIL_BACKEND")
# EMAIL_HOST = os.getenv("EMAIL_HOST")
# EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
# EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
# EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
# EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
# DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")
