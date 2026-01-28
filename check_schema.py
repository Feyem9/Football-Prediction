import sqlite3
conn = sqlite3.connect('backend/app/test.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(expert_predictions);")
for row in cursor.fetchall():
    print(row)
conn.close()
