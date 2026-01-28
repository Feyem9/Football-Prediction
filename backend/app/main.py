"""
Pronoscore API - Application de prédictions de matchs de football.

Ce module initialise l'application FastAPI avec la documentation OpenAPI,
les routes, et le scheduler pour les tâches automatiques.
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from sqlalchemy.orm import Session
from sqlalchemy import text
from contextlib import asynccontextmanager

from core.database import get_db, engine
from models import Base
from api.v1.routes.auth import router as auth_router
from api.v1.routes.profile import router as profile_router
from api.v1.routes.matches import router as matches_router
from api.v1.routes.teams import router as teams_router
from api.v1.routes.admin import router as admin_router
from core.scheduler import start_scheduler, stop_scheduler

# Création des tables au démarrage (pour le développement)
Base.metadata.create_all(bind=engine)


# Configuration OpenAPI
API_TITLE = "Pronoscore API"
API_VERSION = "1.0.0"
API_DESCRIPTION = """
## 🏆 API de Prédictions de Matchs de Football

Pronoscore est une API complète pour:
- 📊 Consulter les matchs et classements de 7 compétitions majeures
- 🎯 Obtenir des prédictions basées sur 3 logiques familiales
- 👤 Gérer l'authentification utilisateur
- 📈 Analyser les statistiques d'équipes

### 🔐 Authentification
L'API utilise **JWT (JSON Web Tokens)** pour l'authentification.
Récupérez votre token via `/auth/login` puis passez-le dans le header:
```
Authorization: Bearer <votre_token>
```

### 🎲 Système de Prédiction
Nos prédictions combinent 3 logiques:
- **Papa (35%)** : Niveau du championnat + Position au classement
- **Grand Frère (35%)** : H2H + Loi du domicile
- **Ma Logique (30%)** : Forme sur 10 matchs + Consensus

### 📌 Compétitions Supportées
| Code | Compétition |
|------|-------------|
| PL | Premier League |
| PD | La Liga |
| BL1 | Bundesliga |
| SA | Serie A |
| FL1 | Ligue 1 |
| CL | Champions League |
| WC | World Cup |
"""

TAGS_METADATA = [
    {
        "name": "Auth",
        "description": "🔐 Authentification et gestion des utilisateurs (register, login, logout).",
    },
    {
        "name": "Profile",
        "description": "👤 Gestion du profil utilisateur (avatar, infos).",
    },
    {
        "name": "Matches",
        "description": "⚽ Matchs, compétitions, et prédictions.",
    },
    {
        "name": "Teams",
        "description": "📊 Statistiques d'équipes.",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gère le cycle de vie de l'application."""
    # Auto-migration: Ajouter colonnes si elles n'existent pas
    try:
        with engine.connect() as conn:
            # Vérifier et ajouter home_goals_avg si manquant
            result = conn.execute(text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name='expert_predictions' AND column_name='home_goals_avg'
            """))
            if not result.fetchone():
                conn.execute(text("ALTER TABLE expert_predictions ADD COLUMN home_goals_avg FLOAT DEFAULT 0.0"))
                conn.execute(text("ALTER TABLE expert_predictions ADD COLUMN away_goals_avg FLOAT DEFAULT 0.0"))
                conn.commit()
                print("✅ Auto-migration: colonnes avg_goals ajoutées")
            # Vérifier et ajouter ma_logique_analysis si manquant
            result = conn.execute(text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name='expert_predictions' AND column_name='ma_logique_analysis'
            """))
            if not result.fetchone():
                conn.execute(text("ALTER TABLE expert_predictions ADD COLUMN ma_logique_analysis TEXT"))
                conn.commit()
                print("✅ Auto-migration: colonne ma_logique_analysis ajoutée")
    except Exception as e:
        print(f"⚠️ Auto-migration ignorée: {e}")
    
    # Startup: Démarrer le scheduler
    start_scheduler()
    yield
    # Shutdown: Arrêter le scheduler
    stop_scheduler()


app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
    openapi_tags=TAGS_METADATA,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "Pronoscore Team",
        "email": "support@pronoscore.app",
    },
    license_info={
        "name": "MIT",
    },
)

# Configuration CORS pour permettre les requêtes depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enregistrer les routes avec tags
app.include_router(auth_router, prefix="/api/v1", tags=["Auth"])
app.include_router(profile_router, prefix="/api/v1", tags=["Profile"])
app.include_router(matches_router, prefix="/api/v1", tags=["Matches"])
app.include_router(teams_router, prefix="/api/v1", tags=["Teams"])
app.include_router(admin_router, prefix="/api/v1", tags=["Admin"])


@app.get("/", tags=["Health"])
def read_root():
    """
    Point d'entrée de l'API.
    
    Retourne le statut et la version de l'API.
    """
    return {
        "status": "online",
        "message": "Bienvenue sur l'API Pronoscore 2026",
        "version": API_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """
    Vérifie l'état de santé de l'API.
    
    Teste la connexion à la base de données et retourne le statut.
    
    Returns:
        dict: Statut de l'API et de la base de données
    """
    try:
        # Test simple de connexion à la base de données
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}

