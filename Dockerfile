FROM python:3.12-slim

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Répertoire de travail
WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gettext \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Installation de Poetry
RUN pip install --upgrade pip \
    && pip install poetry

# Copie des fichiers de dépendances
COPY pyproject.toml poetry.lock* /app/

# Configuration de Poetry pour ne pas créer d'environnement virtuel
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Copie du reste du code source
COPY . /app/

# Création des répertoires pour les fichiers statiques et médias
RUN mkdir -p /app/staticfiles /app/media

# Collecte des fichiers statiques
RUN python manage.py collectstatic --noinput

# Exposer le port
EXPOSE 8000

# Commande par défaut
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]