from fastapi import APIRouter, Depends
from middleware.auth_middleware import get_current_user
from services.metrics.performance_tracker import performance_tracker

router = APIRouter(prefix="/api/v1/metrics", tags=["metrics"])

@router.get("/performance")
async def get_performance_metrics(time_range: int = 60, current_user: dict = Depends(get_current_user)):
    avg_latency = await performance_tracker.get_average_latency(time_range)
    throughput_stats = await performance_tracker.get_throughput_stats(time_range)
    success_rate = await performance_tracker.get_success_rate(time_range)
    percentiles = await performance_tracker.get_latency_percentiles(time_range)
    return {"average_latency_ms": avg_latency, "throughput": throughput_stats, "success_rate": success_rate, "latency_percentiles": percentiles, "time_range_minutes": time_range}

@router.get("/throughput")
async def get_throughput_metrics(time_range: int = 60, current_user: dict = Depends(get_current_user)):
    return await performance_tracker.get_throughput_stats(time_range)

@router.get("/latency")
async def get_latency_metrics(time_range: int = 60, current_user: dict = Depends(get_current_user)):
    avg_latency = await performance_tracker.get_average_latency(time_range)
    percentiles = await performance_tracker.get_latency_percentiles(time_range)
    return {"average": avg_latency, "percentiles": percentiles}
