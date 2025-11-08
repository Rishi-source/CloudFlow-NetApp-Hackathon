from fastapi import APIRouter, Depends
from typing import Dict, List
from datetime import datetime, timedelta
from config.database import get_database
from middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

cost_matrix = {"on-premise": {"hot": 0.050, "warm": 0.020, "cold": 0.010}, "aws": {"hot": 0.023, "warm": 0.0125, "cold": 0.004}, "azure": {"hot": 0.020, "warm": 0.010, "cold": 0.002}, "gcp": {"hot": 0.020, "warm": 0.010, "cold": 0.004}, "simulation": {"hot": 0.015, "warm": 0.008, "cold": 0.003}}

@router.get("/distribution")
async def get_user_data_distribution(current_user: dict = Depends(get_current_user)):
    collection = get_database()["data_objects"]
    user_objects = list(collection.find({"user_id": current_user["sub"]}))
    tier_counts = {"hot": 0, "warm": 0, "cold": 0}
    location_counts = {}
    total_size = 0
    for obj in user_objects:
        tier = obj.get("current_tier", "warm")
        location = obj.get("current_location", "on-premise")
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
        location_counts[location] = location_counts.get(location, 0) + 1
        total_size += obj.get("size_bytes", 0)
    return {"by_tier": tier_counts, "by_location": location_counts, "total_objects": len(user_objects), "total_size_gb": round(total_size / (1024**3), 2)}

@router.get("/costs")
async def get_user_cost_breakdown(current_user: dict = Depends(get_current_user)):
    collection = get_database()["data_objects"]
    user_objects = list(collection.find({"user_id": current_user["sub"]}))
    total_cost = 0.0
    cost_by_location = {}
    cost_by_tier = {"hot": 0.0, "warm": 0.0, "cold": 0.0}
    for obj in user_objects:
        location = obj.get("current_location", "on-premise")
        tier = obj.get("current_tier", "warm")
        size_gb = obj.get("size_bytes", 0) / (1024**3)
        cost_per_gb = cost_matrix.get(location, {}).get(tier, 0.020)
        obj_cost = size_gb * cost_per_gb
        total_cost += obj_cost
        cost_by_location[location] = cost_by_location.get(location, 0.0) + obj_cost
        cost_by_tier[tier] += obj_cost
    return {"current_month": round(total_cost, 2), "projected": round(total_cost * 1.1, 2), "by_location": {k: round(v, 2) for k, v in cost_by_location.items()}, "by_tier": {k: round(v, 2) for k, v in cost_by_tier.items()}, "currency": "USD"}

@router.get("/performance")
async def get_user_performance_metrics(current_user: dict = Depends(get_current_user)):
    logs_collection = get_database()["access_logs"]
    recent_logs = list(logs_collection.find({"user_id": current_user["sub"]}).sort("timestamp", -1).limit(1000))
    if not recent_logs:
        return {"avg_latency_ms": 0, "success_rate": 100, "total_accesses": 0}
    total_latency = sum(log.get("latency_ms", 0) for log in recent_logs)
    successful = sum(1 for log in recent_logs if log.get("success", True))
    return {"avg_latency_ms": round(total_latency / len(recent_logs), 2) if recent_logs else 0, "success_rate": round((successful / len(recent_logs)) * 100, 2) if recent_logs else 100, "total_accesses": len(recent_logs), "period": "last_1000_accesses"}

@router.get("/summary")
async def get_user_dashboard_summary(current_user: dict = Depends(get_current_user)):
    distribution = await get_user_data_distribution(current_user)
    costs = await get_user_cost_breakdown(current_user)
    performance = await get_user_performance_metrics(current_user)
    migration_collection = get_database()["migration_jobs"]
    active_migrations = list(migration_collection.find({"user_id": current_user["sub"], "status": {"$in": ["pending", "in_progress"]}}))
    return {"distribution": distribution, "costs": costs, "performance": performance, "active_migrations_count": len(active_migrations), "timestamp": datetime.utcnow().isoformat()}
