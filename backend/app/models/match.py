"""Modèle Match enrichi pour stocker les données de Football-Data.org."""
from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .base import Base


class Match(Base):
    """
    Modèle représentant un match de football.
    
    Synchronisé depuis l'API Football-Data.org avec les données enrichies
    (équipes, compétition, écussons, etc.)
    """
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    
    # Identifiant externe (Football-Data.org)
    external_id = Column(Integer, unique=True, index=True, nullable=True)
    
    # Compétition
    competition_code = Column(String(10), index=True)  # "PL", "FL1", "CL", etc.
    competition_name = Column(String(100))
    matchday = Column(Integer, nullable=True)
    
    # Équipe domicile
    home_team = Column(String(100), nullable=False)
    home_team_id = Column(Integer, nullable=True, index=True)
    home_team_short = Column(String(50), nullable=True)  # Nom court (ex: "PSG")
    home_team_crest = Column(String(500), nullable=True)  # URL écusson
    
    # Équipe extérieur
    away_team = Column(String(100), nullable=False)
    away_team_id = Column(Integer, nullable=True, index=True)
    away_team_short = Column(String(50), nullable=True)
    away_team_crest = Column(String(500), nullable=True)
    
    # Date et heure
    match_date = Column(DateTime, nullable=False, index=True)
    
    # Scores
    score_home = Column(Integer, nullable=True)
    score_away = Column(Integer, nullable=True)
    score_home_halftime = Column(Integer, nullable=True)
    score_away_halftime = Column(Integer, nullable=True)
    
    # Statut: SCHEDULED, TIMED, IN_PLAY, PAUSED, FINISHED, POSTPONED, CANCELLED
    status = Column(String(20), default="SCHEDULED", index=True)
    
    # === Cotes de Paris (The Odds API) ===
    odds_home = Column(Float, nullable=True)    # Cote victoire domicile
    odds_draw = Column(Float, nullable=True)    # Cote match nul
    odds_away = Column(Float, nullable=True)    # Cote victoire extérieur
    odds_updated_at = Column(DateTime, nullable=True)  # Dernière mise à jour des cotes
    
    # Métadonnées de synchronisation
    last_synced = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relation avec les prédictions
    expert_prediction = relationship("ExpertPrediction", back_populates="match", uselist=False)
    
    def __repr__(self):
        return f"<Match {self.home_team} vs {self.away_team} ({self.match_date.date()})>"
