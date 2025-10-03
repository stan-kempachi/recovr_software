import os

from config.settings import *  # noqa: F403

# Database test
DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.postgresql"),
        "NAME": os.getenv("DB_NAME", "recovr_test"),
        "USER": os.getenv("DB_USER", "stan"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "host.docker.internal"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}
