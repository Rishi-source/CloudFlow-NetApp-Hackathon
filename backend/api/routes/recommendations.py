from fastapi import APIRouter, Depends
from typing import List
from datetime import datetime, timedelta
from bson import ObjectId
from config.database import get_database
from middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/api/v1/recommendations", tags=["recommendations"])

cost_matrix = {"on-premise": {"hot": 0.050, "warm": 0.020, "cold": 0.010}, "aws": {"hot": 0.023, "warm": 0.0125, "cold": 0.004}, "azure": {"hot": 0.020, "warm": 0.010, "cold": 0.002}, "gcp": {"hot": 0.020, "warm": 0.010, "cold": 0.004}, "simulation": {"hot": 0.015, "warm": 0.008, "cold": 0.003}}

def calculate_cost_savings(size_bytes, current_location, current_tier, target_location, target_tier):
    size_gb = size_bytes / (1024**3)
    current_cost = size_gb * cost_matrix.get(current_location, {}).get(current_tier, 0.020)
    target_cost = size_gb * cost_matrix.get(target_location, {}).get(target_tier, 0.020)
    return round(current_cost - target_cost, 2)

@router.get("/")
async def get_user_recommendations(current_user: dict = Depends(get_current_user)):
    data_collection = get_database()["data_objects"]
    user_objects = list(data_collection.find({"user_id": current_user["sub"]}))
    recommendations = []
    for obj in user_objects:
        days_since_access = (datetime.utcnow() - obj.get("last_accessed", datetime.utcnow())).days
        current_tier = obj.get("current_tier", "warm")
        current_location = obj.get("current_location", "simulation")
        access_count = obj.get("access_count", 0)
        if days_since_access > 30 and current_tier == "hot":
            savings = calculate_cost_savings(obj["size_bytes"], current_location, "hot", current_location, "cold")
            if savings > 0:
                recommendations.append({"object_id": str(obj["_id"]), "object_name": obj["name"], "action": "tier_downgrade", "current_tier": "hot", "recommended_tier": "cold", "reason": f"Not accessed in {days_since_access} days", "savings_per_month": savings, "priority": "high"})
        elif days_since_access > 14 and current_tier == "hot":
            savings = calculate_cost_savings(obj["size_bytes"], current_location, "hot", current_location, "warm")
            if savings > 0:
                recommendations.append({"object_id": str(obj["_id"]), "object_name": obj["name"], "action": "tier_downgrade", "current_tier": "hot", "recommended_tier": "warm", "reason": f"Low access frequency ({days_since_access} days)", "savings_per_month": savings, "priority": "medium"})
        if access_count > 100 and current_tier == "cold":
            recommendations.append({"object_id": str(obj["_id"]), "object_name": obj["name"], "action": "tier_upgrade", "current_tier": "cold", "recommended_tier": "hot", "reason": f"High access frequency ({access_count} accesses)", "savings_per_month": 0, "priority": "high"})
        if current_location == "on-premise" and obj["size_bytes"] > 100000000:
            aws_savings = calculate_cost_savings(obj["size_bytes"], "on-premise", current_tier, "aws", current_tier)
            if aws_savings > 5:
                recommendations.append({"object_id": str(obj["_id"]), "object_name": obj["name"], "action": "location_change", "current_location": "on-premise", "recommended_location": "aws", "reason": "High cost on-premise for large file", "savings_per_month": aws_savings, "priority": "high"})
    recommendations.sort(key=lambda x: x.get("savings_per_month", 0), reverse=True)
    return {"recommendations": recommendations[:10], "total_potential_savings": round(sum(r.get("savings_per_month", 0) for r in recommendations), 2), "count": len(recommendations)}

@router.post("/simulate-access")
async def simulate_user_access_patterns(current_user: dict = Depends(get_current_user)):
    import random
    data_collection = get_database()["data_objects"]
    logs_collection = get_database()["access_logs"]
    user_objects = list(data_collection.find({"user_id": current_user["sub"]}))
    if not user_objects:
        return {"status": "no_data", "message": "Generate sample data first"}
    simulated_accesses = 0
    for obj in user_objects:
        access_probability = 0.7 if obj.get("current_tier") == "hot" else 0.3 if obj.get("current_tier") == "warm" else 0.1
        if random.random() < access_probability:
            access_log = {"data_object_id": str(obj["_id"]), "user_id": current_user["sub"], "access_type": random.choice(["read", "write"]), "latency_ms": random.uniform(10, 200), "location": obj.get("current_location", "simulation"), "timestamp": datetime.utcnow(), "success": True}
            logs_collection.insert_one(access_log)
            data_collection.update_one({"_id": obj["_id"]}, {"$inc": {"access_count": 1}, "$set": {"last_accessed": datetime.utcnow()}})
            simulated_accesses += 1
    return {"status": "success", "simulated_accesses": simulated_accesses, "total_objects": len(user_objects)}
