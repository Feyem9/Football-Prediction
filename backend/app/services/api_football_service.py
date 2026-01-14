"""
Service pour l'intégration de API-Football (RapidAPI).

Fournit les données de cartons et corners qui ne sont pas disponibles
dans Football-Data.org (l'API gratuite actuelle).

Documentation: https://www.api-football.com/documentation-v3
RapidAPI: https://rapidapi.com/api-sports/api/api-football
"""
import httpx
import logging
from typing import Optional, Dict, List
from dataclasses import dataclass

from core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class MatchStatistics:
    """Statistiques d'un match (cartons, corners, etc.)."""
    fixture_id: int
    home_team: str
    away_team: str
    
    # Corners
    home_corners: int = 0
    away_corners: int = 0
    
    # Cartons
    home_yellow_cards: int = 0
    away_yellow_cards: int = 0
    home_red_cards: int = 0
    away_red_cards: int = 0
    
    # Tirs
    home_shots_on_target: int = 0
    away_shots_on_target: int = 0
    home_shots_total: int = 0
    away_shots_total: int = 0
    
    # Possession
    home_possession: float = 0.0
    away_possession: float = 0.0


@dataclass
class TeamSeasonStats:
    """Statistiques saisonnières d'une équipe (cartons, corners moyens)."""
    team_id: int
    team_name: str
    
    # Moyennes par match
    avg_corners_for: float = 0.0
    avg_corners_against: float = 0.0
    avg_yellow_cards: float = 0.0
    avg_red_cards: float = 0.0
    
    # Totaux
    total_corners_for: int = 0
    total_corners_against: int = 0
    total_yellow_cards: int = 0
    total_red_cards: int = 0
    matches_played: int = 0


