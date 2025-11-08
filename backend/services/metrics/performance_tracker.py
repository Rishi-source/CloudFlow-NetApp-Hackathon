from datetime import datetime, timedelta
from typing import Dict, List
from config.settings import settings
from config.database import get_database
import time

class PerformanceTracker:
    def __init__(self):
        self.enabled = settings.performance_metrics_enabled
        self.collection_interval = settings.metrics_collection_interval
    async def track_migration_performance(self, job_id: str, operation: str, start_time: float, success: bool, data_size: int):
        if not self.enabled:
            return
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        throughput_mbps = (data_size / (1024 * 1024)) / ((end_time - start_time) if (end_time - start_time) > 0 else 1)
        metrics_collection = get_database()["performance_metrics"]
        metric = {"job_id": job_id, "operation": operation, "duration_ms": round(duration_ms, 2), "throughput_mbps": round(throughput_mbps, 2), "data_size_bytes": data_size, "success": success, "timestamp": datetime.utcnow()}
        metrics_collection.insert_one(metric)
    async def get_average_latency(self, time_range_minutes: int = 60) -> float:
        metrics_collection = get_database()["performance_metrics"]
        cutoff_time = datetime.utcnow() - timedelta(minutes=time_range_minutes)
        metrics = list(metrics_collection.find({"timestamp": {"$gte": cutoff_time}, "success": True}))
        if not metrics:
            return 0.0
        total_latency = sum(m["duration_ms"] for m in metrics)
        return round(total_latency / len(metrics), 2)
    async def get_throughput_stats(self, time_range_minutes: int = 60) -> Dict[str, float]:
        metrics_collection = get_database()["performance_metrics"]
        cutoff_time = datetime.utcnow() - timedelta(minutes=time_range_minutes)
        metrics = list(metrics_collection.find({"timestamp": {"$gte": cutoff_time}, "success": True}))
        if not metrics:
            return {"average": 0.0, "max": 0.0, "min": 0.0, "total_data_gb": 0.0}
        throughputs = [m["throughput_mbps"] for m in metrics]
        total_data = sum(m["data_size_bytes"] for m in metrics) / (1024 ** 3)
        return {"average": round(sum(throughputs) / len(throughputs), 2), "max": round(max(throughputs), 2), "min": round(min(throughputs), 2), "total_data_gb": round(total_data, 2)}
    async def get_success_rate(self, time_range_minutes: int = 60) -> float:
        metrics_collection = get_database()["performance_metrics"]
        cutoff_time = datetime.utcnow() - timedelta(minutes=time_range_minutes)
        total = metrics_collection.count_documents({"timestamp": {"$gte": cutoff_time}})
        if total == 0:
            return 100.0
        successful = metrics_collection.count_documents({"timestamp": {"$gte": cutoff_time}, "success": True})
        return round((successful / total) * 100, 2)
    async def get_latency_percentiles(self, time_range_minutes: int = 60) -> Dict[str, float]:
        metrics_collection = get_database()["performance_metrics"]
        cutoff_time = datetime.utcnow() - timedelta(minutes=time_range_minutes)
        metrics = list(metrics_collection.find({"timestamp": {"$gte": cutoff_time}, "success": True}).sort("duration_ms", 1))
        if not metrics:
            return {"p50": 0.0, "p90": 0.0, "p95": 0.0, "p99": 0.0}
        durations = [m["duration_ms"] for m in metrics]
        n = len(durations)
        return {"p50": durations[int(n * 0.50)] if n > 0 else 0.0, "p90": durations[int(n * 0.90)] if n > 0 else 0.0, "p95": durations[int(n * 0.95)] if n > 0 else 0.0, "p99": durations[int(n * 0.99)] if n > 0 else 0.0}

performance_tracker = PerformanceTracker()
