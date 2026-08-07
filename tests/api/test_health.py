import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_endpoint(async_client: AsyncClient):
    """Test root endpoint metadata response."""
    response = await async_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert data["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_health_endpoint_direct(async_client: AsyncClient):
    """Test GET /health endpoint."""
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in {"healthy", "ok"}


@pytest.mark.asyncio
async def test_health_endpoint_api_v1(async_client: AsyncClient):
    """Test GET /api/v1/health endpoint."""
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in {"healthy", "ok"}