class APIFootballService:
    """
    Service pour accéder à l'API API-Football via RapidAPI.
    
    Free tier: 100 requêtes/jour
    Endpoints utilisés:
    - /fixtures/statistics : Stats d'un match (corners, cartons)
    - /teams/statistics : Stats saisonnières d'une équipe
    """
    
    BASE_URL = "https://api-football-v1.p.rapidapi.com/v3"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialise le service.
        
        Args:
            api_key: Clé API RapidAPI. Si None, utilise settings.
        """
        self.api_key = api_key or getattr(settings, 'rapidapi_key', '')
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        }
    
    async def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """
        Effectue une requête à l'API.
        
        Args:
            endpoint: Endpoint (ex: "/fixtures/statistics")
            params: Paramètres de la requête
            
        Returns:
            Réponse JSON ou None en cas d'erreur
        """
        if not self.api_key:
            logger.warning("API-Football: Clé API non configurée")
            return None
        
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("errors"):
                        logger.error(f"API-Football errors: {data['errors']}")
                        return None
                    return data
                else:
                    logger.error(f"API-Football error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"API-Football request failed: {e}")
            return None
    
    async def get_fixture_statistics(self, fixture_id: int) -> Optional[MatchStatistics]:
        """
        Récupère les statistiques d'un match.
        
        Args:
            fixture_id: ID du match dans API-Football
            
        Returns:
            MatchStatistics ou None
        """
        data = await self._make_request(
            "/fixtures/statistics",
            params={"fixture": fixture_id}
        )
        
        if not data or not data.get("response"):
            return None
        
        response = data["response"]
        if len(response) < 2:
            return None
        
        home_stats = response[0]
        away_stats = response[1]
        
        def find_stat(stats_list: List[Dict], stat_type: str) -> int:
            for stat in stats_list.get("statistics", []):
                if stat["type"] == stat_type:
                    value = stat["value"]
                    if value is None:
                        return 0
                    if isinstance(value, str) and "%" in value:
                        return float(value.replace("%", ""))
                    return int(value) if isinstance(value, (int, float)) else 0
            return 0
        
        return MatchStatistics(
            fixture_id=fixture_id,
            home_team=home_stats.get("team", {}).get("name", ""),
            away_team=away_stats.get("team", {}).get("name", ""),
            home_corners=find_stat(home_stats, "Corner Kicks"),
            away_corners=find_stat(away_stats, "Corner Kicks"),
            home_yellow_cards=find_stat(home_stats, "Yellow Cards"),
            away_yellow_cards=find_stat(away_stats, "Yellow Cards"),
            home_red_cards=find_stat(home_stats, "Red Cards"),
            away_red_cards=find_stat(away_stats, "Red Cards"),
            home_shots_on_target=find_stat(home_stats, "Shots on Goal"),
            away_shots_on_target=find_stat(away_stats, "Shots on Goal"),
            home_shots_total=find_stat(home_stats, "Total Shots"),
            away_shots_total=find_stat(away_stats, "Total Shots"),
            home_possession=find_stat(home_stats, "Ball Possession"),
            away_possession=find_stat(away_stats, "Ball Possession"),
        )
    
    async def get_team_statistics(
        self, 
        team_id: int, 
        league_id: int, 
        season: int
    ) -> Optional[TeamSeasonStats]:
        """
        Récupère les statistiques saisonnières d'une équipe.
        
        Args:
            team_id: ID de l'équipe dans API-Football
            league_id: ID de la ligue
            season: Année de la saison (ex: 2025)
            
        Returns:
            TeamSeasonStats ou None
        """
        data = await self._make_request(
            "/teams/statistics",
            params={
                "team": team_id,
                "league": league_id,
                "season": season
            }
        )
        
        if not data or not data.get("response"):
            return None
        
        response = data["response"]
        
        # Extraire les stats
        fixtures = response.get("fixtures", {})
        cards = response.get("cards", {})
        
        played = fixtures.get("played", {})
        total_matches = (played.get("home", 0) or 0) + (played.get("away", 0) or 0)
        
        # Calculer les totaux de cartons
        yellow_total = 0
        red_total = 0
        for period, period_cards in cards.items():
            if isinstance(period_cards, dict):
                yellow_total += period_cards.get("yellow", {}).get("total", 0) or 0
                red_total += period_cards.get("red", {}).get("total", 0) or 0
        
        return TeamSeasonStats(
            team_id=team_id,
            team_name=response.get("team", {}).get("name", ""),
            total_yellow_cards=yellow_total,
            total_red_cards=red_total,
            matches_played=total_matches,
            avg_yellow_cards=yellow_total / total_matches if total_matches > 0 else 0,
            avg_red_cards=red_total / total_matches if total_matches > 0 else 0,
        )
    
    async def search_team(self, team_name: str) -> Optional[int]:
        """
        Recherche l'ID API-Football d'une équipe par son nom.
        
        Args:
            team_name: Nom de l'équipe
            
        Returns:
            ID de l'équipe ou None
        """
        data = await self._make_request(
            "/teams",
            params={"search": team_name}
        )
        
        if not data or not data.get("response"):
            return None
        
        teams = data["response"]
        if teams:
            return teams[0].get("team", {}).get("id")
        return None
    
    async def get_fixtures_by_date(
        self, 
        date: str, 
        league_id: int = None
    ) -> List[Dict]:
        """
        Récupère les matchs d'une date.
        
        Args:
            date: Date au format YYYY-MM-DD
            league_id: ID de la ligue (optionnel)
            
        Returns:
            Liste des matchs
        """
        params = {"date": date}
        if league_id:
            params["league"] = league_id
        
        data = await self._make_request("/fixtures", params=params)
        
        if not data or not data.get("response"):
            return []
        
        return data["response"]


# Instance globale (sera configurée si la clé API est présente)
api_football_service = APIFootballService()


# Mapping des codes de ligue Football-Data.org -> API-Football
LEAGUE_MAPPING = {
    "PL": 39,    # Premier League
    "PD": 140,   # La Liga
    "BL1": 78,   # Bundesliga
    "SA": 135,   # Serie A
    "FL1": 61,   # Ligue 1
    "CL": 2,     # Champions League
}
