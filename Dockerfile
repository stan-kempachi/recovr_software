FROM python:3.12-slim

# Variables d'environnement
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

# Installer Poetry et configurer pour ne pas créer d'environnement virtuel
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && /opt/poetry/bin/poetry config virtualenvs.create false

# Copier les fichiers de dépendances
COPY pyproject.toml poetry.lock /app/

# Installer les dépendances via Poetry
RUN /opt/poetry/bin/poetry install --no-interaction --no-ansi --no-root --no-cache

# Copier le reste du code
COPY . /app/

# Créer les répertoires pour les fichiers statiques et médias
RUN mkdir -p /app/staticfiles /app/media

# Exposer le port
EXPOSE 8000

# Commande par défaut, à remplacer ou surcharger via docker-compose
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
