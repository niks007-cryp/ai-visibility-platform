import pytest
import uuid
from httpx import AsyncClient
from app.services.analysis_job_service import analysis_job_service
from app.models.analysis_job import AnalysisJobStatus


@pytest.mark.asyncio
async def test_get_job_report_success(async_client: AsyncClient, db_session):
    """Test retrieving complete MVP report for a COMPLETED analysis job."""
    # 1. Create project
    proj_res = await async_client.post("/api/v1/projects", json={"name": "Report Test Co", "url": "https://reporttest.io"})
    assert proj_res.status_code == 201
    project_id = uuid.UUID(proj_res.json()["id"])

    # 2. Trigger job
    job = await analysis_job_service.create_job(db_session, project_id=project_id)

    # 3. Execute job (transitions Pending -> Running -> Completed and saves ProviderResult & ExtractedEvidence)
    await analysis_job_service.execute_job(
        db_session,
        job_id=job.id,
        prompt="Top tools for developer productivity 2026"
    )

    # 4. Query GET /jobs/{job_id}/report endpoint
    report_res = await async_client.get(f"/api/v1/jobs/{job.id}/report")
    assert report_res.status_code == 200
    data = report_res.json()

    assert data["job_id"] == str(job.id)
    assert data["project_id"] == str(project_id)
    assert data["project_name"] == "Report Test Co"
    assert data["target_domain"] == "reporttest.io"
    assert data["job_status"] == AnalysisJobStatus.COMPLETED.value
    assert data["provider_name"] == "mock"
    assert "reporttest.io" in data["raw_response"]
    assert data["mentioned"] is True
    assert isinstance(data["raw_citations"], list)
    assert isinstance(data["matched_snippets"], list)
    assert isinstance(data["extracted_brand_mentions"], list)


@pytest.mark.asyncio
async def test_get_job_report_job_not_found(async_client: AsyncClient):
    """Test requesting report for non-existent job UUID returns 404 Not Found."""
    random_uuid = uuid.uuid4()
    response = await async_client.get(f"/api/v1/jobs/{random_uuid}/report")
    assert response.status_code == 404
    assert f"Analysis Job with ID '{random_uuid}' not found." in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_job_report_not_completed_bad_request(async_client: AsyncClient, db_session):
    """Test requesting report for job in PENDING state returns 400 Bad Request."""
    # 1. Create project
    proj_res = await async_client.post("/api/v1/projects", json={"name": "Pending Co", "url": "https://pendingco.io"})
    assert proj_res.status_code == 201
    project_id = uuid.UUID(proj_res.json()["id"])

    # 2. Trigger job (remains in Pending state)
    job = await analysis_job_service.create_job(db_session, project_id=project_id)
    assert job.status == AnalysisJobStatus.PENDING

    # 3. Query report for Pending job
    report_res = await async_client.get(f"/api/v1/jobs/{job.id}/report")
    assert report_res.status_code == 400
    assert "Job must be COMPLETED" in report_res.json()["detail"]
