from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")
db = client["surveillance"]

log_collection = db["logs"]
tracking_collection = db["tracking"]

def save_log(name):
    log_collection.insert_one({
        "name": name,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

def get_logs():
    return list(log_collection.find({}, {"_id": 0}).sort("time", -1).limit(20))

def save_tracking(face_id, x, y):
    tracking_collection.insert_one({
        "id": face_id,
        "x": x,
        "y": y,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })