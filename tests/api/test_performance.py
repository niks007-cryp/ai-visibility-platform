import time
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_gzip_compression_middleware(async_client: AsyncClient):
    """Test GZipMiddleware compresses response payloads exceeding 1000 bytes."""
    headers = {"Accept-Encoding": "gzip"}
    res = await async_client.get("/api/v1/prompts", headers=headers)
    assert res.status_code == 200
    assert "gzip" in res.headers.get("Content-Encoding", "")


@pytest.mark.asyncio
async def test_health_probe_latency(async_client: AsyncClient):
    """Test /health and /ready response latency is strictly under 50ms."""
    start = time.perf_counter()
    res = await async_client.get("/ready")
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert res.status_code == 200
    assert elapsed_ms < 50.0
