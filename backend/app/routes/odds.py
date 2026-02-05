"""
Routes API pour les cotes de paris (The Odds API)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from core.database import get_db
from services.odds_service import OddsService
from models.match import Match


router = APIRouter(prefix="/odds", tags=["odds"])


class OddsResponse(BaseModel):
    """Réponse avec les cotes d'un match."""
    match_id: int
    home_team: str
    away_team: str
    odds_home: Optional[float] = None
    odds_draw: Optional[float] = None
    odds_away: Optional[float] = None
    odds_updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ValueBetResponse(BaseModel):
    """Réponse d'analyse de value bet."""
    is_value_bet: bool
    expected_value: float
    value_percentage: float
    implied_probability: float
    our_probability: float
    recommendation: str


class UpdateStatsResponse(BaseModel):
    """Stats de mise à jour des cotes."""
    updated: int
    failed: int
    skipped: int


@router.get("/{match_id}", response_model=OddsResponse)
async def get_match_odds(match_id: int, db: Session = Depends(get_db)):
    """
    Récupère les cotes d'un match spécifique.
    """
    match = db.query(Match).filter(Match.id == match_id).first()
    
    if not match:
        raise HTTPException(status_code=404, detail="Match non trouvé")
    
    return OddsResponse(
        match_id=match.id,
        home_team=match.home_team,
        away_team=match.away_team,
        odds_home=match.odds_home,
        odds_draw=match.odds_draw,
        odds_away=match.odds_away,
        odds_updated_at=match.odds_updated_at
    )


@router.post("/{match_id}/refresh", response_model=OddsResponse)
async def refresh_match_odds(match_id: int, db: Session = Depends(get_db)):
    """
    Force la mise à jour des cotes d'un match depuis The Odds API.
    
    ⚠️ Consomme 1 crédit API par appel.
    """
    match = db.query(Match).filter(Match.id == match_id).first()
    
    if not match:
        raise HTTPException(status_code=404, detail="Match non trouvé")
    
    odds_service = OddsService()
    success = await odds_service.update_match_odds(db, match)
    
    if not success:
        raise HTTPException(
            status_code=503, 
            detail="Impossible de récupérer les cotes. Vérifiez la compétition et les noms d'équipes."
        )
    
    # Recharger le match avec les nouvelles cotes
    db.refresh(match)
    
    return OddsResponse(
        match_id=match.id,
        home_team=match.home_team,
        away_team=match.away_team,
        odds_home=match.odds_home,
        odds_draw=match.odds_draw,
        odds_away=match.odds_away,
        odds_updated_at=match.odds_updated_at
    )


@router.post("/refresh-all", response_model=UpdateStatsResponse)
async def refresh_all_odds(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Met à jour les cotes de tous les matchs à venir.
    
    ⚠️ Consomme plusieurs crédits API (1 par compétition unique).
    
    Args:
        limit: Nombre maximum de matchs à traiter (défaut: 50)
    """
    odds_service = OddsService()
    stats = await odds_service.update_all_upcoming_odds(db, limit)
    
    return UpdateStatsResponse(**stats)


@router.get("/{match_id}/value-bet", response_model=ValueBetResponse)
async def analyze_value_bet(
    match_id: int, 
    bet_type: str = "home",  # home, draw, away
    db: Session = Depends(get_db)
):
    """
    Analyse si un pari sur ce match est un value bet.
    
    Compare notre prédiction avec les cotes du bookmaker.
    
    Args:
        match_id: ID du match
        bet_type: Type de pari (home, draw, away)
    """
    match = db.query(Match).filter(Match.id == match_id).first()
    
    if not match:
        raise HTTPException(status_code=404, detail="Match non trouvé")
    
    # Récupérer les cotes
    if bet_type == "home" and match.odds_home:
        odds = match.odds_home
    elif bet_type == "draw" and match.odds_draw:
        odds = match.odds_draw
    elif bet_type == "away" and match.odds_away:
        odds = match.odds_away
    else:
        raise HTTPException(status_code=400, detail=f"Cotes non disponibles pour {bet_type}")
    
    # Récupérer la prédiction
    prediction = match.expert_prediction
    
    if not prediction:
        raise HTTPException(status_code=400, detail="Pas de prédiction pour ce match")
    
    # Calculer la confiance selon le type de pari
    # Utiliser la confiance de Ma Logique (APEX-30)
    confidence = prediction.ma_logique_confidence or 0.5
    
    # Ajuster la confiance selon le type de pari
    if bet_type == "home":
        # Si on prédit victoire domicile
        if prediction.ma_logique_home_score > prediction.ma_logique_away_score:
            adjusted_confidence = confidence
        else:
            adjusted_confidence = 1 - confidence  # Inverser si on prédit contre
    elif bet_type == "away":
        if prediction.ma_logique_away_score > prediction.ma_logique_home_score:
            adjusted_confidence = confidence
        else:
            adjusted_confidence = 1 - confidence
    else:  # draw
        # Pour le nul, confiance réduite
        if prediction.ma_logique_home_score == prediction.ma_logique_away_score:
            adjusted_confidence = confidence * 0.8
        else:
            adjusted_confidence = 0.25  # Faible confiance pour le nul non prédit
    
    odds_service = OddsService()
    result = odds_service.calculate_value_bet(odds, adjusted_confidence)
    
    return ValueBetResponse(**result)


@router.get("/sports/available")
async def get_available_sports():
    """
    Liste les championnats de football disponibles sur The Odds API.
    """
    odds_service = OddsService()
    
    return {
        "supported_competitions": odds_service.COMPETITION_MAPPING,
        "message": "Ces codes de compétition peuvent avoir leurs cotes mises à jour"
    }
