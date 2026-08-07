import pytest
import uuid
from httpx import AsyncClient
from app.core.prompt_catalog import PROMPT_CATALOG, get_active_prompts
from app.schemas.prompt import PromptCategory
from app.services.prompt_service import prompt_service
from app.services.analysis_job_service import analysis_job_service
from app.repositories.provider_result_repository import provider_result_repository
from app.repositories.extracted_evidence_repository import extracted_evidence_repository


def test_prompt_catalog_active_templates():
    """Test prompt catalog contains active templates for all 4 categories."""
    active_prompts = get_active_prompts()
    assert len(active_prompts) >= 4

    categories = {p.category for p in active_prompts}
    assert PromptCategory.DIRECT in categories
    assert PromptCategory.COMPARISON in categories
    assert PromptCategory.USE_CASE in categories
    assert PromptCategory.BUYING in categories


def test_prompt_service():
    """Test PromptService returns active prompt templates."""
    prompts = prompt_service.list_active_prompts()
    assert len(prompts) >= 4
    for p in prompts:
        assert p.id.startswith("PROMPT_")
        assert p.version == "1.0.0"
        assert p.active is True


@pytest.mark.asyncio
async def test_get_prompts_api_endpoint(async_client: AsyncClient):
    """Test GET /api/v1/prompts endpoint returns active catalog."""
    res = await async_client.get("/api/v1/prompts")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 4
    assert data[0]["id"].startswith("PROMPT_")


@pytest.mark.asyncio
async def test_execute_job_multi_prompt_evaluation(async_client: AsyncClient, db_session):
    """Test executing Analysis Job runs provider & evidence pipeline across all catalog prompts."""
    # 1. Create project
    proj_res = await async_client.post("/api/v1/projects", json={"name": "Multi Prompt Co", "url": "https://multiprompt.io"})
    assert proj_res.status_code == 201
    project_id = uuid.UUID(proj_res.json()["id"])

    # 2. Trigger job
    job = await analysis_job_service.create_job(db_session, project_id=project_id)

    # 3. Execute job (iterates over active catalog prompts)
    await analysis_job_service.execute_job(db_session, job_id=job.id)

    # 4. Verify ProviderResult evidence records created for each prompt
    results = await provider_result_repository.list_by_job(db_session, job_id=job.id)
    assert len(results) >= 4

    categories = {r.prompt_category for r in results}
    assert "DIRECT" in categories
    assert "COMPARISON" in categories
    assert "USE_CASE" in categories
    assert "BUYING" in categories

    # 5. Verify ExtractedEvidence records created for each prompt
    evidences = await extracted_evidence_repository.list_by_job(db_session, job_id=job.id)
    assert len(evidences) >= 4
