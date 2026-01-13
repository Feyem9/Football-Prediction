"""
Script d'analyse des performances SQL.
Exécute EXPLAIN sur les requêtes critiques et mesure le temps d'exécution.
"""
import sys
import os
import time
from sqlalchemy import text
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal, engine

def analyze_performance():
    print("🚀 Analyse des performances DB...")
    db = SessionLocal()
    
    queries = [
        ("Liste des matches (avec filtres)", 
         "EXPLAIN ANALYZE SELECT * FROM matches WHERE competition_code = 'PL' AND status = 'SCHEDULED' ORDER BY match_date LIMIT 20"),
        
        ("Matches avec Prédictions (JOIN)", 
         "EXPLAIN ANALYZE SELECT * FROM matches m JOIN expert_predictions p ON m.id = p.match_id LIMIT 10"),
        
        ("Recherche par ID Équipe", 
         "EXPLAIN ANALYZE SELECT * FROM matches WHERE home_team_id = 57 OR away_team_id = 57")
    ]
    
    try:
        for description, query in queries:
            print(f"\n--- {description} ---")
            start_time = time.time()
            result = db.execute(text(query))
            end_time = time.time()
            
            for row in result:
                print(row[0])
            
            print(f"⏱️ Temps d'exécution : {(end_time - start_time) * 1000:.2f}ms")
            
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse : {e}")
    finally:
        db.close()

if __name__ == "__main__":
    analyze_performance()
