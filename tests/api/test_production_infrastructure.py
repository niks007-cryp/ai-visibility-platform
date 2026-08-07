import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_and_readiness_probes(async_client: AsyncClient):
    """Test /health, /ready, /live, and /metrics production endpoints."""
    # /health
    res_health = await async_client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"

    # /ready
    res_ready = await async_client.get("/ready")
    assert res_ready.status_code == 200
    assert res_ready.json()["status"] == "ready"

    # /live
    res_live = await async_client.get("/live")
    assert res_live.status_code == 200
    assert res_live.json()["status"] == "alive"

    # /metrics
    res_metrics = await async_client.get("/metrics")
    assert res_metrics.status_code == 200
    assert "http_requests_total" in res_metrics.text


@pytest.mark.asyncio
async def test_request_correlation_middleware(async_client: AsyncClient):
    """Test X-Request-ID and X-Correlation-ID headers generated and returned."""
    res = await async_client.get("/health", headers={"X-Request-ID": "test-req-12345"})
    assert res.status_code == 200
    assert res.headers.get("X-Request-ID") == "test-req-12345"
    assert res.headers.get("X-Correlation-ID") == "test-req-12345"


@pytest.mark.asyncio
async def test_security_headers_middleware(async_client: AsyncClient):
    """Test security hardening headers applied to HTTP responses."""
    res = await async_client.get("/health")
    assert res.status_code == 200
    assert res.headers.get("X-Content-Type-Options") == "nosniff"
    assert res.headers.get("X-Frame-Options") == "DENY"
    assert "Strict-Transport-Security" in res.headers
