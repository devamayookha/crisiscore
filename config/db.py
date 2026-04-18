from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

_db = None

def get_db():
    global _db
    if _db is not None:
        return _db
    try:
        uri = os.getenv("MONGO_URI")
        client = MongoClient(uri)
        _db = client["crisiscore"]
        print("MongoDB connected!")
        return _db
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        return None