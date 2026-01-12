#!/usr/bin/env python3
"""
Script de test pour l'API Football-Data.org.

Usage:
    1. Crée un compte sur https://www.football-data.org/client/register
    2. Ajoute ta clé API dans .env: FOOTBALL_DATA_API_KEY=ta_cle_ici
    3. Lance: python -m scripts.test_football_api
"""
import asyncio
import os
import sys

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.football_api import football_data_service, FootballDataService


async def test_competitions():
    """Test de l'endpoint /competitions."""
    print("=" * 60)
    print("🏆 Test: GET /competitions")
    print("=" * 60)
    
    try:
        result = await football_data_service.get_competitions()
        competitions = result.get("competitions", [])
        
        print(f"\n✅ {len(competitions)} compétitions trouvées\n")
        
        # Afficher les compétitions Tier 1 (plan gratuit)
        print("📋 Compétitions disponibles (Plan Gratuit):\n")
        tier_one_codes = list(FootballDataService.TIER_ONE_COMPETITIONS.keys())
        
        for comp in competitions:
            code = comp.get("code", "")
            if code in tier_one_codes:
                name = comp.get("name", "")
                area = comp.get("area", {}).get("name", "")
                print(f"  • {code}: {name} ({area})")
        
        return True
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        return False


async def test_premier_league_matches():
    """Test de récupération des matchs de Premier League."""
    print("\n" + "=" * 60)
    print("⚽ Test: GET /competitions/PL/matches")
    print("=" * 60)
    
    try:
        result = await football_data_service.get_competition_matches("PL", status="SCHEDULED")
        matches = result.get("matches", [])
        
        print(f"\n✅ {len(matches)} matchs programmés en Premier League\n")
        
        # Afficher les 5 prochains matchs
        print("📅 Prochains matchs:\n")
        for match in matches[:5]:
            home = match.get("homeTeam", {}).get("shortName", "?")
            away = match.get("awayTeam", {}).get("shortName", "?")
            date = match.get("utcDate", "?")[:10]
            print(f"  • {date}: {home} vs {away}")
        
        return True
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        return False


async def test_standings():
    """Test de récupération du classement Ligue 1."""
    print("\n" + "=" * 60)
    print("📊 Test: GET /competitions/FL1/standings")
    print("=" * 60)
    
    try:
        result = await football_data_service.get_standings("FL1")
        standings = result.get("standings", [])
        
        if standings:
            table = standings[0].get("table", [])
            print(f"\n✅ Classement Ligue 1 ({len(table)} équipes)\n")
            
            # Top 5
            print("🥇 Top 5:\n")
            for team in table[:5]:
                pos = team.get("position")
                name = team.get("team", {}).get("shortName", "?")
                pts = team.get("points")
                print(f"  {pos}. {name} - {pts} pts")
        
        return True
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        return False


async def main():
    """Exécute tous les tests."""
    print("\n🔐 API Key configurée:", "✅ Oui" if football_data_service.api_key else "❌ Non")
    
    if not football_data_service.api_key:
        print("\n⚠️  ATTENTION: Ajoute ta clé API dans .env")
        print("   FOOTBALL_DATA_API_KEY=ta_cle_ici")
        print("\n   Pour obtenir une clé: https://www.football-data.org/client/register")
        return
    
    print("\n")
    
    # Tests
    await test_competitions()
    await test_premier_league_matches()
    await test_standings()
    
    print("\n" + "=" * 60)
    print("✅ Tests terminés!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
