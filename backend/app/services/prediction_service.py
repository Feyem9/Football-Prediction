"""
Service de génération de prédictions automatiques.

Ce service génère des pronostics basés sur les données du classement
et la forme récente des équipes.
"""
from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from models.match import Match
from models.prediction import ExpertPrediction
from services.football_api import football_data_service
from services.api_football import api_football_service


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
    # Basé sur les coefficients UEFA et la qualité générale
    LEAGUE_STRENGTH = {
        # Top Tier (95-100%)
        "PL": 1.00,   # Premier League (Angleterre)
        "PD": 0.98,   # La Liga (Espagne)
        "CL": 1.00,   # Champions League
        "WC": 1.00,   # World Cup
        
        # Tier 1 (85-94%)
        "BL1": 0.92,  # Bundesliga (Allemagne)
        "SA": 0.90,   # Serie A (Italie)
        "FL1": 0.85,  # Ligue 1 (France)
        
        # Tier 2 (70-84%)
        "PPL": 0.80,  # Primeira Liga (Portugal)
        "DED": 0.78,  # Eredivisie (Pays-Bas)
        "BSA": 0.75,  # Jupiler Pro League (Belgique)
        "EL": 0.90,   # Europa League (moyenne)
        
        # Tier 3 (55-69%)
        "SL": 0.68,   # Super Lig (Turquie)
        "PL": 0.65,   # Ekstraklasa (Pologne)
        "ASL": 0.62,  # Austrian Bundesliga (Autriche)
        "SFL": 0.60,  # Scottish Premiership (Écosse)
        "GSL": 0.58,  # Super League (Grèce)
        
        # Tier 4 (40-54%)
        "EL": 0.52,   # Eliteserien (Norvège)
        "SSL": 0.50,  # Allsvenskan (Suède)
        "HNL": 0.50,  # Croatian First League (Croatie)
        "SL": 0.48,   # Superligaen (Danemark)
        "RSL": 0.45,  # Super League (Suisse)
        "CL": 0.42,   # Czech First League (Tchéquie)
        
        # Tier 5 (25-39%) - Autres ligues
        "BFL": 0.38,  # Bulgarian First League (Bulgarie)
        "UPL": 0.35,  # Ukrainian Premier League
        "RPL": 0.30,  # Russian Premier League
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
    
    def _check_upcoming_important_match(self, team_id: int, match_date: datetime, days: int = 3) -> Optional[dict]:
        """
        Vérifie si une équipe a un match important dans les N prochains jours.
        
        Args:
            team_id: ID de l'équipe
            match_date: Date du match actuel
            days: Nombre de jours à vérifier (par défaut 3)
            
        Returns:
            Dict avec infos du match important ou None
        """
        from models.match import Match
        from datetime import timedelta
        
        # Compétitions considérées comme importantes
        important_competitions = ['CL', 'EL', 'FAC', 'FLC']  # CL, Europa League, FA Cup, League Cup
        
        # Chercher matchs de l'équipe dans les N jours suivants
        start_date = match_date
        end_date = match_date + timedelta(days=days)
        
        upcoming_match = self.db.query(Match).filter(
            Match.match_date > start_date,
            Match.match_date <= end_date,
            Match.competition_code.in_(important_competitions)
        ).filter(
            (Match.home_team_id == team_id) | (Match.away_team_id == team_id)
        ).order_by(Match.match_date.asc()).first()
        
        if upcoming_match:
            return {
                'competition': upcoming_match.competition_name,
                'opponent': upcoming_match.away_team if upcoming_match.home_team_id == team_id else upcoming_match.home_team,
                'date': upcoming_match.match_date,
                'days_until': (upcoming_match.match_date - match_date).days
            }
        return None
    
    def _check_recent_important_match(self, team_id: int, match_date: datetime, days: int = 3) -> Optional[dict]:
        """
        Vérifie si une équipe a joué un match important dans les N derniers jours.
        
        Args:
            team_id: ID de l'équipe
            match_date: Date du match actuel
            days: Nombre de jours à vérifier (par défaut 3)
            
        Returns:
            Dict avec infos du match important ou None
        """
        from models.match import Match
        from datetime import timedelta
        
        # Compétitions considérées comme importantes
        important_competitions = ['CL', 'EL', 'FAC', 'FLC']
        
        # Chercher matchs de l'équipe dans les N jours précédents
        start_date = match_date - timedelta(days=days)
        end_date = match_date
        
        recent_match = self.db.query(Match).filter(
            Match.match_date >= start_date,
            Match.match_date < end_date,
            Match.competition_code.in_(important_competitions),
            Match.status == 'FINISHED'  # Match déjà joué
        ).filter(
            (Match.home_team_id == team_id) | (Match.away_team_id == team_id)
        ).order_by(Match.match_date.desc()).first()
        
        if recent_match:
            return {
                'competition': recent_match.competition_name,
                'opponent': recent_match.away_team if recent_match.home_team_id == team_id else recent_match.home_team,
                'date': recent_match.match_date,
                'days_ago': (match_date - recent_match.match_date).days,
                'score': f"{recent_match.score_home}-{recent_match.score_away}"
            }
        return None
    
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
        Retourne la force relative d'un championnat (Logique de Papa).
        
        Cette logique permet de comparer des équipes de championnats différents.
        Exemple : PSG (Ligue 1, 85%) vs Bodø/Glimt (Norvège, 52%)
        
        Même si Bodø est 1er en Norvège et PSG 5ème en Ligue 1,
        PSG aura un avantage car la Ligue 1 est un championnat plus relevé.
        
        Args:
            competition_code: Code de la compétition (PL, FL1, etc.)
            
        Returns:
            Force entre 0.3 et 1.0 (1 = top niveau européen)
        """
        # Si championnat inconnu, on estime à un niveau moyen-bas (50%)
        # Pour éviter de surestimer des championnats mineurs
        return self.LEAGUE_STRENGTH.get(competition_code, 0.50)
    
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
    
    def _calculate_detailed_h2h_stats(self, matches: List[dict], home_team_id: int, away_team_id: int) -> dict:
        """
        Calcule les statistiques H2H détaillées pour Grand Frère.
        
        Analyse les 10 dernières confrontations pour extraire :
        - Victoires/Nuls/Défaites pour chaque équipe
        - Buts marqués par chaque équipe au total
        - Fréquence de buts par match pour chaque équipe
        
        Args:
            matches: Liste des matchs H2H
            home_team_id: ID de l'équipe domicile du match actuel
            away_team_id: ID de l'équipe extérieur du match actuel
            
        Returns:
            Dict avec toutes les stats détaillées
        """
        h_wins = 0
        a_wins = 0
        draws = 0
        home_goals_total = 0  # Buts marqués par l'équipe domicile actuelle
        away_goals_total = 0  # Buts marqués par l'équipe extérieur actuelle
        matches_counted = 0
        
        for m in matches:
            if m.get("status") != "FINISHED":
                continue
                
            score = m.get("score", {}).get("fullTime", {})
            h_score = score.get("home")
            a_score = score.get("away")
            
            if h_score is None or a_score is None:
                continue
            
            matches_counted += 1
            match_home_id = m.get("homeTeam", {}).get("id")
            match_away_id = m.get("awayTeam", {}).get("id")
            
            # Comptabiliser les buts pour chaque équipe
            # L'équipe "home_team_id" peut avoir joué à domicile OU à l'extérieur dans ce match
            if match_home_id == home_team_id:
                # L'équipe domicile actuelle jouait à domicile dans ce H2H
                home_goals_total += h_score
                away_goals_total += a_score
            elif match_away_id == home_team_id:
                # L'équipe domicile actuelle jouait à l'extérieur dans ce H2H
                home_goals_total += a_score
                away_goals_total += h_score
            
            # Comptabiliser victoires/nuls/défaites
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
        
        # Calculer les fréquences de buts par match
        home_goals_freq = round(home_goals_total / matches_counted, 2) if matches_counted > 0 else 0
        away_goals_freq = round(away_goals_total / matches_counted, 2) if matches_counted > 0 else 0
        
        # Déterminer qui marque le plus
        top_scorer = "equal"
        if home_goals_total > away_goals_total:
            top_scorer = "home"
        elif away_goals_total > home_goals_total:
            top_scorer = "away"
        
        return {
            "home_wins": h_wins,
            "away_wins": a_wins,
            "draws": draws,
            "matches_counted": matches_counted,
            "home_goals_total": home_goals_total,
            "away_goals_total": away_goals_total,
            "total_goals": home_goals_total + away_goals_total,
            "home_goals_freq": home_goals_freq,
            "away_goals_freq": away_goals_freq,
            "top_scorer": top_scorer
        }
    
    def _generate_gf_verdict(
        self,
        home_strength: float,
        away_strength: float,
        home_form: float,
        away_form: float,
        home_h2h: float,
        away_h2h: float,
        home_league_level: float,
        away_league_level: float,
        h2h_detailed: Optional[dict],
        home_team: str,
        away_team: str
    ) -> str:
        """
        Génère le verdict de Grand Frère basé sur l'analyse combinée.
        
        Prend en compte:
        - H2H (qui gagne historiquement)
        - Niveau de ligue (force du championnat)
        - Forme actuelle
        - Avantage domicile
        
        Returns:
            Verdict textuel expliquant la prédiction
        """
        verdict_parts = []
        
        # 1. Analyser le H2H
        if h2h_detailed:
            h_wins = h2h_detailed.get("home_wins", 0)
            a_wins = h2h_detailed.get("away_wins", 0)
            draws = h2h_detailed.get("draws", 0)
            total_goals = h2h_detailed.get("total_goals", 0)
            h_goals = h2h_detailed.get("home_goals_total", 0)
            a_goals = h2h_detailed.get("away_goals_total", 0)
            matches = h2h_detailed.get("matches_counted", 0)
            
            if matches > 0:
                if h_wins > a_wins + 2:
                    verdict_parts.append(f"{home_team} domine clairement les H2H ({h_wins}V-{draws}N-{a_wins}D)")
                elif a_wins > h_wins + 2:
                    verdict_parts.append(f"{away_team} domine clairement les H2H ({a_wins}V-{draws}N-{h_wins}D)")
                elif draws >= h_wins and draws >= a_wins:
                    verdict_parts.append(f"Les H2H sont équilibrés avec beaucoup de nuls ({draws}N sur {matches} matchs)")
                else:
                    verdict_parts.append(f"H2H serré: {home_team} {h_wins}V vs {away_team} {a_wins}V")
                
                # Analyse des buts
                if total_goals > 0:
                    if h_goals > a_goals * 1.5:
                        verdict_parts.append(f"{home_team} marque plus en H2H ({h_goals} buts vs {a_goals})")
                    elif a_goals > h_goals * 1.5:
                        verdict_parts.append(f"{away_team} marque plus en H2H ({a_goals} buts vs {h_goals})")
        
        # 2. Analyser le niveau et la force
        # Déterminer si équipe est forte/moyenne/faible
        def get_team_level(strength: float, form: float) -> str:
            combined = (strength + form) / 2
            if combined >= 0.7:
                return "forte"
            elif combined >= 0.4:
                return "moyenne"
            else:
                return "faible"
        
        home_level = get_team_level(home_strength, home_form)
        away_level = get_team_level(away_strength, away_form)
        
        # 3. Appliquer la loi de Grand Frère
        if home_level == "moyenne" and away_level == "forte":
            if home_league_level >= away_league_level:
                # Même niveau de ligue → le moyen à domicile peut tenir le nul
                verdict_parts.append(f"{home_team} (équipe moyenne) peut tenir le nul à domicile contre {away_team}")
            else:
                # Ligue extérieure plus forte → l'extérieur peut gagner
                verdict_parts.append(f"{away_team} (équipe forte, ligue supérieure) a l'avantage malgré le déplacement")
        elif home_level == "forte" and away_level == "moyenne":
            verdict_parts.append(f"{home_team} (équipe forte) devrait s'imposer à domicile")
        elif home_level == "forte" and away_level == "forte":
            verdict_parts.append(f"Choc au sommet! Deux équipes fortes, l'avantage domicile peut faire la différence")
        elif home_level == "moyenne" and away_level == "moyenne":
            verdict_parts.append(f"Match équilibré entre deux équipes moyennes, avantage léger à {home_team} (domicile)")
        elif home_level == "faible":
            if away_level == "forte":
                verdict_parts.append(f"{away_team} (équipe forte) devrait s'imposer même à l'extérieur")
            else:
                verdict_parts.append(f"Match difficile pour {home_team}, mais le domicile peut aider")
        
        # 4. Forme récente
        if abs(home_form - away_form) > 0.3:
            if home_form > away_form:
                verdict_parts.append(f"{home_team} est en meilleure forme actuellement")
            else:
                verdict_parts.append(f"{away_team} est en meilleure forme actuellement")
        
        return " | ".join(verdict_parts) if verdict_parts else "Analyse équilibrée, match ouvert"

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
        
        # Récupérer H2H avec stats détaillées pour Grand Frère
        # Priorité: API-Football (historique complet) > Football-Data.org (fallback)
        h2h_stats = None
        h2h_detailed = None
        home_h2h = 0.5
        away_h2h = 0.5
        
        # Essayer d'abord API-Football (historique complet jusqu'à 20+ ans)
        if match.home_team and match.away_team:
            try:
                api_football_h2h = await api_football_service.get_h2h_by_names(
                    match.home_team, match.away_team, limit=20
                )
                
                if api_football_h2h.get("success") and api_football_h2h.get("stats", {}).get("total_matches", 0) > 0:
                    stats = api_football_h2h["stats"]
                    h_wins = stats.get("home_wins", 0)
                    a_wins = stats.get("away_wins", 0)
                    draws = stats.get("draws", 0)
                    
                    h2h_stats = (h_wins, a_wins, draws)
                    h2h_detailed = {
                        "home_wins": h_wins,
                        "away_wins": a_wins,
                        "draws": draws,
                        "matches_counted": stats.get("total_matches", 0),
                        "home_goals_total": stats.get("home_goals_total", 0),
                        "away_goals_total": stats.get("away_goals_total", 0),
                        "home_goals_freq": stats.get("home_goals_freq", 0),
                        "away_goals_freq": stats.get("away_goals_freq", 0),
                        "top_scorer": stats.get("top_scorer", "equal")
                    }
                    
                    total = h_wins + a_wins + draws
                    if total > 0:
                        home_h2h = (h_wins * 3 + draws * 1) / (total * 3)
                        away_h2h = (a_wins * 3 + draws * 1) / (total * 3)
                    
                    print(f"✅ H2H API-Football: {match.home_team} vs {match.away_team} = {h_wins}-{draws}-{a_wins}")
            except Exception as e:
                print(f"⚠️ API-Football H2H error: {e}")
        
        # Fallback: Football-Data.org (si API-Football n'a rien retourné)
        if h2h_stats is None and match.external_id and match.home_team_id and match.away_team_id:
            try:
                h2h_data = await football_data_service.get_match_h2h(match.external_id, limit=10)
                matches = h2h_data.get("matches", [])
                
                if matches:
                    h_wins, a_wins, draws = self._calculate_h2h_stats(
                        matches, match.home_team_id, match.away_team_id
                    )
                    h2h_stats = (h_wins, a_wins, draws)
                    
                    h2h_detailed = self._calculate_detailed_h2h_stats(
                        matches, match.home_team_id, match.away_team_id
                    )
                    
                    total = h_wins + a_wins + draws
                    if total > 0:
                        home_h2h = (h_wins * 3 + draws * 1) / (total * 3)
                        away_h2h = (a_wins * 3 + draws * 1) / (total * 3)
                    
                    print(f"✅ H2H Football-Data: {match.home_team} vs {match.away_team} = {h_wins}-{draws}-{a_wins}")
            except Exception as e:
                print(f"⚠️ Football-Data H2H error: {e}")

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
        
        # === AJUSTEMENT PAPA : Matchs importants ===
        # Vérifier si les équipes ont des matchs importants proches
        home_upcoming = None
        home_recent = None
        away_upcoming = None
        away_recent = None
        
        if match.home_team_id and match.match_date:
            home_upcoming = self._check_upcoming_important_match(match.home_team_id, match.match_date)
            home_recent = self._check_recent_important_match(match.home_team_id, match.match_date)
        
        if match.away_team_id and match.match_date:
            away_upcoming = self._check_upcoming_important_match(match.away_team_id, match.match_date)
            away_recent = self._check_recent_important_match(match.away_team_id, match.match_date)
        
        # Ajuster la force et la confiance selon les matchs importants
        rotation_factor_home = 1.0
        rotation_factor_away = 1.0
        
        if home_upcoming:
            # Équipe domicile a un match important à venir → risque de rotation
            papa_confidence *= 0.85  # Réduire confiance de 15%
            rotation_factor_home = 0.90  # Réduire force de 10%
            
        if home_recent:
            # Équipe domicile vient de jouer un match important → fatigue possible
            papa_confidence *= 0.90  # Réduire confiance de 10%
            rotation_factor_home *=0.92  # Réduire force de 8%
            
        if away_upcoming:
            # Équipe extérieur a un match important à venir
            papa_confidence *= 0.85
            rotation_factor_away = 0.90
            
        if away_recent:
            # Équipe extérieur vient de jouer un match important
            papa_confidence *= 0.90
            rotation_factor_away *= 0.92
        
        # Recalculer le score avec les facteurs d'ajustement
        if rotation_factor_home != 1.0 or rotation_factor_away != 1.0:
            papa_home_score, papa_away_score = self._predict_score(
                papa_home_strength * rotation_factor_home,
                papa_away_strength * rotation_factor_away,
                home_goals_avg, away_goals_avg
            )
        
        papa_tip = self._generate_bet_tip(papa_home_score, papa_away_score, papa_confidence)
        
        # === LOGIQUE GRAND FRÈRE (H2H + Loi Domicile + Analyse combinée Papa) ===
        # Basé sur: Confrontations directes, avantage domicile, niveau de ligue
        home_adv = self._calculate_home_advantage(home_strength, away_strength, home_strength > away_strength)
        gf_home_strength = home_h2h + home_adv
        gf_away_strength = away_h2h
        
        # Récupérer les niveaux de ligue pour l'analyse combinée
        # (On utilise le même niveau pour les deux si même championnat)
        gf_home_league = league_level
        gf_away_league = league_level
        
        # Générer le verdict Grand Frère basé sur l'analyse combinée
        gf_verdict = self._generate_gf_verdict(
            home_strength=home_strength,
            away_strength=away_strength,
            home_form=home_form,
            away_form=away_form,
            home_h2h=home_h2h,
            away_h2h=away_h2h,
            home_league_level=gf_home_league,
            away_league_level=gf_away_league,
            h2h_detailed=h2h_detailed,
            home_team=match.home_team,
            away_team=match.away_team
        )
        
        gf_home_score, gf_away_score = self._predict_score(
            gf_home_strength, gf_away_strength,
            home_goals_avg, away_goals_avg
        )
        gf_confidence = min(0.8, 0.4 + abs(home_h2h - away_h2h))
        gf_tip = self._generate_bet_tip(gf_home_score, gf_away_score, gf_confidence)
        
        # === MA LOGIQUE (APEX-30: Système 8 modules) ===
        # Remplacé par APEX-30: IFP, Force Off/Def, Domicile, Fatigue, Motivation, Absences, H2H
        from services.apex30_service import APEX30Service, creer_equipe_analyse, creer_h2h_stats, MatchHistorique
        
        try:
            apex30 = APEX30Service(self.db)
            
            # Préparer les données pour APEX-30
            # Créer l'historique de matchs (simplifié à partir des données de forme)
            home_matchs_data = []
            away_matchs_data = []
            
            # Calculer les points domicile/extérieur à partir des standings
            home_pts_dom = 2.0  # Default
            home_pts_ext = 1.5
            away_pts_dom = 2.0
            away_pts_ext = 1.5
            
            if home_entry:
                total_pts = home_entry.get('points', 30)
                total_matchs = home_entry.get('played', 20)
                if total_matchs > 0:
                    avg_pts = total_pts / total_matchs
                    home_pts_dom = avg_pts * 1.2  # Bonus domicile estimé
                    home_pts_ext = avg_pts * 0.8
            
            if away_entry:
                total_pts = away_entry.get('points', 30)
                total_matchs = away_entry.get('played', 20)
                if total_matchs > 0:
                    avg_pts = total_pts / total_matchs
                    away_pts_dom = avg_pts * 1.2
                    away_pts_ext = avg_pts * 0.8
            
            # Créer les équipes pour APEX-30 avec les vrais 10 derniers matchs
            # Récupérer les 10 derniers matchs via API-Football
            home_last_matches = await api_football_service.get_team_last_matches(match.home_team, last=10)
            away_last_matches = await api_football_service.get_team_last_matches(match.away_team, last=10)
            
            # Récupérer les positions au classement avec stats domicile/extérieur
            home_standings_api = await api_football_service.get_team_standings_position(match.home_team)
            away_standings_api = await api_football_service.get_team_standings_position(match.away_team)
            
            # Mettre à jour les points domicile/extérieur si disponibles
            if home_standings_api.get("success"):
                home_data = home_standings_api.get("home", {})
                away_data = home_standings_api.get("away", {})
                home_played = home_data.get("played", 1) or 1
                away_played = away_data.get("played", 1) or 1
                home_pts_dom = (home_data.get("win", 0) * 3 + home_data.get("draw", 0)) / home_played
                home_pts_ext = (away_data.get("win", 0) * 3 + away_data.get("draw", 0)) / away_played
            
            if away_standings_api.get("success"):
                home_data = away_standings_api.get("home", {})
                away_data = away_standings_api.get("away", {})
                home_played = home_data.get("played", 1) or 1
                away_played = away_data.get("played", 1) or 1
                away_pts_dom = (home_data.get("win", 0) * 3 + home_data.get("draw", 0)) / home_played
                away_pts_ext = (away_data.get("win", 0) * 3 + away_data.get("draw", 0)) / away_played
            
            # Convertir les matchs API-Football au format APEX-30
            home_matchs_data = home_last_matches.get("matches", []) if home_last_matches.get("success") else []
            away_matchs_data = away_last_matches.get("matches", []) if away_last_matches.get("success") else []
            
            # === FALLBACK 1: Si API-Football échoue, essayer Football-Data.org ===
            if not home_matchs_data and match.home_team_id:
                try:
                    fd_matches = await football_data_service.get_team_matches(
                        match.home_team_id, status="FINISHED", limit=10
                    )
                    for fd_match in fd_matches.get("matches", [])[:10]:
                        is_home = fd_match.get("homeTeam", {}).get("id") == match.home_team_id
                        h_score = fd_match.get("score", {}).get("fullTime", {}).get("home", 0) or 0
                        a_score = fd_match.get("score", {}).get("fullTime", {}).get("away", 0) or 0
                        
                        if is_home:
                            buts_pour, buts_contre = h_score, a_score
                        else:
                            buts_pour, buts_contre = a_score, h_score
                        
                        if buts_pour > buts_contre:
                            resultat = 'V'
                        elif buts_pour < buts_contre:
                            resultat = 'D'
                        else:
                            resultat = 'N'
                        
                        home_matchs_data.append({
                            'date': fd_match.get("utcDate", ""),
                            'domicile': is_home,
                            'resultat': resultat,
                            'buts_pour': buts_pour,
                            'buts_contre': buts_contre,
                            'adversaire_classement': 10,
                            'competition': fd_match.get("competition", {}).get("name", "Championnat")
                        })
                    if home_matchs_data:
                        print(f"APEX-30 Fallback FD: {match.home_team} - {len(home_matchs_data)} matchs")
                except Exception as e:
                    print(f"Football-Data.org fallback error for {match.home_team}: {e}")
            
            if not away_matchs_data and match.away_team_id:
                try:
                    fd_matches = await football_data_service.get_team_matches(
                        match.away_team_id, status="FINISHED", limit=10
                    )
                    for fd_match in fd_matches.get("matches", [])[:10]:
                        is_home = fd_match.get("homeTeam", {}).get("id") == match.away_team_id
                        h_score = fd_match.get("score", {}).get("fullTime", {}).get("home", 0) or 0
                        a_score = fd_match.get("score", {}).get("fullTime", {}).get("away", 0) or 0
                        
                        if is_home:
                            buts_pour, buts_contre = h_score, a_score
                        else:
                            buts_pour, buts_contre = a_score, h_score
                        
                        if buts_pour > buts_contre:
                            resultat = 'V'
                        elif buts_pour < buts_contre:
                            resultat = 'D'
                        else:
                            resultat = 'N'
                        
                        away_matchs_data.append({
                            'date': fd_match.get("utcDate", ""),
                            'domicile': is_home,
                            'resultat': resultat,
                            'buts_pour': buts_pour,
                            'buts_contre': buts_contre,
                            'adversaire_classement': 10,
                            'competition': fd_match.get("competition", {}).get("name", "Championnat")
                        })
                    if away_matchs_data:
                        print(f"APEX-30 Fallback FD: {match.away_team} - {len(away_matchs_data)} matchs")
                except Exception as e:
                    print(f"Football-Data.org fallback error for {match.away_team}: {e}")
            
            # === FALLBACK 2: Si toujours vide, utiliser les données de forme ===
            from datetime import datetime, timedelta
            
            if not home_matchs_data and home_entry:
                # Générer un historique simulé à partir de la forme (VVNDD)
                form_str = home_entry.get("form", "NNNNN") or "NNNNN"
                print(f"APEX-30 Fallback: {match.home_team} - utilisation forme {form_str}")
                for i, res in enumerate(form_str[:10]):
                    result_map = {'W': 'V', 'D': 'N', 'L': 'D', 'V': 'V', 'N': 'N'}
                    home_matchs_data.append({
                        'date': (datetime.now() - timedelta(days=(i+1)*7)).isoformat(),
                        'domicile': (i % 2 == 0),
                        'resultat': result_map.get(res, 'N'),
                        'buts_pour': 2 if res in ['W', 'V'] else (1 if res in ['D', 'N'] else 0),
                        'buts_contre': 0 if res in ['W', 'V'] else (1 if res in ['D', 'N'] else 2),
                        'adversaire_classement': 10,
                        'competition': 'Championnat'
                    })
            
            if not away_matchs_data and away_entry:
                form_str = away_entry.get("form", "NNNNN") or "NNNNN"
                print(f"APEX-30 Fallback: {match.away_team} - utilisation forme {form_str}")
                for i, res in enumerate(form_str[:10]):
                    result_map = {'W': 'V', 'D': 'N', 'L': 'D', 'V': 'V', 'N': 'N'}
                    away_matchs_data.append({
                        'date': (datetime.now() - timedelta(days=(i+1)*7)).isoformat(),
                        'domicile': (i % 2 == 1),
                        'resultat': result_map.get(res, 'N'),
                        'buts_pour': 2 if res in ['W', 'V'] else (1 if res in ['D', 'N'] else 0),
                        'buts_contre': 0 if res in ['W', 'V'] else (1 if res in ['D', 'N'] else 2),
                        'adversaire_classement': 10,
                        'competition': 'Championnat'
                    })
            
            equipe_home = creer_equipe_analyse(
                nom=match.home_team,
                matchs_recents=home_matchs_data,
                classement=home_position,
                est_domicile=True,
                points_domicile=home_pts_dom,
                points_exterieur=home_pts_ext
            )
            
            equipe_away = creer_equipe_analyse(
                nom=match.away_team,
                matchs_recents=away_matchs_data,
                classement=away_position,
                est_domicile=False,
                points_domicile=away_pts_dom,
                points_exterieur=away_pts_ext
            )
            
            # Créer les stats H2H pour APEX-30
            apex_h2h = creer_h2h_stats({
                'home_wins': h2h_detailed.get('home_wins', 0),
                'draws': h2h_detailed.get('draws', 0),
                'away_wins': h2h_detailed.get('away_wins', 0),
                'recent_winners': h2h_detailed.get('recent_winners', [])
            })
            
            # Lancer l'analyse APEX-30
            apex_result = apex30.analyser_match(equipe_home, equipe_away, apex_h2h)
            
            # Extraire les résultats
            decision = apex_result['decision']
            ml_home_score = decision['home_goals']
            ml_away_score = decision['away_goals']
            ml_confidence = decision['confiance_pct']
            ml_tip = decision['pronostic']
            
            print(f"APEX-30: {match.home_team} vs {match.away_team} -> {ml_home_score}-{ml_away_score} ({ml_confidence:.0%})")
            
        except Exception as e:
            # Fallback si APEX-30 échoue
            print(f"APEX-30 fallback: {e}")
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
        
        # Sérialiser les données des matchs importants en JSON
        import json
        # Utiliser default=str pour convertir les datetime en string
        home_upcoming_json = json.dumps(home_upcoming, default=str) if home_upcoming else None
        home_recent_json = json.dumps(home_recent, default=str) if home_recent else None
        away_upcoming_json = json.dumps(away_upcoming, default=str) if away_upcoming else None
        away_recent_json = json.dumps(away_recent, default=str) if away_recent else None
        
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
            ma_logique_tip=ml_tip,
            # Matchs importants (contexte Papa)
            home_upcoming_important=home_upcoming_json,
            home_recent_important=home_recent_json,
            away_upcoming_important=away_upcoming_json,
            away_recent_important=away_recent_json,
            # Données pour Preuves
            h2h_home_wins=h2h_stats[0] if h2h_stats else 0,
            h2h_away_wins=h2h_stats[1] if h2h_stats else 0,
            h2h_draws=h2h_stats[2] if h2h_stats else 0,
            h2h_matches_count=h2h_detailed.get("matches_counted", 0) if h2h_detailed else 0,
            h2h_home_goals_total=h2h_detailed.get("home_goals_total", 0) if h2h_detailed else 0,
            h2h_away_goals_total=h2h_detailed.get("away_goals_total", 0) if h2h_detailed else 0,
            h2h_home_goals_freq=h2h_detailed.get("home_goals_freq", 0) if h2h_detailed else 0,
            h2h_away_goals_freq=h2h_detailed.get("away_goals_freq", 0) if h2h_detailed else 0,
            h2h_top_scorer=h2h_detailed.get("top_scorer", "equal") if h2h_detailed else "equal",
            home_form_score=round(home_form, 2) if home_form else 0.5,
            away_form_score=round(away_form, 2) if away_form else 0.5,
            # Grand Frère : Analyse combinée
            gf_home_league_level=round(gf_home_league, 2) if gf_home_league else 0.5,
            gf_away_league_level=round(gf_away_league, 2) if gf_away_league else 0.5,
            gf_home_advantage_bonus=round(home_adv, 3) if home_adv else 0.1,
            gf_verdict=gf_verdict
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
