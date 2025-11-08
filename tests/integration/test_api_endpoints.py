import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

def test_health_endpoint():
    from api.main import app
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert "status" in response.json()

@pytest.mark.asyncio
async def test_upload_data_object():
    from api.main import app
    async with AsyncClient(app=app, base_url="http://test") as client:
        data = {
            "name": "test_file.txt",
            "size_bytes": 1024000,
            "current_location": "on-premise",
            "current_tier": "warm",
            "metadata": {"file_type": "document", "owner": "test_user"}
        }
        response = await client.post("/api/v1/data/upload", json=data)
        assert response.status_code == 200
        assert "id" in response.json()

@pytest.mark.asyncio
async def test_get_analytics_summary():
    from api.main import app
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/analytics/summary")
        assert response.status_code == 200
        data = response.json()
        assert "distribution" in data
        assert "costs" in data

@pytest.mark.asyncio
async def test_initiate_migration():
    from api.main import app
    async with AsyncClient(app=app, base_url="http://test") as client:
        migration_data = {
            "data_object_id": "test_obj_123",
            "target_location": "aws",
            "target_tier": "hot",
            "priority": 5
        }
        response = await client.post("/api/v1/migration/initiate", json=migration_data)
        assert response.status_code in [200, 404]

@pytest.mark.asyncio
async def test_list_data_objects():
    from api.main import app
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/data/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
