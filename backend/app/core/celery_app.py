"""
Configuration Celery pour les tâches asynchrones.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Configuration du Broker Redis
# Par défaut: redis://localhost:6379/0
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "pronoscore_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["tasks.sync_tasks"]  # On inclura nos tasks ici
)

# Configuration par défaut
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Paris",
    enable_utc=True,
)

# Configuration du Beat (Scheduler)
celery_app.conf.beat_schedule = {
    # 1. Sync Matchs quotidiens (tous les jours à 06:00)
    "sync-daily-matches-morning": {
        "task": "tasks.sync_tasks.sync_daily_matches",
        "schedule": crontab(hour=6, minute=0),
    },
    # 2. Mise à jour des classements (tous les jours à 06:15)
    "update-standings-morning": {
        "task": "tasks.sync_tasks.update_standings",
        "schedule": crontab(hour=6, minute=15),
    },
    # 3. Recalcul des stats équipes (tous les jours à 06:30)
    "update-team-stats-morning": {
        "task": "tasks.sync_tasks.update_team_stats",
        "schedule": crontab(hour=6, minute=30),
    },
    # 4. Sync rapide des scores (toutes les heures)
    "sync-live-scores": {
        "task": "tasks.sync_tasks.sync_daily_matches",
        "schedule": crontab(minute=5), # à xx:05 chaque heure
    }
}
