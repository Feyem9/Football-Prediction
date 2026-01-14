"""
Multi-Logic Prediction Engine.

Ce service combine les 3 logiques de prédiction:
- Logique de Papa: Niveau des championnats, position, moyenne de buts
- Logique de Grand Frère: H2H, loi du domicile, force relative
- Ma Logique: Double validation, consensus, 10 derniers matchs

Pondération: Papa (35%) + Grand Frère (35%) + Ma Logique (30%)
"""
from typing import Optional, Dict, List, Tuple, NamedTuple
from dataclasses import dataclass
from sqlalchemy.orm import Session
import logging

from models.match import Match
from models.standing import Standing
from models.team_stats import TeamStats
from services.prediction_service import PredictionService

logger = logging.getLogger(__name__)


@dataclass
class LogicResult:
    """Résultat d'une logique de prédiction."""
    home_win_prob: float      # Probabilité victoire domicile (0-1)
    draw_prob: float          # Probabilité match nul (0-1)
    away_win_prob: float      # Probabilité victoire extérieur (0-1)
    predicted_home_goals: int
    predicted_away_goals: int
    confidence: float         # Confiance dans cette prédiction (0-1)
    bet_tip: str              # Conseil de pari
    analysis: str             # Analyse textuelle


@dataclass
class CombinedPrediction:
    """Prédiction combinée des 3 logiques."""
    # Résultats par logique
    papa_result: Optional[LogicResult]
    grand_frere_result: Optional[LogicResult]
    ma_logique_result: Optional[LogicResult]
    
    # Prédiction finale combinée
    final_home_goals: int
    final_away_goals: int
    final_confidence: float
    final_bet_tip: str
    
    # Indicateur de consensus
    consensus_level: str  # "FORT", "MOYEN", "FAIBLE"
    all_agree: bool       # Les 3 logiques sont d'accord?


