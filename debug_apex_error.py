import sys
import os
import asyncio

# Setup paths
sys.path.insert(0, os.path.join(os.getcwd(), 'backend', 'app'))

from core.database import SessionLocal
from models.match import Match
from models.prediction import ExpertPrediction
from services.prediction_service import PredictionService

async def debug_apex():
    db = SessionLocal()
    # Let's try to regenerate match 1022
    match_id = 1022
    match = db.query(Match).filter_by(id=match_id).first()
    if not match:
        print(f"Match {match_id} not found")
        return

    # DELETE existing prediction to FORCE regeneration
    existing = db.query(ExpertPrediction).filter_by(match_id=match_id).first()
    if existing:
        print(f"Deleting existing prediction for match {match_id}")
        db.delete(existing)
        db.commit()

    service = PredictionService(db)
    print(f"DEBUG: Generating prediction for match {match_id}: {match.home_team} vs {match.away_team}")
    
    try:
        prediction = await service.generate_prediction(match)
        print("Function generate_prediction finished.")
        if prediction:
            print(f"ML Analysis content: {prediction.ma_logique_analysis}")
            if prediction.ma_logique_analysis is None:
                print("WARNING: ma_logique_analysis is None. This means APEX-30 failed and fallback was used.")
        else:
            print("ERROR: generate_prediction returned None")
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        print(traceback.format_exc())
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(debug_apex())
