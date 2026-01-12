"""
Controller pour les classements.

Contient toute la logique métier pour les endpoints standings.
"""
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.standing import Standing
from schemas.match import StandingsResponse, StandingEntry
from services.standing_sync import StandingSyncService


def standings_to_response(
    standings: List[Standing], 
    competition_code: str
) -> StandingsResponse:
    """Convertit une liste de Standing en StandingsResponse."""
    if not standings:
        raise HTTPException(status_code=404, detail="Classement non trouvé")
    
    first = standings[0]
    entries = [
        StandingEntry(
            position=s.position,
            team_id=s.team_id,
            team_name=s.team_name,
            team_short=s.team_short,
            team_crest=s.team_crest,
            played_games=s.played_games,
            won=s.won,
            draw=s.draw,
            lost=s.lost,
            points=s.points,
            goals_for=s.goals_for,
            goals_against=s.goals_against,
            goal_difference=s.goal_difference,
            form=s.form
        )
        for s in standings
    ]
    
    return StandingsResponse(
        competition_code=first.competition_code,
        competition_name=first.competition_name or "",
        season=first.season,
        matchday=first.matchday,
        standings=entries
    )


async def get_standings(db: Session, competition_code: str, force_refresh: bool = False) -> StandingsResponse:
    """
    Récupère le classement d'une compétition.
    
    Utilise le cache DB si disponible et non périmé.
    Sinon, synchronise depuis l'API.
    
    Args:
        db: Session SQLAlchemy
        competition_code: Code de la compétition
        force_refresh: Forcer la resynchronisation
        
    Returns:
        StandingsResponse avec le classement
    """
    sync_service = StandingSyncService(db)
    code = competition_code.upper()
    
    # Vérifier si on doit rafraîchir
    if force_refresh or sync_service.is_stale(code, max_age_hours=6):
        try:
            await sync_service.sync_standings(code)
        except Exception as e:
            # Si sync échoue mais qu'on a des données, les utiliser
            standings = sync_service.get_standings(code)
            if standings:
                return standings_to_response(standings, code)
            raise HTTPException(status_code=502, detail=f"Erreur API: {str(e)}")
    
    # Récupérer depuis la DB
    standings = sync_service.get_standings(code)
    return standings_to_response(standings, code)


async def sync_standings(db: Session, competition_code: str = None) -> dict:
    """
    Synchronise les classements.
    
    Args:
        db: Session SQLAlchemy
        competition_code: Code spécifique ou None pour toutes
        
    Returns:
        Message de confirmation
    """
    sync_service = StandingSyncService(db)
    
    try:
        if competition_code:
            count = await sync_service.sync_standings(competition_code.upper())
            return {"message": f"{count} entrées synchronisées pour {competition_code.upper()}"}
        else:
            count = await sync_service.sync_all_standings()
            return {"message": f"{count} entrées synchronisées pour toutes les compétitions"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de synchronisation: {str(e)}")
