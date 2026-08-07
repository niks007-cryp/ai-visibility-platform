import json
import logging
import pytest
from httpx import AsyncClient
from app.core.observability import JSONFormatter, metrics_exporter


def test_json_formatter_output():
    """Test JSONFormatter converts log record to valid JSON string with context metadata."""
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="Structured JSON telemetry test message",
        args=(),
        exc_info=None
    )
    record.request_id = "req-test-999"

    formatted = formatter.format(record)
    data = json.loads(formatted)

    assert data["level"] == "INFO"
    assert data["message"] == "Structured JSON telemetry test message"
    assert data["request_id"] == "req-test-999"
    assert "environment" in data
    assert "hostname" in data


@pytest.mark.asyncio
async def test_metrics_endpoint(async_client: AsyncClient):
    """Test Prometheus metrics endpoint returns counters and gauges."""
    metrics_exporter.record_http_request()
    metrics_exporter.record_auth_failure()

    res = await async_client.get("/metrics")
    assert res.status_code == 200
    assert "http_requests_total" in res.text
    assert "auth_failures_total" in res.text


@pytest.mark.asyncio
async def test_readiness_probe_dependencies(async_client: AsyncClient):
    """Test /ready endpoint checks database and worker readiness."""
    res = await async_client.get("/ready")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"
    assert data["worker"] == "ready"
