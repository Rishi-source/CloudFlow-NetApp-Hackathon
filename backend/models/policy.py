from pydantic import BaseModel, Field
from typing import Dict, List
from datetime import datetime
from bson import ObjectId

class PolicyRules(BaseModel):
    max_cost_per_gb: float
    min_access_frequency: int
    required_latency_ms: float
    encryption_required: bool
    retention_days: int
    auto_tier: bool
    allowed_locations: List[str]

class AlertThresholds(BaseModel):
    cost_threshold: float
    latency_threshold: float
    access_threshold: int

class StoragePolicy(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    policy_id: str = Field(default_factory=lambda: str(ObjectId()))
    name: str
    description: str = ""
    rules: PolicyRules
    alert_thresholds: AlertThresholds
    created_by: str = "admin"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    active: bool = True
    priority: int = 5
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}

class PolicyCreate(BaseModel):
    name: str
    description: str = ""
    rules: PolicyRules
    alert_thresholds: AlertThresholds
    priority: int = 5

class PolicyUpdate(BaseModel):
    name: str = None
    description: str = None
    rules: PolicyRules = None
    alert_thresholds: AlertThresholds = None
    active: bool = None
    priority: int = None
