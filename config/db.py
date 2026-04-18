from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

def get_db():
    try:
        uri = os.getenv("MONGO_URI")
        client = MongoClient(
            uri,
            serverSelectionTimeoutMS=5000,
            tls=True,
            tlsAllowInvalidCertificates=True
        )
        client.server_info()
        db = client["crisiscore"]
        print("MongoDB connected!")
        return db
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        return None