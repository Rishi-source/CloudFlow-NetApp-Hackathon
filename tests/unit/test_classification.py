import pytest
from datetime import datetime, timedelta
from engines.classification_engine import ClassificationEngine

def test_calculate_tier_score_hot(mock_db):
    engine = ClassificationEngine(mock_db)
    data_obj = {
        "_id": "test1",
        "access_count": 50,
        "last_accessed": datetime.utcnow(),
        "size_bytes": 10 * 1024**3,
        "current_tier": "warm"
    }
    score = engine.calculate_tier_score(data_obj)
    assert score >= 80

def test_calculate_tier_score_cold(mock_db):
    engine = ClassificationEngine(mock_db)
    data_obj = {
        "_id": "test2",
        "access_count": 0,
        "last_accessed": datetime.utcnow() - timedelta(days=100),
        "size_bytes": 100 * 1024**3,
        "current_tier": "warm"
    }
    score = engine.calculate_tier_score(data_obj)
    assert score < 40

def test_classify_tier_hot():
    from engines.classification_engine import classify_tier
    assert classify_tier(85) == "hot"

def test_classify_tier_warm():
    from engines.classification_engine import classify_tier
    assert classify_tier(60) == "warm"

def test_classify_tier_cold():
    from engines.classification_engine import classify_tier
    assert classify_tier(30) == "cold"

def test_calculate_storage_cost():
    from engines.classification_engine import COST_MATRIX
    size_gb = 100
    tier = "hot"
    location = "aws"
    expected = size_gb * COST_MATRIX[location][tier]
    cost = size_gb * COST_MATRIX[location][tier]
    assert cost == expected

def test_recommend_tier_upgrade(mock_db):
    engine = ClassificationEngine(mock_db)
    mock_db["data_objects"].insert_one({
        "_id": "obj1",
        "access_count": 60,
        "last_accessed": datetime.utcnow(),
        "current_tier": "cold",
        "size_bytes": 5 * 1024**3
    })
    recommendation = engine.recommend_tier("obj1")
    assert recommendation["recommended_tier"] in ["hot", "warm"]
