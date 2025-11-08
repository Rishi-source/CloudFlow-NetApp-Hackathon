import uuid
from datetime import datetime
from .email_notifier import EmailNotifier
from .alert_rules import AlertRules

class AlertManager:
    def __init__(self, db, kafka_producer):
        self.db = db
        self.kafka_producer = kafka_producer
        self.email_notifier = EmailNotifier()
        self.alert_rules = AlertRules(db)
    async def send_alert(self, alert_type: str, severity: str, message: str, recipients: list = None):
        alert = {
            "alert_id": str(uuid.uuid4()),
            "type": alert_type,
            "severity": severity,
            "message": message,
            "timestamp": datetime.utcnow(),
            "status": "active",
            "resolved": False
        }
        self.db["alerts"].insert_one(alert)
        await self.kafka_producer.send_alert_event(alert_type, severity, message)
        if severity in ["error", "critical"] and recipients:
            await self.email_notifier.send_email_alert(recipients, alert)
        return alert["alert_id"]
    async def create_alert_rule(self, rule_name: str, condition: dict, action: dict) -> str:
        return self.alert_rules.create_rule(rule_name, condition, action)
    async def evaluate_alert_rules(self):
        rules = self.alert_rules.get_active_rules()
        for rule in rules:
            if await self.alert_rules.evaluate_condition(rule["condition"]):
                await self._execute_action(rule["action"])
    async def _execute_action(self, action: dict):
        if action["type"] == "email":
            await self.send_alert(
                action["alert_type"],
                action["severity"],
                action["message"],
                action.get("recipients", [])
            )
        elif action["type"] == "auto_migrate":
            self.db["pending_migrations"].insert_one({
                "data_object_id": action["data_object_id"],
                "target_location": action["target_location"],
                "target_tier": action["target_tier"],
                "reason": "alert_triggered",
                "created_at": datetime.utcnow()
            })
    def get_active_alerts(self, limit: int = 50) -> list:
        return list(self.db["alerts"].find({"resolved": False}).sort("timestamp", -1).limit(limit))
    def resolve_alert(self, alert_id: str) -> bool:
        result = self.db["alerts"].update_one(
            {"alert_id": alert_id},
            {"$set": {"resolved": True, "resolved_at": datetime.utcnow()}}
        )
        return result.modified_count > 0
    def get_alert_statistics(self) -> dict:
        total_alerts = self.db["alerts"].count_documents({})
        active_alerts = self.db["alerts"].count_documents({"resolved": False})
        critical_alerts = self.db["alerts"].count_documents({"severity": "critical", "resolved": False})
        return {
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "critical_alerts": critical_alerts,
            "resolved_alerts": total_alerts - active_alerts
        }
