---
description: Comment configurer SendGrid SMTP pour la production
---

# Configuration SendGrid pour Production

## Prérequis

- Compte SendGrid (https://sendgrid.com)
- API Key SendGrid

## Étapes

### 1. Créer l'API Key sur SendGrid

1. Connecte-toi sur https://app.sendgrid.com
2. Va dans **Settings** → **API Keys**
3. Clique **Create API Key**
4. Donne un nom (ex: "Pronoscore Production")
5. Choisis **Restricted Access** avec permissions **Mail Send**
6. Copie la clé API (format: `SG.xxxx...`)

### 2. Vérifier un domaine expéditeur (recommandé)

1. Va dans **Settings** → **Sender Authentication**
2. Ajoute et vérifie ton domaine pour éviter le spam

### 3. Configurer le fichier .env.production

```bash
cp .env.production.example .env.production
```

Édite `.env.production` avec ta vraie clé API :

```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=SG.ta_vraie_cle_api
SMTP_USE_TLS=true
FROM_EMAIL=noreply@ton-domaine.com
```

### 4. Déployer

// turbo

```bash
# Utilise .env.production au lieu de .env
cp .env.production .env
```

## Test

```bash
curl -X POST http://localhost:8000/api/v1/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "ton-email@example.com"}'
```

## Limites SendGrid (gratuit)

- 100 emails/jour (gratuit)
- Pour plus : plans payants à partir de ~$15/mois
