import pytest
import uuid
from httpx import AsyncClient
from app.models.analysis_job import AnalysisJobStatus
from app.services.analysis_job_service import analysis_job_service
from app.repositories.analysis_job_repository import analysis_job_repository


@pytest.mark.asyncio
async def test_create_job_success(async_client: AsyncClient):
    """Test successful creation of an Analysis Job for a project."""
    # 1. Create a project
    proj_res = await async_client.post("/api/v1/projects", json={"name": "Job Test Co", "url": "https://jobtest.com"})
    assert proj_res.status_code == 201
    project_id = proj_res.json()["id"]

    # 2. Trigger job
    job_res = await async_client.post(f"/api/v1/projects/{project_id}/jobs")
    assert job_res.status_code == 201
    job_data = job_res.json()
    assert job_data["project_id"] == project_id
    assert job_data["status"] == AnalysisJobStatus.PENDING.value
    assert "id" in job_data
    assert "created_at" in job_data


@pytest.mark.asyncio
async def test_create_job_invalid_project(async_client: AsyncClient):
    """Test triggering job for non-existent project returns 404 Not Found."""
    fake_project_id = str(uuid.uuid4())
    job_res = await async_client.post(f"/api/v1/projects/{fake_project_id}/jobs")
    assert job_res.status_code == 404


@pytest.mark.asyncio
async def test_create_job_concurrent_conflict(async_client: AsyncClient, db_session):
    """Test creating a second job for a project while another is active returns 409 Conflict."""
    proj_res = await async_client.post("/api/v1/projects", json={"name": "Concurrent Co", "url": "https://concurrent.com"})
    project_id = uuid.UUID(proj_res.json()["id"])

    # Create explicit active PENDING job in DB
    await analysis_job_repository.create(db_session, project_id=project_id)
    await db_session.commit()

    # Second job (concurrent conflict)
    job2_res = await async_client.post(f"/api/v1/projects/{project_id}/jobs")
    assert job2_res.status_code == 409
    assert "already in progress" in job2_res.json()["detail"]


@pytest.mark.asyncio
async def test_valid_state_transitions(async_client: AsyncClient, db_session):
    """Test valid state machine transitions: Pending -> Running -> Completed."""
    proj_res = await async_client.post("/api/v1/projects", json={"name": "Transition Co", "url": "https://transition.org"})
    project_id = proj_res.json()["id"]

    job_res = await async_client.post(f"/api/v1/projects/{project_id}/jobs")
    job_id = uuid.UUID(job_res.json()["id"])

    # Pending -> Running
    running_job = await analysis_job_service.transition_job_status(
        db_session, job_id=job_id, target_status=AnalysisJobStatus.RUNNING
    )
    assert running_job.status == AnalysisJobStatus.RUNNING
    assert running_job.started_at is not None

    # Running -> Completed
    completed_job = await analysis_job_service.transition_job_status(
        db_session, job_id=job_id, target_status=AnalysisJobStatus.COMPLETED
    )
    assert completed_job.status == AnalysisJobStatus.COMPLETED
    assert completed_job.completed_at is not None


@pytest.mark.asyncio
async def test_invalid_state_transition_protection(async_client: AsyncClient, db_session):
    """Test invalid transition from terminal state Completed -> Running returns 400 Bad Request."""
    proj_res = await async_client.post("/api/v1/projects", json={"name": "Invalid State Co", "url": "https://invalidstate.io"})
    project_id = proj_res.json()["id"]

    job_res = await async_client.post(f"/api/v1/projects/{project_id}/jobs")
    job_id = uuid.UUID(job_res.json()["id"])

    # Move to Running then Completed
    await analysis_job_service.transition_job_status(db_session, job_id=job_id, target_status=AnalysisJobStatus.RUNNING)
    await analysis_job_service.transition_job_status(db_session, job_id=job_id, target_status=AnalysisJobStatus.COMPLETED)

    # Attempt illegal transition Completed -> Running
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await analysis_job_service.transition_job_status(db_session, job_id=job_id, target_status=AnalysisJobStatus.RUNNING)
    assert exc_info.value.status_code == 400
    assert "Cannot transition job status from 'Completed' to 'Running'" in exc_info.value.detail


@pytest.mark.asyncio
async def test_cancel_job_success(async_client: AsyncClient):
    """Test cancelling an active job via API endpoint."""
    proj_res = await async_client.post("/api/v1/projects", json={"name": "Cancel Co", "url": "https://cancel.com"})
    project_id = proj_res.json()["id"]

    job_res = await async_client.post(f"/api/v1/projects/{project_id}/jobs")
    job_id = job_res.json()["id"]

    cancel_res = await async_client.post(f"/api/v1/jobs/{job_id}/cancel")
    assert cancel_res.status_code == 200
    cancel_data = cancel_res.json()
    assert cancel_data["status"] == AnalysisJobStatus.CANCELLED.value
    assert cancel_data["completed_at"] is not None


@pytest.mark.asyncio
async def test_cancel_terminal_job_failure(async_client: AsyncClient, db_session):
    """Test cancelling a job already in a terminal state returns 400 Bad Request."""
    proj_res = await async_client.post("/api/v1/projects", json={"name": "Terminal Cancel Co", "url": "https://termcancel.com"})
    project_id = proj_res.json()["id"]

    job_res = await async_client.post(f"/api/v1/projects/{project_id}/jobs")
    job_id = job_res.json()["id"]
    job_uuid = uuid.UUID(job_id)

    # Move job to Running then Completed
    await analysis_job_service.transition_job_status(db_session, job_id=job_uuid, target_status=AnalysisJobStatus.RUNNING)
    await analysis_job_service.transition_job_status(db_session, job_id=job_uuid, target_status=AnalysisJobStatus.COMPLETED)

    # Attempt cancel on Completed job via API
    cancel_res = await async_client.post(f"/api/v1/jobs/{job_id}/cancel")
    assert cancel_res.status_code == 400
    assert "Cannot transition job status from 'Completed' to 'Cancelled'" in cancel_res.json()["detail"]


@pytest.mark.asyncio
async def test_list_jobs_for_project(async_client: AsyncClient):
    """Test listing jobs for a project."""
    proj_res = await async_client.post("/api/v1/projects", json={"name": "List Jobs Co", "url": "https://listjobs.com"})
    project_id = proj_res.json()["id"]

    # Job 1
    job1_res = await async_client.post(f"/api/v1/projects/{project_id}/jobs")
    job1_id = job1_res.json()["id"]
    # Cancel job 1 so we can create job 2
    await async_client.post(f"/api/v1/jobs/{job1_id}/cancel")

    # Job 2
    await async_client.post(f"/api/v1/projects/{project_id}/jobs")

    list_res = await async_client.get(f"/api/v1/projects/{project_id}/jobs")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert len(list_data) == 2
    assert list_data[0]["project_id"] == project_id
