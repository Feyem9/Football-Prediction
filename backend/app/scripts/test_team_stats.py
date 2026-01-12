#!/usr/bin/env python3
"""
Test réel: Calcul et sauvegarde des statistiques d'une équipe.

Usage:
    cd backend/app && . venv/bin/activate
    python -m scripts.test_team_stats
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal
from services.team_stats_service import TeamStatsService
from services.football_api import football_data_service


async def test_arsenal_stats():
    """Test pour Arsenal (Team ID 57) en Premier League."""
    print("\n" + "=" * 60)
    print("📈 Test: Team Stats - ARSENAL")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        service = TeamStatsService(db)
        
        # 1. Calculer les stats
        print("\n📥 Calcul des statistiques pour Arsenal (ID: 57)...")
        stats = await service.calculate_and_save_stats(57, "PL")
        
        if stats:
            print(f"   ✅ Stats calculées et enregistrées.")
            print(f"   🏆 Compétition: {stats.competition_code}")
            print(f"   📅 Matchs joués: {stats.played}")
            print(f"   ✅ Victoires: {stats.wins}")
            print(f"   🤝 Nuls: {stats.draws}")
            print(f"   ❌ Défaites: {stats.losses}")
            print(f"   ⚽ Buts: {stats.goals_for} (Pour) / {stats.goals_against} (Contre)")
            print(f"   📊 Moyenne Buts: {stats.avg_goals_scored}")
            print(f"   🔥 Forme (5 derniers): {stats.form}")
        else:
            print("   ❌ Impossible de calculer les stats.")
            
        return stats is not None
        
    finally:
        db.close()


async def main():
    print("\n🚀 TEST TEAM STATS\n")
    
    if not football_data_service.api_key:
        print("❌ FOOTBALL_DATA_API_KEY manquante")
        return
    
    await test_arsenal_stats()
    
    limiter = football_data_service.rate_limiter
    print("\n" + "=" * 60)
    print(f"📊 Appels API: {10 - limiter.remaining_calls}/10 cette minute")
    print("=" * 60)
    print("\n✅ Test terminé!\n")


if __name__ == "__main__":
    asyncio.run(main())
