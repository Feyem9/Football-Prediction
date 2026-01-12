from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from contextlib import asynccontextmanager

from core.database import get_db, engine
from models import Base
from api.v1.routes.auth import router as auth_router
from api.v1.routes.profile import router as profile_router
from api.v1.routes.matches import router as matches_router
from api.v1.routes.teams import router as teams_router
from core.scheduler import start_scheduler, stop_scheduler

# Création des tables au démarrage (pour le développement)
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Démarrer le scheduler
    start_scheduler()
    yield
    # Shutdown: Arrêter le scheduler
    stop_scheduler()

app = FastAPI(title="Pronoscore API", lifespan=lifespan)

# Enregistrer les routes
app.include_router(auth_router, prefix="/api/v1")
app.include_router(profile_router, prefix="/api/v1")
app.include_router(matches_router, prefix="/api/v1")
app.include_router(teams_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Bienvenue sur l'API Pronoscore 2026",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Vérifie l'état de santé de l'API et de la connexion à la base de données."""
    try:
        # Test simple de connexion à la base de données
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}
