from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from .base import Base

class Match(Base):
    """Modèle représentant un match de football avec scores et statut."""
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    home_team = Column(String, nullable=False)
    away_team = Column(String, nullable=False)
    match_date = Column(DateTime, nullable=False)
    score_home = Column(Integer, nullable=True)
    score_away = Column(Integer, nullable=True)
    status = Column(String, default="scheduled") # scheduled, live, finished

    expert_prediction = relationship("ExpertPrediction", back_populates="match", uselist=False)
