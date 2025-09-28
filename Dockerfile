FROM python:3.12-slim

# Variables d'environnement Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Variables pour Poetry
ENV POETRY_VERSION=1.7.1
ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"

# Répertoire de travail
WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libpq-dev \
    gettext \
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Installer Poetry et désactiver les environnements virtuels
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && poetry config virtualenvs.create false

# Copier uniquement les fichiers de dépendances en premier (pour cache)
COPY pyproject.toml poetry.lock /app/

# Installer les dépendances
RUN poetry install --no-interaction --no-ansi --no-root --no-cache

# Créer les répertoires pour staticfiles et media
RUN mkdir -p /app/staticfiles /app/media

# Exposer le port Django
EXPOSE 8000


# Commande par défaut (peut être surchargée par docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
