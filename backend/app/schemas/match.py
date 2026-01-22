"""Schémas Pydantic pour les matchs et compétitions."""
from pydantic import BaseModel, ConfigDict
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
    home_standing_position: Optional[int] = None
    home_standing_points: Optional[int] = None
    away_team: str
    away_team_short: Optional[str] = None
    away_team_crest: Optional[str] = None
    away_standing_position: Optional[int] = None
    away_standing_points: Optional[int] = None
    
    # Date et statut
    match_date: datetime
    status: str
    
    # Scores
    score_home: Optional[int] = None
    score_away: Optional[int] = None
    
    # Prédiction (si disponible)
    prediction: Optional["PredictionSummary"] = None
    
    model_config = ConfigDict(from_attributes=True)


class MatchListResponse(BaseModel):
    """Liste de matchs avec pagination."""
    count: int
    matches: List[MatchResponse]


# =====================
# Competition Schemas
# =====================

class CompetitionResponse(BaseModel):
    """Informations d'une compétition."""
    id: Optional[int] = None
    code: Optional[str] = None
    name: Optional[str] = None
    area: Optional[str] = None
    emblem: Optional[str] = None
    type: Optional[str] = None  # LEAGUE, CUP, etc.
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
    # Score final (consensus)
    home_score_forecast: int
    away_score_forecast: int
    confidence: float
    bet_tip: Optional[str] = None
    home_goals_avg: Optional[float] = None
    away_goals_avg: Optional[float] = None
    
    # Logique de Papa (Classement + Niveau Championnat)
    papa_home_score: Optional[int] = None
    papa_away_score: Optional[int] = None
    papa_confidence: Optional[float] = None
    papa_tip: Optional[str] = None
    
    # Logique Grand Frère (H2H + Domicile)
    grand_frere_home_score: Optional[int] = None
    grand_frere_away_score: Optional[int] = None
    grand_frere_confidence: Optional[float] = None
    grand_frere_tip: Optional[str] = None
    
    # Ma Logique (Forme + Consensus)
    ma_logique_home_score: Optional[int] = None
    ma_logique_away_score: Optional[int] = None
    ma_logique_confidence: Optional[float] = None
    ma_logique_tip: Optional[str] = None
    
    # Matchs importants (contexte Papa)
    home_upcoming_important: Optional[str] = None
    home_recent_important: Optional[str] = None
    away_upcoming_important: Optional[str] = None
    away_recent_important: Optional[str] = None


class PredictionResponse(BaseModel):
    """Réponse complète d'une prédiction."""
    id: int
    match_id: int
    home_score_forecast: int
    away_score_forecast: int
    confidence: float
    home_goals_avg: Optional[float] = None  # Moyenne buts domicile
    away_goals_avg: Optional[float] = None  # Moyenne buts extérieur
    analysis: Optional[str] = None
    bet_tip: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class LogicEvidenceSchema(BaseModel):
    """Preuves utilisées par une logique de prédiction."""
    # Papa - classement
    home_position: int = 0
    away_position: int = 0
    home_points: int = 0
    away_points: int = 0
    league_level: float = 0.0
    # Grand Frère - domicile & H2H
    home_advantage: float = 0.0
    home_strength: str = "MOYEN"
    away_strength: str = "MOYEN"
    h2h_home_wins: int = 0
    h2h_away_wins: int = 0
    h2h_draws: int = 0
    # Ma Logique - forme & buts
    home_form: float = 0.0
    away_form: float = 0.0
    home_avg_goals: float = 0.0
    away_avg_goals: float = 0.0


class LogicPredictionResult(BaseModel):
    """Résultat d'une logique individuelle."""
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    predicted_home_goals: int
    predicted_away_goals: int
    confidence: float
    bet_tip: str
    analysis: str
    evidence: Optional[LogicEvidenceSchema] = None


class CombinedPredictionResponse(BaseModel):
    """
    Réponse de prédiction combinée des 3 logiques.
    
    Logiques:
    - Papa (35%): Position + Niveau championnat + Buts
    - Grand Frère (35%): H2H + Loi domicile
    - Ma Logique (30%): Forme 10 matchs + Consensus
    """
    match_id: int
    home_team: str
    away_team: str
    
    # Résultats par logique
    papa_prediction: Optional[LogicPredictionResult] = None
    grand_frere_prediction: Optional[LogicPredictionResult] = None
    ma_logique_prediction: Optional[LogicPredictionResult] = None
    
    # Prédiction finale combinée
    final_home_goals: int
    final_away_goals: int
    final_confidence: float
    final_bet_tip: str
    
    # Indicateur de consensus
    consensus_level: str  # "FORT", "MOYEN", "FAIBLE"
    all_agree: bool


# Forward reference resolution
MatchResponse.model_rebuild()
