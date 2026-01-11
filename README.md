# 🏆 Pronoscore - Plateforme de Pronostics Football

Application web de pronostics football avec système d'authentification complet et gestion de profils utilisateurs.

## 🚀 Features Actuelles

### ✅ Authentification Complète

- Inscription avec vérification email
- Connexion avec JWT (access + refresh tokens)
- Mot de passe hashé (bcrypt)
- Reset password par email
- Logout avec blacklist de tokens

### ✅ Gestion de Profil

- Consultation et modification du profil
- Upload d'avatar via Cloudinary
- Bio et nom complet

### ✅ Infrastructure

- PostgreSQL pour la persistance
- Redis (prêt pour cache/sessions)
- RabbitMQ (prêt pour tâches async)
- Tests unitaires avec SQLite in-memory

## 🛠️ Stack Technique

| Composant       | Technologie                             |
| --------------- | --------------------------------------- |
| Backend         | FastAPI + SQLAlchemy                    |
| Base de données | PostgreSQL 17                           |
| Auth            | JWT (python-jose) + bcrypt              |
| Upload d'images | Cloudinary                              |
| Email           | SMTP (MailDev en dev, SendGrid en prod) |
| Tests           | pytest                                  |

## 📦 Installation

```bash
# Cloner le repo
git clone https://github.com/your-repo/pronoscore.git
cd pronoscore

# Démarrer les services
docker compose up -d db redis rabbitmq

# Backend
cd backend/app
python -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt

# Configuration
cp ../../.env.production.example ../../.env
# Éditer .env avec vos credentials

# Lancer
uvicorn main:app --reload
```

## 🧪 Tests

```bash
cd backend/app
source venv/bin/activate
python -m pytest tests/ -v
```

## 📁 Structure du Projet

```
pronoscore/
├── backend/
│   └── app/
│       ├── api/v1/routes/     # Endpoints REST
│       ├── controllers/       # Logique métier
│       ├── core/              # Config, DB, Security, Email
│       ├── models/            # Modèles SQLAlchemy
│       ├── schemas/           # Schémas Pydantic
│       ├── middleware/        # Auth middleware
│       └── tests/             # Tests unitaires
├── frontend/                  # React (Vite)
├── docs/                      # Documentation
└── docker-compose.yml
```

## 🔜 Roadmap

### Semaine Prochaine - APIs Externes

- [ ] Intégration Football-Data API
- [ ] Intégration API-Football (RapidAPI)
- [ ] Système de predictions automatiques

## 📄 License

MIT © 2026 Pronoscore
