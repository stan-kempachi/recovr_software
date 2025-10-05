# RecovR Software

Bienvenue dans le projet **RecovR Software** - une solution SaaS innovante pour le contrôle du processus de facturation et le suivi des statuts.

## À propos

RecovR est une application web SaaS qui permet aux entreprises de :
- Automatiser la vérification du respect du processus de facturation client
- Centraliser le suivi des statuts de factures sur différentes plateformes
- Réduire les délais de paiement et améliorer le recouvrement

[![Pipeline Status](https://gitlab.com/recovr/recovr_software/badges/master/pipeline.svg)](https://gitlab.com/recovr/recovr_software/-/pipelines)
[![Version](https://img.shields.io/badge/version-1.7.1-blue.svg)](https://gitlab.com/recovr/recovr_software/-/tags)

## Public cible

- Grandes entreprises et ETI avec flux de factures important
- PME sous-traitantes avec contraintes de facturation spécifiques
- Cabinets de gestion et recouvrement

## Technologies utilisées

- **Backend** : Django 4.2
- **Frontend** : React.js + TailwindCSS
- **Base de données** : PostgreSQL
- **CI/CD** : GitLab CI/CD
- **Déploiement** : Docker, Docker Compose
- **Tests** : pytest
- **Formatage et qualité du code** : Black, isort, pre-commit

## Fonctionnalités principales

### Authentification & gestion utilisateurs
- Connexion sécurisée (OAuth2 / SSO en option)
- Gestion multi-comptes (Admin / Utilisateur / Lecture seule)
- Stockage sécurisé des identifiants API pour diverses plateformes

### Connexion aux plateformes
- Intégration API avec différentes plateformes de facturation
- Lecture des statuts et suivi des commandes

### Contrôle de conformité des factures
- Vérification des documents requis (PO, BL, PV, CRA)
- Alertes en cas de document manquant avant dépôt
- Validation manuelle ou automatique

### Suivi & alertes
- Tableau de bord avec statut des factures (Soumise, Acceptée, En litige, Payée)
- Notifications par email & dans l'application pour retards ou anomalies

### Reporting
- Export Excel/CSV des statuts et délais de paiement

## Prérequis

- Python 3.12 ou supérieur
- Poetry
- Docker et Docker Compose (pour le déploiement)
- PostgreSQL (pour le développement local)
- Node.js et npm (pour le frontend)

## Installation

1. Cloner le dépôt
```bash
git clone git@gitlab.com:recovr/recovr_software.git
cd recovr_software
```

2. Installer les dépendances
```bash
poetry install
```

3. Configurer les variables d'environnement
```bash
cp .env.example .env
# Éditer le fichier .env avec vos configurations
```

4. Installer les hooks pre-commit
```bash
poetry run pre-commit install
```

5. Exécuter les migrations
```bash
poetry run python manage.py migrate
```

## Développement

### Lancement du serveur local

```bash
poetry run python manage.py runserver
```

### Exécution des tests

```bash
poetry run pytest
```

### Vérification du style et de la qualité du code

```bash
poetry run pre-commit run --all-files
```

## Environnements

Le projet RecovR est configuré avec trois environnements distincts :

### Développement (Local)
- Utilisé pour le développement quotidien
- Base de données PostgreSQL configurée en local
- Accessible via http://localhost:8000
- Variables d'environnement configurées dans `.env`

### Staging
- Réplique de l'environnement de production
- Utilisé pour tester les fonctionnalités avant déploiement en production
- Base de données PostgreSQL
- Accessible via https://staging.recovr.com (protégé par authentification)
- Déploiement automatique lors des fusions dans la branche `master`

### Production
- Environnement de production final
- Base de données PostgreSQL optimisée
- Accessible via https://recovr.com
- Déploiement manuel après validation en staging

## Roadmap des fonctionnalités

| Phase | Période | Fonctionnalités |
|-------|---------|-----------------|
| MVP | M0-M3 | Authentification, connexion aux plateformes, contrôle de conformité, suivi & alertes, reporting basique |
| Évolution 1 | M4-M5 | Ajout de nouvelles plateformes de facturation |
| Évolution 2 | M6 | IA détection anomalies : délais inhabituels, factures incomplètes, doublons |
| Évolution 3 | M7-M8 | Reporting avancé : graphiques interactifs, KPI personnalisables |
| Évolution 4 | M9 | API ouverte pour intégration avec ERP tiers |
| Évolution 5 | M10 | Module recouvrement actif : génération lettres/mails relance automatique |
| Évolution 6 | M11 | Gestion multi-clients : agences comptables et prestataires |
| Évolution 7 | M12 | Tableau de bord mobile (PWA) |

## CI/CD Pipeline

Notre pipeline CI/CD automatise les étapes suivantes :

1. **Lint** : Vérifie le style et la qualité du code
2. **Test** : Exécute les tests unitaires et d'intégration
3. **Changelog** : Met à jour automatiquement le CHANGELOG.md
4. **Sync** : Synchronise le code avec GitHub
5. **Deploy-Staging** : Déploie l'application en environnement de staging
6. **Deploy-Production** : Déploie l'application en production (déclenchement manuel)

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

# Si vous avez des ports utilisé sur le serveur stopper et supprimer les dockers
docker stop $(docker ps -q) && docker rm $(docker ps -aq)
```

## Versionnement et CHANGELOG

Ce projet utilise [python-semantic-release](https://python-semantic-release.readthedocs.io/) pour gérer automatiquement les versions et le CHANGELOG.

### Conventions de message de commit

Pour que vos modifications apparaissent correctement dans le CHANGELOG, suivez ces conventions :

| Type | Description | Exemple | Impact sur version |
|------|-------------|---------|-------------------|
| `feat` | Nouvelles fonctionnalités | `feat: ajouter la fonction de recherche` | Incrémente version mineure (0.x.0) |
| `fix` | Corrections de bugs | `fix: résoudre le problème d'authentification` | Incrémente version de patch (0.0.x) |
| `perf` | Améliorations de performance | `perf: optimiser les requêtes SQL` | Incrémente version de patch (0.0.x) |
| `docs` | Documentation | `docs: mettre à jour le README` | Aucun changement de version |
| `style` | Formatage, point-virgules, etc. | `style: formater selon PEP8` | Aucun changement de version |
| `refactor` | Refactorisation du code | `refactor: simplifier la logique d'authentification` | Aucun changement de version |
| `test` | Ajout ou modification de tests | `test: ajouter des tests pour API` | Aucun changement de version |
| `build` | Système de build ou dépendances | `build: mettre à jour Django vers 4.2` | Aucun changement de version |
| `ci` | Configuration CI | `ci: ajouter le déploiement automatique` | Aucun changement de version |
| `chore` | Tâches diverses | `chore: nettoyer les fichiers temporaires` | Aucun changement de version |
| `revert` | Annuler un commit précédent | `revert: revenir au commit abc123` | Aucun changement de version |

### Gestion des versions en local

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

## Architecture technique

- **Front-end** : React.js + TailwindCSS
- **Back-end** : Django
- **Base de données** : PostgreSQL
- **Intégrations API** : Diverses plateformes de facturation
- **Hébergement** : AWS (EC2 + S3)
- **Sécurité** : Chiffrement SSL/TLS, stockage sécurisé des données sensibles

## Documentation API

La documentation de l'API est disponible à l'URL `/api/docs/` lorsque le serveur est en cours d'exécution.

## Contraintes & risques

- Risque de changements d'API des plateformes externes
- Nécessité de mise à jour continue pour assurer la compatibilité
- Protection des données clients (RGPD strict)

## Contribution

1. Créez une branche à partir de `master`
2. Effectuez vos modifications
3. Soumettez une merge request vers `master`
4. Assurez-vous que tous les tests passent dans la CI

## Contact

Pour toute question concernant le projet, veuillez contacter l'équipe de développement.