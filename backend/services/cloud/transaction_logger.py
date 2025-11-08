from datetime import datetime
from typing import Dict, Any
from config.settings import settings
from config.database import get_database

class TransactionLogger:
    def __init__(self):
        self.enabled = settings.transaction_log_enabled
    async def log_transaction_start(self, job_id: str, operation: str, metadata: Dict[str, Any]) -> str:
        if not self.enabled:
            return ""
        transaction_collection = get_database()["transaction_logs"]
        transaction = {"job_id": job_id, "operation": operation, "metadata": metadata, "status": "started", "start_time": datetime.utcnow(), "end_time": None, "error": None}
        result = transaction_collection.insert_one(transaction)
        transaction_id = str(result.inserted_id)
        print(f"Transaction started: {transaction_id} for job {job_id}")
        return transaction_id
    async def log_transaction_complete(self, transaction_id: str):
        if not self.enabled or not transaction_id:
            return
        transaction_collection = get_database()["transaction_logs"]
        from bson import ObjectId
        transaction_collection.update_one({"_id": ObjectId(transaction_id)}, {"$set": {"status": "completed", "end_time": datetime.utcnow()}})
        print(f"Transaction completed: {transaction_id}")
    async def log_transaction_rollback(self, transaction_id: str, error: str):
        if not self.enabled or not transaction_id:
            return
        transaction_collection = get_database()["transaction_logs"]
        from bson import ObjectId
        transaction_collection.update_one({"_id": ObjectId(transaction_id)}, {"$set": {"status": "rolled_back", "end_time": datetime.utcnow(), "error": error}})
        print(f"Transaction rolled back: {transaction_id}, error: {error}")
    async def log_transaction_failed(self, transaction_id: str, error: str):
        if not self.enabled or not transaction_id:
            return
        transaction_collection = get_database()["transaction_logs"]
        from bson import ObjectId
        transaction_collection.update_one({"_id": ObjectId(transaction_id)}, {"$set": {"status": "failed", "end_time": datetime.utcnow(), "error": error}})
        print(f"Transaction failed: {transaction_id}, error: {error}")
    async def get_transaction_history(self, job_id: str) -> list:
        if not self.enabled:
            return []
        transaction_collection = get_database()["transaction_logs"]
        transactions = list(transaction_collection.find({"job_id": job_id}).sort("start_time", -1))
        for transaction in transactions:
            transaction["_id"] = str(transaction["_id"])
        return transactions
    async def rollback_transaction(self, transaction_id: str) -> bool:
        if not self.enabled:
            return False
        transaction_collection = get_database()["transaction_logs"]
        from bson import ObjectId
        transaction = transaction_collection.find_one({"_id": ObjectId(transaction_id)})
        if not transaction or transaction["status"] != "started":
            return False
        await self.log_transaction_rollback(transaction_id, "Manual rollback")
        return True

transaction_logger = TransactionLogger()
