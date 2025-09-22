import os

from dotenv import load_dotenv

# Charger les variables du fichier .env
load_dotenv()

# Debug désactivé en staging
DEBUG = False

# Permettre l'accès depuis différentes sources
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS").split(",")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
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

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",  # login normal
    "allauth.account.auth_backends.AuthenticationBackend",  # login social
]

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# Configuration allauth
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_UNIQUE_EMAIL = True

# Configuration Google OAuth2
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
        "APP": {
            "client_id": os.getenv("GOOGLE_OAUTH2_CLIENT_ID"),
            "secret": os.getenv("GOOGLE_OAUTH2_CLIENT_SECRET"),
        },
    }
}

DJANGO_SETTINGS_MODULE = os.getenv("DJANGO_SETTINGS_MODULE")
