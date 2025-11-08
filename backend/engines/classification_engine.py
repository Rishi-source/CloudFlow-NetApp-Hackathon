from datetime import datetime, timedelta
from typing import Dict, Tuple
import logging

class DataClassificationEngine:
    def __init__(self, db):
        self.db = db
        self.tier_thresholds = {
            "hot": {"min_access_per_day": 10, "max_latency_ms": 50},
            "warm": {"min_access_per_day": 1, "max_latency_ms": 200},
            "cold": {"min_access_per_day": 0, "max_latency_ms": 1000}
        }
        self.location_costs = {
            "on-premise": {"hot": 0.050, "warm": 0.020, "cold": 0.010},
            "aws": {"hot": 0.023, "warm": 0.0125, "cold": 0.004},
            "azure": {"hot": 0.020, "warm": 0.010, "cold": 0.002},
            "gcp": {"hot": 0.020, "warm": 0.010, "cold": 0.004}
        }
        self.location_latency = {
            "on-premise": {"hot": 10, "warm": 20, "cold": 50},
            "aws": {"hot": 30, "warm": 100, "cold": 500},
            "azure": {"hot": 35, "warm": 120, "cold": 600},
            "gcp": {"hot": 32, "warm": 110, "cold": 550}
        }
    
    def classify_data_object(self, object_id: str) -> Tuple[str, str]:
        data_obj = self.db["data_objects"].find_one({"_id": object_id})
        if not data_obj:
            raise ValueError(f"Data object {object_id} not found")
        access_logs = list(self.db["access_logs"].find(
            {"data_object_id": object_id}
        ).sort("timestamp", -1).limit(100))
        if not access_logs:
            return "warm", "on-premise"
        recent_period = datetime.utcnow() - timedelta(days=7)
        recent_accesses = [log for log in access_logs if log["timestamp"] >= recent_period]
        access_per_day = len(recent_accesses) / 7.0
        avg_latency = sum(log.get("latency_ms", 100) for log in recent_accesses) / max(len(recent_accesses), 1)
        size_gb = data_obj.get("size_bytes", 0) / (1024**3)
        if access_per_day >= self.tier_thresholds["hot"]["min_access_per_day"]:
            tier = "hot"
        elif access_per_day >= self.tier_thresholds["warm"]["min_access_per_day"]:
            tier = "warm"
        else:
            tier = "cold"
        best_location = self._find_optimal_location(tier, size_gb, avg_latency)
        return tier, best_location
    
    def _find_optimal_location(self, tier: str, size_gb: float, required_latency: float) -> str:
        location_scores = {}
        for location in self.location_costs.keys():
            cost = self.location_costs[location][tier] * size_gb
            latency = self.location_latency[location][tier]
            if latency > required_latency * 2:
                continue
            latency_score = 100 - (latency / required_latency * 50)
            cost_score = 100 - (cost * 10)
            location_scores[location] = (latency_score * 0.6 + cost_score * 0.4)
        if not location_scores:
            return "on-premise"
        return max(location_scores.items(), key=lambda x: x[1])[0]
    
    def batch_classify(self, limit: int = 50) -> Dict:
        objects = list(self.db["data_objects"].find().limit(limit))
        results = {"reclassified": 0, "unchanged": 0, "errors": 0}
        for obj in objects:
            try:
                new_tier, new_location = self.classify_data_object(obj["_id"])
                if new_tier != obj["current_tier"] or new_location != obj["current_location"]:
                    self.db["data_objects"].update_one(
                        {"_id": obj["_id"]},
                        {"$set": {"predicted_tier": new_tier, "updated_at": datetime.utcnow()}}
                    )
                    results["reclassified"] += 1
                else:
                    results["unchanged"] += 1
            except Exception as e:
                logging.error(f"Classification error for {obj['_id']}: {str(e)}")
                results["errors"] += 1
        return results
    
    def analyze_optimization_opportunities(self) -> Dict:
        objects = list(self.db["data_objects"].find())
        opportunities = []
        total_potential_savings = 0.0
        for obj in objects:
            try:
                new_tier, new_location = self.classify_data_object(obj["_id"])
                current_cost = self._calculate_cost(
                    obj["current_location"], obj["current_tier"], obj["size_bytes"]
                )
                proposed_cost = self._calculate_cost(new_location, new_tier, obj["size_bytes"])
                if proposed_cost < current_cost * 0.8:
                    savings = current_cost - proposed_cost
                    opportunities.append({
                        "object_id": obj["_id"],
                        "name": obj["name"],
                        "current": f"{obj['current_location']}/{obj['current_tier']}",
                        "proposed": f"{new_location}/{new_tier}",
                        "monthly_savings": round(savings, 2)
                    })
                    total_potential_savings += savings
            except Exception as e:
                logging.error(f"Analysis error for {obj.get('_id', 'unknown')}: {str(e)}")
        return {
            "opportunities": sorted(opportunities, key=lambda x: x["monthly_savings"], reverse=True)[:20],
            "total_potential_savings": round(total_potential_savings, 2),
            "count": len(opportunities)
        }
    
    def _calculate_cost(self, location: str, tier: str, size_bytes: int) -> float:
        size_gb = size_bytes / (1024**3)
        cost_per_gb = self.location_costs.get(location, {}).get(tier, 0.020)
        return size_gb * cost_per_gb
