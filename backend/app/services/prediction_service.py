"""
Service de génération de prédictions automatiques.

Ce service génère des pronostics basés sur les données du classement
et la forme récente des équipes.
"""
from typing import Optional, Dict, List, Tuple
from sqlalchemy.orm import Session

from models.match import Match
from models.prediction import ExpertPrediction
from services.football_api import football_data_service


class PredictionService:
    """
    Service pour générer des prédictions automatiques.
    
    L'algorithme prend en compte:
    - Position au classement
    - Différence de points
    - Forme récente (5 derniers matchs)
    - Avantage du terrain (domicile)
    """
    
    # Bonus domicile (en % de probabilité)
    HOME_ADVANTAGE = 0.10
    
    def __init__(self, db: Session):
        """
        Initialise le service de prédictions.
        
        Args:
            db: Session SQLAlchemy
        """
        self.db = db
        self._standings_cache: Dict[str, List[dict]] = {}
    
    async def _get_standings(self, competition_code: str) -> List[dict]:
        """
        Récupère le classement avec cache.
        
        Args:
            competition_code: Code de la compétition
            
        Returns:
            Liste des positions au classement
        """
        if competition_code not in self._standings_cache:
            try:
                result = await football_data_service.get_standings(competition_code)
                standings = result.get("standings", [])
                if standings:
                    self._standings_cache[competition_code] = standings[0].get("table", [])
                else:
                    self._standings_cache[competition_code] = []
            except Exception:
                self._standings_cache[competition_code] = []
        
        return self._standings_cache[competition_code]
    
    def _get_team_position(self, standings: List[dict], team_id: int) -> Optional[dict]:
        """
        Trouve les infos d'une équipe dans le classement.
        
        Args:
            standings: Classement complet
            team_id: ID de l'équipe
            
        Returns:
            Dict avec position, points, forme ou None
        """
        for entry in standings:
            if entry.get("team", {}).get("id") == team_id:
                return entry
        return None
    
    def _calculate_form_score(self, form: str) -> float:
        """
        Calcule un score de forme basé sur les 5 derniers matchs.
        
        Args:
            form: Forme sous format "W,D,L,W,W"
            
        Returns:
            Score entre 0 et 1
        """
        if not form:
            return 0.5
        
        results = form.split(",")
        score = 0
        for result in results:
            if result == "W":
                score += 3
            elif result == "D":
                score += 1
            # L = 0
        
        # Max possible = 15 (5 victoires)
        return score / 15
    
    def _predict_score(
        self, 
        home_strength: float, 
        away_strength: float,
        home_goals_avg: float,
        away_goals_avg: float
    ) -> Tuple[int, int]:
        """
        Prédit le score basé sur les forces des équipes.
        
        Args:
            home_strength: Force équipe domicile (0-1)
            away_strength: Force équipe extérieur (0-1)
            home_goals_avg: Moyenne buts marqués domicile
            away_goals_avg: Moyenne buts marqués extérieur
            
        Returns:
            Tuple (buts_domicile, buts_exterieur)
        """
        # Score prédit basé sur la force relative et moyenne de buts
        home_expected = (home_strength + self.HOME_ADVANTAGE) * home_goals_avg
        away_expected = away_strength * away_goals_avg * 0.9  # Malus extérieur
        
        # Arrondir aux entiers
        home_goals = max(0, round(home_expected))
        away_goals = max(0, round(away_expected))
        
        return home_goals, away_goals
    
    def _generate_bet_tip(
        self, 
        home_goals: int, 
        away_goals: int, 
        confidence: float
    ) -> str:
        """
        Génère un conseil de pari.
        
        Args:
            home_goals: Buts prédits domicile
            away_goals: Buts prédits extérieur
            confidence: Niveau de confiance
            
        Returns:
            Conseil de pari
        """
        total_goals = home_goals + away_goals
        
        if confidence >= 0.7:
            if home_goals > away_goals:
                return "Victoire domicile"
            elif away_goals > home_goals:
                return "Victoire extérieur"
            else:
                return "Match nul"
        elif total_goals >= 3:
            return "Plus de 2.5 buts"
        elif total_goals <= 2:
            return "Moins de 2.5 buts"
        else:
            return "Les deux équipes marquent"
    
    def _generate_analysis(
        self,
        home_team: str,
        away_team: str,
        home_entry: Optional[dict],
        away_entry: Optional[dict],
        home_goals: int,
        away_goals: int
    ) -> str:
        """
        Génère une analyse textuelle de la prédiction.
        
        Args:
            home_team: Nom équipe domicile
            away_team: Nom équipe extérieur
            home_entry: Données classement domicile
            away_entry: Données classement extérieur
            home_goals: Score prédit domicile
            away_goals: Score prédit extérieur
            
        Returns:
            Texte d'analyse
        """
        analysis_parts = []
        
        if home_entry and away_entry:
            home_pos = home_entry.get("position", 0)
            away_pos = away_entry.get("position", 0)
            home_pts = home_entry.get("points", 0)
            away_pts = away_entry.get("points", 0)
            
            analysis_parts.append(
                f"{home_team} ({home_pos}e, {home_pts} pts) reçoit "
                f"{away_team} ({away_pos}e, {away_pts} pts)."
            )
            
            if home_pos < away_pos:
                diff = away_pos - home_pos
                analysis_parts.append(
                    f"Avantage classement de {diff} places pour {home_team}."
                )
            elif away_pos < home_pos:
                diff = home_pos - away_pos
                analysis_parts.append(
                    f"Attention, {away_team} est {diff} places devant au classement."
                )
        
        if home_goals > away_goals:
            analysis_parts.append(f"Nous prévoyons une victoire de {home_team} à domicile.")
        elif away_goals > home_goals:
            analysis_parts.append(f"Nous voyons {away_team} s'imposer en déplacement.")
        else:
            analysis_parts.append("Match équilibré, le nul semble probable.")
        
        return " ".join(analysis_parts)
    
    async def generate_prediction(self, match: Match) -> Optional[ExpertPrediction]:
        """
        Génère une prédiction pour un match.
        
        Args:
            match: Instance Match
            
        Returns:
            ExpertPrediction générée ou None si impossible
        """
        # Vérifier si prédiction existe déjà
        existing = self.db.query(ExpertPrediction).filter(
            ExpertPrediction.match_id == match.id
        ).first()
        
        if existing:
            return existing
        
        # Récupérer le classement
        if not match.competition_code:
            return None
        
        standings = await self._get_standings(match.competition_code)
        
        if not standings:
            # Prédiction par défaut sans données
            prediction = ExpertPrediction(
                match_id=match.id,
                home_score_forecast=1,
                away_score_forecast=1,
                confidence=0.3,
                analysis=f"Match entre {match.home_team} et {match.away_team}. Données insuffisantes pour une analyse détaillée.",
                bet_tip="Match nul"
            )
            self.db.add(prediction)
            self.db.commit()
            return prediction
        
        # Trouver les équipes dans le classement
        home_entry = self._get_team_position(standings, match.home_team_id) if match.home_team_id else None
        away_entry = self._get_team_position(standings, match.away_team_id) if match.away_team_id else None
        
        # Calculer les forces
        total_teams = len(standings)
        
        if home_entry:
            home_pos = home_entry.get("position", total_teams // 2)
            home_strength = 1 - (home_pos / total_teams)
            home_form = self._calculate_form_score(home_entry.get("form", ""))
            home_goals_avg = home_entry.get("goalsFor", 20) / max(1, home_entry.get("playedGames", 1))
        else:
            home_strength = 0.5
            home_form = 0.5
            home_goals_avg = 1.3
        
        if away_entry:
            away_pos = away_entry.get("position", total_teams // 2)
            away_strength = 1 - (away_pos / total_teams)
            away_form = self._calculate_form_score(away_entry.get("form", ""))
            away_goals_avg = away_entry.get("goalsFor", 20) / max(1, away_entry.get("playedGames", 1))
        else:
            away_strength = 0.5
            away_form = 0.5
            away_goals_avg = 1.2
        
        # Combiner classement et forme
        home_final = (home_strength * 0.6) + (home_form * 0.4)
        away_final = (away_strength * 0.6) + (away_form * 0.4)
        
        # Prédire le score
        home_goals, away_goals = self._predict_score(
            home_final, away_final, 
            home_goals_avg, away_goals_avg
        )
        
        # Calculer la confiance
        strength_diff = abs(home_final - away_final)
        confidence = min(0.85, 0.4 + strength_diff)
        
        # Générer conseil et analyse
        bet_tip = self._generate_bet_tip(home_goals, away_goals, confidence)
        analysis = self._generate_analysis(
            match.home_team, match.away_team,
            home_entry, away_entry,
            home_goals, away_goals
        )
        
        # Créer la prédiction
        prediction = ExpertPrediction(
            match_id=match.id,
            home_score_forecast=home_goals,
            away_score_forecast=away_goals,
            confidence=round(confidence, 2),
            analysis=analysis,
            bet_tip=bet_tip
        )
        
        self.db.add(prediction)
        self.db.commit()
        self.db.refresh(prediction)
        
        return prediction
    
    async def generate_predictions_for_upcoming(self, limit: int = 20) -> int:
        """
        Génère des prédictions pour les prochains matchs.
        
        Args:
            limit: Nombre maximum de matchs à traiter
            
        Returns:
            Nombre de prédictions générées
        """
        from datetime import datetime, timezone
        
        # Matchs à venir sans prédiction
        matches = self.db.query(Match).filter(
            Match.match_date > datetime.now(timezone.utc),
            Match.status.in_(["SCHEDULED", "TIMED"]),
            ~Match.id.in_(
                self.db.query(ExpertPrediction.match_id)
            )
        ).order_by(Match.match_date).limit(limit).all()
        
        count = 0
        for match in matches:
            try:
                await self.generate_prediction(match)
                count += 1
            except Exception:
                continue
        
        return count
