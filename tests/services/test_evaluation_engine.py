import pytest
import uuid
from httpx import AsyncClient
from app.schemas.evaluation import ConfidenceLevel
from app.services.evaluation_service import evaluation_service
from app.services.analysis_job_service import analysis_job_service
from tests.helpers import FakeGeminiProvider


@pytest.mark.asyncio
async def test_evaluation_summary_calculation(async_client: AsyncClient, db_session):
    """Test EvaluationService calculates multi-prompt consistency and confidence levels."""
    # 1. Create project
    proj_res = await async_client.post("/api/v1/projects", json={"name": "Eval Test Co", "url": "https://evaltest.io"})
    assert proj_res.status_code == 201
    project_id = uuid.UUID(proj_res.json()["id"])

    # 2. Trigger job
    job = await analysis_job_service.create_job(db_session, project_id=project_id)

    # 3. Execute job with structured single-request pipeline
    await analysis_job_service.execute_job(db_session, job_id=job.id, provider=FakeGeminiProvider())

    # 4. Calculate evaluation summary
    summary = await evaluation_service.get_evaluation_summary(db_session, job_id=job.id)

    assert summary.job_id == job.id
    # 1 structured result = 1 provider result record
    assert summary.total_prompts >= 1
    assert summary.consistency_percentage == 100.0
    assert summary.confidence_level == ConfidenceLevel.HIGH
    assert len(summary.contradictions) == 0


@pytest.mark.asyncio
async def test_evaluation_api_endpoint(async_client: AsyncClient, db_session):
    """Test GET /api/v1/jobs/{job_id}/evaluation endpoint."""
    # 1. Create project
    proj_res = await async_client.post("/api/v1/projects", json={"name": "Eval Endpoint Co", "url": "https://evalend.io"})
    assert proj_res.status_code == 201
    project_id = uuid.UUID(proj_res.json()["id"])

    # 2. Trigger job
    job = await analysis_job_service.create_job(db_session, project_id=project_id)

    # 3. Execute job
    await analysis_job_service.execute_job(db_session, job_id=job.id, provider=FakeGeminiProvider())

    # 4. Query GET /jobs/{job_id}/evaluation
    res = await async_client.get(f"/api/v1/jobs/{job.id}/evaluation")
    assert res.status_code == 200
    data = res.json()

    assert data["job_id"] == str(job.id)
    assert data["consistency_percentage"] == 100.0
    assert data["confidence_level"] == "HIGH"
    assert "prompt_categories_tested" in data
    assert isinstance(data["contradictions"], list)
