import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from config.settings import settings

class AuthService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.jwt_secret = settings.jwt_secret_key
    def create_access_token(self, user_id: str, role: str) -> str:
        payload = {"sub": user_id, "role": role, "exp": datetime.utcnow() + timedelta(hours=24)}
        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")
    def verify_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise Exception("Token expired")
        except jwt.InvalidTokenError:
            raise Exception("Invalid token")
    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)
    def create_user(self, user_id: str, password: str, role: str, db) -> dict:
        hashed_password = self.hash_password(password)
        user = {"user_id": user_id, "password": hashed_password, "role": role, "created_at": datetime.utcnow()}
        db["users"].insert_one(user)
        return {"user_id": user_id, "role": role}
    def authenticate_user(self, user_id: str, password: str, db) -> dict:
        user = db["users"].find_one({"user_id": user_id})
        if not user or not self.verify_password(password, user["password"]):
            raise Exception("Invalid credentials")
        return {"user_id": user["user_id"], "role": user["role"]}
