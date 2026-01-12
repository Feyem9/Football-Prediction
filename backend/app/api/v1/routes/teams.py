"""Routes API pour les équipes."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from core.database import get_db
from schemas.team import TeamStatsResponse
from controllers import teams_controller

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.get("/{team_id}/stats", response_model=TeamStatsResponse)
async def get_team_stats(
    team_id: int,
    competition: str = Query(..., description="Code de la compétition (ex: PL, FL1)"),
    refresh: bool = Query(False, description="Forcer le recalcul des statistiques"),
    db: Session = Depends(get_db)
):
    """
    Récupère les statistiques détaillées d'une équipe pour une compétition.
    Inclut la forme récente, les moyennes de buts, etc.
    """
    return await teams_controller.get_team_stats(db, team_id, competition, refresh)
