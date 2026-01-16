from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from .base import Base

class ExpertPrediction(Base):
    """
    Représente le pronostic officiel donné par l'application (l'Expert) pour un match.
    Le joueur consulte ce pronostic pour s'orienter.
    """
    __tablename__ = "expert_predictions"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), unique=True, nullable=False)
    
    # Le score prédit par l'expert
    home_score_forecast = Column(Integer, nullable=False)
    away_score_forecast = Column(Integer, nullable=False)
    
    # Niveau de confiance (ex: 0.85 pour 85%)
    confidence = Column(Float, default=0.5)
    
    # TODO: Ajouter après migration sur Render
    # home_goals_avg = Column(Float, default=0.0)  # Moyenne buts domicile
    # away_goals_avg = Column(Float, default=0.0)  # Moyenne buts extérieur
    
    # L'analyse détaillée expliquant pourquoi ce pronostic
    analysis = Column(String, nullable=True)
    
    # Le conseil/type de pari (ex: "Victoire domicile", "Plus de 2.5 buts")
    bet_tip = Column(String, nullable=True)

    match = relationship("Match", back_populates="expert_prediction")
