import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_project_success(async_client: AsyncClient):
    """Test successful project creation with domain normalization."""
    payload = {
        "name": " Acme Software ",
        "url": "https://WWW.AcmeSoftware.io/product?source=ref"
    }
    response = await async_client.post("/api/v1/projects", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Acme Software"
    assert data["domain"] == "acmesoftware.io"
    assert "acmesoftware.io" in data["url"]


@pytest.mark.asyncio
async def test_create_project_duplicate_domain_conflict(async_client: AsyncClient):
    """Test creating duplicate domain project returns 409 Conflict."""
    payload = {"name": "Acme", "url": "https://acmesoftware.io"}
    
    # First creation
    res1 = await async_client.post("/api/v1/projects", json=payload)
    assert res1.status_code == 201

    # Duplicate creation
    res2 = await async_client.post("/api/v1/projects", json=payload)
    assert res2.status_code == 409


@pytest.mark.asyncio
async def test_create_project_invalid_url(async_client: AsyncClient):
    """Test creating project with invalid URL returns 422 Unprocessable Entity."""
    payload = {"name": "Invalid Domain Project", "url": "not-a-valid-domain"}
    response = await async_client.post("/api/v1/projects", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_projects(async_client: AsyncClient):
    """Test listing created projects."""
    await async_client.post("/api/v1/projects", json={"name": "Proj 1", "url": "https://p1.com"})
    await async_client.post("/api/v1/projects", json={"name": "Proj 2", "url": "https://p2.com"})

    res = await async_client.get("/api/v1/projects")
    assert res.status_code == 200
    projects = res.json()
    assert len(projects) >= 2


@pytest.mark.asyncio
async def test_get_project_by_id_success_and_not_found(async_client: AsyncClient):
    """Test getting project by ID and handling non-existent ID."""
    create_res = await async_client.post("/api/v1/projects", json={"name": "Target Co", "url": "https://target.com"})
    project_id = create_res.json()["id"]

    # Valid ID
    get_res = await async_client.get(f"/api/v1/projects/{project_id}")
    assert get_res.status_code == 200
    assert get_res.json()["domain"] == "target.com"

    # Non-existent ID
    fake_id = "00000000-0000-0000-0000-000000000000"
    missing_res = await async_client.get(f"/api/v1/projects/{fake_id}")
    assert missing_res.status_code == 404


@pytest.mark.asyncio
async def test_update_project_success(async_client: AsyncClient):
    """Test updating project details."""
    create_res = await async_client.post("/api/v1/projects", json={"name": "Delta", "url": "https://delta.net"})
    project_id = create_res.json()["id"]

    update_payload = {"name": "Delta Corporation", "url": "https://delta.app"}
    update_res = await async_client.patch(f"/api/v1/projects/{project_id}", json=update_payload)
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["name"] == "Delta Corporation"
    assert data["domain"] == "delta.app"


@pytest.mark.asyncio
async def test_delete_project_success(async_client: AsyncClient):
    """Test deleting project by ID (204 No Content)."""
    create_res = await async_client.post("/api/v1/projects", json={"name": "Epsilon", "url": "https://epsilon.ai"})
    project_id = create_res.json()["id"]

    # Delete
    del_res = await async_client.delete(f"/api/v1/projects/{project_id}")
    assert del_res.status_code == 204

    # Verify deleted
    get_res = await async_client.get(f"/api/v1/projects/{project_id}")
    assert get_res.status_code == 404
