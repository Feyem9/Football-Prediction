"""
Service de synchronisation des matchs depuis Football-Data.org.

Ce service permet de synchroniser les matchs depuis l'API externe
vers la base de données locale.
"""
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session

from models.match import Match
from services.football_api import football_data_service


class MatchSyncService:
    """Service pour synchroniser les matchs avec Football-Data.org."""
    
    # Compétitions à synchroniser (plan gratuit)
    SYNC_COMPETITIONS = ["PL", "FL1", "BL1", "SA", "PD", "CL"]
    
    def __init__(self, db: Session):
        """
        Initialise le service de synchronisation.
        
        Args:
            db: Session SQLAlchemy
        """
        self.db = db
    
    def _parse_match_data(self, match_data: dict) -> dict:
        """
        Parse les données d'un match depuis l'API vers le format DB.
        
        Args:
            match_data: Données brutes de l'API
            
        Returns:
            Dict formaté pour le modèle Match
        """
        home_team = match_data.get("homeTeam", {})
        away_team = match_data.get("awayTeam", {})
        competition = match_data.get("competition", {})
        score = match_data.get("score", {})
        full_time = score.get("fullTime", {})
        half_time = score.get("halfTime", {})
        
        return {
            "external_id": match_data.get("id"),
            "competition_code": competition.get("code"),
            "competition_name": competition.get("name"),
            "matchday": match_data.get("matchday"),
            
            "home_team": home_team.get("name", "Unknown"),
            "home_team_id": home_team.get("id"),
            "home_team_short": home_team.get("shortName") or home_team.get("tla"),
            "home_team_crest": home_team.get("crest"),
            
            "away_team": away_team.get("name", "Unknown"),
            "away_team_id": away_team.get("id"),
            "away_team_short": away_team.get("shortName") or away_team.get("tla"),
            "away_team_crest": away_team.get("crest"),
            
            "match_date": datetime.fromisoformat(match_data["utcDate"].replace("Z", "+00:00")),
            "status": match_data.get("status", "SCHEDULED"),
            
            "score_home": full_time.get("home"),
            "score_away": full_time.get("away"),
            "score_home_halftime": half_time.get("home"),
            "score_away_halftime": half_time.get("away"),
            
            "last_synced": datetime.now(timezone.utc)
        }
    
    def _upsert_match(self, match_data: dict) -> Match:
        """
        Insert ou update un match dans la DB.
        
        Args:
            match_data: Données du match formatées
            
        Returns:
            Instance Match créée ou mise à jour
        """
        external_id = match_data["external_id"]
        
        # Chercher match existant
        existing = self.db.query(Match).filter(Match.external_id == external_id).first()
        
        if existing:
            # Update
            for key, value in match_data.items():
                setattr(existing, key, value)
            return existing
        else:
            # Insert
            new_match = Match(**match_data)
            self.db.add(new_match)
            return new_match
    
    async def sync_competition_matches(
        self, 
        competition_code: str,
        status: Optional[str] = None
    ) -> int:
        """
        Synchronise les matchs d'une compétition.
        
        Args:
            competition_code: Code de la compétition (ex: "PL", "FL1")
            status: Filtre par statut (SCHEDULED, FINISHED, etc.)
            
        Returns:
            Nombre de matchs synchronisés
        """
        try:
            result = await football_data_service.get_competition_matches(
                competition_code, 
                status=status
            )
            matches = result.get("matches", [])
            
            count = 0
            for match_data in matches:
                parsed = self._parse_match_data(match_data)
                self._upsert_match(parsed)
                count += 1
            
            self.db.commit()
            return count
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    async def sync_upcoming_matches(self, days: int = 7) -> int:
        """
        Synchronise les matchs à venir pour toutes les compétitions.
        
        Args:
            days: Nombre de jours à synchroniser
            
        Returns:
            Nombre total de matchs synchronisés
        """
        date_from = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        date_to = (datetime.now(timezone.utc) + timedelta(days=days)).strftime("%Y-%m-%d")
        
        try:
            result = await football_data_service.get_matches(
                date_from=date_from,
                date_to=date_to
            )
            matches = result.get("matches", [])
            
            count = 0
            for match_data in matches:
                # Filtrer par compétitions supportées
                comp_code = match_data.get("competition", {}).get("code")
                if comp_code in self.SYNC_COMPETITIONS:
                    parsed = self._parse_match_data(match_data)
                    self._upsert_match(parsed)
                    count += 1
            
            self.db.commit()
            return count
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    async def sync_finished_matches(self) -> int:
        """
        Met à jour les scores des matchs terminés.
        
        Returns:
            Nombre de matchs mis à jour
        """
        total = 0
        for code in self.SYNC_COMPETITIONS:
            try:
                count = await self.sync_competition_matches(code, status="FINISHED")
                total += count
            except Exception:
                continue  # Skip si erreur sur une compétition
        
        return total
    
    def get_matches_by_date(
        self, 
        date: Optional[datetime] = None,
        competition_code: Optional[str] = None
    ) -> List[Match]:
        """
        Récupère les matchs pour une date donnée.
        
        Args:
            date: Date des matchs (défaut: aujourd'hui)
            competition_code: Filtre par compétition
            
        Returns:
            Liste des matchs
        """
        if date is None:
            date = datetime.now(timezone.utc)
        
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        query = self.db.query(Match).filter(
            Match.match_date >= start_of_day,
            Match.match_date < end_of_day
        )
        
        if competition_code:
            query = query.filter(Match.competition_code == competition_code)
        
        return query.order_by(Match.match_date).all()
    
    def get_upcoming_matches(self, limit: int = 20) -> List[Match]:
        """
        Récupère les prochains matchs programmés.
        
        Args:
            limit: Nombre maximum de matchs
            
        Returns:
            Liste des matchs à venir
        """
        now = datetime.now(timezone.utc)
        
        return self.db.query(Match).filter(
            Match.match_date > now,
            Match.status.in_(["SCHEDULED", "TIMED"])
        ).order_by(Match.match_date).limit(limit).all()
