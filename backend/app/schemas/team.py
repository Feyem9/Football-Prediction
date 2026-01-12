"""Schémas Pydantic pour les statistiques d'équipes."""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class TeamStatsResponse(BaseModel):
    """Réponse détaillée des statistiques d'une équipe."""
    team_id: int
    competition_code: str
    season: int
    
    # Statistiques Globales
    played: int
    wins: int
    draws: int
    losses: int
    
    # Buts
    goals_for: int
    goals_against: int
    avg_goals_scored: float
    avg_goals_conceded: float
    
    # Forme (ex: "WDLWW")
    form: Optional[str] = None
    
    last_updated: datetime
    
    model_config = ConfigDict(from_attributes=True)
