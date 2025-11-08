from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

class DataObjectMetadata(BaseModel):
    file_type: str
    owner: str
    tags: List[str] = []
    description: str = ""

class DataObject(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    name: str
    size_bytes: int
    current_tier: str
    current_location: str
    access_count: int = 0
    last_accessed: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: DataObjectMetadata
    checksum: str
    encryption_enabled: bool = False
    access_policy_id: Optional[str] = None
    predicted_tier: Optional[str] = None
    cost_per_month: float = 0.0
    url: str = ""
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}

class DataObjectCreate(BaseModel):
    name: str
    size_bytes: int
    current_tier: str = "warm"
    current_location: str = "on-premise"
    metadata: DataObjectMetadata
    checksum: str = ""

class DataObjectUpdate(BaseModel):
    current_tier: Optional[str] = None
    current_location: Optional[str] = None
    access_count: Optional[int] = None
    last_accessed: Optional[datetime] = None
    predicted_tier: Optional[str] = None
    cost_per_month: Optional[float] = None
    url: Optional[str] = None
