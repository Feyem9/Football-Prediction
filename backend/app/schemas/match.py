"""Schémas Pydantic pour les matchs et compétitions."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# =====================
# Team Schemas
# =====================

class TeamInfo(BaseModel):
    """Informations d'une équipe."""
    id: Optional[int] = None
    name: str
    short_name: Optional[str] = None
    crest: Optional[str] = None


# =====================
# Match Schemas
# =====================

class MatchBase(BaseModel):
    """Schéma de base pour un match."""
    home_team: str
    away_team: str
    match_date: datetime
    competition_code: Optional[str] = None
    competition_name: Optional[str] = None


class MatchResponse(BaseModel):
    """Réponse détaillée d'un match."""
    id: int
    external_id: Optional[int] = None
    
    # Compétition
    competition_code: Optional[str] = None
    competition_name: Optional[str] = None
    matchday: Optional[int] = None
    
    # Équipes
    home_team: str
    home_team_short: Optional[str] = None
    home_team_crest: Optional[str] = None
    away_team: str
    away_team_short: Optional[str] = None
    away_team_crest: Optional[str] = None
    
    # Date et statut
    match_date: datetime
    status: str
    
    # Scores
    score_home: Optional[int] = None
    score_away: Optional[int] = None
    
    # Prédiction (si disponible)
    prediction: Optional["PredictionSummary"] = None
    
    class Config:
        from_attributes = True


class MatchListResponse(BaseModel):
    """Liste de matchs avec pagination."""
    count: int
    matches: List[MatchResponse]


# =====================
# Competition Schemas
# =====================

class CompetitionResponse(BaseModel):
    """Informations d'une compétition."""
    id: int
    code: str
    name: str
    area: str
    emblem: Optional[str] = None
    type: str  # LEAGUE, CUP, etc.
    current_season: Optional[int] = None
    current_matchday: Optional[int] = None


class CompetitionListResponse(BaseModel):
    """Liste des compétitions."""
    count: int
    competitions: List[CompetitionResponse]


# =====================
# Standings Schemas
# =====================

class StandingEntry(BaseModel):
    """Une ligne du classement."""
    position: int
    team_id: int
    team_name: str
    team_short: Optional[str] = None
    team_crest: Optional[str] = None
    played_games: int
    won: int
    draw: int
    lost: int
    points: int
    goals_for: int
    goals_against: int
    goal_difference: int
    form: Optional[str] = None  # Ex: "W,D,L,W,W"


class StandingsResponse(BaseModel):
    """Classement d'une compétition."""
    competition_code: str
    competition_name: str
    season: int
    matchday: Optional[int] = None
    standings: List[StandingEntry]


# =====================
# Prediction Schemas
# =====================

class PredictionSummary(BaseModel):
    """Résumé d'une prédiction pour affichage dans un match."""
    home_score_forecast: int
    away_score_forecast: int
    confidence: float
    bet_tip: Optional[str] = None


class PredictionResponse(BaseModel):
    """Réponse complète d'une prédiction."""
    id: int
    match_id: int
    home_score_forecast: int
    away_score_forecast: int
    confidence: float
    analysis: Optional[str] = None
    bet_tip: Optional[str] = None
    
    class Config:
        from_attributes = True


# Forward reference resolution
MatchResponse.model_rebuild()
