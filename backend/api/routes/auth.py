from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime
from config.database import get_database
from models.user import UserCreate, UserLogin, UserResponse, TokenResponse
from utils.jwt_handler import hash_password, verify_password, create_access_token
from middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    users_collection = get_database()["users"]
    existing_user = users_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user_document = {
        "email": user_data.email,
        "password_hash": hash_password(user_data.password),
        "full_name": user_data.full_name,
        "role": "user",
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    result = users_collection.insert_one(user_document)
    user_id = str(result.inserted_id)
    access_token = create_access_token(user_id, user_data.email, "user")
    user_response = UserResponse(id=user_id, email=user_data.email, full_name=user_data.full_name, role="user", is_active=True, created_at=user_document["created_at"])
    return TokenResponse(access_token=access_token, user=user_response)

@router.post("/login", response_model=TokenResponse)
async def login_user(credentials: UserLogin):
    users_collection = get_database()["users"]
    user = users_collection.find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not user.get("is_active", True):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")
    user_id = str(user["_id"])
    access_token = create_access_token(user_id, user["email"], user["role"])
    user_response = UserResponse(id=user_id, email=user["email"], full_name=user["full_name"], role=user["role"], is_active=user["is_active"], created_at=user["created_at"])
    return TokenResponse(access_token=access_token, user=user_response)

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    users_collection = get_database()["users"]
    from bson import ObjectId
    user = users_collection.find_one({"_id": ObjectId(current_user["sub"])})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse(id=str(user["_id"]), email=user["email"], full_name=user["full_name"], role=user["role"], is_active=user["is_active"], created_at=user["created_at"])

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(full_name: str, current_user: dict = Depends(get_current_user)):
    users_collection = get_database()["users"]
    from bson import ObjectId
    users_collection.update_one({"_id": ObjectId(current_user["sub"])}, {"$set": {"full_name": full_name, "updated_at": datetime.utcnow()}})
    user = users_collection.find_one({"_id": ObjectId(current_user["sub"])})
    return UserResponse(id=str(user["_id"]), email=user["email"], full_name=user["full_name"], role=user["role"], is_active=user["is_active"], created_at=user["created_at"])
