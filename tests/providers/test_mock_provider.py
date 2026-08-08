import pytest
import uuid
from app.providers.mock import MockProvider, mock_provider
from app.providers.base import ProviderOutput
from app.services.analysis_job_service import analysis_job_service
from app.repositories.provider_result_repository import provider_result_repository
from app.models.analysis_job import AnalysisJobStatus
from httpx import AsyncClient
from tests.helpers import FakeGeminiProvider


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
    """Test full execution of an Analysis Job through FakeGeminiProvider (structured pipeline)."""
    # 1. Create project
    proj_res = await async_client.post("/api/v1/projects", json={"name": "Provider Exec Co", "url": "https://provexec.com"})
    assert proj_res.status_code == 201
    project_id = uuid.UUID(proj_res.json()["id"])

    # 2. Trigger job
    job = await analysis_job_service.create_job(db_session, project_id=project_id)
    assert job.status == AnalysisJobStatus.PENDING

    # 3. Execute job with FakeGeminiProvider (structured single-request pipeline)
    result = await analysis_job_service.execute_job(
        db_session,
        job_id=job.id,
        provider=FakeGeminiProvider()
    )

    assert result.job_id == job.id
    assert result.provider_name == "gemini"
    # raw_response is the scorecard summary text
    assert "provexec.com" in result.raw_response or "Provexec" in result.raw_response

    # Verify job state transitioned Pending -> Running -> Completed
    updated_job = await analysis_job_service.get_job(db_session, job_id=job.id)
    assert updated_job.status == AnalysisJobStatus.COMPLETED

    # Verify DB repository retrieval — 1 result per structured analysis
    results = await provider_result_repository.list_by_job(db_session, job_id=job.id)
    assert len(results) >= 1
    assert results[0].id == result.id