class MultiLogicPredictionEngine:
    """
    Moteur de prédiction combinant les 3 logiques familiales.
    
    Pondérations:
    - Papa: 35% (position + niveau championnat + moyenne buts)
    - Grand Frère: 35% (H2H + domicile + cartons)
    - Ma Logique: 30% (double validation + consensus)
    """
    
    # Pondérations des logiques
    WEIGHT_PAPA = 0.35
    WEIGHT_GRAND_FRERE = 0.35
    WEIGHT_MA_LOGIQUE = 0.30
    
    def __init__(self, db: Session):
        """Initialise le moteur multi-logique."""
        self.db = db
        self.prediction_service = PredictionService(db)
    
    # =========================================
    # LOGIQUE DE PAPA
    # =========================================
    
    async def logic_papa(self, match: Match) -> Optional[LogicResult]:
        """
        Logique de Papa: Focus sur les performances et championnats.
        
        Critères:
        1. Performances individuelles (forme V/N/D)
        2. Niveau des championnats (PL > FL1)
        3. Position dans le championnat
        4. Identifier les extrêmes (fort/faible)
        5. Position exacte de chaque équipe
        + Moyenne de buts sur 10 matchs
        + H2H: équipe dominante
        """
        try:
            # 1. Récupérer les standings
            home_standing = self.db.query(Standing).filter(
                Standing.team_id == match.home_team_id,
                Standing.competition_code == match.competition_code
            ).first()
            
            away_standing = self.db.query(Standing).filter(
                Standing.team_id == match.away_team_id,
                Standing.competition_code == match.competition_code
            ).first()
            
            if not home_standing or not away_standing:
                return None
            
            # 2. Niveau du championnat
            league_strength = self.prediction_service._get_league_strength(
                match.competition_code
            )
            
            # 3. Position relative (plus basse = meilleure)
            home_position_score = 1 - (home_standing.position / 20)
            away_position_score = 1 - (away_standing.position / 20)
            
            # 4. Différence de points
            points_diff = home_standing.points - away_standing.points
            points_advantage = min(max(points_diff / 30, -1), 1) * 0.5 + 0.5
            
            # 5. Moyenne de buts (récupérer stats si dispo)
            home_stats = self.db.query(TeamStats).filter(
                TeamStats.team_id == match.home_team_id,
                TeamStats.competition_code == match.competition_code
            ).first()
            
            away_stats = self.db.query(TeamStats).filter(
                TeamStats.team_id == match.away_team_id,
                TeamStats.competition_code == match.competition_code
            ).first()
            
            home_goals_avg = home_stats.avg_goals_scored if home_stats else 1.2
            away_goals_avg = away_stats.avg_goals_scored if away_stats else 1.0
            
            # Calculer les forces
            home_strength = (
                home_position_score * 0.4 +
                points_advantage * 0.3 +
                league_strength * 0.3
            )
            
            away_strength = (
                away_position_score * 0.4 +
                (1 - points_advantage) * 0.3 +
                league_strength * 0.3
            )
            
            # Prédire le score
            home_goals = round(home_strength * home_goals_avg * 1.5)
            away_goals = round(away_strength * away_goals_avg * 1.2)
            
            # Probabilités
            total_strength = home_strength + away_strength
            home_win_prob = home_strength / total_strength + 0.05  # Bonus domicile
            away_win_prob = away_strength / total_strength - 0.05
            draw_prob = 1 - abs(home_strength - away_strength)
            
            # Normaliser
            total_prob = home_win_prob + draw_prob + away_win_prob
            home_win_prob /= total_prob
            draw_prob /= total_prob
            away_win_prob /= total_prob
            
            # Confiance basée sur la différence de position
            confidence = min(abs(home_standing.position - away_standing.position) / 10 + 0.4, 0.9)
            
            # Conseil
            if home_win_prob > 0.5:
                bet_tip = "1 (Victoire domicile)"
            elif away_win_prob > 0.5:
                bet_tip = "2 (Victoire extérieur)"
            else:
                bet_tip = "X (Match nul)"
            
            analysis = (
                f"📊 Papa: {match.home_team} (#{home_standing.position}, {home_standing.points}pts) "
                f"vs {match.away_team} (#{away_standing.position}, {away_standing.points}pts). "
                f"Niveau ligue: {league_strength:.0%}"
            )
            
            return LogicResult(
                home_win_prob=home_win_prob,
                draw_prob=draw_prob,
                away_win_prob=away_win_prob,
                predicted_home_goals=home_goals,
                predicted_away_goals=away_goals,
                confidence=confidence,
                bet_tip=bet_tip,
                analysis=analysis
            )
            
        except Exception as e:
            logger.error(f"Erreur logique Papa: {e}")
            return None
    
    # =========================================
    # LOGIQUE DE GRAND FRÈRE
    # =========================================
    
    async def logic_grand_frere(self, match: Match) -> Optional[LogicResult]:
        """
        Logique de Grand Frère: Focus H2H et domicile.
        
        Critères:
        1. Rencontres passées (H2H)
        2. Force de l'équipe
        3. Impact cartons rouges (si dispo)
        4. Nombre de buts
        5. Contexte buts (vs fort/faible)
        + Loi du domicile (Fort @ Moyen = Nul possible)
        """
        try:
            # 1. Récupérer les standings pour la force
            home_standing = self.db.query(Standing).filter(
                Standing.team_id == match.home_team_id,
                Standing.competition_code == match.competition_code
            ).first()
            
            away_standing = self.db.query(Standing).filter(
                Standing.team_id == match.away_team_id,
                Standing.competition_code == match.competition_code
            ).first()
            
            if not home_standing or not away_standing:
                return None
            
            # 2. Calculer les forces relatives
            home_strength = 1 - (home_standing.position / 20)
            away_strength = 1 - (away_standing.position / 20)
            
            is_home_stronger = home_strength > away_strength
            strength_diff = abs(home_strength - away_strength)
            
            # 3. Appliquer la loi du domicile
            home_advantage = self.prediction_service._calculate_home_advantage(
                home_strength, away_strength, is_home_stronger
            )
            
            # 4. Ajuster les probabilités avec la loi
            if not is_home_stronger and strength_diff > 0.15:
                # Fort @ Moyen: potentiel match nul!
                draw_prob = 0.35 + home_advantage
                home_win_prob = 0.30 + home_advantage
                away_win_prob = 1 - draw_prob - home_win_prob
            else:
                home_win_prob = home_strength + home_advantage
                away_win_prob = away_strength * 0.85  # Malus extérieur
                draw_prob = 1 - home_win_prob - away_win_prob
            
            # Normaliser
            total = home_win_prob + draw_prob + away_win_prob
            home_win_prob /= total
            draw_prob /= total
            away_win_prob /= total
            
            # 5. Prédire les buts
            home_stats = self.db.query(TeamStats).filter(
                TeamStats.team_id == match.home_team_id,
                TeamStats.competition_code == match.competition_code
            ).first()
            
            away_stats = self.db.query(TeamStats).filter(
                TeamStats.team_id == match.away_team_id,
                TeamStats.competition_code == match.competition_code
            ).first()
            
            home_goals_avg = home_stats.avg_goals_scored if home_stats else 1.3
            away_goals_avg = away_stats.avg_goals_scored if away_stats else 1.0
            
            home_goals = round(home_goals_avg * (1 + home_advantage))
            away_goals = round(away_goals_avg * 0.9)
            
            # Confiance basée sur H2H et position
            confidence = 0.5 + (strength_diff * 0.5)
            
            # Conseil avec la loi du domicile
            if not is_home_stronger and strength_diff > 0.15:
                bet_tip = "X ou 1X (Loi domicile)"
            elif home_win_prob > 0.5:
                bet_tip = "1 (Victoire domicile)"
            elif away_win_prob > 0.5:
                bet_tip = "2 (Victoire extérieur)"
            else:
                bet_tip = "X (Match nul)"
            
            analysis = (
                f"🏠 Grand Frère: Loi domicile appliquée. "
                f"Fort @ Moyen = {'OUI' if not is_home_stronger and strength_diff > 0.15 else 'NON'}. "
                f"Avantage domicile: {home_advantage:.0%}"
            )
            
            return LogicResult(
                home_win_prob=home_win_prob,
                draw_prob=draw_prob,
                away_win_prob=away_win_prob,
                predicted_home_goals=home_goals,
                predicted_away_goals=away_goals,
                confidence=confidence,
                bet_tip=bet_tip,
                analysis=analysis
            )
            
        except Exception as e:
            logger.error(f"Erreur logique Grand Frère: {e}")
            return None
    
    # =========================================
    # MA LOGIQUE
    # =========================================
    
    async def logic_ma_logique(self, match: Match) -> Optional[LogicResult]:
        """
        Ma Logique: Double validation et consensus.
        
        Critères:
        1. Récupérer les 10 derniers matchs V/N/D
        2. Calculer moyenne buts (÷10)
        3. H2H (buts totaux, dominant)
        4. Double validation (mon analyse vs apps)
        
        Note: Sans API externe, on utilise les stats locales.
        """
        try:
            # 1. Récupérer les stats d'équipe (10 derniers matchs)
            home_stats = self.db.query(TeamStats).filter(
                TeamStats.team_id == match.home_team_id,
                TeamStats.competition_code == match.competition_code
            ).first()
            
            away_stats = self.db.query(TeamStats).filter(
                TeamStats.team_id == match.away_team_id,
                TeamStats.competition_code == match.competition_code
            ).first()
            
            # 2. Construire la forme V/N/D sur 10 matchs
            home_form = ""
            away_form = ""
            
            if home_stats:
                wins = home_stats.wins or 0
                draws = home_stats.draws or 0
                losses = home_stats.losses or 0
                total = wins + draws + losses
                if total > 0:
                    home_form = ",".join(["W"] * wins + ["D"] * draws + ["L"] * losses)
            
            if away_stats:
                wins = away_stats.wins or 0
                draws = away_stats.draws or 0
                losses = away_stats.losses or 0
                total = wins + draws + losses
                if total > 0:
                    away_form = ",".join(["W"] * wins + ["D"] * draws + ["L"] * losses)
            
            # 3. Calculer le score de forme (10 matchs)
            home_form_score = self.prediction_service._calculate_form_score(home_form, 10)
            away_form_score = self.prediction_service._calculate_form_score(away_form, 10)
            
            # 4. Moyenne de buts
            home_goals_avg = home_stats.avg_goals_scored if home_stats else 1.2
            away_goals_avg = away_stats.avg_goals_scored if away_stats else 1.0
            
            # 5. Calculer les probabilités basées sur la forme
            total_form = home_form_score + away_form_score
            if total_form > 0:
                home_win_prob = home_form_score / total_form + 0.05  # Bonus domicile
                away_win_prob = away_form_score / total_form - 0.05
            else:
                home_win_prob = 0.40
                away_win_prob = 0.35
            
            draw_prob = 0.25  # Base pour match nul
            
            # Normaliser
            total = home_win_prob + draw_prob + away_win_prob
            home_win_prob /= total
            draw_prob /= total
            away_win_prob /= total
            
            # 6. Prédire les buts
            home_goals = round(home_goals_avg * (1 + home_form_score * 0.3))
            away_goals = round(away_goals_avg * (1 + away_form_score * 0.3))
            
            # 7. Confiance basée sur la différence de forme
            confidence = min(abs(home_form_score - away_form_score) * 2 + 0.3, 0.85)
            
            # Conseil
            if home_win_prob > away_win_prob and home_win_prob > draw_prob:
                bet_tip = "1 (Forme domicile)"
            elif away_win_prob > home_win_prob and away_win_prob > draw_prob:
                bet_tip = "2 (Forme extérieur)"
            else:
                bet_tip = "X (Formes similaires)"
            
            analysis = (
                f"📈 Ma Logique: Forme domicile={home_form_score:.0%}, "
                f"Forme extérieur={away_form_score:.0%}. "
                f"Moy. buts: {home_goals_avg:.1f} vs {away_goals_avg:.1f}"
            )
            
            return LogicResult(
                home_win_prob=home_win_prob,
                draw_prob=draw_prob,
                away_win_prob=away_win_prob,
                predicted_home_goals=home_goals,
                predicted_away_goals=away_goals,
                confidence=confidence,
                bet_tip=bet_tip,
                analysis=analysis
            )
            
        except Exception as e:
            logger.error(f"Erreur ma logique: {e}")
            return None
    
    # =========================================
    # COMBINAISON DES 3 LOGIQUES
    # =========================================
    
    async def generate_combined_prediction(self, match: Match) -> Optional[CombinedPrediction]:
        """
        Génère une prédiction combinée des 3 logiques.
        
        Pondération: Papa (35%) + Grand Frère (35%) + Ma Logique (30%)
        """
        # Exécuter les 3 logiques
        papa_result = await self.logic_papa(match)
        gf_result = await self.logic_grand_frere(match)
        ma_result = await self.logic_ma_logique(match)
        
        # Collecter les résultats valides
        results = []
        weights = []
        
        if papa_result:
            results.append(papa_result)
            weights.append(self.WEIGHT_PAPA)
        
        if gf_result:
            results.append(gf_result)
            weights.append(self.WEIGHT_GRAND_FRERE)
        
        if ma_result:
            results.append(ma_result)
            weights.append(self.WEIGHT_MA_LOGIQUE)
        
        if not results:
            return None
        
        # Normaliser les poids
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]
        
        # Moyenne pondérée des buts
        final_home_goals = round(sum(
            r.predicted_home_goals * w for r, w in zip(results, weights)
        ))
        final_away_goals = round(sum(
            r.predicted_away_goals * w for r, w in zip(results, weights)
        ))
        
        # Moyenne pondérée de la confiance
        final_confidence = sum(
            r.confidence * w for r, w in zip(results, weights)
        )
        
        # Déterminer le consensus
        bet_tips = [r.bet_tip.split()[0] for r in results]  # Premier mot (1, 2, X)
        unique_tips = set(bet_tips)
        
        if len(unique_tips) == 1:
            consensus_level = "FORT"
            all_agree = True
        elif len(unique_tips) == 2:
            consensus_level = "MOYEN"
            all_agree = False
        else:
            consensus_level = "FAIBLE"
            all_agree = False
        
        # Conseil final basé sur le consensus
        if final_home_goals > final_away_goals:
            final_bet_tip = f"1 (Victoire domicile) - Consensus: {consensus_level}"
        elif final_away_goals > final_home_goals:
            final_bet_tip = f"2 (Victoire extérieur) - Consensus: {consensus_level}"
        else:
            final_bet_tip = f"X (Match nul) - Consensus: {consensus_level}"
        
        return CombinedPrediction(
            papa_result=papa_result,
            grand_frere_result=gf_result,
            ma_logique_result=ma_result,
            final_home_goals=final_home_goals,
            final_away_goals=final_away_goals,
            final_confidence=final_confidence,
            final_bet_tip=final_bet_tip,
            consensus_level=consensus_level,
            all_agree=all_agree
        )
