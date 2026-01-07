# Pronoscore - Football Prediction Platform

## 🎯 Mission

**Pronoscore** est une plateforme moderne de prédiction de football conçue pour fournir des analyses précises et des pronostics basés sur des données en temps réel. Le projet vise à offrir une expérience utilisateur fluide tout en gérant des flux de données complexes via une architecture distribuée et scalable.

## 🏗️ Architecture Technique

Le projet adopte une architecture microservices/modulaire moderne, orchestrée par Docker pour assurer la cohérence entre les environnements de développement et de production.

### Stack Technologique

- **Frontend**: [React 19](https://react.dev/) + [TypeScript](https://www.typescriptlang.org/) + [Vite](https://vitejs.dev/)
- **Backend API**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12+)
- **Base de Données**: [PostgreSQL 17](https://www.postgresql.org/)
- **Cache & Session**: [Redis 7](https://redis.io/)
- **Message Broker**: [RabbitMQ 3](https://www.rabbitmq.com/) (pour les tâches asynchrones et le traitement de données)
- **Conteneurisation**: [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)

## 🚀 Fonctionnalités Clés (Focus Développeur)

- **API REST Haute Performance**: Propulsée par FastAPI pour une documentation automatique (Swagger/ReDoc) et une validation de données robuste via Pydantic.
- **Traitement Asynchrone**: Utilisation de RabbitMQ pour gérer les calculs lourds de prédiction et les mises à jour de données sans bloquer l'interface utilisateur.
- **Réactivité**: Frontend React optimisé pour la performance et la rapidité de chargement.
- **Gestion de Données**: Architecture de base de données relationnelle optimisée pour les statistiques sportives.

## 📁 Structure du Projet

```text
Pronoscore/
├── backend/          # API FastAPI, modèles SQLAlchemy, workers
├── frontend/         # Application React (Vite, TS)
├── docs/             # Documentation technique
├── docker-compose.yml # Orchestration des services
└── .env              # Configuration des variables d'environnement
```

## 🛠️ Pour Commencer

1.  **Prérequis**: Docker et Docker Compose installés.
2.  **Configuration**: Copier `.env.example` vers `.env` (si applicable).
3.  **Lancement**: `docker-compose up --build`
4.  **Accès**:
    - Frontend: `http://localhost:5173`
    - API Documentation: `http://localhost:8000/docs`
    - RabbitMQ Management: `http://localhost:15672`

---

_Ce document est destiné à faciliter l'onboarding des nouveaux développeurs sur le projet Pronoscore._
