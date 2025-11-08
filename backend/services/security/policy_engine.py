from datetime import datetime

class PolicyEngine:
    def __init__(self, db):
        self.db = db
    def evaluate_policy(self, data_object_id: str, action: str) -> bool:
        data_object = self.db["data_objects"].find_one({"_id": data_object_id})
        if not data_object:
            return False
        policy_id = data_object.get("access_policy_id")
        if not policy_id:
            return True
        policy = self.db["policies"].find_one({"policy_id": policy_id})
        if not policy or not policy.get("active"):
            return True
        if policy["rules"].get("encryption_required") and not data_object.get("encryption_enabled"):
            return False
        if data_object.get("current_location") not in policy["rules"].get("allowed_locations", []):
            return False
        age_days = (datetime.utcnow() - data_object["created_at"]).days
        if action == "delete" and age_days < policy["rules"].get("retention_days", 0):
            return False
        return True
    def enforce_compliance_rules(self):
        self._enforce_data_residency()
        self._enforce_retention_limits()
        self._enforce_encryption_requirements()
        self._audit_access_logs()
    def _enforce_data_residency(self):
        policies = list(self.db["policies"].find({"active": True}))
        for policy in policies:
            allowed_locations = policy["rules"].get("allowed_locations", [])
            violating_objects = list(self.db["data_objects"].find({
                "access_policy_id": policy["policy_id"],
                "current_location": {"$nin": allowed_locations}
            }))
            for obj in violating_objects:
                self._queue_migration(obj["_id"], allowed_locations[0])
    def _enforce_retention_limits(self):
        policies = list(self.db["policies"].find({"active": True}))
        for policy in policies:
            retention_days = policy["rules"].get("retention_days", 365)
            cutoff_date = datetime.utcnow()
            old_objects = list(self.db["data_objects"].find({
                "access_policy_id": policy["policy_id"],
                "created_at": {"$lt": cutoff_date}
            }))
            for obj in old_objects:
                age_days = (datetime.utcnow() - obj["created_at"]).days
                if age_days > retention_days:
                    self.db["data_objects"].delete_one({"_id": obj["_id"]})
    def _enforce_encryption_requirements(self):
        policies = list(self.db["policies"].find({"active": True, "rules.encryption_required": True}))
        for policy in policies:
            unencrypted_objects = list(self.db["data_objects"].find({
                "access_policy_id": policy["policy_id"],
                "encryption_enabled": {"$ne": True}
            }))
            for obj in unencrypted_objects:
                self.db["data_objects"].update_one(
                    {"_id": obj["_id"]},
                    {"$set": {"encryption_enabled": True}}
                )
    def _audit_access_logs(self):
        total_objects = self.db["data_objects"].count_documents({})
        total_logs = self.db["access_logs"].count_documents({})
        return {"total_objects": total_objects, "total_logs": total_logs}
    def _queue_migration(self, data_object_id: str, target_location: str):
        self.db["pending_migrations"].insert_one({
            "data_object_id": data_object_id,
            "target_location": target_location,
            "reason": "policy_enforcement",
            "created_at": datetime.utcnow()
        })
    def generate_compliance_report(self) -> dict:
        total_objects = self.db["data_objects"].count_documents({})
        encrypted_objects = self.db["data_objects"].count_documents({"encryption_enabled": True})
        policy_violations = self.find_policy_violations()
        return {
            "total_objects": total_objects,
            "encrypted_objects": encrypted_objects,
            "encryption_percentage": (encrypted_objects / total_objects * 100) if total_objects > 0 else 0,
            "policy_violations": len(policy_violations),
            "compliance_score": self._calculate_compliance_score(total_objects, encrypted_objects, policy_violations)
        }
    def find_policy_violations(self) -> list:
        violations = []
        policies = list(self.db["policies"].find({"active": True}))
        for policy in policies:
            objects = list(self.db["data_objects"].find({"access_policy_id": policy["policy_id"]}))
            for obj in objects:
                if not self.evaluate_policy(obj["_id"], "read"):
                    violations.append({"object_id": obj["_id"], "policy_id": policy["policy_id"]})
        return violations
    def _calculate_compliance_score(self, total: int, encrypted: int, violations: list) -> float:
        if total == 0:
            return 100.0
        encryption_score = (encrypted / total) * 50
        violation_penalty = min(50, len(violations) * 5)
        return max(0, encryption_score + (50 - violation_penalty))
