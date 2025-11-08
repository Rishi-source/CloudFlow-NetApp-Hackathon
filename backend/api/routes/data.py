from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from config.database import get_database
from middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/api/v1/data", tags=["data"])

def get_data_collection():
    return get_database()["data_objects"]

@router.get("/", response_model=List[dict])
async def list_user_data_objects(tier: Optional[str] = None, location: Optional[str] = None, limit: int = 100, current_user: dict = Depends(get_current_user)):
    collection = get_data_collection()
    query = {"user_id": current_user["sub"]}
    if tier:
        query["current_tier"] = tier
    if location:
        query["current_location"] = location
    data_list = list(collection.find(query).limit(limit))
    for item in data_list:
        if "_id" in item:
            item["_id"] = str(item["_id"])
    return data_list

@router.get("/{object_id}")
async def get_user_data_object(object_id: str, current_user: dict = Depends(get_current_user)):
    collection = get_data_collection()
    data = collection.find_one({"_id": ObjectId(object_id), "user_id": current_user["sub"]})
    if not data:
        raise HTTPException(status_code=404, detail="Data object not found")
    data["_id"] = str(data["_id"])
    return data

@router.delete("/{object_id}")
async def delete_user_data_object(object_id: str, current_user: dict = Depends(get_current_user)):
    collection = get_data_collection()
    result = collection.delete_one({"_id": ObjectId(object_id), "user_id": current_user["sub"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Data object not found")
    return {"status": "deleted", "object_id": object_id}

@router.post("/{object_id}/access")
async def log_user_access(object_id: str, access_type: str, latency_ms: float, location: str, current_user: dict = Depends(get_current_user)):
    collection = get_data_collection()
    logs_collection = get_database()["access_logs"]
    data = collection.find_one({"_id": ObjectId(object_id), "user_id": current_user["sub"]})
    if not data:
        raise HTTPException(status_code=404, detail="Data object not found")
    access_log = {"data_object_id": object_id, "user_id": current_user["sub"], "access_type": access_type, "latency_ms": latency_ms, "location": location, "timestamp": datetime.utcnow()}
    logs_collection.insert_one(access_log)
    collection.update_one({"_id": ObjectId(object_id)}, {"$inc": {"access_count": 1}, "$set": {"last_accessed": datetime.utcnow()}})
    return {"status": "logged", "object_id": object_id}

@router.get("/{object_id}/history")
async def get_user_access_history(object_id: str, limit: int = 50, current_user: dict = Depends(get_current_user)):
    logs_collection = get_database()["access_logs"]
    logs = list(logs_collection.find({"data_object_id": object_id, "user_id": current_user["sub"]}).sort("timestamp", -1).limit(limit))
    for log in logs:
        log["_id"] = str(log["_id"])
    return {"object_id": object_id, "logs": logs, "count": len(logs)}

@router.post("/generate-sample")
async def generate_sample_user_data(count: int = 10, current_user: dict = Depends(get_current_user)):
    import random
    collection = get_data_collection()
    tiers = ["hot", "warm", "cold"]
    locations = ["aws", "azure", "gcp", "on-premise"]
    sample_data = []
    for i in range(count):
        size_bytes = random.randint(1000000, 500000000)
        obj = {"user_id": current_user["sub"], "name": f"sample_file_{i+1}.pdf", "size_bytes": size_bytes, "current_tier": random.choice(tiers), "current_location": random.choice(locations), "is_real": False, "cloud_url": None, "access_count": random.randint(0, 100), "last_accessed": datetime.utcnow(), "created_at": datetime.utcnow(), "updated_at": datetime.utcnow(), "metadata": {"file_type": "pdf", "owner": current_user["email"], "tags": ["sample"], "description": "Sample data for demo"}, "checksum": f"sha256:sample_{i}", "encryption_enabled": False, "access_policy_id": None, "predicted_tier": None, "cost_per_month": round(size_bytes / 1073741824 * 0.023, 2)}
        result = collection.insert_one(obj)
        sample_data.append(str(result.inserted_id))
    return {"status": "success", "generated_count": count, "object_ids": sample_data}
