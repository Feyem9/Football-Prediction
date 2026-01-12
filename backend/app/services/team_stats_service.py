"""Service pour le calcul et la persistance des statistiques d'équipes."""
import logging
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.orm import Session

from models.team_stats import TeamStats
from services.football_api import football_data_service

logger = logging.getLogger(__name__)


class TeamStatsService:
    """
    Service responsable du calcul des statistiques d'une équipe
    en se basant sur ses derniers matchs.
    """
    
    def __init__(self, db: Session):
        self.db = db
        
    async def calculate_and_save_stats(
        self, 
        team_id: int, 
        competition_code: str,
        season: Optional[int] = None
    ) -> TeamStats:
        """
        Récupère les derniers matchs, calcule les stats et les enregistre.
        """
        logger.info(f"Calcul des stats pour l'équipe {team_id} ({competition_code})")
        
        # 1. Récupérer les derniers matchs finis de l'équipe
        # Note: Dans le plan gratuit, on est limité sur le nombre de matchs
        result = await football_data_service.get_team_matches(
            team_id, 
            status="FINISHED", 
            limit=20
        )
        
        matches = result.get("matches", [])
        if not matches:
            logger.warning(f"Aucun match trouvé pour l'équipe {team_id}")
            # Retourner un objet vide ou lever une erreur selon le besoin
            return None

        # Filtrer par compétition si nécessaire
        relevant_matches = [
            m for m in matches 
            if m.get("competition", {}).get("code") == competition_code
        ]
        
        if not relevant_matches:
            # Si aucun match dans CETTE compétition, on prend les derniers tous confondus
            relevant_matches = matches[:10]

        # 2. Calculer les statistiques
        played = 0
        wins = 0
        draws = 0
        losses = 0
        goals_for = 0
        goals_against = 0
        form_list = []
        
        actual_season = season or relevant_matches[0].get("season", {}).get("id")

        for m in relevant_matches:
            played += 1
            score = m.get("score", {}).get("fullTime", {})
            h_score = score.get("home")
            a_score = score.get("away")
            
            # Déterminer si l'équipe est Home ou Away
            is_home = m.get("homeTeam", {}).get("id") == team_id
            
            if is_home:
                goals_for += h_score or 0
                goals_against += a_score or 0
                if (h_score or 0) > (a_score or 0):
                    wins += 1
                    form_list.append("W")
                elif h_score == a_score:
                    draws += 1
                    form_list.append("D")
                else:
                    losses += 1
                    form_list.append("L")
            else:
                goals_for += a_score or 0
                goals_against += h_score or 0
                if (a_score or 0) > (h_score or 0):
                    wins += 1
                    form_list.append("W")
                elif a_score == h_score:
                    draws += 1
                    form_list.append("D")
                else:
                    losses += 1
                    form_list.append("L")

        # Inverser la forme pour avoir du plus récent au plus ancien (ou l'inverse, restons cohérents)
        # API renvoie souvent chronologique, on veut les 5 derniers
        form_str = "".join(form_list[-5:]) if form_list else ""
        
        avg_scored = goals_for / played if played > 0 else 0.0
        avg_conceded = goals_against / played if played > 0 else 0.0

        # 3. Upsert en DB
        stats_data = {
            "team_id": team_id,
            "competition_code": competition_code,
            "season": actual_season,
            "played": played,
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "goals_for": goals_for,
            "goals_against": goals_against,
            "avg_goals_scored": round(avg_scored, 2),
            "avg_goals_conceded": round(avg_conceded, 2),
            "form": form_str,
            "last_updated": datetime.now(timezone.utc)
        }
        
        existing = self.db.query(TeamStats).filter(
            TeamStats.team_id == team_id,
            TeamStats.competition_code == competition_code,
            TeamStats.season == actual_season
        ).first()
        
        if existing:
            for key, value in stats_data.items():
                setattr(existing, key, value)
            stats_obj = existing
        else:
            stats_obj = TeamStats(**stats_data)
            self.db.add(stats_obj)
            
        self.db.commit()
        self.db.refresh(stats_obj)
        
        return stats_obj

    def get_stats_from_db(self, team_id: int, competition_code: str) -> Optional[TeamStats]:
        """Récupère les stats depuis la DB si elles existent."""
        return self.db.query(TeamStats).filter(
            TeamStats.team_id == team_id,
            TeamStats.competition_code == competition_code
        ).order_by(TeamStats.last_updated.desc()).first()
