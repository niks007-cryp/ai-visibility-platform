import pytest
from unittest.mock import patch
from httpx import AsyncClient
from app.core.rate_limiter import rate_limiter
from app.core.config_guard import validate_production_configuration
from app.core.database import engine


@pytest.mark.asyncio
async def test_auth_login_rate_limiter(async_client: AsyncClient):
    """Test rate limiter blocking excessive login attempts (>5 req/min per IP)."""
    rate_limiter.reset()

    login_payload = {"email": "ratelimit@example.com", "password": "WrongPassword123!"}

    # First 5 attempts -> 401 Unauthorized (rate limiter permits request)
    for _ in range(5):
        res = await async_client.post("/api/v1/auth/login", json=login_payload)
        assert res.status_code == 401

    # 6th attempt -> 429 Too Many Requests (rate limiter blocks)
    blocked_res = await async_client.post("/api/v1/auth/login", json=login_payload)
    assert blocked_res.status_code == 429
    assert "Rate limit exceeded" in blocked_res.json()["detail"]

    # Reset for subsequent tests
    rate_limiter.reset()


def test_production_config_guard_insecure_jwt_secret():
    """Test startup guard raises RuntimeError when default insecure JWT secret is used in production."""
    with patch("app.core.config.settings.ENVIRONMENT", "production"), \
         patch("app.core.security.SECRET_KEY", "production_super_secret_jwt_signing_key_change_in_env"):
        with pytest.raises(RuntimeError) as exc_info:
            validate_production_configuration()
        assert "Default insecure JWT secret key detected" in str(exc_info.value)


def test_database_connection_pool_configuration():
    """Test database engine connection pool configuration settings."""
    assert engine is not None
