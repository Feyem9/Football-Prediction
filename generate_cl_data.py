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

async def generate_cl_tables():
    db = SessionLocal()
    # Fetch CL matches for tomorrow
    matches = db.query(Match).filter(
        Match.competition_code == 'CL',
        Match.match_date >= '2026-01-28',
        Match.match_date < '2026-01-29'
    ).all()
    
    print(f"Found {len(matches)} matches to process.")
    
    service = PredictionService(db)
    results = []
    
    for match in matches:
        print(f"Processing {match.home_team} vs {match.away_team}...")
        # Force delete existing prediction
        db.query(ExpertPrediction).filter_by(match_id=match.id).delete()
        db.commit()
        
        try:
            prediction = await service.generate_prediction(match)
            if prediction and prediction.ma_logique_analysis:
                analysis = json.loads(prediction.ma_logique_analysis)
                results.append({
                    'home': match.home_team,
                    'away': match.away_team,
                    'tip': prediction.ma_logique_tip,
                    'conf': int(prediction.ma_logique_confidence * 100),
                    'score': f"{prediction.ma_logique_home_score}-{prediction.ma_logique_away_score}",
                    'data': analysis
                })
        except Exception as e:
            print(f"Error for {match.home_team}: {e}")
            
    print("---JSON_START---")
    print(json.dumps(results))
    print("---JSON_END---")
    db.close()

if __name__ == "__main__":
    asyncio.run(generate_cl_tables())
