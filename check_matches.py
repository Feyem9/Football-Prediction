import sqlite3
try:
    conn = sqlite3.connect('backend/app/test.db')
    cursor = conn.cursor()
    cursor.execute("SELECT m.id, m.home_team, m.away_team FROM matches m JOIN expert_predictions p ON m.id = p.match_id WHERE p.ma_logique_analysis IS NOT NULL LIMIT 5;")
    rows = cursor.fetchall()
    for row in rows:
        print(f"ID: {row[0]} | {row[1]} vs {row[2]}")
    conn.close()
except Exception as e:
    print(e)
