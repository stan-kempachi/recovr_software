# RecovR

SaaS de contrôle du processus de facturation et de suivi des statuts de factures (Chorus Pro, Ariba…).

**Démo / instance de référence** : https://recovr.stan-aria.dev

RecovR permet à une entreprise de :
- vérifier que le processus de facturation client est respecté avant dépôt (PO, BL, PV, CRA…) ;
- centraliser le suivi des statuts de factures sur plusieurs plateformes ;
- réduire les délais de paiement et améliorer le recouvrement.

## Stack

| Couche | Choix |
|---|---|
| Backend | Django 4.2, Django REST Framework, django-allauth |
| Frontend | Templates Django + Tailwind CSS (CDN) + DataTables |
| Base de données | PostgreSQL 16 |
| Serveur | gunicorn + whitenoise, derrière un reverse proxy (TLS Cloudflare) |
| Qualité | black, isort, ruff, pre-commit, pytest / pytest-django |
| Versionnement | python-semantic-release (conventional commits) |

## Modules

| App Django | Rôle | État |
|---|---|---|
| `accounts` | Utilisateur personnalisé (login par email, rôles admin / user / readonly), entreprises, rattachement utilisateur ↔ entreprise | ✅ |
| `dashboard` | Tableau de bord | ✅ |
| `invoices` | Dépôt de documents (PDF), détail des factures, API JSON | ✅ |
| `tasks` | Tâches, commentaires, assignation, règles de récurrence | ✅ |
| `api_connectors` | Stockage des identifiants API des plateformes de facturation | modèles seulement |
| `compliance` | Contrôle de conformité des factures | modèles seulement |
| `notifications` | Notifications email / in-app | modèles seulement |
| `reporting` | Exports et reporting | modèles seulement |

## Authentification

- Connexion par **email + mot de passe** (django-allauth, UI `allauth-ui`).
- **Google OAuth2** : disponible mais désactivé tant que `GOOGLE_OAUTH2_CLIENT_ID` / `GOOGLE_OAUTH2_CLIENT_SECRET` ne sont pas définis. URL de callback à déclarer côté Google : `https://<hôte>/accounts/google/login/callback/`.
- Vérification d'email : `mandatory` par défaut (`config/settings.py`), `none` dans `config/pi_settings.py` (pas de SMTP sur l'instance de référence).

## Installation locale

Prérequis : Python 3.12+, Poetry, PostgreSQL.

```bash
git clone git@github.com:stan-kempachi/recovr_software.git
cd recovr_software
poetry install
cp .env.example .env          # puis renseigner SECRET_KEY et DB_*
poetry run pre-commit install
poetry run python manage.py migrate
poetry run python manage.py createsuperuser
poetry run python manage.py runserver
```

Tests et qualité :

```bash
poetry run pytest
poetry run pre-commit run --all-files
```

> Les tests utilisent `tests/config/settings_test.py` (base `recovr_test`). En CI, lancer `pytest --create-db --no-migrations` pour créer le schéma directement depuis les modèles.

## Fichiers de settings

| Fichier | Usage |
|---|---|
| `config/settings.py` | Base commune (lit `.env` via python-dotenv) |
| `config/pi_settings.py` | Déploiement auto-hébergé (instance de référence) : `DEBUG=False`, whitenoise, Google OAuth2 optionnel, hôte via `PUBLIC_HOST` |
| `config/staging_settings.py` / `config/production_settings.py` | Anciens déploiements Docker (DigitalOcean) — conservés pour référence |
| `tests/config/settings_test.py` | Tests |

Variables d'environnement principales : `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `PUBLIC_HOST`, `GOOGLE_OAUTH2_CLIENT_ID`, `GOOGLE_OAUTH2_CLIENT_SECRET`.

## Déploiement (instance de référence)

Hébergement auto-géré, sans Docker pour l'application :

```bash
python3 -m venv .venv
.venv/bin/pip install django djangorestframework django-cors-headers pillow python-dotenv \
  psycopg2-binary gunicorn "django-allauth[socialaccount]" pyjwt cryptography \
  django-allauth-ui pypdf2 whitenoise
# .env avec DJANGO_SETTINGS_MODULE=config.pi_settings et les variables ci-dessus
.venv/bin/python manage.py migrate --noinput
.venv/bin/python manage.py collectstatic --noinput
.venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8116 --workers 2 --timeout 120
```

Un service systemd (`recovr.service`) lance gunicorn ; un reverse proxy route `recovr.stan-aria.dev` vers le port 8116 ; TLS terminé par Cloudflare (`SECURE_PROXY_SSL_HEADER` configuré). Endpoint de santé : `GET /health/`.

Les fichiers `Dockerfile`, `docker_compose.*.yml` et `.gitlab-ci.yml` correspondent à l'ancien déploiement DigitalOcean (staging/production via GitLab CI) et ne sont plus utilisés tels quels.

## Conventions de commit

Le projet suit les *conventional commits* ; `python-semantic-release` en déduit la version et le `CHANGELOG.md`.

| Type | Impact version |
|---|---|
| `feat` | mineure |
| `fix`, `perf` | patch |
| `docs`, `style`, `refactor`, `test`, `build`, `ci`, `chore`, `revert` | aucun |

```bash
poetry run semantic-release version --no-push
```

## Roadmap

- [x] Authentification, rôles, entreprises
- [x] Dépôt et suivi de documents / factures
- [x] Gestion de tâches
- [ ] Google OAuth2 sur l'instance de référence
- [ ] Connecteurs Chorus Pro / Ariba (`api_connectors`)
- [ ] Contrôle de conformité automatique (`compliance`)
- [ ] Notifications email / in-app (`notifications`)
- [ ] Exports Excel/CSV, reporting (`reporting`)
- [ ] Détection d'anomalies (délais inhabituels, doublons, factures incomplètes)
- [ ] API ouverte pour intégration ERP
- [ ] Module de relance / recouvrement
- [ ] Multi-clients (cabinets comptables, prestataires)

## Licence

Code source publié à titre de portfolio. Tous droits réservés — Stan Bruyère.
