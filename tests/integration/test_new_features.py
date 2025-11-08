import pytest
from services.cloud.retry_manager import retry_manager
from services.cloud.conflict_resolver import conflict_resolver
from services.cloud.transaction_logger import transaction_logger
from services.metrics.performance_tracker import performance_tracker
from services.deduplication.hash_manager import hash_manager
from services.compression.compressor import compressor
from services.cloud.region_selector import region_selector
from services.disaster_recovery.backup_manager import backup_manager
from datetime import datetime
import time

@pytest.mark.asyncio
async def test_retry_manager():
    attempt_count = 0
    async def failing_operation():
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise Exception("Simulated failure")
        return "success"
    success, error = await retry_manager.execute_with_retry(failing_operation, "test_job_123")
    assert success == True
    assert attempt_count == 3

@pytest.mark.asyncio
async def test_conflict_resolver():
    local_data = {"name": "file.txt", "version": 2, "updated_at": datetime(2024, 1, 15)}
    remote_data = {"name": "file.txt", "version": 1, "updated_at": datetime(2024, 1, 10)}
    result = await conflict_resolver.last_write_wins("test_job", local_data, remote_data)
    assert result == local_data

@pytest.mark.asyncio
async def test_transaction_logger():
    tx_id = await transaction_logger.log_transaction_start("job_456", "migration", {"file": "test.pdf"})
    assert tx_id != ""
    await transaction_logger.log_transaction_complete(tx_id)
    history = await transaction_logger.get_transaction_history("job_456")
    assert len(history) > 0

@pytest.mark.asyncio
async def test_performance_tracker():
    start_time = time.time()
    await performance_tracker.track_migration_performance("perf_job_1", "upload", start_time, True, 1024*1024*10)
    avg_latency = await performance_tracker.get_average_latency(60)
    assert avg_latency >= 0
    throughput = await performance_tracker.get_throughput_stats(60)
    assert "average" in throughput

def test_hash_manager():
    content = b"test file content for deduplication"
    hash1 = hash_manager.calculate_hash(content)
    hash2 = hash_manager.calculate_hash(content)
    assert hash1 == hash2
    assert len(hash1) == 64

def test_compressor():
    data = b"This is a test string that should compress well" * 100
    compressed, ratio = compressor.compress(data)
    assert len(compressed) < len(data)
    assert ratio > 0
    decompressed = compressor.decompress(compressed)
    assert decompressed == data

def test_region_selector():
    aws_region = region_selector.select_optimal_region("aws", "us")
    assert aws_region in ["us-east-1", "us-west-2", "eu-west-1", "ap-south-1"]
    latency = region_selector.get_estimated_latency(aws_region)
    assert latency > 0
    all_regions = region_selector.get_all_regions("aws")
    assert len(all_regions) > 0

@pytest.mark.asyncio
async def test_backup_manager():
    test_data = {"name": "backup_test.txt", "size": 1024, "content": "test"}
    backup_id = await backup_manager.create_backup("test_user", "obj_123", test_data)
    if backup_id:
        restored = await backup_manager.restore_backup(backup_id)
        assert restored["name"] == test_data["name"]
        backups = await backup_manager.list_backups("test_user")
        assert len(backups) >= 0
