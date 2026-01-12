"""
Service pour l'intégration avec l'API Football-Data.org.

Cette classe fournit des méthodes pour récupérer les données de matchs,
compétitions, équipes et classements depuis l'API Football-Data.org (v4).

Documentation API: https://docs.football-data.org
"""
import httpx
import asyncio
import time
from typing import Optional, Any, List
from core.config import settings


class RateLimiter:
    """
    Rate limiter simple pour le plan gratuit Football-Data.org.
    Limite: 10 requêtes par minute.
    """
    
    def __init__(self, max_calls: int = 10, period: float = 60.0):
        """
        Args:
            max_calls: Nombre maximum d'appels autorisés
            period: Période en secondes
        """
        self.max_calls = max_calls
        self.period = period
        self.calls: List[float] = []
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """Attend si nécessaire avant de permettre un nouvel appel."""
        async with self._lock:
            now = time.time()
            
            # Nettoyer les appels expirés
            self.calls = [t for t in self.calls if now - t < self.period]
            
            if len(self.calls) >= self.max_calls:
                # Calculer le temps d'attente
                oldest = self.calls[0]
                wait_time = self.period - (now - oldest)
                
                if wait_time > 0:
                    print(f"⏳ Rate limit atteint. Attente de {wait_time:.1f}s...")
                    await asyncio.sleep(wait_time)
                    # Nettoyer à nouveau après l'attente
                    now = time.time()
                    self.calls = [t for t in self.calls if now - t < self.period]
            
            # Enregistrer cet appel
            self.calls.append(time.time())
    
    @property
    def remaining_calls(self) -> int:
        """Retourne le nombre d'appels restants dans la période."""
        now = time.time()
        active_calls = [t for t in self.calls if now - t < self.period]
        return max(0, self.max_calls - len(active_calls))


