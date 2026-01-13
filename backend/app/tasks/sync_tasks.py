"""
Tâches Celery pour la synchronisation des données.
"""
import asyncio
import logging
from core.celery_app import celery_app
from core.database import SessionLocal
from services.match_sync import MatchSyncService
from services.standing_sync import StandingSyncService
from services.team_stats_service import TeamStatsService
from services.football_api import FootballDataService

logger = logging.getLogger(__name__)

def run_async(coro):
    """Helper pour exécuter une coroutine dans un contexte synchrone."""
    try:
        return asyncio.run(coro)
    except RuntimeError:
        # Fallback si une boucle est déjà active (rare en worker celery pur)
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro)

@celery_app.task
def sync_daily_matches():
    """
    Synchronise les matchs :
    - Matchs d'hier (pour les résultats finaux)
    - Matchs d'aujourd'hui
    - Matchs des 7 prochains jours
    """
    logger.info("⚡ [Task] Démarrage sync_daily_matches...")
    db = SessionLocal()
    try:
        service = MatchSyncService(db)
        
        # 1. Sync des matchs récents et à venir
        # Note: sync_upcoming_matches fait par défaut J-1 à J+7
        count = run_async(service.sync_upcoming_matches(days=10))
        
        logger.info(f"✅ [Task] sync_daily_matches terminé: {count} matchs traités.")
        return f"{count} matchs synchronisés"
    except Exception as e:
        logger.error(f"❌ [Task] Erreur sync_daily_matches: {e}")
        raise
    finally:
        db.close()

@celery_app.task
def update_standings():
    """
    Met à jour les classements pour toutes les compétitions majeures.
    """
    logger.info("⚡ [Task] Démarrage update_standings...")
    db = SessionLocal()
    try:
        service = StandingSyncService(db)
        count = run_async(service.sync_all_standings())
        
        logger.info(f"✅ [Task] update_standings terminé: {count} classements.")
        return f"{count} classements mis à jour"
    except Exception as e:
        logger.error(f"❌ [Task] Erreur update_standings: {e}")
        raise
    finally:
        db.close()

@celery_app.task
def update_team_stats():
    """
    Recalcule les statistiques pour toutes les équipes des ligues majeures.
    Se base sur les classements actuels pour trouver les équipes actives.
    """
    logger.info("⚡ [Task] Démarrage update_team_stats...")
    db = SessionLocal()
    try:
        stats_service = TeamStatsService(db)
        standing_service = StandingSyncService(db)
        
        total_updated = 0
        
        # Pour chaque compétition majeure
        for code in FootballDataService.TIER_ONE_COMPETITIONS.keys():
            # Récupérer le classement (depuis cache DB si dispo)
            standings = standing_service.get_standings(code)
            if not standings:
                continue
                
            logger.info(f"   📊 Mise à jour stats pour {code} ({len(standings)} équipes)...")
            
            for entry in standings:
                # Recalculer les stats pour cette équipe
                run_async(stats_service.calculate_and_save_stats(entry.team_id, code))
                total_updated += 1
                
        logger.info(f"✅ [Task] update_team_stats terminé: {total_updated} équipes.")
        return f"{total_updated} stats d'équipes mises à jour"
        
    except Exception as e:
        logger.error(f"❌ [Task] Erreur update_team_stats: {e}")
        raise
    finally:
        db.close()
