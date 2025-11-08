from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from config.settings import settings

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return password_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)

def create_access_token(user_id: str, email: str, role: str) -> str:
    expiration = datetime.utcnow() + timedelta(minutes=settings.jwt_expiration_minutes)
    payload = {"sub": user_id, "email": email, "role": role, "exp": expiration, "iat": datetime.utcnow()}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload if payload.get("exp") and datetime.fromtimestamp(payload["exp"]) > datetime.utcnow() else None
    except jwt.InvalidTokenError:
        return None
