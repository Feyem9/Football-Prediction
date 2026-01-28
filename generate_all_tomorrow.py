import sys
import os
import asyncio
import json

# Setup paths
sys.path.insert(0, os.path.join(os.getcwd(), 'backend', 'app'))

from core.database import SessionLocal
from models.match import Match
from models.prediction import ExpertPrediction
from services.prediction_service import PredictionService

async def generate_all_predictions_tomorrow():
    db = SessionLocal()
    # Fetch ALL matches for tomorrow (2026-01-28) across ALL competitions
    target_date = '2026-01-28'
    matches = db.query(Match).filter(
        Match.match_date >= target_date,
        Match.match_date < '2026-01-29'
    ).all()
    
    print(f"Found {len(matches)} matches to process for {target_date}.")
    
    service = PredictionService(db)
    count = 0
    
    for match in matches:
        print(f"[{match.competition_code}] Processing {match.home_team} vs {match.away_team}...")
        # Force delete existing prediction to trigger APEX-30 regeneration
        db.query(ExpertPrediction).filter_by(match_id=match.id).delete()
        db.commit()
        
        try:
            prediction = await service.generate_prediction(match)
            if prediction and prediction.ma_logique_analysis:
                count += 1
                print(f"  ✅ SUCCESS: APEX-30 analysis generated for {match.home_team}")
            else:
                print(f"  ⚠️ WARNING: Prediction generated but NO APEX-30 analysis for {match.home_team}")
        except Exception as e:
            print(f"  ❌ ERROR for {match.home_team} vs {match.away_team}: {e}")
            
    print(f"\nFINISH: {count} matches regenerated with APEX-30 analysis.")
    db.close()

if __name__ == "__main__":
    asyncio.run(generate_all_predictions_tomorrow())
