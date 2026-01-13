#!/usr/bin/env python3
"""
Test: Prédiction avec Head-to-Head (H2H).

Vérifie que l'algorithme prend en compte les confrontations historiques.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal
from models.match import Match
from services.prediction_service import PredictionService


async def test_h2h_pred():
    print("\n" + "=" * 60)
    print("🧠 Test: Prediction with H2H awareness")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # On prend le match Man Utd vs Man City (ID extern: 538001)
        match = db.query(Match).filter(Match.external_id == 538001).first()
        if not match:
            print("❌ Match non trouvé en base. Lancez une synchronisation d'abord.")
            return

        service = PredictionService(db)
        
        # Supprimer ancienne prédiction pour forcer régénération
        from models.prediction import ExpertPrediction
        db.query(ExpertPrediction).filter(ExpertPrediction.match_id == match.id).delete()
        db.commit()

        print(f"\n📥 Génération de la prédiction pour: {match.home_team} vs {match.away_team}")
        prediction = await service.generate_prediction(match)
        
        if prediction:
            print(f"\n📊 Résultat de la prédiction:")
            print(f"   ⚽ Score prédit: {prediction.home_score_forecast} - {prediction.away_score_forecast}")
            print(f"   🎯 Confiance: {prediction.confidence * 100:.1f}%")
            print(f"   💡 Tip: {prediction.bet_tip}")
            print(f"\n📝 Analyse générée:\n   {prediction.analysis}")
            
            if "H2H" in prediction.analysis:
                print("\n✅ Succès: L'analyse inclut les données H2H !")
            else:
                print("\n⚠️ Attention: L'analyse ne semble pas mentionner le H2H.")
        else:
            print("❌ Échec de la génération.")
            
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(test_h2h_pred())
