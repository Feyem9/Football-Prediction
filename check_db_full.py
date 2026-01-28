import sqlite3
import json

conn = sqlite3.connect('backend/app/test.db')
cursor = conn.cursor()

# Check table columns
cursor.execute("PRAGMA table_info(expert_predictions);")
columns = cursor.fetchall()
print("Columns in expert_predictions:")
for col in columns:
    print(col)

# Check first few rows
cursor.execute("SELECT * FROM expert_predictions LIMIT 2;")
rows = cursor.fetchall()
print("\nFirst 2 rows:")
for row in rows:
    print(row)

conn.close()
