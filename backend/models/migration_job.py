from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime
from bson import ObjectId

class MigrationJob(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    job_id: str = Field(default_factory=lambda: str(ObjectId()))
    data_object_id: str
    source_location: str
    source_tier: str
    target_location: str
    target_tier: str
    status: str = "pending"
    priority: int = 5
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    bytes_transferred: int = 0
    total_bytes: int = 0
    progress_percentage: float = 0.0
    estimated_completion: Optional[datetime] = None
    error_message: str = ""
    retry_count: int = 0
    rollback_available: bool = True
    created_by: str = "system"
    metadata: Dict = Field(default_factory=dict)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}

class MigrationJobCreate(BaseModel):
    data_object_id: str
    target_location: str
    target_tier: str
    priority: int = 5

class MigrationJobUpdate(BaseModel):
    status: Optional[str] = None
    bytes_transferred: Optional[int] = None
    progress_percentage: Optional[float] = None
    error_message: Optional[str] = None
    estimated_completion: Optional[datetime] = None
