"""Modèle Standing pour stocker les classements en base de données."""
from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from datetime import datetime, timezone
from .base import Base


class Standing(Base):
    """
    Modèle représentant une ligne de classement d'une compétition.
    
    Permet de cacher les données de classement depuis Football-Data.org
    pour réduire les appels API et avoir un historique.
    """
    __tablename__ = "standings"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Compétition
    competition_code = Column(String(10), nullable=False, index=True)
    competition_name = Column(String(100))
    season = Column(Integer, nullable=False)
    matchday = Column(Integer, nullable=True)
    
    # Position et équipe
    position = Column(Integer, nullable=False)
    team_id = Column(Integer, nullable=False, index=True)
    team_name = Column(String(100), nullable=False)
    team_short = Column(String(50), nullable=True)
    team_crest = Column(String(500), nullable=True)
    
    # Statistiques
    played_games = Column(Integer, default=0)
    won = Column(Integer, default=0)
    draw = Column(Integer, default=0)
    lost = Column(Integer, default=0)
    points = Column(Integer, default=0)
    goals_for = Column(Integer, default=0)
    goals_against = Column(Integer, default=0)
    goal_difference = Column(Integer, default=0)
    form = Column(String(20), nullable=True)  # Ex: "W,D,L,W,W"
    
    # Métadonnées
    last_synced = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Contrainte unique: une seule entrée par équipe/compétition/saison
    __table_args__ = (
        UniqueConstraint('competition_code', 'season', 'team_id', name='uq_standing_team_season'),
    )
    
    def __repr__(self):
        return f"<Standing {self.position}. {self.team_name} ({self.competition_code})>"
