from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

def get_db():
    try:
        uri = os.getenv("MONGO_URI")
        client = MongoClient(
            uri,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
            tls=True,
            tlsAllowInvalidCertificates=True,
            retryWrites=True
        )
        db = client["crisiscore"]
        db.command("ping")
        print("MongoDB connected!")
        return db
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        return None