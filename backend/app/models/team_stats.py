"""Modèle TeamStats pour stocker les statistiques calculées par équipe."""
from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint
from datetime import datetime, timezone
from .base import Base


class TeamStats(Base):
    """
    Statistiques détaillées d'une équipe pour une compétition et saison donnée.
    """
    __tablename__ = "team_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, nullable=False, index=True)
    competition_code = Column(String(10), nullable=False, index=True)
    season = Column(Integer, nullable=False)
    
    # Statistiques Globales
    played = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    draws = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    
    # Buts
    goals_for = Column(Integer, default=0)
    goals_against = Column(Integer, default=0)
    avg_goals_scored = Column(Float, default=0.0)
    avg_goals_conceded = Column(Float, default=0.0)
    
    # Forme (ex: "WDLWW")
    form = Column(String(50), nullable=True)
    
    # Métadonnées
    last_updated = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        UniqueConstraint('team_id', 'competition_code', 'season', name='uq_team_competition_season'),
    )
    
    def __repr__(self):
        return f"<TeamStats Team:{self.team_id} Matchs:{self.played}>"
