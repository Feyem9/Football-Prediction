"""Tests d'intégration pour les routes API."""
import pytest
from fastapi.testclient import TestClient
from main import app
from core.database import get_db, Base, engine, SessionLocal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configuration de la DB de test (SQLite en mémoire pour la rapidité ou fichier local)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine_test = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

Base.metadata.drop_all(bind=engine_test)
Base.metadata.create_all(bind=engine_test)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_get_competitions():
    """Test de la récupération des compétitions (mocké ou réel si cache)."""
    # Note: En test réel sans mock, cela appellera l'API externe si pas de cache.
    # Pour l'intégration simple, on vérifie juste que la route répond.
    response = client.get("/api/v1/matches/competitions")
    if response.status_code == 422:
        print(f"\n❌ 422 Error: {response.json()}")
    # 502 est acceptable si pas de clé API ou hors ligne, mais la route existe
    assert response.status_code in [200, 502] 

def test_get_matches_structure():
    """Vérifie la structure de réponse de l'endpoint matches."""
    response = client.get("/api/v1/matches?limit=1")
    assert response.status_code in [200, 502]
    if response.status_code == 200:
        data = response.json()
        assert "count" in data
        assert "matches" in data
