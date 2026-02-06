# 📋 Rapport CI/CD - Pronoscore

**Date :** 5 février 2026  
**Auteur :** Assistant IA  
**Version :** 1.0

---

## 📌 Résumé Exécutif

Ce document décrit la stratégie d'Intégration Continue (CI) et de Déploiement Continu (CD) mise en place pour le projet **Pronoscore**. L'objectif est d'automatiser les processus de test, build et déploiement pour garantir la qualité du code et accélérer les mises en production.

---

## 🎯 Objectifs

| Objectif            | Description                                                        |
| ------------------- | ------------------------------------------------------------------ |
| **Qualité du code** | Vérification automatique du linting et des tests à chaque commit   |
| **Fiabilité**       | Détecter les régressions avant qu'elles n'atteignent la production |
| **Rapidité**        | Déploiement automatique en moins de 10 minutes                     |
| **Traçabilité**     | Historique complet des builds et déploiements                      |

---

## 🏗️ Architecture CI/CD

```
┌─────────────────────────────────────────────────────────────────┐
│                        DÉVELOPPEUR                               │
│                            │                                     │
│                      git push / PR                               │
│                            ▼                                     │
├─────────────────────────────────────────────────────────────────┤
│                      GITHUB ACTIONS                              │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    CI Pipeline                               │ │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐         │ │
│  │  │  Lint   │─▶│  Test   │─▶│  Build  │─▶│ Security│         │ │
│  │  │ Check   │  │  Suite  │  │  Check  │  │  Scan   │         │ │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘         │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                            │                                     │
│                     Si branche main                              │
│                            ▼                                     │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    CD Pipeline                               │ │
│  │  ┌─────────────┐              ┌─────────────┐               │ │
│  │  │   Deploy    │              │   Deploy    │               │ │
│  │  │   Backend   │──────────────│  Frontend   │               │ │
│  │  │   (Render)  │              │  (Vercel)   │               │ │
│  │  └─────────────┘              └─────────────┘               │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Structure des Workflows

```
.github/
└── workflows/
    ├── ci.yml              # Pipeline CI (lint, tests, build)
    ├── deploy-backend.yml  # Déploiement backend vers Render
    ├── deploy-frontend.yml # Déploiement frontend vers Vercel
    └── security.yml        # Scan de sécurité hebdomadaire
```

---

## 🔄 Pipeline CI (Intégration Continue)

### Déclencheurs

- **Push** sur toutes les branches
- **Pull Request** vers `main` ou `production`

### Étapes Backend (Python/FastAPI)

| Étape        | Description                       | Durée estimée |
| ------------ | --------------------------------- | ------------- |
| Checkout     | Récupération du code              | ~5s           |
| Setup Python | Installation Python 3.11          | ~10s          |
| Cache pip    | Mise en cache des dépendances     | ~5s           |
| Install deps | `pip install -r requirements.txt` | ~30s          |
| Lint         | `flake8` + `black --check`        | ~15s          |
| Type check   | `mypy` (optionnel)                | ~20s          |
| Tests        | `pytest --cov`                    | ~60s          |
| Coverage     | Rapport de couverture             | ~5s           |

### Étapes Frontend (React/Vite)

| Étape        | Description                | Durée estimée |
| ------------ | -------------------------- | ------------- |
| Checkout     | Récupération du code       | ~5s           |
| Setup Node   | Installation Node 20       | ~10s          |
| Cache npm    | Mise en cache node_modules | ~5s           |
| Install deps | `npm ci`                   | ~30s          |
| Lint         | `npm run lint`             | ~15s          |
| Type check   | `tsc --noEmit`             | ~20s          |
| Tests        | `npm run test`             | ~45s          |
| Build        | `npm run build`            | ~30s          |

---

## 🚀 Pipeline CD (Déploiement Continu)

### Conditions de déclenchement

- Merge sur `main` → Déploiement **staging**
- Merge sur `production` → Déploiement **production**

### Backend → Render

```yaml
Méthode: Webhook Render Deploy Hook
URL: https://api.render.com/deploy/srv-xxx?key=xxx
```

### Frontend → Vercel

```yaml
Méthode: Vercel CLI ou GitHub Integration native
Commande: vercel --prod (si CLI)
```

---

## 🔐 Secrets GitHub Requis

Configure ces secrets dans **Settings > Secrets and variables > Actions** :

| Secret                  | Description                 | Où le trouver                        |
| ----------------------- | --------------------------- | ------------------------------------ |
| `RENDER_API_KEY`        | Clé API Render              | Render Dashboard > Account Settings  |
| `RENDER_SERVICE_ID`     | ID du service backend       | URL du service Render                |
| `VERCEL_TOKEN`          | Token Vercel                | Vercel Dashboard > Settings > Tokens |
| `VERCEL_ORG_ID`         | ID organisation Vercel      | `.vercel/project.json`               |
| `VERCEL_PROJECT_ID`     | ID projet Vercel            | `.vercel/project.json`               |
| `DATABASE_URL`          | URL PostgreSQL (pour tests) | Render PostgreSQL                    |
| `FOOTBALL_DATA_API_KEY` | Clé Football-Data.org       | football-data.org                    |
| `ODDS_API_KEY`          | Clé The Odds API            | the-odds-api.com                     |

---

## 📊 Métriques de Qualité

### Seuils minimaux

| Métrique                  | Seuil   | Action si échec  |
| ------------------------- | ------- | ---------------- |
| Couverture tests backend  | ≥ 70%   | ⛔ Blocage merge |
| Couverture tests frontend | ≥ 60%   | ⚠️ Avertissement |
| Erreurs lint              | 0       | ⛔ Blocage merge |
| Vulnérabilités critiques  | 0       | ⛔ Blocage merge |
| Temps de build            | < 5 min | ⚠️ Avertissement |

---

## 📅 Planification des Workflows

| Workflow          | Fréquence         | Description     |
| ----------------- | ----------------- | --------------- |
| CI                | À chaque push     | Tests et lint   |
| Security Scan     | Chaque lundi 6h00 | Audit npm + pip |
| Dependency Update | Chaque dimanche   | Dependabot PRs  |

---

## 🛠️ Commandes Utiles

### Lancer les tests localement (comme CI)

```bash
# Backend
cd backend/app
source venv/bin/activate
pip install flake8 pytest pytest-cov
flake8 . --max-line-length=120
pytest --cov=. --cov-report=html

# Frontend
cd frontend
npm run lint
npm run test
npm run build
```

### Simuler le build Docker

```bash
docker-compose build
docker-compose up -d
```

---

## 📈 Évolutions Futures

1. **Tests E2E** - Ajout de Playwright pour tests navigateur
2. **Preview Deployments** - Déploiement temporaire pour chaque PR
3. **Performance Testing** - Lighthouse CI pour le frontend
4. **Blue/Green Deployment** - Déploiement sans downtime
5. **Notifications** - Slack/Discord sur échec/succès

---

## ✅ Checklist de Mise en Place

- [ ] Créer les fichiers `.github/workflows/*.yml`
- [ ] Configurer les secrets GitHub
- [ ] Activer les GitHub Actions dans le repo
- [ ] Configurer la protection de branche `main`
- [ ] Tester un premier push
- [ ] Vérifier les déploiements automatiques
- [ ] Documenter les procédures d'urgence (rollback)

---

## 📞 Contact

Pour toute question sur cette configuration CI/CD :

- **Mainteneur** : Équipe Pronoscore
- **Documentation** : `/doc/RAPPORT_CICD.md`

---

_Généré automatiquement le 5 février 2026_
