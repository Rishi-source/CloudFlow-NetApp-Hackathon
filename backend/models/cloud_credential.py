from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, Field
from bson import ObjectId

class CloudCredential(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    user_id: str
    provider: str
    display_name: str
    credentials_encrypted: str
    is_active: bool = True
    is_verified: bool = False
    last_verified: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}

class AWSCredentialCreate(BaseModel):
    display_name: str
    access_key_id: str
    secret_access_key: str
    region: str = "us-east-1"
    bucket_name: str

class AzureCredentialCreate(BaseModel):
    display_name: str
    account_name: str
    account_key: str
    container_name: str

class GCPCredentialCreate(BaseModel):
    display_name: str
    project_id: str
    bucket_name: str
    service_account_json: str

class CloudCredentialResponse(BaseModel):
    id: str
    provider: str
    display_name: str
    is_active: bool
    is_verified: bool
    last_verified: Optional[datetime]
    created_at: datetime

class CredentialTestResult(BaseModel):
    success: bool
    message: str
    details: Optional[Dict] = None
