"""
Script de collecte massive de données (Seed).
Récupère les matchs de Premier League (-30/+30j) et les classements.
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal
from services.match_sync import MatchSyncService
from services.standing_sync import StandingSyncService
from services.team_stats_service import TeamStatsService
from services.football_api import football_data_service

async def seed_data():
    print("🌱 Démarrage du Seed de données...")
    db = SessionLocal()
    
    try:
        # A. Sync Matchs PL (Passé & Futur)
        print("\n1. Sync Matchs Premier League (PL)...")
        match_service = MatchSyncService(db)
        
        # 30 derniers jours
        today = datetime.now()
        date_from = (today - timedelta(days=30)).strftime("%Y-%m-%d")
        date_to = (today + timedelta(days=30)).strftime("%Y-%m-%d")
        
        print(f"   📅 Période: {date_from} à {date_to}")
        
        # Note: get_competition_matches dans le service ne supporte pas encore date_from/to direct
        # On va utiliser sync_competition_matches qui fait tout
        # Mais pour être précis, on appelle l'API via le sync service qui gère la logique
        
        # Pour simplifier, on sync tout le calendrier SCHEDULED et FINISHED de la PL
        # Attention au quota, on fait juste la PL pour l'instant
        count_finished = await match_service.sync_competition_matches("PL", status="FINISHED")
        count_scheduled = await match_service.sync_competition_matches("PL", status="SCHEDULED")
        
        print(f"   ✅ {count_finished} matchs terminés")
        print(f"   ✅ {count_scheduled} matchs programmés")

        # B. Sync Classements (Toutes compétitions majeures)
        print("\n2. Sync Classements...")
        standing_service = StandingSyncService(db)
        count_standings = await standing_service.sync_all_standings()
        print(f"   ✅ {count_standings} entrées de classement mises à jour.")

        # C. Calcul Stats Équipes (Top 6 PL)
        print("\n3. Calcul Stats Top 6 PL...")
        team_service = TeamStatsService(db)
        standings = standing_service.get_standings("PL")
        
        top_6 = standings[:6]
        for entry in top_6:
            print(f"   📊 Calcul pour {entry.team_name}...")
            await team_service.calculate_and_save_stats(entry.team_id, "PL")
            
        print("\n✅ Seed terminé avec succès !")
        
    except Exception as e:
        print(f"\n❌ Erreur durant le seed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(seed_data())
