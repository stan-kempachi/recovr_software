import os

from dotenv import load_dotenv

# Charger les variables du fichier .env
load_dotenv()

# Désactiver le debug en production
DEBUG = False

# Permettre l'accès depuis le domaine de production
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Applications RecovR
    "accounts",
    "api_connectors",
    "compliance",
    "core",
    "dashboard",
    "invoices",
    "notifications",
    "reporting",
    "recovr_software",
    "tests",
    # Dépendances tierces
    "rest_framework",
    "corsheaders",
    # Django-allauth
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth_ui",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

db_host = os.getenv("DB_HOST", "")
if not db_host or db_host.lower() in ["localhost", "127.0.0.1"]:
    db_host = "host.docker.internal"

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

# Configuration des fichiers statiques
STATIC_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "staticfiles"
)

# Paramètres de sécurité pour la production (HTTPS obligatoire)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 an
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Exemptions pour les healthchecks
SECURE_REDIRECT_EXEMPT = [r"^health/$", r"^nginx-health/$"]

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


# Configuration des emails pour la production
# EMAIL_BACKEND = os.getenv("EMAIL_BACKEND")
# EMAIL_HOST = os.getenv("EMAIL_HOST")
# EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
# EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
# EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
# EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
# DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")
