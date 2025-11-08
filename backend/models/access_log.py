from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId

class AccessLog(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    log_id: str = Field(default_factory=lambda: str(ObjectId()))
    data_object_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    access_type: str
    latency_ms: float
    user_id: Optional[str] = "anonymous"
    ip_address: str = "0.0.0.0"
    success: bool = True
    bytes_transferred: int = 0
    location: str
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}

class AccessLogCreate(BaseModel):
    data_object_id: str
    access_type: str
    latency_ms: float
    location: str
    user_id: Optional[str] = "anonymous"
    success: bool = True
    bytes_transferred: int = 0
