# recovr_software

Bienvenue dans le projet **recovr_software**.

## Description

Ce projet utilise :

- **Framework** : Django
- **Package principal** : recovr_software

## Commandes de Base

### Installation des dépendances

```bash
poetry install
```

### Lancement


- Pour Django :
```bash
poetry run python manage.py runserver
```

- Pour pre-commit :
```bash
poetry run pre-commit run --all-files
```

## Environnements

Le projet RecovR est configuré avec trois environnements :

### Développement (Local)
- Utilisé pour le développement quotidien
- Base de données PostgreSQL configurée en local
- Accessible via http://localhost:8000

### Staging
- Réplique de l'environnement de production
- Utilisé pour tester les fonctionnalités avant déploiement en production
- Base de données PostgreSQL
- Accessible via https://staging.recovr.com (protégé par authentification)

### Production
- Environnement de production final
- Base de données PostgreSQL optimisée
- Accessible via https://recovr.com

## Déploiement avec Docker

Le projet utilise Docker et Docker Compose pour les déploiements :

```bash
# Démarrer tous les services
docker-compose up -d

# Démarrer uniquement l'environnement de staging
docker-compose up -d web_staging nginx

# Exécuter les migrations dans l'environnement de staging
docker-compose exec web_staging python manage.py migrate

# Créer un superutilisateur pour l'environnement de staging
docker-compose exec web_staging python manage.py createsuperuser
```

## Versionnement et CHANGELOG

Ce projet utilise [python-semantic-release](https://python-semantic-release.readthedocs.io/) pour gérer automatiquement les versions et le CHANGELOG.

### Conventions de message de commit

Les messages de commit doivent suivre les conventions suivantes :
- `feat:` - Nouvelles fonctionnalités (incrémente la version mineure)
- `fix:` - Corrections de bugs (incrémente la version de patch)
- `perf:` - Améliorations de performance (incrémente la version de patch)
- Autres préfixes autorisés : `docs:`, `style:`, `refactor:`, `test:`, `build:`, `ci:`, `chore:`, `revert:`

### Exécuter semantic-release en local

Pour tester les mises à jour du CHANGELOG sans pousser les changements :
```bash
poetry run semantic-release version --no-push
```

Pour forcer une version spécifique :
```bash
poetry run semantic-release version --patch --no-push  # Pour version 0.x.1
poetry run semantic-release version --minor --no-push  # Pour version 0.2.0
poetry run semantic-release version --major --no-push  # Pour version 1.0.0
```

### Récupérer les mises à jour du CHANGELOG depuis la CI

Si le CHANGELOG a été mis à jour par la CI dans GitLab :
```bash
git checkout master
git pull origin master
```

### Fonctionnement

- **En local** : Les modifications sont créées mais restent en local
- **Dans la CI** : Les modifications sont automatiquement poussées vers GitLab et synchronisées avec GitHub