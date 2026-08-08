import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

from httpx import AsyncClient

from app.providers.gemini import (
    GeminiAPIException,
    GeminiNotConfiguredException,
    GeminiProvider,
)
from app.providers.base import ProviderOutput
from app.services.analysis_job_service import analysis_job_service
from app.models.analysis_job import AnalysisJobStatus
from app.repositories.provider_result_repository import (
    provider_result_repository,
)


@pytest.mark.asyncio
async def test_gemini_provider_unconfigured(monkeypatch):
    """
    Test GeminiProvider raises GeminiNotConfiguredException
    when no API key is configured.
    """

    monkeypatch.setattr(
        "app.core.config.settings.GEMINI_API_KEY",
        None,
    )

    provider = GeminiProvider(
        model_name="gemini-2.5-flash",
    )

    assert provider.name == "gemini"
    assert provider.model_name == "gemini-2.5-flash"

    with pytest.raises(GeminiNotConfiguredException):
        await provider.query(
            prompt="Test prompt",
            domain="testdomain.com",
        )


@pytest.mark.asyncio
async def test_gemini_provider_query_mocked_sdk():
    """
    Test GeminiProvider executes successfully
    using mocked Google GenAI SDK.
    """

    provider = GeminiProvider(
        api_key="mock_key_12345",
        model_name="gemini-2.5-flash",
    )

    mock_response = MagicMock()
    mock_response.text = (
        "Simulated Gemini 2.5 Flash response."
    )

    with patch("google.genai.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.aio.models.generate_content = AsyncMock(
            return_value=mock_response
        )
        mock_client_cls.return_value = mock_client

        output = await provider.query(
            prompt="Recommend accounting software",
            domain="testdomain.com",
        )

        mock_client_cls.assert_called_once_with(
            api_key="mock_key_12345"
        )
        mock_client.aio.models.generate_content.assert_called_once_with(
            model="gemini-2.5-flash",
            contents="Analyze visibility and recommendations for business website 'testdomain.com'. Query: Recommend accounting software"
        )

        assert isinstance(output, ProviderOutput)
        assert output.provider_name == "gemini"
        assert (
            "Simulated Gemini 2.5 Flash response"
            in output.raw_response
        )


@pytest.mark.asyncio
async def test_execute_job_with_gemini_provider(
    async_client: AsyncClient,
    db_session,
):
    """
    Test executing an Analysis Job
    using mocked Gemini provider.
    """

    project_response = await async_client.post(
        "/api/v1/projects",
        json={
            "name": "Gemini Co",
            "url": "https://gemini-test.com",
        },
    )

    assert project_response.status_code == 201

    project_id = uuid.UUID(
        project_response.json()["id"]
    )

    job = await analysis_job_service.create_job(
        db_session,
        project_id=project_id,
    )

    provider = GeminiProvider(
        api_key="mock_test_key",
        model_name="gemini-2.5-flash",
    )

    mock_response = MagicMock()
    mock_response.text = (
        "Gemini AI recommendation text for gemini-test.com."
    )

    with patch("google.genai.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.aio.models.generate_content = AsyncMock(
            return_value=mock_response
        )
        mock_client_cls.return_value = mock_client

        result = await analysis_job_service.execute_job(
            db=db_session,
            job_id=job.id,
            prompt="Top recommendations for 2026",
            provider=provider,
        )

        assert result.job_id == job.id
        assert result.provider_name == "gemini"
        assert (
            "gemini-test.com"
            in result.raw_response
        )

        updated_job = await analysis_job_service.get_job(
            db_session,
            job_id=job.id,
        )

        assert (
            updated_job.status
            == AnalysisJobStatus.COMPLETED
        )

        provider_results = (
            await provider_result_repository.list_by_job(
                db_session,
                job_id=job.id,
            )
        )

        assert len(provider_results) >= 1
        assert (
            provider_results[0].provider_name
            == "gemini"
        )
