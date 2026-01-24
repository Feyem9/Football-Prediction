"""
Service pour l'API API-Football (RapidAPI).
Utilisé principalement pour les données H2H historiques complètes.
"""
import os
import httpx
from typing import Optional, Dict, List
from datetime import datetime

class APIFootballService:
    """
    Service pour interagir avec API-Football via RapidAPI.
    
    Cette API est utilisée pour les données H2H car elle a un historique
    beaucoup plus complet que Football-Data.org (jusqu'à 20+ ans).
    """
    
    BASE_URL = "https://api-football-v1.p.rapidapi.com/v3"
    
    def __init__(self):
        self.api_key = os.getenv("RAPIDAPI_KEY")
        self.headers = {
            "X-RapidAPI-Key": self.api_key or "",
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        }
        # Cache pour éviter les requêtes répétées
        self._team_id_cache: Dict[str, int] = {}
    
    async def _make_request(self, endpoint: str, params: dict = None) -> dict:
        """Effectue une requête à l'API."""
        if not self.api_key:
            return {"response": [], "errors": ["RAPIDAPI_KEY not configured"]}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}{endpoint}",
                    headers=self.headers,
                    params=params or {}
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"API-Football error: {e}")
                return {"response": [], "errors": [str(e)]}
    
    async def search_team(self, team_name: str) -> Optional[int]:
        """
        Recherche l'ID API-Football d'une équipe par son nom.
        
        Args:
            team_name: Nom de l'équipe (ex: "West Ham United FC")
            
        Returns:
            ID de l'équipe dans API-Football ou None
        """
        # Vérifier le cache
        cache_key = team_name.lower()
        if cache_key in self._team_id_cache:
            return self._team_id_cache[cache_key]
        
        # Nettoyer le nom (enlever "FC", "AFC", etc.)
        clean_name = team_name.replace(" FC", "").replace(" AFC", "").strip()
        
        data = await self._make_request("/teams", {"search": clean_name})
        
        teams = data.get("response", [])
        if teams:
            team_id = teams[0].get("team", {}).get("id")
            if team_id:
                self._team_id_cache[cache_key] = team_id
                return team_id
        
        return None
    
    async def get_h2h(
        self, 
        team1_id: int, 
        team2_id: int, 
        limit: int = 20
    ) -> dict:
        """
        Récupère l'historique complet des confrontations (H2H).
        
        Args:
            team1_id: ID API-Football de l'équipe 1
            team2_id: ID API-Football de l'équipe 2
            limit: Nombre max de matchs à retourner
            
        Returns:
            Dict avec les matchs H2H
        """
        data = await self._make_request(
            "/fixtures/headtohead",
            {"h2h": f"{team1_id}-{team2_id}", "last": limit}
        )
        
        return data
    
    async def get_h2h_by_names(
        self, 
        home_team_name: str, 
        away_team_name: str,
        limit: int = 20
    ) -> dict:
        """
        Récupère l'historique H2H en utilisant les noms d'équipes.
        
        Cette méthode recherche d'abord les IDs des équipes,
        puis récupère les H2H.
        
        Args:
            home_team_name: Nom de l'équipe domicile
            away_team_name: Nom de l'équipe extérieur
            limit: Nombre max de matchs
            
        Returns:
            Dict avec statistiques H2H détaillées
        """
        # Rechercher les IDs
        home_id = await self.search_team(home_team_name)
        away_id = await self.search_team(away_team_name)
        
        if not home_id or not away_id:
            return {
                "success": False,
                "error": f"Team not found: {home_team_name if not home_id else away_team_name}",
                "matches": [],
                "stats": {}
            }
        
        # Récupérer les H2H
        h2h_data = await self.get_h2h(home_id, away_id, limit)
        
        matches = h2h_data.get("response", [])
        
        if not matches:
            return {
                "success": True,
                "matches": [],
                "stats": {
                    "home_wins": 0,
                    "away_wins": 0,
                    "draws": 0,
                    "total_matches": 0,
                    "home_goals_total": 0,
                    "away_goals_total": 0
                }
            }
        
        # Calculer les statistiques
        home_wins = 0
        away_wins = 0
        draws = 0
        home_goals = 0
        away_goals = 0
        
        for match in matches:
            fixture = match.get("fixture", {})
            teams = match.get("teams", {})
            goals = match.get("goals", {})
            
            # Vérifier que le match est terminé
            if fixture.get("status", {}).get("short") != "FT":
                continue
            
            home_score = goals.get("home") or 0
            away_score = goals.get("away") or 0
            
            match_home_id = teams.get("home", {}).get("id")
            match_away_id = teams.get("away", {}).get("id")
            
            # Comptabiliser les buts pour notre équipe "home" actuelle
            if match_home_id == home_id:
                home_goals += home_score
                away_goals += away_score
                if home_score > away_score:
                    home_wins += 1
                elif away_score > home_score:
                    away_wins += 1
                else:
                    draws += 1
            else:
                # Notre équipe "home" jouait à l'extérieur dans ce match
                home_goals += away_score
                away_goals += home_score
                if away_score > home_score:
                    home_wins += 1
                elif home_score > away_score:
                    away_wins += 1
                else:
                    draws += 1
        
        total_matches = home_wins + away_wins + draws
        
        return {
            "success": True,
            "home_team_id": home_id,
            "away_team_id": away_id,
            "matches": matches,
            "stats": {
                "home_wins": home_wins,
                "away_wins": away_wins,
                "draws": draws,
                "total_matches": total_matches,
                "home_goals_total": home_goals,
                "away_goals_total": away_goals,
                "home_goals_freq": round(home_goals / total_matches, 2) if total_matches > 0 else 0,
                "away_goals_freq": round(away_goals / total_matches, 2) if total_matches > 0 else 0,
                "top_scorer": "home" if home_goals > away_goals else ("away" if away_goals > home_goals else "equal")
            }
        }


# Instance globale
api_football_service = APIFootballService()
