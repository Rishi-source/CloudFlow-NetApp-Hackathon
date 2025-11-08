import asyncio
from typing import Callable, Any, Optional
from datetime import datetime
from config.settings import settings
from config.database import get_database

class RetryManager:
    def __init__(self):
        self.max_retries = settings.migration_max_retries
        self.base_delay = settings.migration_retry_delay
        self.multiplier = settings.migration_retry_multiplier
    async def execute_with_retry(self, operation: Callable, job_id: str, *args, **kwargs) -> tuple[bool, Optional[Exception]]:
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                await operation(*args, **kwargs)
                if attempt > 0:
                    await self.log_retry_success(job_id, attempt + 1)
                return True, None
            except Exception as error:
                last_exception = error
                await self.log_retry_attempt(job_id, attempt + 1, str(error))
                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (self.multiplier ** attempt)
                    await asyncio.sleep(delay)
                else:
                    await self.log_retry_failure(job_id, self.max_retries, str(error))
        return False, last_exception
    async def log_retry_attempt(self, job_id: str, attempt: int, error_message: str):
        retry_collection = get_database()["retry_logs"]
        retry_collection.insert_one({"job_id": job_id, "attempt": attempt, "error": error_message, "timestamp": datetime.utcnow(), "status": "retrying"})
        print(f"Retry attempt {attempt}/{self.max_retries} for job {job_id}: {error_message}")
    async def log_retry_success(self, job_id: str, total_attempts: int):
        retry_collection = get_database()["retry_logs"]
        retry_collection.insert_one({"job_id": job_id, "total_attempts": total_attempts, "timestamp": datetime.utcnow(), "status": "success"})
        print(f"Job {job_id} succeeded after {total_attempts} attempts")
    async def log_retry_failure(self, job_id: str, total_attempts: int, final_error: str):
        retry_collection = get_database()["retry_logs"]
        retry_collection.insert_one({"job_id": job_id, "total_attempts": total_attempts, "final_error": final_error, "timestamp": datetime.utcnow(), "status": "failed"})
        print(f"Job {job_id} failed after {total_attempts} attempts: {final_error}")

retry_manager = RetryManager()
