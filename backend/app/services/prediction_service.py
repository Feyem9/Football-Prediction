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
    
    Intègre les 3 logiques de prédiction:
    - Logique de Papa: Niveau des championnats, position, moyenne de buts
    - Logique Grand Frère: H2H, loi du domicile, force relative
    - Ma Logique: Double validation, consensus, 10 derniers matchs
    
    L'algorithme prend en compte:
    - Position au classement
    - Différence de points
    - Forme récente (10 derniers matchs)
    - Avantage du terrain (domicile) avec loi Grand Frère
    - Niveau relatif des championnats
    """
    
    # Ranking des championnats (Logique de Papa)
    LEAGUE_STRENGTH = {
        "PL": 1.00,   # Premier League - Top niveau
        "PD": 0.95,   # La Liga
        "SA": 0.90,   # Serie A
        "BL1": 0.90,  # Bundesliga
        "FL1": 0.80,  # Ligue 1
        "CL": 1.00,   # Champions League
        "WC": 1.00,   # World Cup
    }
    
    # Bonus domicile de base (en % de probabilité)
    HOME_ADVANTAGE = 0.12
    
    # Poids des différents facteurs (Papa + Grand Frère = 70%)
    WEIGHT_STANDINGS = 0.35   # Position au classement
    WEIGHT_LEAGUE = 0.15      # Niveau du championnat (Papa)
    WEIGHT_FORM = 0.25        # Forme récente (10 matchs)
    WEIGHT_H2H = 0.25         # Confrontations directes (Grand Frère)
    
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
    
    def _calculate_form_score(self, form: str, num_matches: int = 10) -> float:
        """
        Calcule un score de forme basé sur les derniers matchs.
        
        Logique de Papa + Ma Logique: Utilise les 10 derniers matchs.
        
        Args:
            form: Forme sous format "W,D,L,W,W" ou liste de résultats
            num_matches: Nombre de matchs à considérer (défaut: 10)
            
        Returns:
            Score entre 0 et 1
        """
        if not form:
            return 0.5
        
        results = form.split(",") if isinstance(form, str) else form
        # Limiter au nombre de matchs demandé
        results = results[:num_matches]
        
        score = 0
        for result in results:
            if result == "W":
                score += 3
            elif result == "D":
                score += 1
            # L = 0
        
        # Max possible = 3 * num_matches (toutes victoires)
        max_score = 3 * len(results) if results else 1
        return score / max_score
    
    def _get_league_strength(self, competition_code: str) -> float:
        """
        Retourne la force relative d'un championnat.
        
        Logique de Papa: Comparer le niveau des championnats.
        
        Args:
            competition_code: Code de la compétition (PL, FL1, etc.)
            
        Returns:
            Force entre 0 et 1 (1 = top niveau)
        """
        return self.LEAGUE_STRENGTH.get(competition_code, 0.75)
    
    def _calculate_home_advantage(
        self, 
        home_strength: float, 
        away_strength: float,
        is_home_team_stronger: bool
    ) -> float:
        """
        Calcule l'avantage à domicile avec la loi de Grand Frère.
        
        Loi du domicile: Si un fort joue chez un moyen, 
        le moyen à domicile peut obtenir le nul.
        
        Args:
            home_strength: Force équipe domicile (0-1)
            away_strength: Force équipe extérieur (0-1)
            is_home_team_stronger: True si domicile est plus fort
            
        Returns:
            Bonus domicile ajusté
        """
        base_advantage = self.HOME_ADVANTAGE
        
        # Loi de Grand Frère: Fort @ Moyen = avantage domicile renforcé
        strength_diff = abs(home_strength - away_strength)
        
        if not is_home_team_stronger and strength_diff > 0.15:
            # Le faible est à domicile contre un fort -> bonus renforcé
            base_advantage *= 1.5  # +50% bonus
        elif is_home_team_stronger and strength_diff < 0.10:
            # Match équilibré -> bonus standard
            pass
        
        return min(base_advantage, 0.20)  # Cap à 20%

    
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
    
    def _calculate_h2h_stats(self, matches: List[dict], home_team_id: int, away_team_id: int) -> Tuple[int, int, int]:
        """Calcul les stats H2H à partir de la liste des matchs."""
        h_wins = 0
        a_wins = 0
        draws = 0
        
        for m in matches:
            if m.get("status") != "FINISHED":
                continue
                
            score = m.get("score", {}).get("fullTime", {})
            h_score = score.get("home")
            a_score = score.get("away")
            
            if h_score is None or a_score is None:
                continue
                
            match_home_id = m.get("homeTeam", {}).get("id")
            match_away_id = m.get("awayTeam", {}).get("id")
            
            winner = None
            if h_score > a_score:
                winner = match_home_id
            elif a_score > h_score:
                winner = match_away_id
            else:
                draws += 1
                continue
                
            if winner == home_team_id:
                h_wins += 1
            elif winner == away_team_id:
                a_wins += 1
                
        return h_wins, a_wins, draws

    def _generate_analysis(
        self,
        home_team: str,
        away_team: str,
        home_entry: Optional[dict],
        away_entry: Optional[dict],
        home_goals: int,
        away_goals: int,
        h2h_stats: Optional[Tuple[int, int, int]] = None
    ) -> str:
        """
        Génère une analyse textuelle de la prédiction.
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
                    f"Avantage classement (+{diff} places) pour {home_team}."
                )
            elif away_pos < home_pos:
                diff = home_pos - away_pos
                analysis_parts.append(
                    f"Attention, {away_team} est {diff} places devant au classement."
                )

        # Ajout analyse H2H
        if h2h_stats:
            h_wins, a_wins, draws = h2h_stats
            total = h_wins + a_wins + draws
            if total > 0:
                analysis_parts.append(
                    f"Historique H2H ({total} matchs) : {h_wins} victoires pour {home_team}, "
                    f"{a_wins} pour {away_team} et {draws} nuls."
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
        
        # Récupérer H2H
        h2h_stats = None
        home_h2h = 0.5
        away_h2h = 0.5
        
        if match.external_id and match.home_team_id and match.away_team_id:
            try:
                # On récupère plus de matchs (limit=10) pour avoir un bon échantillon
                h2h_data = await football_data_service.get_match_h2h(match.external_id, limit=10)
                matches = h2h_data.get("matches", [])
                
                if matches:
                    h_wins, a_wins, draws = self._calculate_h2h_stats(
                        matches, match.home_team_id, match.away_team_id
                    )
                    h2h_stats = (h_wins, a_wins, draws)
                    total = h_wins + a_wins + draws
                    
                    if total > 0:
                        # Score entre 0 et 1 (Victoire = 1, Nul = 0.33)
                        # On donne moins de points au nul pour le winner
                        home_h2h = (h_wins * 3 + draws * 1) / (total * 3)
                        away_h2h = (a_wins * 3 + draws * 1) / (total * 3)
            except Exception:
                pass

        # === LOGIQUE DE PAPA (Classement + Niveau Championnat) ===
        # Basé sur: Position au classement, moyenne de buts, niveau du championnat
        league_level = self._get_league_strength(match.competition_code)
        papa_home_strength = home_strength * league_level
        papa_away_strength = away_strength * league_level
        
        papa_home_score, papa_away_score = self._predict_score(
            papa_home_strength, papa_away_strength,
            home_goals_avg, away_goals_avg
        )
        papa_confidence = min(0.9, 0.5 + abs(home_strength - away_strength) * 0.5)
        papa_tip = self._generate_bet_tip(papa_home_score, papa_away_score, papa_confidence)
        
        # === LOGIQUE GRAND FRÈRE (H2H + Loi Domicile) ===
        # Basé sur: Confrontations directes, avantage domicile
        home_adv = self._calculate_home_advantage(home_strength, away_strength, home_strength > away_strength)
        gf_home_strength = home_h2h + home_adv
        gf_away_strength = away_h2h
        
        gf_home_score, gf_away_score = self._predict_score(
            gf_home_strength, gf_away_strength,
            home_goals_avg, away_goals_avg
        )
        gf_confidence = min(0.8, 0.4 + abs(home_h2h - away_h2h))
        gf_tip = self._generate_bet_tip(gf_home_score, gf_away_score, gf_confidence)
        
        # === MA LOGIQUE (Forme + Double Validation) ===
        # Basé sur: Forme récente (10 matchs), consensus des 2 autres logiques
        ml_home_strength = home_form
        ml_away_strength = away_form
        
        ml_home_score, ml_away_score = self._predict_score(
            ml_home_strength, ml_away_strength,
            home_goals_avg, away_goals_avg
        )
        ml_confidence = min(0.7, 0.3 + abs(home_form - away_form))
        ml_tip = self._generate_bet_tip(ml_home_score, ml_away_score, ml_confidence)
        
        # === CONSENSUS FINAL ===
        # Moyenne des 3 logiques, pondérée par la confiance
        total_weight = papa_confidence + gf_confidence + ml_confidence
        
        if total_weight > 0:
            home_goals = round(
                (papa_home_score * papa_confidence + 
                 gf_home_score * gf_confidence + 
                 ml_home_score * ml_confidence) / total_weight
            )
            away_goals = round(
                (papa_away_score * papa_confidence + 
                 gf_away_score * gf_confidence + 
                 ml_away_score * ml_confidence) / total_weight
            )
        else:
            home_goals = 1
            away_goals = 1
        
        # Confiance finale = moyenne des confiances
        confidence = round((papa_confidence + gf_confidence + ml_confidence) / 3, 2)
        
        # Générer conseil et analyse
        bet_tip = self._generate_bet_tip(home_goals, away_goals, confidence)
        analysis = self._generate_analysis(
            match.home_team, match.away_team,
            home_entry, away_entry,
            home_goals, away_goals,
            h2h_stats
        )
        
        # Créer la prédiction avec les 3 logiques
        prediction = ExpertPrediction(
            match_id=match.id,
            # Score final (consensus)
            home_score_forecast=home_goals,
            away_score_forecast=away_goals,
            confidence=confidence,
            home_goals_avg=round(home_goals_avg, 2),
            away_goals_avg=round(away_goals_avg, 2),
            analysis=analysis,
            bet_tip=bet_tip,
            # Logique de Papa
            papa_home_score=papa_home_score,
            papa_away_score=papa_away_score,
            papa_confidence=round(papa_confidence, 2),
            papa_tip=papa_tip,
            # Logique Grand Frère
            grand_frere_home_score=gf_home_score,
            grand_frere_away_score=gf_away_score,
            grand_frere_confidence=round(gf_confidence, 2),
            grand_frere_tip=gf_tip,
            # Ma Logique
            ma_logique_home_score=ml_home_score,
            ma_logique_away_score=ml_away_score,
            ma_logique_confidence=round(ml_confidence, 2),
            ma_logique_tip=ml_tip
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
