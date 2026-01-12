"""
Configuration et gestion des tâches de fond (Scheduler).

Utilise APScheduler pour automatiser la synchronisation des données
et la génération de prédictions.
"""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from core.database import SessionLocal
from services.match_sync import MatchSyncService
from services.standing_sync import StandingSyncService
from services.prediction_service import PredictionService

# Configuration du logging pour le scheduler
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scheduler")

# Instance globale du scheduler
scheduler = AsyncIOScheduler()


async def sync_standings_job():
    """Tâche auto: Synchronisation des classements."""
    logger.info("🔄 [Job] Démarrage de la synchronisation des classements...")
    db = SessionLocal()
    try:
        standing_sync = StandingSyncService(db)
        count = await standing_sync.sync_all_standings()
        logger.info(f"✅ [Job] Terminé: {count} entrées de classement synchronisées.")
    except Exception as e:
        logger.error(f"❌ [Job] Erreur lors de la sync des classements: {e}")
    finally:
        db.close()


async def sync_matches_and_predictions_job():
    """Tâche auto: Synchronisation des matchs et génération des prédictions."""
    logger.info("🔄 [Job] Démarrage de la synchronisation des matchs et prédictions...")
    db = SessionLocal()
    try:
        # 1. Sync upcoming matches (7 prochains jours)
        match_sync = MatchSyncService(db)
        sync_count = await match_sync.sync_upcoming_matches(days=7)
        logger.info(f"📥 [Job] {sync_count} matchs synchronisés.")
        
        # 2. Générer les prédictions pour les nouveaux matchs
        prediction_service = PredictionService(db)
        pred_count = await prediction_service.generate_predictions_for_upcoming(limit=50)
        logger.info(f"🧠 [Job] {pred_count} prédictions générées.")
        
    except Exception as e:
        logger.error(f"❌ [Job] Erreur lors de la sync des matchs/prédictions: {e}")
    finally:
        db.close()


async def update_scores_job():
    """Tâche auto: Mise à jour des scores pour les matchs terminés."""
    logger.info("🔄 [Job] Démarrage de la mise à jour des scores...")
    db = SessionLocal()
    try:
        match_sync = MatchSyncService(db)
        count = await match_sync.sync_finished_matches()
        logger.info(f"✅ [Job] Scores mis à jour pour {count} matchs.")
    except Exception as e:
        logger.error(f"❌ [Job] Erreur lors de la mise à jour des scores: {e}")
    finally:
        db.close()


def start_scheduler():
    """Initialise et démarre le scheduler."""
    if not scheduler.running:
        # 1. Sync Classements: Toutes les 12 heures
        scheduler.add_job(
            sync_standings_job,
            CronTrigger(hour="0,12"),
            id="sync_standings",
            replace_existing=True
        )
        
        # 2. Sync Matchs & Préd: Toutes les 4 heures
        scheduler.add_job(
            sync_matches_and_predictions_job,
            CronTrigger(hour="2,6,10,14,18,22"),
            id="sync_matches",
            replace_existing=True
        )
        
        # 3. Update Scores: Toutes les heures (à la minute 5)
        scheduler.add_job(
            update_scores_job,
            CronTrigger(minute=5),
            id="update_scores",
            replace_existing=True
        )
        
        scheduler.start()
        logger.info("🚀 Scheduler démarré avec succès.")
    else:
        logger.warning("⚠️ Le scheduler est déjà en cours d'exécution.")


def stop_scheduler():
    """Arrête proprement le scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("🛑 Scheduler arrêté.")
