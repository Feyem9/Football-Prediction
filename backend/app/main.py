from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from core.database import get_db, engine
from models import Base
from api.v1.routes.auth import router as auth_router
from api.v1.routes.profile import router as profile_router
import os

# Création des tables au démarrage (pour le développement)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Pronoscore API")

# Enregistrer les routes
app.include_router(auth_router, prefix="/api/v1")
app.include_router(profile_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Bienvenue sur l'API Pronoscore 2026",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Test simple de connexion à la base de données
        db.execute(Base.metadata.tables.get("dual", "SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}
