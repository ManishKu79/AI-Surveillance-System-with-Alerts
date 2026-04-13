import cv2
import sqlite3
from datetime import datetime
import os

class EvidenceRecorder:
    def __init__(self):
        os.makedirs("evidence", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        self.setup_database()
        self.last_saved = {}

    def setup_database(self):
        self.conn = sqlite3.connect("logs/surveillance.db")
        
        # Create table with all columns
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT,
                name TEXT,
                timestamp TEXT,
                image_path TEXT,
                alert_sent INTEGER DEFAULT 0
            )
        ''')
        
        # Check if alert_sent column exists, if not add it
        cursor = self.conn.execute("PRAGMA table_info(detections)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'alert_sent' not in columns:
            self.conn.execute("ALTER TABLE detections ADD COLUMN alert_sent INTEGER DEFAULT 0")
            print("✅ Added alert_sent column to database")
        
        self.conn.commit()

    def save_snapshot(self, frame, detection_type, name, alert_sent=False):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"evidence/{detection_type}_{name}_{timestamp}.jpg"
            cv2.imwrite(filename, frame)
            
            # Log to database
            self.conn.execute(
                "INSERT INTO detections (type, name, timestamp, image_path, alert_sent) VALUES (?, ?, ?, ?, ?)",
                (detection_type, name, datetime.now().isoformat(), filename, 1 if alert_sent else 0)
            )
            self.conn.commit()
            
            print(f"📸 Saved: {filename}")
            return filename
        except Exception as e:
            print(f"Error saving snapshot: {e}")
            return None
    
    def get_history(self, name=None):
        try:
            if name:
                cursor = self.conn.execute(
                    "SELECT * FROM detections WHERE name = ? ORDER BY timestamp DESC LIMIT 20",
                    (name,)
                )
            else:
                cursor = self.conn.execute(
                    "SELECT * FROM detections ORDER BY timestamp DESC LIMIT 50"
                )
            return cursor.fetchall()
        except Exception as e:
            print(f"Error getting history: {e}")
            return []
    
    def get_today_summary(self):
        try:
            today = datetime.now().date().isoformat()
            cursor = self.conn.execute(
                "SELECT type, name, COUNT(*) FROM detections WHERE date(timestamp) = ? GROUP BY type, name",
                (today,)
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"Error getting summary: {e}")
            return []