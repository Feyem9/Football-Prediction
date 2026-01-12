"""
Service de synchronisation des classements depuis Football-Data.org.

Ce service permet de synchroniser les classements depuis l'API externe
vers la base de données locale pour réduire les appels API.
"""
import logging
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.orm import Session

from models.standing import Standing
from services.football_api import football_data_service

logger = logging.getLogger(__name__)


class StandingSyncService:
    """Service pour synchroniser les classements avec Football-Data.org."""
    
    # Compétitions à synchroniser (plan gratuit)
    SYNC_COMPETITIONS = ["PL", "FL1", "BL1", "SA", "PD", "CL", "DED", "PPL"]
    
    def __init__(self, db: Session):
        """
        Initialise le service de synchronisation.
        
        Args:
            db: Session SQLAlchemy
        """
        self.db = db
    
    def _parse_standing_data(
        self, 
        entry: dict, 
        competition_code: str,
        competition_name: str,
        season: int,
        matchday: Optional[int]
    ) -> dict:
        """
        Parse les données d'une entrée de classement depuis l'API vers le format DB.
        
        Args:
            entry: Données brutes d'une ligne de classement
            competition_code: Code de la compétition
            competition_name: Nom de la compétition
            season: ID de la saison
            matchday: Journée actuelle
            
        Returns:
            Dict formaté pour le modèle Standing
        """
        team = entry.get("team", {})
        
        return {
            "competition_code": competition_code,
            "competition_name": competition_name,
            "season": season,
            "matchday": matchday,
            "position": entry.get("position"),
            "team_id": team.get("id"),
            "team_name": team.get("name", "Unknown"),
            "team_short": team.get("shortName") or team.get("tla"),
            "team_crest": team.get("crest"),
            "played_games": entry.get("playedGames", 0),
            "won": entry.get("won", 0),
            "draw": entry.get("draw", 0),
            "lost": entry.get("lost", 0),
            "points": entry.get("points", 0),
            "goals_for": entry.get("goalsFor", 0),
            "goals_against": entry.get("goalsAgainst", 0),
            "goal_difference": entry.get("goalDifference", 0),
            "form": entry.get("form"),
            "last_synced": datetime.now(timezone.utc)
        }
    
    def _upsert_standing(self, standing_data: dict) -> Standing:
        """
        Insert ou update une entrée de classement dans la DB.
        
        Args:
            standing_data: Données du classement formatées
            
        Returns:
            Instance Standing créée ou mise à jour
        """
        # Chercher entrée existante
        existing = self.db.query(Standing).filter(
            Standing.competition_code == standing_data["competition_code"],
            Standing.season == standing_data["season"],
            Standing.team_id == standing_data["team_id"]
        ).first()
        
        if existing:
            # Update
            for key, value in standing_data.items():
                setattr(existing, key, value)
            return existing
        else:
            # Insert
            new_standing = Standing(**standing_data)
            self.db.add(new_standing)
            return new_standing
    
    async def sync_standings(self, competition_code: str) -> int:
        """
        Synchronise le classement d'une compétition.
        
        Args:
            competition_code: Code de la compétition (ex: "PL", "FL1")
            
        Returns:
            Nombre d'entrées synchronisées
        """
        try:
            logger.info(f"Syncing standings for competition: {competition_code}")
            result = await football_data_service.get_standings(competition_code)
            
            standings_data = result.get("standings", [])
            if not standings_data:
                logger.warning(f"No standings data found for {competition_code}")
                return 0
            
            competition = result.get("competition", {})
            season = result.get("season", {})
            
            table = standings_data[0].get("table", [])
            
            count = 0
            for entry in table:
                parsed = self._parse_standing_data(
                    entry=entry,
                    competition_code=competition.get("code", competition_code),
                    competition_name=competition.get("name", ""),
                    season=season.get("id", 0),
                    matchday=season.get("currentMatchday")
                )
                self._upsert_standing(parsed)
                count += 1
            
            self.db.commit()
            logger.info(f"Successfully synced {count} entries for {competition_code}")
            return count
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error syncing standings for {competition_code}: {e}")
            raise e
    
    async def sync_all_standings(self) -> int:
        """
        Synchronise les classements de toutes les compétitions.
        
        Returns:
            Nombre total d'entrées synchronisées
        """
        total = 0
        logger.info("Starting sync for all supported competitions")
        for code in self.SYNC_COMPETITIONS:
            try:
                count = await self.sync_standings(code)
                total += count
            except Exception:
                continue  # Skip si erreur sur une compétition
        
        logger.info(f"Finished sync for all competitions. Total entries: {total}")
        return total
    
    def get_standings(self, competition_code: str) -> List[Standing]:
        """
        Récupère le classement d'une compétition depuis la DB.
        
        Args:
            competition_code: Code de la compétition
            
        Returns:
            Liste des entrées de classement ordonnées par position
        """
        return self.db.query(Standing).filter(
            Standing.competition_code == competition_code.upper()
        ).order_by(Standing.position).all()
    
    def is_stale(self, competition_code: str, max_age_hours: int = 6) -> bool:
        """
        Vérifie si le classement est périmé.
        
        Args:
            competition_code: Code de la compétition
            max_age_hours: Âge maximum en heures avant péremption
            
        Returns:
            True si le classement doit être rafraîchi
        """
        latest = self.db.query(Standing).filter(
            Standing.competition_code == competition_code.upper()
        ).first()
        
        if not latest or not latest.last_synced:
            return True
        
        # Ensure UTC comparison
        now = datetime.now(timezone.utc)
        last_synced = latest.last_synced
        if last_synced.tzinfo is None:
            last_synced = last_synced.replace(tzinfo=timezone.utc)
            
        age = now - last_synced
        return age.total_seconds() > (max_age_hours * 3600)
