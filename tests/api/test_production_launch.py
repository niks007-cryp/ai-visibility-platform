import os
import uuid
import pytest
from httpx import AsyncClient
from app.core.rate_limiter import rate_limiter


def test_github_release_artifacts_exist():
    """Test open-source GitHub release files and deployment manifests exist."""
    assert os.path.exists("LICENSE")
    assert os.path.exists("README.md")
    assert os.path.exists("frontend/vercel.json")


def test_production_deployment_documentation_exists():
    """Test production deployment, rollback, disaster recovery, and env checklist guides exist."""
    assert os.path.exists("docs/PRODUCTION_DEPLOYMENT_GUIDE.md")
    assert os.path.exists("docs/ROLLBACK_GUIDE.md")
    assert os.path.exists("docs/DISASTER_RECOVERY_GUIDE.md")
    assert os.path.exists("docs/ENVIRONMENT_CHECKLIST.md")


@pytest.mark.asyncio
async def test_full_production_system_e2e_verification(async_client: AsyncClient, db_session):
    """Verifies end-to-end user registration, authentication, project creation, job execution, and report generation."""
    rate_limiter.reset()

    # 1. User Registration
    email = "production_launch_user@example.com"
    password = "SuperSecretPassword123!"
    reg_res = await async_client.post("/api/v1/auth/register", json={"email": email, "password": password})
    assert reg_res.status_code == 201

    # 2. User Login
    login_res = await async_client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Create Project
    proj_res = await async_client.post("/api/v1/projects", json={"name": "Prod Launch Co", "url": "https://prodlaunch.io"}, headers=headers)
    assert proj_res.status_code == 201
    project_id = proj_res.json()["id"]

    # 4. Trigger Analysis Job
    job_res = await async_client.post(f"/api/v1/projects/{project_id}/jobs", headers=headers)
    assert job_res.status_code == 201
    job_id_str = job_res.json()["id"]
    job_id = uuid.UUID(job_id_str)

    # 5. Execute Job Pipeline (Mocking Worker Process)
    from app.services.analysis_job_service import analysis_job_service
    await analysis_job_service.execute_job(db_session, job_id=job_id)

    # 6. Fetch Completed Report
    report_res = await async_client.get(f"/api/v1/jobs/{job_id}/report", headers=headers)
    assert report_res.status_code == 200
    report_data = report_res.json()
    assert report_data["target_domain"] == "prodlaunch.io"

    # 7. Fetch Recommendations
    rec_res = await async_client.get(f"/api/v1/jobs/{job_id}/recommendations", headers=headers)
    assert rec_res.status_code == 200
    assert len(rec_res.json()) >= 1

    # 8. Fetch Worker Health
    worker_res = await async_client.get("/api/v1/worker/health")
    assert worker_res.status_code == 200
    assert worker_res.json()["status"] == "healthy"
