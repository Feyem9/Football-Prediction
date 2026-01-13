"""
Script de population massive de la base de données.
Couvre les 5 grands championnats : PL, PD, BL1, SA, FL1.
Période : J-30 à J+60.
"""
import asyncio
import logging
import sys
import os
from datetime import datetime, timedelta, timezone

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("populate_db")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal, engine, Base
from services.match_sync import MatchSyncService
from services.standing_sync import StandingSyncService
from services.team_stats_service import TeamStatsService
from sqlalchemy import text

# Configuration
COMPETITIONS = ["PL", "PD", "BL1", "SA", "FL1", "CL", "WC"]
DAYS_PAST = 30
DAYS_FUTURE = 60

async def populate_all():
    # Déterminer les compétitions à traiter
    target_competitions = COMPETITIONS
    if len(sys.argv) > 1:
        arg = sys.argv[1].upper()
        if arg in COMPETITIONS:
            target_competitions = [arg]
            logger.info(f"🎯 Mode ciblé : {arg} uniquement")
        else:
            logger.error(f"❌ Compétition non supportée : {arg}. Liste possible : {COMPETITIONS}")
            return

    logger.info("🚀 Démarrage de la population...")
    db = SessionLocal()
    
    match_service = MatchSyncService(db)
    standing_service = StandingSyncService(db)
    stats_service = TeamStatsService(db)
    
    today = datetime.now()
    date_from = (today - timedelta(days=DAYS_PAST)).strftime("%Y-%m-%d")
    date_to = (today + timedelta(days=DAYS_FUTURE)).strftime("%Y-%m-%d")
    
    logger.info(f"📅 Période cible : {date_from} à {date_to}")

    try:
        for league in target_competitions:
            try:
                logger.info(f"\n🏆 Traitement de la compétition : {league}")
                
                # 1. Matchs (avec retry)
                m_count = 0
                for attempt in range(3):
                    try:
                        logger.info(f"   ⚽ Synchronisation des matchs ({league})... Tentative {attempt+1}/3")
                        m_count = await match_service.sync_competition_matches(
                            league, 
                            date_from=date_from, 
                            date_to=date_to
                        )
                        break
                    except Exception as e:
                        if attempt < 2:
                            logger.warning(f"      ⚠️ Échec matchs {league}, nouvelle tentative dans 5s... ({e})")
                            await asyncio.sleep(5)
                        else:
                            raise e
                logger.info(f"   ✅ {m_count} matchs synchronisés.")
                
                # 2. Classements (avec retry)
                for attempt in range(3):
                    try:
                        logger.info(f"   📊 Synchronisation du classement ({league})... Tentative {attempt+1}/3")
                        await standing_service.sync_standings(league)
                        break
                    except Exception as e:
                        if attempt < 2:
                            logger.warning(f"      ⚠️ Échec classement {league}, nouvelle tentative dans 5s... ({e})")
                            await asyncio.sleep(5)
                        else:
                            raise e
                
                standings = standing_service.get_standings(league)
                logger.info(f"   ✅ {len(standings)} entrées de classement.")
                
                # 3. Stats Équipes (Top 20 = Toute la ligue en général)
                logger.info(f"   📈 Calcul des statistiques d'équipes ({league})...")
                s_count = 0
                for entry in standings:
                    try:
                        logger.info(f"      Calcul pour {entry.team_name}...")
                        await stats_service.calculate_and_save_stats(entry.team_id, league)
                        s_count += 1
                    except Exception as e:
                        logger.warning(f"      ⚠️ Erreur pour {entry.team_name}: {e}")
                    
                    # Petit délai de courtoisie en plus du rate limiter
                    await asyncio.sleep(0.5)
                logger.info(f"   ✅ Stats calculées pour {s_count}/{len(standings)} équipes.")

            except Exception as e:
                logger.error(f"❌ Erreur lors du traitement de la compétition {league}: {e}")
                continue

        # --- Audit Final ---
        logger.info("\n🔍 Audit d'intégrité final...")
        
        tables = ["matches", "standings", "team_stats"]
        for table in tables:
            count = db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            logger.info(f"   - {table.ljust(12)} : {count} lignes")
            
        # Check scores manquants sur matchs finis
        missing_scores = db.execute(text(
            "SELECT COUNT(*) FROM matches WHERE status='FINISHED' AND (score_home IS NULL OR score_away IS NULL)"
        )).scalar()
        if missing_scores > 0:
            logger.warning(f"   ⚠️ {missing_scores} matchs FINISHED n'ont pas de score !")
        else:
            logger.info("   ✅ Tous les matchs terminés ont un score.")

        logger.info("\n✨ Population terminée avec succès !")
        logger.info("💡 Conseil : Tu peux faire un backup avec : pg_dump -U ton_user pronoscore > backup.sql")

    except Exception as e:
        logger.error(f"❌ Erreur critique lors de la population : {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(populate_all())
