from datetime import datetime, timedelta
from typing import List, Dict
from config.settings import settings
from config.database import get_database

class BackupManager:
    def __init__(self):
        self.enabled = settings.backup_enabled
        self.interval = settings.backup_interval
        self.retention_days = settings.backup_retention_days
    async def create_backup(self, user_id: str, object_id: str, data: Dict) -> str:
        if not self.enabled:
            return ""
        backup_collection = get_database()["backups"]
        backup = {"user_id": user_id, "object_id": object_id, "data": data, "created_at": datetime.utcnow(), "expires_at": datetime.utcnow() + timedelta(days=self.retention_days)}
        result = backup_collection.insert_one(backup)
        return str(result.inserted_id)
    async def restore_backup(self, backup_id: str) -> Dict:
        if not self.enabled:
            return {}
        backup_collection = get_database()["backups"]
        from bson import ObjectId
        backup = backup_collection.find_one({"_id": ObjectId(backup_id)})
        return backup["data"] if backup else {}
    async def list_backups(self, user_id: str, object_id: str = None) -> List[Dict]:
        if not self.enabled:
            return []
        backup_collection = get_database()["backups"]
        query = {"user_id": user_id}
        if object_id:
            query["object_id"] = object_id
        backups = list(backup_collection.find(query).sort("created_at", -1).limit(50))
        for backup in backups:
            backup["_id"] = str(backup["_id"])
        return backups
    async def cleanup_expired_backups(self):
        if not self.enabled:
            return 0
        backup_collection = get_database()["backups"]
        result = backup_collection.delete_many({"expires_at": {"$lt": datetime.utcnow()}})
        return result.deleted_count

backup_manager = BackupManager()
