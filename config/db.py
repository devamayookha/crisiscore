from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

load_dotenv()

def get_db():
    try:
        uri = os.getenv("MONGO_URI")
        client = MongoClient(uri, server_api=ServerApi('1'))
        client.admin.command('ping')
        db = client["crisiscore"]
        print("MongoDB connected!")
        return db
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        return None