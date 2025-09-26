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

# Installer Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Vérifier l'installation
RUN poetry --version

# Configurer Poetry pour ne pas créer d'environnement virtuel
RUN poetry config virtualenvs.create false

# Copier les fichiers de dépendances
COPY pyproject.toml poetry.lock /app/

# Installer les dépendances Python
RUN poetry install --no-interaction --no-ansi --no-root --no-cache

# Copier le reste du code source
COPY . /app/

# Création des répertoires pour fichiers statiques et médias
RUN mkdir -p /app/staticfiles /app/media

# Exposer le port
EXPOSE 8000

# Commande par défaut (peut être surchargée dans docker-compose)
CMD ["gunicorn", "recovr.wsgi:application", "--bind", "0.0.0.0:8000"]
