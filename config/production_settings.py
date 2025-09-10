import os

# Désactiver le debug en production
DEBUG = False

# Permettre l'accès depuis le domaine de production
ALLOWED_HOSTS = ["recovr.com", "www.recovr.com", "localhost", "127.0.0.1"]

# Base de données PostgreSQL pour l'environnement de production
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

# Configuration des emails pour la production
# EMAIL_BACKEND = os.getenv("EMAIL_BACKEND")
# EMAIL_HOST = os.getenv("EMAIL_HOST")
# EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
# EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
# EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
# EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
# DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")

# Configuration des fichiers statiques
STATIC_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "staticfiles"
)

# Paramètres de sécurité pour la production
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 an
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
