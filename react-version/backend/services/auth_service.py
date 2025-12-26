import os
import datetime
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from google.oauth2 import id_token
from google.auth.transport import requests
from database.mongodb import get_subscriptions_collection, get_logs_collection
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-for-jwt")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 1 día
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_google_token(token: str):
    try:
        if not GOOGLE_CLIENT_ID:
            print("ERROR: GOOGLE_CLIENT_ID no configurado en .env")
            return None
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
        return idinfo
    except Exception as e:
        print(f"Error verificando token de Google: {str(e)}")
        return None

def log_login_event(email: str):
    try:
        collection = get_logs_collection()
        if collection is not None:
            collection.insert_one({
                "timestamp": datetime.datetime.utcnow(),
                "user_email": email
            })
    except Exception as e:
        print(f"Error al registrar log de login en MongoDB: {str(e)}")

def check_subscription_status(email: str) -> str:
    # 1. Verificar Admins (desde variable de entorno)
    admins = os.getenv("ADMINS", "").split(",")
    if email in [a.strip() for a in admins]:
        return "active"
    
    # 2. Verificar en MongoDB
    collection = get_subscriptions_collection()
    if collection is not None:
        suscripcion = collection.find_one({"user_email": email})
        if suscripcion and suscripcion.get("status") == "active":
            return "active"
            
    return "inactive"
