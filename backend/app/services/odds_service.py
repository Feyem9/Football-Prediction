"""
Service d'intégration des cotes de paris - The Odds API

Ce service récupère les cotes de paris en temps réel depuis The Odds API
et les associe aux matchs dans notre base de données.
"""
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session

from core.config import settings
from models.match import Match

logger = logging.getLogger(__name__)


class OddsService:
    """Service pour récupérer et gérer les cotes de paris."""
    
    BASE_URL = "https://api.the-odds-api.com/v4"
    
    # Mapping entre nos codes de compétition et ceux de The Odds API
    COMPETITION_MAPPING = {
        'PL': 'soccer_epl',                    # Premier League
        'BL1': 'soccer_germany_bundesliga',     # Bundesliga
        'SA': 'soccer_italy_serie_a',           # Serie A
        'PD': 'soccer_spain_la_liga',           # La Liga
        'FL1': 'soccer_france_ligue_one',       # Ligue 1
        'CL': 'soccer_uefa_champs_league',      # Champions League
        'EL': 'soccer_uefa_europa_league',      # Europa League
        'ECL': 'soccer_uefa_europa_conference_league',  # Conference League
        'DED': 'soccer_netherlands_eredivisie', # Eredivisie
        'PPL': 'soccer_portugal_primeira_liga', # Primeira Liga
    }
    
    # Bookmakers prioritaires (européens)
    PREFERRED_BOOKMAKERS = [
        'bet365',
        'unibet_eu',
        'betfair_ex_eu',
        'pinnacle',
        'williamhill',
        '1xbet',
        'betclic',
    ]
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.ODDS_API_KEY
        if not self.api_key:
            logger.warning("Pas de clé API The Odds API configurée!")
    
    async def get_odds_for_sport(
        self, 
        sport_key: str, 
        markets: str = 'h2h',  # h2h = 1X2, spreads = handicap, totals = over/under
        regions: str = 'eu',
        odds_format: str = 'decimal'
    ) -> List[Dict]:
        """
        Récupère les cotes pour un sport/championnat donné.
        
        Args:
            sport_key: Clé du sport (ex: 'soccer_epl')
            markets: Type de marché (h2h, spreads, totals)
            regions: Région des bookmakers (eu, uk, us, au)
            odds_format: Format des cotes (decimal, american)
        
        Returns:
            Liste des matchs avec leurs cotes
        """
        if not self.api_key:
            logger.error("Clé API manquante")
            return []
        
        url = f"{self.BASE_URL}/sports/{sport_key}/odds"
        params = {
            'apiKey': self.api_key,
            'regions': regions,
            'markets': markets,
            'oddsFormat': odds_format,
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                
                # Log les crédits restants
                remaining = response.headers.get('x-requests-remaining', 'N/A')
                used = response.headers.get('x-requests-used', 'N/A')
                logger.info(f"The Odds API - Requêtes: {used} utilisées, {remaining} restantes")
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    logger.error("Clé API invalide")
                elif response.status_code == 429:
                    logger.error("Quota API dépassé")
                else:
                    logger.error(f"Erreur API: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des cotes: {e}")
        
        return []
    
    def extract_best_odds(self, match_data: Dict) -> Dict[str, float]:
        """
        Extrait les meilleures cotes (les plus hautes) parmi tous les bookmakers.
        
        Returns:
            Dict avec odds_home, odds_draw, odds_away et le bookmaker
        """
        best_odds = {
            'odds_home': 0.0,
            'odds_draw': 0.0,
            'odds_away': 0.0,
            'bookmaker': None,
            'last_update': None
        }
        
        bookmakers = match_data.get('bookmakers', [])
        
        for bookmaker in bookmakers:
            bookmaker_key = bookmaker.get('key', '')
            
            for market in bookmaker.get('markets', []):
                if market.get('key') != 'h2h':
                    continue
                
                outcomes = market.get('outcomes', [])
                
                for outcome in outcomes:
                    name = outcome.get('name', '')
                    price = outcome.get('price', 0.0)
                    
                    # Identifier home/draw/away
                    if name == match_data.get('home_team'):
                        if price > best_odds['odds_home']:
                            best_odds['odds_home'] = price
                    elif name == match_data.get('away_team'):
                        if price > best_odds['odds_away']:
                            best_odds['odds_away'] = price
                    elif name.lower() == 'draw':
                        if price > best_odds['odds_draw']:
                            best_odds['odds_draw'] = price
            
            # Garder trace du dernier bookmaker pour info
            if bookmaker.get('last_update'):
                best_odds['last_update'] = bookmaker['last_update']
        
        return best_odds
    
    def find_match_odds(
        self, 
        odds_data: List[Dict], 
        home_team: str, 
        away_team: str
    ) -> Optional[Dict]:
        """
        Trouve les cotes pour un match spécifique par nom d'équipe.
        
        Utilise une correspondance floue car les noms peuvent différer
        entre notre base et The Odds API.
        """
        home_normalized = self._normalize_team_name(home_team)
        away_normalized = self._normalize_team_name(away_team)
        
        for match in odds_data:
            api_home = self._normalize_team_name(match.get('home_team', ''))
            api_away = self._normalize_team_name(match.get('away_team', ''))
            
            # Correspondance exacte ou partielle
            if (self._teams_match(home_normalized, api_home) and 
                self._teams_match(away_normalized, api_away)):
                return self.extract_best_odds(match)
        
        return None
    
    def _normalize_team_name(self, name: str) -> str:
        """Normalise le nom d'équipe pour la comparaison."""
        # Supprimer les préfixes numériques (1. FC, 1899, etc.)
        import re
        normalized = re.sub(r'^\d+\.\s*', '', name)  # Retirer "1. " au début
        normalized = re.sub(r'\b\d{4}\b', '', normalized)  # Retirer les années comme 1899
        
        # Supprimer les suffixes courants
        suffixes = ['FC', 'CF', 'SC', 'AC', 'AS', 'SS', 'SV', 'VfB', 'VfL', 'FSV', 
                    'Calcio', 'United', 'City', 'Sporting', 'Athletic', 'Club',
                    'Hotspur', 'Wanderers', 'Albion', 'Palace', 'Rangers', 'Town',
                    'Ham', 'Villa', 'Forest', 'County', 'Olympic', 'Real']
        
        normalized = normalized.lower().strip()
        
        for suffix in suffixes:
            # Retirer le suffixe seulement s'il est un mot séparé
            normalized = re.sub(r'\b' + suffix.lower() + r'\b', '', normalized)
        
        # Supprimer caractères spéciaux
        normalized = ''.join(c for c in normalized if c.isalnum() or c.isspace())
        
        return ' '.join(normalized.split())  # Nettoyer les espaces multiples
    
    def _teams_match(self, name1: str, name2: str) -> bool:
        """Vérifie si deux noms d'équipe correspondent."""
        if not name1 or not name2:
            return False
            
        if name1 == name2:
            return True
        
        # Vérifier si un nom est contenu dans l'autre
        if name1 in name2 or name2 in name1:
            return True
        
        # Vérifier les mots clés communs
        words1 = set(name1.split())
        words2 = set(name2.split())
        common = words1 & words2
        
        # Si au moins 1 mot significatif en commun (longueur > 3)
        significant_common = [w for w in common if len(w) > 3]
        if len(significant_common) >= 1:
            return True
        
        # Dernière chance: premier mot en commun (ex: "Union" dans "Union Berlin")
        if words1 and words2:
            first1 = list(words1)[0] if words1 else ''
            first2 = list(words2)[0] if words2 else ''
            if len(first1) > 4 and len(first2) > 4:
                if first1 == first2:
                    return True
        
        return False
    
    async def update_match_odds(self, db: Session, match: Match) -> bool:
        """
        Met à jour les cotes d'un match spécifique.
        
        Returns:
            True si les cotes ont été mises à jour, False sinon
        """
        # Trouver la clé API correspondante
        sport_key = self.COMPETITION_MAPPING.get(match.competition_code)
        
        if not sport_key:
            logger.warning(f"Pas de mapping pour la compétition {match.competition_code}")
            return False
        
        # Récupérer les cotes
        odds_data = await self.get_odds_for_sport(sport_key)
        
        if not odds_data:
            return False
        
        # Trouver notre match
        match_odds = self.find_match_odds(odds_data, match.home_team, match.away_team)
        
        if match_odds:
            match.odds_home = match_odds['odds_home']
            match.odds_draw = match_odds['odds_draw']
            match.odds_away = match_odds['odds_away']
            match.odds_updated_at = datetime.utcnow()
            
            db.commit()
            logger.info(f"Cotes mises à jour pour {match.home_team} vs {match.away_team}: "
                       f"1={match_odds['odds_home']:.2f} X={match_odds['odds_draw']:.2f} 2={match_odds['odds_away']:.2f}")
            return True
        
        logger.warning(f"Cotes non trouvées pour {match.home_team} vs {match.away_team}")
        return False
    
    async def update_all_upcoming_odds(self, db: Session, limit: int = 50) -> Dict[str, int]:
        """
        Met à jour les cotes de tous les matchs à venir.
        
        Returns:
            Stats de mise à jour
        """
        stats = {'updated': 0, 'failed': 0, 'skipped': 0}
        
        # Récupérer les matchs à venir
        upcoming_matches = db.query(Match).filter(
            Match.match_date >= datetime.now(),
            Match.status.in_(['TIMED', 'SCHEDULED'])
        ).order_by(Match.match_date).limit(limit).all()
        
        # Grouper par compétition pour optimiser les appels API
        by_competition = {}
        for match in upcoming_matches:
            comp = match.competition_code
            if comp not in by_competition:
                by_competition[comp] = []
            by_competition[comp].append(match)
        
        # Récupérer les cotes par compétition
        for comp_code, matches in by_competition.items():
            sport_key = self.COMPETITION_MAPPING.get(comp_code)
            
            if not sport_key:
                stats['skipped'] += len(matches)
                continue
            
            odds_data = await self.get_odds_for_sport(sport_key)
            
            if not odds_data:
                stats['failed'] += len(matches)
                continue
            
            for match in matches:
                match_odds = self.find_match_odds(odds_data, match.home_team, match.away_team)
                
                if match_odds and match_odds['odds_home'] > 0:
                    match.odds_home = match_odds['odds_home']
                    match.odds_draw = match_odds['odds_draw']
                    match.odds_away = match_odds['odds_away']
                    match.odds_updated_at = datetime.utcnow()
                    stats['updated'] += 1
                else:
                    stats['failed'] += 1
        
        db.commit()
        logger.info(f"Mise à jour cotes terminée: {stats}")
        
        return stats
    
    def calculate_value_bet(
        self, 
        odds: float, 
        confidence: float
    ) -> Dict[str, Any]:
        """
        Calcule si un pari a de la valeur (value bet).
        
        Un value bet existe quand la probabilité estimée est supérieure
        à la probabilité implicite de la cote.
        
        Args:
            odds: La cote du bookmaker (ex: 2.50)
            confidence: Notre confiance en % (ex: 0.65 = 65%)
        
        Returns:
            Dict avec is_value_bet, expected_value, etc.
        """
        # Probabilité implicite de la cote (sans marge)
        implied_prob = 1 / odds
        
        # Notre probabilité estimée
        our_prob = confidence
        
        # Expected Value = (Prob * Gain) - (1 - Prob) * Mise
        # Simplifié pour mise de 1: EV = (Prob * (Odds - 1)) - (1 - Prob)
        ev = (our_prob * (odds - 1)) - (1 - our_prob)
        
        # Value = notre prob - prob implicite
        value = our_prob - implied_prob
        
        return {
            'is_value_bet': value > 0.05,  # Au moins 5% de value
            'expected_value': round(ev, 3),
            'value_percentage': round(value * 100, 1),
            'implied_probability': round(implied_prob * 100, 1),
            'our_probability': round(our_prob * 100, 1),
            'recommendation': self._get_bet_recommendation(ev, value)
        }
    
    def _get_bet_recommendation(self, ev: float, value: float) -> str:
        """Génère une recommandation de pari basée sur l'EV et la value."""
        if ev > 0.15 and value > 0.10:
            return "🔥 EXCELLENT - Forte value, miser 3-5% de la bankroll"
        elif ev > 0.08 and value > 0.05:
            return "✅ BON - Value correcte, miser 2-3% de la bankroll"
        elif ev > 0 and value > 0:
            return "⚠️ MARGINALE - Petite value, miser 1% max"
        else:
            return "❌ PAS DE VALUE - Ne pas miser"


# Instance globale (optionnelle)
odds_service = OddsService()
