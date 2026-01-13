"""Schémas Pydantic pour l'historique des confrontations (Head-to-Head)."""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class H2HTeamAggregate(BaseModel):
    """Statistiques agrégées pour une équipe dans le H2H."""
    id: int
    name: str
    wins: int
    draws: int
    losses: int


class H2HAggregate(BaseModel):
    """Agrégats globaux du H2H."""
    numberOfMatches: int
    totalGoals: int
    homeTeam: H2HTeamAggregate
    awayTeam: H2HTeamAggregate


class H2HMatch(BaseModel):
    """Un match historique dans le H2H."""
    id: int
    utcDate: datetime
    status: str
    competition_name: Optional[str] = None
    homeTeam: dict # On simplifie car on a déjà les détails
    awayTeam: dict
    score: dict


class H2HResponse(BaseModel):
    """Réponse complète pour le Head-to-Head."""
    aggregates: H2HAggregate
    matches: List[dict] # On garde le dict pour flexibilité ou on définit H2HMatch finement
    
    model_config = ConfigDict(from_attributes=True)
