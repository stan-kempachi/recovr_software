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
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Installation de Poetry
RUN pip install --upgrade pip \
    && pip install poetry

# Copie des fichiers de dépendances
COPY pyproject.toml /app/

# Configuration de Poetry pour ne pas créer d'environnement virtuel
# (puisque le conteneur est déjà isolé)
RUN poetry config virtualenvs.create false

# Régénérer le fichier lock si nécessaire
RUN poetry lock

# Installer les dépendances en fonction de l'environnement
ARG ENVIRONMENT=production
RUN if [ "$ENVIRONMENT" = "production" ]; then \
        poetry install --only main --no-interaction --no-ansi --no-root; \
    else \
        poetry install --no-interaction --no-ansi --no-root; \
    fi

# Copie du reste du code source
COPY . /app/

# Création des répertoires pour les fichiers statiques et médias
RUN mkdir -p /app/staticfiles /app/media

# Collecte des fichiers statiques - sera exécutée au démarrage dans le docker-compose
# pour utiliser les variables d'environnement correctes

# Exposer le port
EXPOSE 8000

# La commande par défaut sera définie dans docker-compose.yml