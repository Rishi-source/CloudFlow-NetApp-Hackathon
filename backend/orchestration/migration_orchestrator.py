from datetime import datetime
import logging
import time
import threading
from typing import Optional
import random

class MigrationOrchestrator:
    def __init__(self, db, kafka_producer):
        self.db = db
        self.kafka = kafka_producer
        self.running = False
        self.worker_thread = None
    
    def start(self):
        self.running = True
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()
        logging.info("Migration orchestrator started")
    
    def stop(self):
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        logging.info("Migration orchestrator stopped")
    
    def _process_queue(self):
        while self.running:
            try:
                pending_job = self.db["migration_jobs"].find_one_and_update(
                    {"status": "pending"},
                    {"$set": {"status": "in_progress", "start_time": datetime.utcnow()}},
                    sort=[("priority", -1), ("created_at", 1)],
                    return_document=True
                )
                if pending_job:
                    self._execute_migration(pending_job)
                else:
                    time.sleep(5)
            except Exception as e:
                logging.error(f"Queue processing error: {str(e)}")
                time.sleep(10)
    
    def _execute_migration(self, job: dict):
        job_id = job["job_id"]
        try:
            self.kafka.send_migration_event(job_id, "in_progress", 0.0, job["data_object_id"])
            data_obj = self.db["data_objects"].find_one({"_id": job["data_object_id"]})
            if not data_obj:
                self._fail_job(job_id, "Data object not found")
                return
            total_bytes = job["total_bytes"]
            transferred = 0
            chunk_size = max(total_bytes // 10, 1024 * 1024)
            while transferred < total_bytes and self.running:
                transfer_amount = min(chunk_size, total_bytes - transferred)
                time.sleep(random.uniform(0.1, 0.5))
                transferred += transfer_amount
                progress = (transferred / total_bytes) * 100
                self.db["migration_jobs"].update_one(
                    {"job_id": job_id},
                    {"$set": {
                        "bytes_transferred": transferred,
                        "progress_percentage": progress
                    }}
                )
                self.kafka.send_migration_event(job_id, "in_progress", progress, job["data_object_id"])
            if transferred >= total_bytes:
                self._complete_migration(job)
            else:
                self._fail_job(job_id, "Migration interrupted")
        except Exception as e:
            logging.error(f"Migration execution error for job {job_id}: {str(e)}")
            self._fail_job(job_id, str(e))
    
    def _complete_migration(self, job: dict):
        job_id = job["job_id"]
        self.db["migration_jobs"].update_one(
            {"job_id": job_id},
            {"$set": {
                "status": "completed",
                "end_time": datetime.utcnow(),
                "progress_percentage": 100.0
            }}
        )
        self.db["data_objects"].update_one(
            {"_id": job["data_object_id"]},
            {"$set": {
                "current_location": job["target_location"],
                "current_tier": job["target_tier"],
                "updated_at": datetime.utcnow()
            }}
        )
        self.kafka.send_migration_event(job_id, "completed", 100.0, job["data_object_id"])
        logging.info(f"Migration job {job_id} completed successfully")
    
    def _fail_job(self, job_id: str, error_message: str):
        job = self.db["migration_jobs"].find_one({"job_id": job_id})
        if not job:
            return
        retry_count = job.get("retry_count", 0)
        max_retries = 3
        if retry_count < max_retries:
            self.db["migration_jobs"].update_one(
                {"job_id": job_id},
                {"$set": {
                    "status": "pending",
                    "retry_count": retry_count + 1,
                    "error_message": error_message
                }}
            )
            logging.warning(f"Migration job {job_id} retry {retry_count + 1}/{max_retries}: {error_message}")
        else:
            self.db["migration_jobs"].update_one(
                {"job_id": job_id},
                {"$set": {
                    "status": "failed",
                    "end_time": datetime.utcnow(),
                    "error_message": error_message
                }}
            )
            self.kafka.send_migration_event(job_id, "failed", 0.0, job["data_object_id"])
            logging.error(f"Migration job {job_id} failed after {max_retries} retries: {error_message}")
    
    def cancel_job(self, job_id: str) -> bool:
        result = self.db["migration_jobs"].update_one(
            {"job_id": job_id, "status": {"$in": ["pending", "in_progress"]}},
            {"$set": {"status": "cancelled", "end_time": datetime.utcnow()}}
        )
        if result.modified_count > 0:
            self.kafka.send_migration_event(job_id, "cancelled", 0.0, "")
            logging.info(f"Migration job {job_id} cancelled")
            return True
        return False
    
    def get_queue_status(self) -> dict:
        pending = self.db["migration_jobs"].count_documents({"status": "pending"})
        in_progress = self.db["migration_jobs"].count_documents({"status": "in_progress"})
        completed = self.db["migration_jobs"].count_documents({"status": "completed"})
        failed = self.db["migration_jobs"].count_documents({"status": "failed"})
        return {
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed,
            "failed": failed,
            "total": pending + in_progress + completed + failed
        }
