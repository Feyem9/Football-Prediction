from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from .base import Base

class ExpertPrediction(Base):
    """
    Représente le pronostic officiel donné par l'application (l'Expert) pour un match.
    Le joueur consulte ce pronostic pour s'orienter.
    
    Intègre les 3 logiques de prédiction:
    - Papa: Classement, niveau championnat, moyenne de buts
    - Grand Frère: H2H, loi du domicile, force relative
    - Ma Logique: Forme récente, double validation, consensus
    """
    __tablename__ = "expert_predictions"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), unique=True, nullable=False)
    
    # === Score Final (Consensus des 3 logiques) ===
    home_score_forecast = Column(Integer, nullable=False)
    away_score_forecast = Column(Integer, nullable=False)
    confidence = Column(Float, default=0.5)
    bet_tip = Column(String, nullable=True)
    analysis = Column(String, nullable=True)
    
    # Moyenne de buts par match pour chaque équipe
    home_goals_avg = Column(Float, default=0.0)
    away_goals_avg = Column(Float, default=0.0)
    
    # === Logique de Papa (Classement + Niveau Championnat) ===
    papa_home_score = Column(Integer, nullable=True)
    papa_away_score = Column(Integer, nullable=True)
    papa_confidence = Column(Float, nullable=True)
    papa_tip = Column(String, nullable=True)
    
    # === Logique Grand Frère (H2H + Domicile) ===
    grand_frere_home_score = Column(Integer, nullable=True)
    grand_frere_away_score = Column(Integer, nullable=True)
    grand_frere_confidence = Column(Float, nullable=True)
    grand_frere_tip = Column(String, nullable=True)
    
    # === Ma Logique (Forme + Consensus) ===
    ma_logique_home_score = Column(Integer, nullable=True)
    ma_logique_away_score = Column(Integer, nullable=True)
    ma_logique_confidence = Column(Float, nullable=True)
    ma_logique_tip = Column(String, nullable=True)
    
    # === Matchs importants (données contextuelles pour Papa) ===
    # Format JSON: {"competition": "...", "opponent": "...", "date": "...", "days_until": N}
    home_upcoming_important = Column(String, nullable=True)  # Match important à venir (domicile)
    home_recent_important = Column(String, nullable=True)    # Match important récent (domicile)
    away_upcoming_important = Column(String, nullable=True)  # Match important à venir (extérieur)
    away_recent_important = Column(String, nullable=True)    # Match important récent (extérieur)
    
    # === Données pour Preuves (Stats utilisées lors du calcul) ===
    h2h_home_wins = Column(Integer, nullable=True)
    h2h_away_wins = Column(Integer, nullable=True)
    h2h_draws = Column(Integer, nullable=True)
    h2h_matches_count = Column(Integer, nullable=True)  # Nombre de matchs H2H analysés
    h2h_home_goals_total = Column(Integer, nullable=True)  # Total buts équipe domicile dans H2H
    h2h_away_goals_total = Column(Integer, nullable=True)  # Total buts équipe extérieur dans H2H
    h2h_home_goals_freq = Column(Float, nullable=True)  # Fréquence buts/match équipe domicile
    h2h_away_goals_freq = Column(Float, nullable=True)  # Fréquence buts/match équipe extérieur
    h2h_top_scorer = Column(String, nullable=True)  # "home", "away", ou "equal"
    home_form_score = Column(Float, nullable=True)
    away_form_score = Column(Float, nullable=True)
    
    # === Grand Frère : Analyse combinée Papa + Domicile ===
    gf_home_league_level = Column(Float, nullable=True)  # Niveau ligue équipe domicile
    gf_away_league_level = Column(Float, nullable=True)  # Niveau ligue équipe extérieur
    gf_home_advantage_bonus = Column(Float, nullable=True)  # Bonus domicile calculé
    gf_verdict = Column(String, nullable=True)  # Verdict Grand Frère (explication)

    match = relationship("Match", back_populates="expert_prediction")
