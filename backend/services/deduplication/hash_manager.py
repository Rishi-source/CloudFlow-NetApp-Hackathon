import hashlib
from typing import Optional
from config.settings import settings
from config.database import get_database
from datetime import datetime

class HashManager:
    def __init__(self):
        self.enabled = settings.deduplication_enabled
    def calculate_hash(self, file_content: bytes) -> str:
        return hashlib.sha256(file_content).hexdigest()
    async def check_duplicate(self, file_hash: str, user_id: str) -> Optional[dict]:
        if not self.enabled:
            return None
        hash_collection = get_database()["file_hashes"]
        existing = hash_collection.find_one({"hash": file_hash, "user_id": user_id})
        return existing
    async def store_hash(self, file_hash: str, user_id: str, object_id: str, file_size: int):
        if not self.enabled:
            return
        hash_collection = get_database()["file_hashes"]
        hash_collection.insert_one({"hash": file_hash, "user_id": user_id, "object_id": object_id, "file_size": file_size, "created_at": datetime.utcnow()})
    async def get_storage_savings(self, user_id: str) -> dict:
        if not self.enabled:
            return {"duplicates_found": 0, "space_saved_bytes": 0, "space_saved_gb": 0.0}
        hash_collection = get_database()["file_hashes"]
        pipeline = [{"$match": {"user_id": user_id}}, {"$group": {"_id": "$hash", "count": {"$sum": 1}, "size": {"$first": "$file_size"}}}, {"$match": {"count": {"$gt": 1}}}]
        duplicates = list(hash_collection.aggregate(pipeline))
        total_saved = sum(d["size"] * (d["count"] - 1) for d in duplicates)
        return {"duplicates_found": len(duplicates), "space_saved_bytes": total_saved, "space_saved_gb": round(total_saved / (1024 ** 3), 2)}

hash_manager = HashManager()
