from datetime import datetime
from typing import Dict, Any
from config.settings import settings
from config.database import get_database

class ConflictResolver:
    def __init__(self):
        self.strategy = settings.conflict_resolution_strategy
    async def resolve_conflict(self, job_id: str, local_data: Dict[str, Any], remote_data: Dict[str, Any]) -> Dict[str, Any]:
        if self.strategy == "last_write_wins":
            return await self.last_write_wins(job_id, local_data, remote_data)
        elif self.strategy == "first_write_wins":
            return await self.first_write_wins(job_id, local_data, remote_data)
        elif self.strategy == "merge":
            return await self.merge_data(job_id, local_data, remote_data)
        return local_data
    async def last_write_wins(self, job_id: str, local_data: Dict[str, Any], remote_data: Dict[str, Any]) -> Dict[str, Any]:
        local_timestamp = local_data.get("updated_at", datetime.min)
        remote_timestamp = remote_data.get("updated_at", datetime.min)
        winner = local_data if local_timestamp > remote_timestamp else remote_data
        await self.log_conflict_resolution(job_id, "last_write_wins", winner == local_data)
        return winner
    async def first_write_wins(self, job_id: str, local_data: Dict[str, Any], remote_data: Dict[str, Any]) -> Dict[str, Any]:
        local_timestamp = local_data.get("created_at", datetime.max)
        remote_timestamp = remote_data.get("created_at", datetime.max)
        winner = local_data if local_timestamp < remote_timestamp else remote_data
        await self.log_conflict_resolution(job_id, "first_write_wins", winner == local_data)
        return winner
    async def merge_data(self, job_id: str, local_data: Dict[str, Any], remote_data: Dict[str, Any]) -> Dict[str, Any]:
        merged = {**remote_data, **local_data}
        await self.log_conflict_resolution(job_id, "merge", True)
        return merged
    async def log_conflict_resolution(self, job_id: str, strategy: str, local_won: bool):
        conflict_collection = get_database()["conflict_logs"]
        conflict_collection.insert_one({"job_id": job_id, "strategy": strategy, "local_won": local_won, "timestamp": datetime.utcnow()})
        print(f"Conflict resolved for job {job_id} using {strategy}, local_won={local_won}")
    async def check_for_conflicts(self, object_id: str, current_version: int) -> bool:
        data_collection = get_database()["data_objects"]
        from bson import ObjectId
        remote_obj = data_collection.find_one({"_id": ObjectId(object_id)})
        if remote_obj and remote_obj.get("version", 0) > current_version:
            return True
        return False

conflict_resolver = ConflictResolver()
