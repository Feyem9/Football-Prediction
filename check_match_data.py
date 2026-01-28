import sqlite3
import json

conn = sqlite3.connect('backend/app/test.db')
cursor = conn.cursor()

match_id = 1899
cursor.execute("SELECT id, home_team, away_team FROM matches WHERE id = ?", (match_id,))
match = cursor.fetchone()
if match:
    print(f"Match {match_id} found: {match[1]} vs {match[2]}")
    cursor.execute("SELECT * FROM expert_predictions WHERE match_id = ?", (match_id,))
    pred = cursor.fetchone()
    if pred:
        print(f"Prediction found for match {match_id}")
        # Get column names for expert_predictions
        cursor.execute("PRAGMA table_info(expert_predictions);")
        cols = [c[1] for c in cursor.fetchall()]
        pred_dict = dict(zip(cols, pred))
        print(f"Prediction columns: {list(pred_dict.keys())}")
        if 'ma_logique_analysis' in pred_dict:
            print("ma_logique_analysis value:", pred_dict['ma_logique_analysis'])
        else:
            print("ma_logique_analysis column NOT found in database.")
    else:
        print(f"No prediction found for match {match_id}")
else:
    print(f"Match {match_id} NOT found in local database.")

conn.close()
