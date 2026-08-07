import pytest
import uuid
from unittest.mock import MagicMock
from httpx import AsyncClient
from app.models.extracted_evidence import ExtractedEvidence
from app.schemas.recommendation import PriorityLevel
from app.services.recommendation_engine import RecommendationRuleEngine
from app.services.analysis_job_service import analysis_job_service


def test_recommendation_rule_engine_omitted_case():
    """Test RecommendationRuleEngine generates P0 recommendation when brand is omitted."""
    engine = RecommendationRuleEngine()

    mock_evidence = MagicMock(spec=ExtractedEvidence)
    mock_evidence.id = uuid.uuid4()
    mock_evidence.target_domain = "omittedbrand.io"
    mock_evidence.mentioned = False
    mock_evidence.raw_citations = []
    mock_evidence.matched_snippets = []
    mock_evidence.extracted_brand_mentions = ["CompetitorA", "CompetitorB"]

    recs = engine.generate_recommendations(mock_evidence)
    assert len(recs) >= 1
    p0_rec = recs[0]
    assert p0_rec.priority == PriorityLevel.P0
    assert "omittedbrand.io" in p0_rec.description
    assert p0_rec.trigger == "mentioned == False"


def test_recommendation_rule_engine_competitor_density_case():
    """Test RecommendationRuleEngine generates P2 competitor recommendation when competitor_count > 3."""
    engine = RecommendationRuleEngine()

    mock_evidence = MagicMock(spec=ExtractedEvidence)
    mock_evidence.id = uuid.uuid4()
    mock_evidence.target_domain = "popularbrand.com"
    mock_evidence.mentioned = True
    mock_evidence.raw_citations = ["https://g2.com/products/popular"]
    mock_evidence.matched_snippets = ["Popular Brand is a top recommendation."]
    mock_evidence.extracted_brand_mentions = ["BrandA", "BrandB", "BrandC", "BrandD", "BrandE"]

    recs = engine.generate_recommendations(mock_evidence)
    assert len(recs) == 1
    p2_rec = recs[0]
    assert p2_rec.priority == PriorityLevel.P2
    assert "High competitor density" in p2_rec.description


@pytest.mark.asyncio
async def test_recommendations_api_endpoint(async_client: AsyncClient, db_session):
    """Test end-to-end job execution and GET /api/v1/jobs/{job_id}/recommendations endpoint."""
    # 1. Create project
    proj_res = await async_client.post("/api/v1/projects", json={"name": "Rec Test Co", "url": "https://rectest.io"})
    assert proj_res.status_code == 201
    project_id = uuid.UUID(proj_res.json()["id"])

    # 2. Trigger job
    job = await analysis_job_service.create_job(db_session, project_id=project_id)

    # 3. Execute job (creates ProviderResult & ExtractedEvidence)
    await analysis_job_service.execute_job(
        db_session,
        job_id=job.id,
        prompt="Top workflow management software"
    )

    # 4. Query GET /jobs/{job_id}/recommendations endpoint
    rec_res = await async_client.get(f"/api/v1/jobs/{job.id}/recommendations")
    assert rec_res.status_code == 200
    recs = rec_res.json()
    assert isinstance(recs, list)
    assert len(recs) >= 1
    first_rec = recs[0]
    assert "priority" in first_rec
    assert "trigger" in first_rec
    assert "verification_method" in first_rec
