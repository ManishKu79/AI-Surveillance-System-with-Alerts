# update_db.py
import sqlite3

conn = sqlite3.connect("logs/surveillance.db")
try:
    conn.execute("ALTER TABLE detections ADD COLUMN alert_sent BOOLEAN DEFAULT 0")
    print("✅ Database updated successfully")
except sqlite3.OperationalError:
    print("✅ Column already exists")
conn.close()