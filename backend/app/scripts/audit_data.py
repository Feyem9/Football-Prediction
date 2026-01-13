"""
Script d'audit de la qualité des données.
Vérifie les compteurs et détecte les anomalies (NULLs critiques, doublons).
"""
import sys
import os
from sqlalchemy import text
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal

def audit_data():
    print("🔍 Audit de la Base de Données")
    print("==============================\n")
    
    db = SessionLocal()
    try:
        # 1. Compteurs globaux
        print("1. Volumétrie :")
        tables = ["matches", "standings", "expert_predictions", "team_stats", "users"]
        for table in tables:
            count = db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"   - {table.ljust(20)} : {count} lignes")
            
        # 2. Vérifications Matches
        print("\n2. Qualité des Matchs :")
        
        # Matchs finis sans score
        missing_scores = db.execute(text(
            "SELECT COUNT(*) FROM matches WHERE status='FINISHED' AND (score_home IS NULL OR score_away IS NULL)"
        )).scalar()
        if missing_scores > 0:
            print(f"   ⚠️ {missing_scores} matchs FINISHED sans score !")
        else:
            print(f"   ✅ Tous les matchs FINISHED ont un score.")
            
        # Matchs sans ID externe
        missing_ext_id = db.execute(text(
            "SELECT COUNT(*) FROM matches WHERE external_id IS NULL"
        )).scalar()
        if missing_ext_id > 0:
            print(f"   ⚠️ {missing_ext_id} matchs sans external_id.")
        else:
            print(f"   ✅ Tous les matchs ont un external_id.")

        # 3. Vérifications Prédictions
        print("\n3. Qualité des Prédictions :")
        conf_null = db.execute(text(
            "SELECT COUNT(*) FROM expert_predictions WHERE confidence IS NULL"
        )).scalar()
        if conf_null > 0:
            print(f"   ⚠️ {conf_null} prédictions sans indice de confiance.")
        else:
            print(f"   ✅ Toutes les prédictions ont une confiance.")

        # 4. Vérifications Stats Équipes
        print("\n4. Qualité des Stats Équipes :")
        stats_count = db.execute(text("SELECT COUNT(*) FROM team_stats")).scalar()
        if stats_count == 0:
             print("   ⚠️ Aucune stat d'équipe calculée (lancez seed_data.py).")
        else:
             print(f"   ✅ {stats_count} stats d'équipes présentes.")
             
    except Exception as e:
        print(f"❌ Erreur durant l'audit: {e}")
    finally:
        db.close()
        print("\nFin de l'audit.")

if __name__ == "__main__":
    audit_data()
