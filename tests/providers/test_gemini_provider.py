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
    using mocked Gemini SDK.
    """

    provider = GeminiProvider(
        api_key="mock_key_12345",
        model_name="gemini-2.5-flash",
    )

    mock_response = MagicMock()
    mock_response.text = (
        "Simulated Gemini 2.5 Flash response."
    )

    with patch(
        "google.generativeai.configure"
    ) as mock_config, patch(
        "google.generativeai.GenerativeModel"
    ) as mock_model_cls:

        mock_model = MagicMock()

        mock_model.generate_content_async = AsyncMock(
            return_value=mock_response
        )

        mock_model_cls.return_value = mock_model

        output = await provider.query(
            prompt="Recommend accounting software",
            domain="testdomain.com",
        )

        mock_config.assert_called_once_with(
            api_key="mock_key_12345"
        )

        mock_model_cls.assert_called_once_with(
            "gemini-2.5-flash"
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

    with patch(
        "google.generativeai.configure"
    ), patch(
        "google.generativeai.GenerativeModel"
    ) as mock_model_cls:

        mock_model = MagicMock()

        mock_model.generate_content_async = AsyncMock(
            return_value=mock_response
        )

        mock_model_cls.return_value = mock_model

        result = await analysis_job_service.execute_job(
            db_session=db_session,
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
