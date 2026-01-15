"""
Routes API pour les opérations d'administration.

Ces endpoints permettent de déclencher des opérations de maintenance
comme la synchronisation des données depuis l'API externe.
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional

from core.database import get_db
from services.match_sync import MatchSyncService
from services.standing_sync import StandingSyncService

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/sync/matches")
async def sync_matches(
    competition: str = "PL",
    db: Session = Depends(get_db),
):
    """
    Synchronise les matchs d'une compétition spécifique.
    
    Args:
        competition: Code de la compétition (PL, FL1, BL1, SA, PD)
    
    Returns:
        Nombre de matchs synchronisés
    """
    try:
        sync_service = MatchSyncService(db)
        
        # Sync par compétition au lieu de date
        count = await sync_service.sync_competition_matches(competition)
        
        return {
            "success": True,
            "message": f"Synchronisation {competition} terminée",
            "matches_synced": count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de synchronisation: {str(e)}")


@router.post("/sync/standings")
async def sync_standings(
    competition_code: str = "PL",
    db: Session = Depends(get_db),
):
    """
    Synchronise les classements d'une compétition.
    
    Args:
        competition_code: Code de la compétition (ex: PL, FL1, BL1)
    
    Returns:
        Résultat de la synchronisation
    """
    try:
        sync_service = StandingSyncService(db)
        count = await sync_service.sync_standings(competition_code)
        
        return {
            "success": True,
            "message": f"Classements {competition_code} synchronisés",
            "teams_synced": count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de synchronisation: {str(e)}")


@router.post("/sync/all")
async def sync_all(
    db: Session = Depends(get_db),
):
    """
    Synchronise toutes les données (matchs et classements) par compétition.
    
    Returns:
        Résumé de la synchronisation
    """
    COMPETITIONS = ["PL", "BL1", "SA", "PD", "FL1"]
    
    try:
        match_service = MatchSyncService(db)
        standing_service = StandingSyncService(db)
        
        results = {
            "matches": {},
            "standings": {}
        }
        
        # Sync matchs et classements pour chaque compétition
        for comp in COMPETITIONS:
            try:
                match_count = await match_service.sync_competition_matches(comp)
                results["matches"][comp] = match_count
            except Exception as e:
                results["matches"][comp] = f"Error: {str(e)}"
            
            try:
                standing_count = await standing_service.sync_standings(comp)
                results["standings"][comp] = standing_count
            except Exception as e:
                results["standings"][comp] = f"Error: {str(e)}"
        
        return {
            "success": True,
            "message": "Synchronisation complète terminée",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de synchronisation: {str(e)}")
