import pytest
import uuid
from app.providers.mock import MockProvider, mock_provider
from app.providers.base import ProviderOutput
from app.services.analysis_job_service import analysis_job_service
from app.repositories.provider_result_repository import provider_result_repository
from app.models.analysis_job import AnalysisJobStatus
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_mock_provider_query():
    """Test direct MockProvider query method."""
    provider = MockProvider()
    assert provider.name == "mock"

    output = await provider.query(
        prompt="Recommend software for accounting",
        domain="acmeaccounting.com"
    )
    assert isinstance(output, ProviderOutput)
    assert output.provider_name == "mock"
    assert "acmeaccounting.com" in output.raw_response
    assert "Recommend software for accounting" in output.prompt


@pytest.mark.asyncio
async def test_execute_job_with_mock_provider(async_client: AsyncClient, db_session):
    """Test full execution of an Analysis Job through MockProvider generating ProviderResult."""
    # 1. Create project
    proj_res = await async_client.post("/api/v1/projects", json={"name": "Provider Exec Co", "url": "https://provexec.com"})
    assert proj_res.status_code == 201
    project_id = uuid.UUID(proj_res.json()["id"])

    # 2. Trigger job
    job = await analysis_job_service.create_job(db_session, project_id=project_id)
    assert job.status == AnalysisJobStatus.PENDING

    # 3. Execute job with MockProvider across prompt evaluation catalog
    result = await analysis_job_service.execute_job(
        db_session,
        job_id=job.id,
        prompt="Top workflow management tools 2026"
    )

    assert result.job_id == job.id
    assert result.provider_name == "mock"
    assert "provexec.com" in result.raw_response

    # Verify job state transitioned Pending -> Running -> Completed
    updated_job = await analysis_job_service.get_job(db_session, job_id=job.id)
    assert updated_job.status == AnalysisJobStatus.COMPLETED

    # Verify DB repository retrieval across multi-prompt evaluation
    results = await provider_result_repository.list_by_job(db_session, job_id=job.id)
    assert len(results) >= 1
    assert results[0].id == result.id
