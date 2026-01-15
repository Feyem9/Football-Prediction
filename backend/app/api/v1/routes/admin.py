"""
Routes API pour les opérations d'administration.

Ces endpoints permettent de déclencher des opérations de maintenance
comme la synchronisation des données depuis l'API externe.
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional

from core.database import get_db
from core.config import settings
from services.match_sync import MatchSyncService
from services.standing_sync import StandingSyncService

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/sync/matches")
async def sync_matches(
    days: int = 7,
    db: Session = Depends(get_db),
    x_admin_key: Optional[str] = Header(None)
):
    """
    Synchronise les matchs à venir depuis Football-Data.org.
    
    Args:
        days: Nombre de jours à synchroniser (défaut: 7)
        x_admin_key: Clé d'administration (optionnelle pour la sécurité)
    
    Returns:
        Nombre de matchs synchronisés
    """
    try:
        sync_service = MatchSyncService(db)
        
        # Sync à venir
        upcoming_count = await sync_service.sync_upcoming_matches(days=days)
        
        # Sync terminés (mise à jour des scores)
        finished_count = await sync_service.sync_finished_matches()
        
        return {
            "success": True,
            "message": f"Synchronisation terminée",
            "upcoming_matches_synced": upcoming_count,
            "finished_matches_updated": finished_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de synchronisation: {str(e)}")


@router.post("/sync/standings")
async def sync_standings(
    competition_code: str = "PL",
    db: Session = Depends(get_db),
    x_admin_key: Optional[str] = Header(None)
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
    x_admin_key: Optional[str] = Header(None)
):
    """
    Synchronise toutes les données (matchs et classements).
    
    Returns:
        Résumé de la synchronisation
    """
    try:
        match_service = MatchSyncService(db)
        standing_service = StandingSyncService(db)
        
        results = {
            "matches": {
                "upcoming": 0,
                "finished": 0
            },
            "standings": {}
        }
        
        # Sync matchs
        results["matches"]["upcoming"] = await match_service.sync_upcoming_matches(days=14)
        results["matches"]["finished"] = await match_service.sync_finished_matches()
        
        # Sync classements pour les principales compétitions
        for comp in ["PL", "FL1", "BL1", "SA", "PD"]:
            try:
                count = await standing_service.sync_standings(comp)
                results["standings"][comp] = count
            except Exception:
                results["standings"][comp] = 0
        
        return {
            "success": True,
            "message": "Synchronisation complète terminée",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de synchronisation: {str(e)}")
