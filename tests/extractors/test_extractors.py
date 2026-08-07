import pytest
import uuid
from httpx import AsyncClient
from app.extractors.brand_mention import BrandMentionExtractor
from app.extractors.citation import CitationExtractor
from app.extractors.snippet import SnippetExtractor
from app.services.evidence_pipeline import EvidencePipeline
from app.services.analysis_job_service import analysis_job_service


def test_brand_mention_extractor():
    """Test BrandMentionExtractor deterministically finds target domain and brand tokens."""
    extractor = BrandMentionExtractor()

    # Mentioned case
    text_1 = "Acme Software is cited as a top automation choice. Competitors like Zapier also rank well."
    mentioned_1, brands_1 = extractor.extract(text_1, "acmesoftware.io")
    assert mentioned_1 is True
    assert "Acme" in brands_1
    assert "Zapier" in brands_1

    # Omitted case
    text_2 = "Make and Zapier lead the market for workflow software."
    mentioned_2, brands_2 = extractor.extract(text_2, "acmesoftware.io")
    assert mentioned_2 is False
    assert "Zapier" in brands_2


def test_citation_extractor():
    """Test CitationExtractor parses HTTP/HTTPS URLs from raw text."""
    extractor = CitationExtractor()

    text = "For details visit https://g2.com/products/acme or review https://trustpilot.com/acme."
    citations = extractor.extract(text)
    assert len(citations) == 2
    assert "https://g2.com/products/acme" in citations
    assert "https://trustpilot.com/acme" in citations


def test_snippet_extractor():
    """Test SnippetExtractor extracts verbatim sentence quotes referencing target domain."""
    extractor = SnippetExtractor()

    text = "Zapier leads in integration count. Acme Software provides ultra-fast visual pipelines. Make is also popular."
    snippets = extractor.extract(text, "acmesoftware.io")
    assert len(snippets) == 1
    assert snippets[0] == "Acme Software provides ultra-fast visual pipelines."


def test_evidence_pipeline():
    """Test EvidencePipeline orchestrates extractors deterministically."""
    pipeline = EvidencePipeline()

    raw_text = "Acme Software is listed on https://g2.com/acme as a premier platform. Competitors include Zapier."
    payload = pipeline.process(raw_text=raw_text, target_domain="acmesoftware.io")

    assert payload["mentioned"] is True
    assert "https://g2.com/acme" in payload["raw_citations"]
    assert len(payload["matched_snippets"]) == 1
    assert "Acme" in payload["extracted_brand_mentions"]


@pytest.mark.asyncio
async def test_evidence_api_endpoint(async_client: AsyncClient, db_session):
    """Test end-to-end job execution, evidence extraction, and GET /jobs/{job_id}/evidence endpoint."""
    # 1. Create project
    proj_res = await async_client.post("/api/v1/projects", json={"name": "Evidence Test Co", "url": "https://evidencetest.io"})
    assert proj_res.status_code == 201
    project_id = uuid.UUID(proj_res.json()["id"])

    # 2. Trigger job
    job = await analysis_job_service.create_job(db_session, project_id=project_id)

    # 3. Execute job (runs EvidencePipeline across prompt evaluation catalog)
    await analysis_job_service.execute_job(
        db_session,
        job_id=job.id,
        prompt="Recommend modern workflow automation tools"
    )

    # 4. Query GET /jobs/{job_id}/evidence endpoint
    ev_res = await async_client.get(f"/api/v1/jobs/{job.id}/evidence")
    assert ev_res.status_code == 200
    ev_data = ev_res.json()
    assert len(ev_data) >= 1
    evidence = ev_data[0]
    assert evidence["job_id"] == str(job.id)
    assert evidence["target_domain"] == "evidencetest.io"
    assert evidence["mentioned"] is True
    assert isinstance(evidence["raw_citations"], list)
    assert isinstance(evidence["matched_snippets"], list)
    assert isinstance(evidence["extracted_brand_mentions"], list)
