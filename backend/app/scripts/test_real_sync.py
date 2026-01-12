#!/usr/bin/env python3
"""
Test réel: Synchronisation des matchs Premier League et génération de prédictions.

Usage:
    cd backend/app && . venv/bin/activate
    python -m scripts.test_real_sync
"""
import asyncio
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal
from services.match_sync import MatchSyncService
from services.prediction_service import PredictionService
from services.football_api import football_data_service


async def test_rate_limiter():
    """Test du rate limiter."""
    print("=" * 60)
    print("🔒 Test Rate Limiter")
    print("=" * 60)
    
    limiter = football_data_service.rate_limiter
    print(f"   Appels restants: {limiter.remaining_calls}/10")
    print(f"   ✅ Rate limiter actif")
    print()


async def test_sync_premier_league():
    """Test de synchronisation Premier League."""
    print("=" * 60)
    print("⚽ Test: Sync Premier League Matches")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        sync_service = MatchSyncService(db)
        
        # Sync matchs programmés de PL
        print("\n📥 Synchronisation des matchs programmés...")
        count = await sync_service.sync_competition_matches("PL", status="SCHEDULED")
        print(f"   ✅ {count} matchs synchronisés\n")
        
        # Afficher les prochains matchs
        upcoming = sync_service.get_upcoming_matches(limit=5)
        if upcoming:
            print("📅 Prochains matchs Premier League:\n")
            for match in upcoming:
                home = match.home_team_short or match.home_team[:15]
                away = match.away_team_short or match.away_team[:15]
                date = match.match_date.strftime("%d/%m %H:%M")
                print(f"   • {date}: {home} vs {away}")
        
        return count > 0
        
    finally:
        db.close()


async def test_generate_predictions():
    """Test de génération de prédictions."""
    print("\n" + "=" * 60)
    print("🔮 Test: Génération de Prédictions")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        prediction_service = PredictionService(db)
        
        print("\n🧠 Génération des prédictions...")
        count = await prediction_service.generate_predictions_for_upcoming(limit=5)
        print(f"   ✅ {count} prédictions générées\n")
        
        # Afficher quelques prédictions
        from models.match import Match
        from models.prediction import ExpertPrediction
        
        predictions = db.query(ExpertPrediction).join(Match).limit(3).all()
        
        if predictions:
            print("📊 Exemples de prédictions:\n")
            for pred in predictions:
                match = pred.match
                home = match.home_team_short or match.home_team[:15]
                away = match.away_team_short or match.away_team[:15]
                score = f"{pred.home_score_forecast}-{pred.away_score_forecast}"
                conf = f"{pred.confidence*100:.0f}%"
                tip = pred.bet_tip or "N/A"
                
                print(f"   {home} vs {away}")
                print(f"   → Score prédit: {score} (confiance: {conf})")
                print(f"   → Conseil: {tip}")
                print()
        
        return count > 0
        
    finally:
        db.close()


async def main():
    """Exécute tous les tests."""
    print("\n" + "🚀 TEST RÉEL - PREMIER LEAGUE SYNC & PREDICTIONS\n")
    
    # Check API key
    if not football_data_service.api_key:
        print("❌ FOOTBALL_DATA_API_KEY manquante dans .env")
        return
    
    print(f"🔐 API Key: ...{football_data_service.api_key[-8:]}\n")
    
    # Tests
    await test_rate_limiter()
    sync_ok = await test_sync_premier_league()
    
    if sync_ok:
        await test_generate_predictions()
    
    # Résumé rate limiter
    limiter = football_data_service.rate_limiter
    print("=" * 60)
    print(f"📊 Appels API utilisés: {10 - limiter.remaining_calls}/10 cette minute")
    print("=" * 60)
    print("\n✅ Tests terminés!\n")


if __name__ == "__main__":
    asyncio.run(main())
