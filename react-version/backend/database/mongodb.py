import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

def get_database():
    if not MONGO_URI:
        # Fallback para desarrollo si no hay URI
        return None
    client = MongoClient(MONGO_URI)
    return client.login_logs

def get_subscriptions_collection():
    db = get_database()
    return db.suscripciones if db is not None else None

def get_logs_collection():
    db = get_database()
    return db.saas_dbvideo if db is not None else None
