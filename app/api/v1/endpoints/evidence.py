import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.extracted_evidence import ExtractedEvidenceResponse
from app.services.analysis_job_service import analysis_job_service, AnalysisJobService

router = APIRouter()


@router.get(
    "/jobs/{job_id}/evidence",
    response_model=List[ExtractedEvidenceResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Extracted Evidence for an Analysis Job",
    description="Fetches raw observable evidence records extracted from AI responses for a specific Analysis Job.",
    responses={
        200: {
            "description": "Extracted evidence records returned successfully.",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "c2ffcd99-9b0a-4ef8-bb6d-7bb9bd380b22",
                            "job_id": "b1ffcd88-8b0a-3ef7-aa5c-5aa8ac270900",
                            "provider_result_id": "d3ffcd00-0c0b-5ef9-cc7d-8cc9bd380c33",
                            "target_domain": "acmesoftware.io",
                            "mentioned": True,
                            "raw_citations": ["https://g2.com/products/acmesoftware"],
                            "matched_snippets": ["Acme Software is cited as a key recommendation for visual pipelines."],
                            "extracted_brand_mentions": ["Acme", "Zapier", "Make"],
                            "created_at": "2026-08-07T23:59:00Z"
                        }
                    ]
                }
            }
        },
        404: {
            "description": "Not Found — Analysis Job with given UUID does not exist.",
            "content": {
                "application/json": {
                    "example": {"detail": "Analysis Job with ID 'b1ffcd88-8b0a-3ef7-aa5c-5aa8ac270900' not found."}
                }
            }
        }
    }
)
async def get_evidence_for_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    service: AnalysisJobService = Depends(lambda: analysis_job_service)
) -> List[ExtractedEvidenceResponse]:
    evidence_list = await service.get_evidence_for_job(db, job_id=job_id)
    return [ExtractedEvidenceResponse.model_validate(e) for e in evidence_list]
