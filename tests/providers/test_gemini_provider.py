import pytest
import uuid
from unittest.mock import AsyncMock, patch, MagicMock
from app.providers.gemini import GeminiProvider, GeminiNotConfiguredException, GeminiAPIException
from app.providers.base import ProviderOutput
from app.services.analysis_job_service import analysis_job_service
from app.models.analysis_job import AnalysisJobStatus
from app.repositories.provider_result_repository import provider_result_repository
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_gemini_provider_unconfigured():
    """Test GeminiProvider raises GeminiNotConfiguredException when API key is missing."""
    provider = GeminiProvider(api_key=None, model_name="gemini-1.5-flash")
    assert provider.name == "gemini"
    assert provider.model_name == "gemini-1.5-flash"

    with pytest.raises(GeminiNotConfiguredException):
        await provider.query(prompt="Test prompt", domain="testdomain.com")


@pytest.mark.asyncio
async def test_gemini_provider_query_mocked_sdk():
    """Test GeminiProvider executing query against mocked Google GenAI SDK."""
    provider = GeminiProvider(api_key="mock_key_12345", model_name="gemini-1.5-flash")
    
    mock_response = MagicMock()
    mock_response.text = "Simulated live Gemini 1.5 response output for testdomain.com."

    with patch("google.generativeai.configure") as mock_config, \
         patch("google.generativeai.GenerativeModel") as mock_model_cls:
        
        mock_model_inst = MagicMock()
        mock_model_inst.generate_content_async = AsyncMock(return_value=mock_response)
        mock_model_cls.return_value = mock_model_inst

        output = await provider.query(prompt="Recommend accounting tools", domain="testdomain.com")

        mock_config.assert_called_once_with(api_key="mock_key_12345")
        mock_model_cls.assert_called_once_with("gemini-1.5-flash")
        assert isinstance(output, ProviderOutput)
        assert output.provider_name == "gemini"
        assert "Simulated live Gemini 1.5 response" in output.raw_response


@pytest.mark.asyncio
async def test_execute_job_with_gemini_provider(async_client: AsyncClient, db_session):
    """Test executing an Analysis Job using GeminiProvider and persisting ProviderResult."""
    # 1. Create project
    proj_res = await async_client.post("/api/v1/projects", json={"name": "Gemini Co", "url": "https://gemini-test.com"})
    assert proj_res.status_code == 201
    project_id = uuid.UUID(proj_res.json()["id"])

    # 2. Trigger job
    job = await analysis_job_service.create_job(db_session, project_id=project_id)

    # 3. Instantiate GeminiProvider with mock key
    gemini_inst = GeminiProvider(api_key="mock_test_key", model_name="gemini-1.5-flash")

    mock_resp = MagicMock()
    mock_resp.text = "Gemini AI recommendation text for gemini-test.com."

    with patch("google.generativeai.configure"), \
         patch("google.generativeai.GenerativeModel") as mock_model_cls:
        
        mock_model_inst = MagicMock()
        mock_model_inst.generate_content_async = AsyncMock(return_value=mock_resp)
        mock_model_cls.return_value = mock_model_inst

        # Execute job with GeminiProvider
        result = await analysis_job_service.execute_job(
            db_session,
            job_id=job.id,
            prompt="Top recommendations for 2026",
            provider=gemini_inst
        )

        assert result.job_id == job.id
        assert result.provider_name == "gemini"
        assert "gemini-test.com" in result.raw_response

        # Verify job completed state
        updated_job = await analysis_job_service.get_job(db_session, job_id=job.id)
        assert updated_job.status == AnalysisJobStatus.COMPLETED

        # Verify DB evidence
        results = await provider_result_repository.list_by_job(db_session, job_id=job.id)
        assert len(results) >= 1
        assert results[0].provider_name == "gemini"
