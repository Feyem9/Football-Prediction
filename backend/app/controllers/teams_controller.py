"""Controller pour la gestion des équipes et leurs statistiques."""
import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional

from services.team_stats_service import TeamStatsService
from schemas.team import TeamStatsResponse

logger = logging.getLogger(__name__)


async def get_team_stats(
    db: Session, 
    team_id: int, 
    competition_code: str,
    refresh: bool = False
) -> TeamStatsResponse:
    """
    Récupère les statistiques d'une équipe.
    Si refresh est True ou si les stats n'existent pas, on les calcule.
    """
    service = TeamStatsService(db)
    
    # 1. Tenter de récupérer depuis la DB
    stats = service.get_stats_from_db(team_id, competition_code)
    
    # 2. Si non présent ou refresh forcé, on calcule
    if not stats or refresh:
        try:
            stats = await service.calculate_and_save_stats(team_id, competition_code)
        except Exception as e:
            logger.error(f"Erreur lors du calcul des stats: {e}")
            if not stats:  # Si on avait rien en DB et que le calcul échoue
                raise HTTPException(
                    status_code=502, 
                    detail="Impossible de récupérer les statistiques pour le moment."
                )
    
    if not stats:
        raise HTTPException(status_code=404, detail="Statistiques non trouvées pour cette équipe.")
        
    return TeamStatsResponse.model_validate(stats)
