import pytest
from httpx import AsyncClient
from app.core.rate_limiter import rate_limiter


@pytest.mark.asyncio
async def test_user_registration_and_login(async_client: AsyncClient):
    """Test registering new user, duplicate rejection, and login JWT issuance."""
    rate_limiter.reset()

    # 1. Register User A
    reg_res = await async_client.post(
        "/api/v1/auth/register",
        json={"email": "usera@example.com", "password": "SecurePassword123!"}
    )
    assert reg_res.status_code == 201
    user_data = reg_res.json()
    assert user_data["email"] == "usera@example.com"
    assert "id" in user_data

    # 2. Register Duplicate Email (409 Conflict)
    dup_res = await async_client.post(
        "/api/v1/auth/register",
        json={"email": "usera@example.com", "password": "AnotherPassword123!"}
    )
    assert dup_res.status_code == 409

    # 3. Login User A
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "usera@example.com", "password": "SecurePassword123!"}
    )
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert "refresh_token" in token_data
    assert token_data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_jwt_validation_and_me_endpoint(async_client: AsyncClient):
    """Test GET /auth/me requires valid JWT Bearer header."""
    rate_limiter.reset()

    # Register & Login
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": "userb@example.com", "password": "Password123!"}
    )
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "userb@example.com", "password": "Password123!"}
    )
    access_token = login_res.json()["access_token"]

    # Request /auth/me without token -> 401
    res_no_auth = await async_client.get("/api/v1/auth/me")
    assert res_no_auth.status_code == 401

    # Request /auth/me with Bearer token -> 200
    headers = {"Authorization": f"Bearer {access_token}"}
    res_auth = await async_client.get("/api/v1/auth/me", headers=headers)
    assert res_auth.status_code == 200
    assert res_auth.json()["email"] == "userb@example.com"


@pytest.mark.asyncio
async def test_token_refresh(async_client: AsyncClient):
    """Test POST /auth/refresh exchanging refresh token for new access token."""
    rate_limiter.reset()

    await async_client.post(
        "/api/v1/auth/register",
        json={"email": "userc@example.com", "password": "Password123!"}
    )
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "userc@example.com", "password": "Password123!"}
    )
    refresh_token = login_res.json()["refresh_token"]

    # Refresh
    ref_res = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert ref_res.status_code == 200
    assert "access_token" in ref_res.json()


@pytest.mark.asyncio
async def test_multi_tenant_project_isolation(async_client: AsyncClient):
    """Test User B is forbidden from accessing User A's private project."""
    rate_limiter.reset()

    # 1. Register & Login User A
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": "owner_a@example.com", "password": "Password123!"}
    )
    login_a = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "owner_a@example.com", "password": "Password123!"}
    )
    token_a = login_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # 2. User A creates project
    proj_a_res = await async_client.post(
        "/api/v1/projects",
        json={"name": "Owner A Secret Co", "url": "https://ownera-secret.com"},
        headers=headers_a
    )
    assert proj_a_res.status_code == 201
    proj_a_id = proj_a_res.json()["id"]

    rate_limiter.reset()

    # 3. Register & Login User B
    reg_b = await async_client.post(
        "/api/v1/auth/register",
        json={"email": "user_b@example.com", "password": "Password123!"}
    )
    assert reg_b.status_code == 201

    login_b = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "user_b@example.com", "password": "Password123!"}
    )
    assert login_b.status_code == 200
    token_b = login_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 4. User B attempts to access User A's project -> 403 Forbidden
    access_attempt = await async_client.get(f"/api/v1/projects/{proj_a_id}", headers=headers_b)
    assert access_attempt.status_code == 403
