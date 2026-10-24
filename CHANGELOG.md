# Changelog

## 1.12.0 (2026-10-24)

### Features
* feat: gestion des factures et clients, conformité, notifications et exports

## 1.11.0 (2026-10-24)

### Features
* feat(deploy): settings Pi pour recovr.stan-aria.dev (login email/mdp, OAuth2 Google optionnel, whitenoise)

## 1.10.0 (2025-10-15)

### Features
* feat: Establishes invoice document management with quick upload & validation.

### Bug Fixes
* fix changelog stage

All notable changes to this project are documented in this file.

---

## [1.7.0](https://gitlab.com/django1361117/recovr_software/compare/v1.6.0...v1.7.0) (2025-09-29)

### Features
- Succes Oauth2 config ([0282a4b](https://gitlab.com/django1361117/recovr_software/-/commit/0282a4b849290ea4df3b6408eba2cd98590f1f3f), [991f596](https://gitlab.com/django1361117/recovr_software/-/commit/991f596d70c1c6279b47b67b33b4c95b34931259))

### Bug Fixes
- Add `CSRF_TRUSTED_ORIGINS` to settings ([928f80c](https://gitlab.com/django1361117/recovr_software/-/commit/928f80cec86d5425bdeb0f14ee0a9e73e02cd81b))

### Refactoring
- Add CSRF/SSL to staging config ([3e1c776](https://gitlab.com/django1361117/recovr_software/-/commit/3e1c7765d47256b9beae90255196530bc1bf12a0))
- Remove unused app `recovr_software` ([37b6dd5](https://gitlab.com/django1361117/recovr_software/-/commit/37b6dd534df86ba5fe7d2f60c7484348d914df49))

### Chores / CI
- Update deploy jobs to pull latest code on server ([eec3f0c](https://gitlab.com/django1361117/recovr_software/-/commit/eec3f0c28d09b4e241eb5278de1f2973ad9414fb))

---

## [1.6.0](2025-09-27)

### Features
- Add Google OAUTH2 authentication ([bc129f4](https://gitlab.com/django1361117/recovr_software/-/commit/bc129f4a58c7d0c0b48b2a5321cb5601eabde2cc))
- Add SSL/certbot configuration ([0b31b17](https://gitlab.com/django1361117/recovr_software/-/commit/0b31b1730ba548accca93cc296b68336109eee92))
- Succes deployment OAuth2 ([9cfe41b](https://gitlab.com/django1361117/recovr_software/-/commit/9cfe41b5c82b5607708c706eb0d5804a22f07a9d))

### Refactoring
- Nginx config ([4e1348a](https://gitlab.com/django1361117/recovr_software/-/commit/4e1348a06dddab7cf4eca31daf3f9b0e7c2f7c2d))

### CI
- Fix DB configuration in settings files ([9f53d27](https://gitlab.com/django1361117/recovr_software/-/commit/9f53d27b852f1d854b7f63622040cf06aace3b4d))

---

## [1.5.0](2025-09-15)

### Features
- Successful production deployment ([45b5e59](https://gitlab.com/django1361117/recovr_software/-/commit/45b5e59635bb5e38812b73149433d49f41a421e0))
- CI: Successful deployment jobs deploy-staging and deploy-production ([8666e1a](https://gitlab.com/django1361117/recovr_software/-/commit/8666e1ae0b437a1525d84d7da87507b84ff09c0e))

### Bug Fixes
- Docker health-check fixed ([aee7e5f](https://gitlab.com/django1361117/recovr_software/-/commit/aee7e5f1a5d860b0a5078c590426c8cf71a2cedd))

### CI
- Add self-hosted GitLab runner ([c2e777d](https://gitlab.com/django1361117/recovr_software/-/commit/c2e777d83253807a304ff1059bb076e6322f26aa))

---

## [1.4.0](2025-09-14)

### CI
- Add SSH private key to deployment jobs ([bbaa3ea](https://gitlab.com/django1361117/recovr_software/-/commit/bbaa3ea03e27b5fea8b5f8290d001c8ea0fc8362))
- Update deployment scripts and Nginx config for staging/production ([0c1334b](https://gitlab.com/django1361117/recovr_software/-/commit/0c1334b913d408baa0a55f024f10f1c0b266df84), [0ec23f2](https://gitlab.com/django1361117/recovr_software/-/commit/0ec23f243d52de7317e3f4e717bdac74d8dbf913))

---

## [1.3.0](2025-09-12)

### Bug Fixes
- Harmonize environment variable names between Docker and Django ([bcaab13](https://gitlab.com/django1361117/recovr_software/-/commit/bcaab136539e2d7724ed154933b11766d5db0f32))

### CI
- Make pipeline jobs run manually by default for testing production deployment ([91eedf0](https://gitlab.com/django1361117/recovr_software/-/commit/91eedf0166bc80e7fa1b35f58727f5ba1e0ad6e9))

### Refactoring
- Simplify deployment script in GitLab CI/CD pipeline ([8e91746](https://gitlab.com/django1361117/recovr_software/-/commit/8e91746afdbec4191e7ac7d3851ed16568b70469))

---

## [1.2.0](2025-09-10)

### Features
- Add Docker basic configuration and PostgreSQL for local development ([6ca19b7](https://gitlab.com/django1361117/recovr_software/-/commit/6ca19b7))
- Implement Docker-based deployment for staging environment ([1be6107](https://gitlab.com/django1361117/recovr_software/-/commit/1be61071b2abfb5e2b7bbc2d19fef0cf8c5fee89))
- Successful staging deployment ([2f99b1f](https://gitlab.com/django1361117/recovr_software/-/commit/2f99b1f406000178124aad266d5229e218a1bc75))
- Update Nginx configs and CI/CD pipelines for new domains ([3935c03](https://gitlab.com/django1361117/recovr_software/-/commit/3935c03347defe43f6a8d8002cd35875c3cdcce5))

### Refactoring
- Settings for environment-specific configurations ([7e375db](https://gitlab.com/django1361117/recovr_software/-/commit/7e375db72243aba374c062027669b3a471e42854))

### CI
- Add Gunicorn and update CI SSH key setup ([7efeacc](https://gitlab.com/django1361117/recovr_software/-/commit/7efeacc462aa748f4f8762d14c1cfb4fa51c263a))
- Add separate stages for staging and production deployment ([b2668d7](https://gitlab.com/django1361117/recovr_software/-/commit/b2668d7509e9b3906841eb74b27e8a17616047d5))
- Automate pipeline jobs and prepare for production deployment ([2fd2ce3](https://gitlab.com/django1361117/recovr_software/-/commit/2fd2ce39dc2a5b83c2ed8d39a969d76e797f590c))

---

## [1.1.0](2025-09-03)

### Features
- Initialize project structure ([1f805c4](https://gitlab.com/django1361117/recovr_software/-/commit/1f805c41be4794d154f9b28a34404f428ee12583))

### Bug Fixes
- Add GitHub token to deployment and semantic-release configuration
- Convert SSH key to PEM format
- Improve CI pipeline debugging and error handling
- Correct CI/CD pipeline configuration

### Chores
- Remove IntelliJ-specific files and project documentation

---

## [1.0.0](2025-09-02)

- Initial release
