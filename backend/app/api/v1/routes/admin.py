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
    COMPETITIONS = ["PL", "BL1", "SA", "PD", "FL1", "CL"]  # + Champions League
    
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


@router.post("/regenerate-predictions")
async def regenerate_predictions(
    competition: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """
    Régénère les prédictions avec les 3 logiques (Papa, Grand Frère, Ma Logique).
    
    Supprime les anciennes prédictions et en génère de nouvelles avec
    les scores individuels de chaque logique.
    
    Args:
        competition: Code de la compétition (optionnel, toutes si non spécifié)
        limit: Nombre maximum de matchs à traiter
    
    Returns:
        Nombre de prédictions régénérées
    """
    from models.match import Match
    from models.prediction import ExpertPrediction
    from services.prediction_service import PredictionService
    from datetime import datetime, timezone
    
    try:
        # Récupérer les matchs à venir
        query = db.query(Match).filter(
            Match.match_date > datetime.now(timezone.utc),
            Match.status.in_(["SCHEDULED", "TIMED"])
        )
        
        if competition:
            query = query.filter(Match.competition_code == competition)
        
        matches = query.order_by(Match.match_date).limit(limit).all()
        
        if not matches:
            return {
                "success": True,
                "message": "Aucun match à traiter",
                "predictions_regenerated": 0
            }
        
        # Supprimer les anciennes prédictions pour ces matchs
        match_ids = [m.id for m in matches]
        deleted = db.query(ExpertPrediction).filter(
            ExpertPrediction.match_id.in_(match_ids)
        ).delete(synchronize_session=False)
        db.commit()
        
        # Régénérer les prédictions avec les 3 logiques
        pred_service = PredictionService(db)
        count = 0
        errors = []
        
        for match in matches:
            try:
                await pred_service.generate_prediction(match)
                count += 1
            except Exception as e:
                errors.append(f"{match.home_team} vs {match.away_team}: {str(e)}")
        
        return {
            "success": True,
            "message": f"Prédictions régénérées avec les 3 logiques",
            "predictions_deleted": deleted,
            "predictions_regenerated": count,
            "total_matches": len(matches),
            "errors": errors[:5] if errors else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de régénération: {str(e)}")


@router.post("/regenerate-match/{match_id}")
async def regenerate_match_prediction(
    match_id: int,
    db: Session = Depends(get_db),
):
    """
    Régénère la prédiction pour un match spécifique.
    
    Args:
        match_id: ID du match à régénérer
    
    Returns:
        Résultat de la régénération
    """
    from models.match import Match
    from models.prediction import ExpertPrediction
    from services.prediction_service import PredictionService
    
    try:
        # Récupérer le match
        match = db.query(Match).filter(Match.id == match_id).first()
        
        if not match:
            raise HTTPException(status_code=404, detail=f"Match {match_id} non trouvé")
        
        # Supprimer l'ancienne prédiction si elle existe
        deleted = db.query(ExpertPrediction).filter(
            ExpertPrediction.match_id == match_id
        ).delete(synchronize_session=False)
        db.commit()
        
        # Régénérer la prédiction
        pred_service = PredictionService(db)
        await pred_service.generate_prediction(match)
        
        return {
            "success": True,
            "message": f"Prédiction régénérée pour {match.home_team} vs {match.away_team}",
            "match_id": match_id,
            "predictions_deleted": deleted
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")
