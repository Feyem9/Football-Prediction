#!/usr/bin/env python3
"""
Test réel: Synchronisation des classements.

Usage:
    cd backend/app && . venv/bin/activate
    python -m scripts.test_standings_sync
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal
from services.standing_sync import StandingSyncService
from services.football_api import football_data_service


async def test_sync_standings():
    """Test de synchronisation des classements."""
    print("\n" + "=" * 60)
    print("📊 Test: Sync Standings")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        sync_service = StandingSyncService(db)
        
        # Sync Premier League
        print("\n📥 Synchronisation classement Premier League...")
        count = await sync_service.sync_standings("PL")
        print(f"   ✅ {count} entrées synchronisées\n")
        
        # Afficher le classement
        standings = sync_service.get_standings("PL")
        if standings:
            print("🏆 Classement Premier League:\n")
            for s in standings[:10]:  # Top 10
                form = s.form or "---"
                print(f"   {s.position:2}. {s.team_short or s.team_name[:12]:12} | {s.points:2} pts | {s.won}W {s.draw}D {s.lost}L | {form}")
        
        # Test is_stale
        print(f"\n   📊 Données périmées? {sync_service.is_stale('PL')}")
        
        return True
        
    finally:
        db.close()


async def test_sync_ligue1():
    """Test Ligue 1."""
    print("\n" + "=" * 60)
    print("🇫🇷 Test: Sync Ligue 1")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        sync_service = StandingSyncService(db)
        
        print("\n📥 Synchronisation classement Ligue 1...")
        count = await sync_service.sync_standings("FL1")
        print(f"   ✅ {count} entrées synchronisées\n")
        
        standings = sync_service.get_standings("FL1")
        if standings:
            print("🏆 Classement Ligue 1:\n")
            for s in standings[:5]:  # Top 5
                print(f"   {s.position:2}. {s.team_short or s.team_name[:12]:12} | {s.points:2} pts")
        
        return True
        
    finally:
        db.close()


async def main():
    print("\n🚀 TEST STANDINGS SYNC\n")
    
    if not football_data_service.api_key:
        print("❌ FOOTBALL_DATA_API_KEY manquante")
        return
    
    await test_sync_standings()
    await test_sync_ligue1()
    
    limiter = football_data_service.rate_limiter
    print("\n" + "=" * 60)
    print(f"📊 Appels API: {10 - limiter.remaining_calls}/10 cette minute")
    print("=" * 60)
    print("\n✅ Tests terminés!\n")


if __name__ == "__main__":
    asyncio.run(main())
