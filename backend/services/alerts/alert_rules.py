import uuid
from datetime import datetime

class AlertRules:
    def __init__(self, db):
        self.db = db
    def create_rule(self, rule_name: str, condition: dict, action: dict) -> str:
        rule = {
            "rule_id": str(uuid.uuid4()),
            "name": rule_name,
            "condition": condition,
            "action": action,
            "enabled": True,
            "created_at": datetime.utcnow()
        }
        self.db["alert_rules"].insert_one(rule)
        return rule["rule_id"]
    def get_active_rules(self) -> list:
        return list(self.db["alert_rules"].find({"enabled": True}))
    async def evaluate_condition(self, condition: dict) -> bool:
        metric_value = await self._get_metric_value(condition["metric"])
        operator = condition["operator"]
        threshold = condition["threshold"]
        operators = {
            '>': lambda x, y: x > y,
            '<': lambda x, y: x < y,
            '>=': lambda x, y: x >= y,
            '<=': lambda x, y: x <= y,
            '==': lambda x, y: x == y
        }
        return operators[operator](metric_value, threshold)
    async def _get_metric_value(self, metric_name: str) -> float:
        if metric_name == "monthly_cost":
            pipeline = [{"$group": {"_id": None, "total": {"$sum": "$cost_per_month"}}}]
            result = list(self.db["data_objects"].aggregate(pipeline))
            return result[0]["total"] if result else 0.0
        elif metric_name == "avg_latency_ms":
            pipeline = [{"$group": {"_id": None, "avg": {"$avg": "$latency_ms"}}}]
            result = list(self.db["access_logs"].aggregate(pipeline))
            return result[0]["avg"] if result else 0.0
        elif metric_name == "storage_utilization":
            pipeline = [{"$group": {"_id": None, "total": {"$sum": "$size_bytes"}}}]
            result = list(self.db["data_objects"].aggregate(pipeline))
            return result[0]["total"] / (1024**3) if result else 0.0
        elif metric_name == "failed_migrations":
            return self.db["migration_jobs"].count_documents({"status": "failed"})
        return 0.0
    def disable_rule(self, rule_id: str) -> bool:
        result = self.db["alert_rules"].update_one(
            {"rule_id": rule_id},
            {"$set": {"enabled": False}}
        )
        return result.modified_count > 0
    def enable_rule(self, rule_id: str) -> bool:
        result = self.db["alert_rules"].update_one(
            {"rule_id": rule_id},
            {"$set": {"enabled": True}}
        )
        return result.modified_count > 0
    def delete_rule(self, rule_id: str) -> bool:
        result = self.db["alert_rules"].delete_one({"rule_id": rule_id})
        return result.deleted_count > 0
