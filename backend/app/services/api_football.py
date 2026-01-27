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
    Service pour interagir avec API-Football via API-Sports direct.
    
    Cette API est utilisée pour les données H2H car elle a un historique
    beaucoup plus complet que Football-Data.org (jusqu'à 20+ ans).
    """
    
    BASE_URL = "https://v3.football.api-sports.io"
    
    def __init__(self):
        self.api_key = os.getenv("APISPORTS_KEY")
        self.headers = {
            "x-apisports-key": self.api_key or "",
            "Accept": "application/json"
        }
        # Cache pour éviter les requêtes répétées
        self._team_id_cache: Dict[str, int] = {}
    
    async def _make_request(self, endpoint: str, params: dict = None) -> dict:
        """Effectue une requête à l'API."""
        if not self.api_key:
            return {"response": [], "errors": ["APISPORTS_KEY not configured"]}
        
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
        # Note: Le plan gratuit ne supporte pas le paramètre 'last'
        # L'API retourne tous les matchs H2H disponibles
        data = await self._make_request(
            "/fixtures/headtohead",
            {"h2h": f"{team1_id}-{team2_id}"}
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
    
    async def get_team_last_matches(self, team_name: str, last: int = 10) -> dict:
        """
        Récupère les N derniers matchs d'une équipe.
        
        Args:
            team_name: Nom de l'équipe
            last: Nombre de matchs à récupérer (défaut: 10)
            
        Returns:
            Liste des matchs avec scores, adversaires, statistiques
        """
        team_id = await self.search_team(team_name)
        if not team_id:
            return {"success": False, "error": f"Équipe non trouvée: {team_name}", "matches": []}
        
        data = await self._make_request("/fixtures", {
            "team": team_id,
            "last": last,
            "status": "FT"  # Matchs terminés uniquement
        })
        
        matches = []
        for fixture in data.get("response", []):
            fixture_data = fixture.get("fixture", {})
            teams = fixture.get("teams", {})
            goals = fixture.get("goals", {})
            score = fixture.get("score", {})
            
            home_team = teams.get("home", {})
            away_team = teams.get("away", {})
            
            is_home = home_team.get("id") == team_id
            
            # Déterminer le résultat
            home_goals = goals.get("home", 0) or 0
            away_goals = goals.get("away", 0) or 0
            
            if is_home:
                buts_pour = home_goals
                buts_contre = away_goals
                adversaire = away_team.get("name", "Inconnu")
            else:
                buts_pour = away_goals
                buts_contre = home_goals
                adversaire = home_team.get("name", "Inconnu")
            
            if buts_pour > buts_contre:
                resultat = "V"
            elif buts_pour < buts_contre:
                resultat = "D"
            else:
                resultat = "N"
            
            matches.append({
                "fixture_id": fixture_data.get("id"),
                "date": fixture_data.get("date"),
                "domicile": is_home,
                "resultat": resultat,
                "buts_pour": buts_pour,
                "buts_contre": buts_contre,
                "adversaire": adversaire,
                "adversaire_id": away_team.get("id") if is_home else home_team.get("id"),
                "competition": fixture.get("league", {}).get("name", "Championnat"),
                "competition_id": fixture.get("league", {}).get("id")
            })
        
        return {
            "success": True,
            "team_id": team_id,
            "team_name": team_name,
            "matches": matches
        }
    
    async def get_fixture_statistics(self, fixture_id: int) -> dict:
        """
        Récupère les statistiques détaillées d'un match.
        
        Args:
            fixture_id: ID du match
            
        Returns:
            Statistiques: tirs, corners, possession, etc.
        """
        data = await self._make_request("/fixtures/statistics", {
            "fixture": fixture_id
        })
        
        stats = {"home": {}, "away": {}}
        
        for team_stats in data.get("response", []):
            team_data = team_stats.get("team", {})
            statistics = team_stats.get("statistics", [])
            
            # Déterminer si c'est home ou away (premier = home, second = away)
            team_key = "home" if len(stats["home"]) == 0 and data.get("response", []).index(team_stats) == 0 else "away"
            
            for stat in statistics:
                stat_type = stat.get("type", "").lower().replace(" ", "_")
                stat_value = stat.get("value")
                
                # Convertir les pourcentages
                if isinstance(stat_value, str) and "%" in stat_value:
                    try:
                        stat_value = float(stat_value.replace("%", ""))
                    except:
                        pass
                
                stats[team_key][stat_type] = stat_value
        
        return {
            "success": True,
            "fixture_id": fixture_id,
            "statistics": stats
        }
    
    async def get_team_injuries(self, team_name: str) -> dict:
        """
        Récupère les joueurs blessés/absents d'une équipe.
        
        Args:
            team_name: Nom de l'équipe
            
        Returns:
            Liste des joueurs blessés avec détails
        """
        team_id = await self.search_team(team_name)
        if not team_id:
            return {"success": False, "error": f"Équipe non trouvée: {team_name}", "injuries": []}
        
        # Récupérer les blessures pour la saison en cours
        current_season = datetime.now().year
        if datetime.now().month < 7:  # Avant juillet = saison précédente
            current_season -= 1
        
        data = await self._make_request("/injuries", {
            "team": team_id,
            "season": current_season
        })
        
        injuries = []
        for injury in data.get("response", []):
            player = injury.get("player", {})
            injury_data = injury.get("player", {})
            
            # Déterminer l'importance du joueur (simplifié)
            # En production, on utiliserait les stats du joueur
            importance = 5  # Valeur par défaut
            
            injuries.append({
                "nom": player.get("name", "Inconnu"),
                "poste": player.get("type", "Joueur"),
                "raison": injury.get("player", {}).get("reason", "Blessure"),
                "importance": importance
            })
        
        return {
            "success": True,
            "team_id": team_id,
            "team_name": team_name,
            "injuries": injuries[:10]  # Limiter à 10
        }
    
    async def get_team_standings_position(self, team_name: str, league_id: int = None) -> dict:
        """
        Récupère la position au classement d'une équipe.
        
        Args:
            team_name: Nom de l'équipe
            league_id: ID de la ligue (optionnel)
            
        Returns:
            Position, points, forme
        """
        team_id = await self.search_team(team_name)
        if not team_id:
            return {"success": False, "error": f"Équipe non trouvée: {team_name}"}
        
        # Récupérer les standings
        current_season = datetime.now().year
        if datetime.now().month < 7:
            current_season -= 1
        
        params = {"season": current_season, "team": team_id}
        if league_id:
            params["league"] = league_id
        
        data = await self._make_request("/standings", params)
        
        for league in data.get("response", []):
            standings = league.get("league", {}).get("standings", [[]])
            for group in standings:
                for team in group:
                    if team.get("team", {}).get("id") == team_id:
                        return {
                            "success": True,
                            "team_id": team_id,
                            "position": team.get("rank", 10),
                            "points": team.get("points", 0),
                            "played": team.get("all", {}).get("played", 0),
                            "won": team.get("all", {}).get("win", 0),
                            "drawn": team.get("all", {}).get("draw", 0),
                            "lost": team.get("all", {}).get("lose", 0),
                            "goals_for": team.get("all", {}).get("goals", {}).get("for", 0),
                            "goals_against": team.get("all", {}).get("goals", {}).get("against", 0),
                            "form": team.get("form", ""),
                            "home": team.get("home", {}),
                            "away": team.get("away", {})
                        }
        
        return {"success": False, "error": "Position non trouvée"}


# Instance globale
api_football_service = APIFootballService()