class FootballDataService:
    """
    Client pour l'API Football-Data.org.
    
    Plan Gratuit (Free Tier):
    - 10 requêtes/minute (avec rate limiting automatique)
    - Compétitions: Premier League, Bundesliga, La Liga, Serie A, Ligue 1,
      Eredivisie, Primeira Liga, Championship, Champions League, Euro
    """
    
    BASE_URL = "https://api.football-data.org/v4"
    
    # Rate limiter partagé (singleton)
    _rate_limiter: Optional[RateLimiter] = None
    
    def __init__(self):
        """Initialise le client avec la clé API depuis les settings."""
        self.api_key = settings.football_data_api_key
        self.headers = {
            "X-Auth-Token": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Initialiser le rate limiter si pas déjà fait
        if FootballDataService._rate_limiter is None:
            FootballDataService._rate_limiter = RateLimiter(max_calls=10, period=60.0)
    
    @property
    def rate_limiter(self) -> RateLimiter:
        """Retourne le rate limiter partagé."""
        return FootballDataService._rate_limiter
    
    async def _make_request(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """
        Effectue une requête GET vers l'API avec rate limiting.
        
        Args:
            endpoint: Endpoint API (ex: "/competitions")
            params: Paramètres de requête optionnels
            
        Returns:
            Réponse JSON de l'API
            
        Raises:
            httpx.HTTPStatusError: En cas d'erreur HTTP
        """
        # Attendre si rate limit atteint
        await self.rate_limiter.acquire()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}{endpoint}",
                headers=self.headers,
                params=params,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    # =====================
    # Compétitions
    # =====================
    
    async def get_competitions(self) -> dict:
        """
        Récupère la liste de toutes les compétitions disponibles.
        
        Returns:
            Dict contenant la liste des compétitions
        """
        return await self._make_request("/competitions")
    
    async def get_competition(self, code: str) -> dict:
        """
        Récupère les détails d'une compétition spécifique.
        
        Args:
            code: Code de la compétition (ex: "PL" pour Premier League)
            
        Returns:
            Détails de la compétition
        """
        return await self._make_request(f"/competitions/{code}")
    
    async def get_standings(self, competition_code: str, season: Optional[int] = None) -> dict:
        """
        Récupère le classement d'une compétition.
        
        Args:
            competition_code: Code de la compétition (ex: "PL", "FL1")
            season: Année de début de la saison (optionnel, ex: 2025)
            
        Returns:
            Classement avec positions, points, buts, etc.
        """
        params = {"season": season} if season else None
        return await self._make_request(f"/competitions/{competition_code}/standings", params)
    
    async def get_competition_matches(
        self, 
        competition_code: str, 
        matchday: Optional[int] = None,
        status: Optional[str] = None,
        season: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> dict:
        """
        Récupère les matchs d'une compétition.
        
        Args:
            competition_code: Code de la compétition
            matchday: Journée spécifique (optionnel)
            status: Filtre par statut (SCHEDULED, LIVE, FINISHED, etc.)
            season: Année de début de la saison
            date_from: Date de début (YYYY-MM-DD)
            date_to: Date de fin (YYYY-MM-DD)
            
        Returns:
            Liste des matchs
        """
        params = {}
        if matchday:
            params["matchday"] = matchday
        if status:
            params["status"] = status
        if season:
            params["season"] = season
        if date_from:
            params["dateFrom"] = date_from
        if date_to:
            params["dateTo"] = date_to
        return await self._make_request(f"/competitions/{competition_code}/matches", params or None)
    
    # =====================
    # Matchs
    # =====================
    
    async def get_matches(
        self,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        status: Optional[str] = None,
        competitions: Optional[str] = None
    ) -> dict:
        """
        Récupère les matchs selon des filtres.
        
        Args:
            date_from: Date de début (format: YYYY-MM-DD)
            date_to: Date de fin (format: YYYY-MM-DD)
            status: Filtre par statut (SCHEDULED, LIVE, IN_PLAY, FINISHED, etc.)
            competitions: IDs des compétitions séparés par virgule
            
        Returns:
            Liste des matchs correspondant aux filtres
        """
        params = {}
        if date_from:
            params["dateFrom"] = date_from
        if date_to:
            params["dateTo"] = date_to
        if status:
            params["status"] = status
        if competitions:
            params["competitions"] = competitions
        return await self._make_request("/matches", params or None)
    
    async def get_match(self, match_id: int) -> dict:
        """
        Récupère les détails d'un match spécifique.
        
        Args:
            match_id: ID du match
            
        Returns:
            Détails complets du match (équipes, score, stats, etc.)
        """
        return await self._make_request(f"/matches/{match_id}")
    
    # =====================
    # Équipes
    # =====================
    
    async def get_team(self, team_id: int) -> dict:
        """
        Récupère les informations d'une équipe.
        
        Args:
            team_id: ID de l'équipe
            
        Returns:
            Informations de l'équipe (nom, stade, effectif, etc.)
        """
        return await self._make_request(f"/teams/{team_id}")
    
    async def get_team_matches(
        self, 
        team_id: int,
        status: Optional[str] = None,
        limit: Optional[int] = None
    ) -> dict:
        """
        Récupère les matchs d'une équipe.
        
        Args:
            team_id: ID de l'équipe
            status: Filtre par statut
            limit: Nombre maximum de résultats
            
        Returns:
            Liste des matchs de l'équipe
        """
        params = {}
        if status:
            params["status"] = status
        if limit:
            params["limit"] = limit
        return await self._make_request(f"/teams/{team_id}/matches", params or None)
    
    # =====================
    # Codes des compétitions (Plan Gratuit)
    # =====================
    
    TIER_ONE_COMPETITIONS = {
        "PL": "Premier League (Angleterre)",
        "BL1": "Bundesliga (Allemagne)",
        "SA": "Serie A (Italie)",
        "PD": "La Liga (Espagne)",
        "FL1": "Ligue 1 (France)",
        "DED": "Eredivisie (Pays-Bas)",
        "PPL": "Primeira Liga (Portugal)",
        "ELC": "Championship (Angleterre)",
        "CL": "UEFA Champions League",
        "EC": "Championnat d'Europe (Euro)",
        "WC": "Coupe du Monde FIFA",
        "CLI": "Copa Libertadores",
        "BSA": "Campeonato Brasileiro Série A"
    }


# Instance singleton pour faciliter l'import
football_data_service = FootballDataService()
