"""
Routes API pour les matchs, compétitions et prédictions.

Ces endpoints exposent les données Football-Data.org au frontend.
La logique métier est dans controllers/matches_controller.py.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from core.database import get_db
from schemas.match import (
    MatchResponse,
    MatchListResponse,
    CompetitionResponse,
    CompetitionListResponse,
    StandingsResponse,
    PredictionResponse
)
from controllers import matches_controller


router = APIRouter(prefix="/matches", tags=["Matches & Predictions"])


# =====================
# Endpoints Matchs
# =====================

@router.get("", response_model=MatchListResponse)
async def get_matches(
    competition: Optional[str] = Query(None, description="Code compétition (PL, FL1...)"),
    status: Optional[str] = Query(None, description="SCHEDULED, FINISHED, LIVE"),
    date: Optional[str] = Query(None, description="Date format YYYY-MM-DD"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Récupère la liste des matchs avec filtres optionnels."""
    return matches_controller.get_matches(db, competition, status, date, limit)


@router.get("/upcoming", response_model=MatchListResponse)
async def get_upcoming_matches(
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Récupère les prochains matchs programmés."""
    return matches_controller.get_upcoming_matches(db, limit)


@router.get("/today", response_model=MatchListResponse)
async def get_today_matches(db: Session = Depends(get_db)):
    """Récupère les matchs du jour."""
    return matches_controller.get_today_matches(db)


@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(match_id: int, db: Session = Depends(get_db)):
    """Récupère les détails d'un match spécifique."""
    return matches_controller.get_match_by_id(db, match_id)


@router.get("/{match_id}/prediction", response_model=PredictionResponse)
async def get_match_prediction(match_id: int, db: Session = Depends(get_db)):
    """Récupère la prédiction d'un match."""
    return await matches_controller.get_match_prediction(db, match_id)


# =====================
# Endpoints Compétitions
# =====================

@router.get("/competitions", response_model=CompetitionListResponse)
async def get_competitions():
    """Liste toutes les compétitions disponibles."""
    return await matches_controller.get_competitions()


@router.get("/competitions/{code}", response_model=CompetitionResponse)
async def get_competition(code: str):
    """Détails d'une compétition spécifique."""
    return await matches_controller.get_competition(code)


@router.get("/competitions/{code}/standings", response_model=StandingsResponse)
async def get_standings(code: str):
    """Récupère le classement d'une compétition."""
    return await matches_controller.get_standings(code)


# =====================
# Endpoints Admin
# =====================

@router.post("/sync", tags=["Admin"])
async def sync_matches(
    competition: Optional[str] = Query(None, description="Code compétition"),
    db: Session = Depends(get_db)
):
    """Synchronise les matchs depuis Football-Data.org."""
    return await matches_controller.sync_matches(db, competition)


@router.post("/predictions/generate", tags=["Admin"])
async def generate_predictions(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Génère des prédictions pour les matchs à venir."""
    return await matches_controller.generate_predictions(db, limit)
