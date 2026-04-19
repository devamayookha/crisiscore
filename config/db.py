from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

def get_db():
    try:
        uri = os.getenv("MONGO_URI")
        client = MongoClient(
            uri,
            tls=True,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=5000
        )
        db = client["crisiscore"]
        return db
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        return None