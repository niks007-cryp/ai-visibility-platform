import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.recommendation import Recommendation
from app.services.recommendation_service import recommendation_service, RecommendationService

router = APIRouter()


@router.get(
    "/jobs/{job_id}/recommendations",
    response_model=List[Recommendation],
    status_code=status.HTTP_200_OK,
    summary="Get Deterministic Remediation Recommendations",
    description="Evaluates ExtractedEvidence against deterministic business rules and returns prioritized P0/P1/P2 remediation recommendations.",
    responses={
        200: {
            "description": "Recommendations generated and returned successfully.",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "e4ffcd00-0d0c-6fa0-dd8e-9dd0ce491d44",
                            "title": "Improve Entity Recognition Across Authoritative Sources",
                            "description": "Target domain 'acmesoftware.io' was not cited or recommended in AI provider output. Publish a dedicated category landing page and update listings on top third-party review directories.",
                            "category": "Entity Optimization",
                            "priority": "P0",
                            "effort": "Medium",
                            "expected_impact": "High",
                            "trigger": "mentioned == False",
                            "evidence_reference": "ExtractedEvidence ID: c2ffcd99-9b0a-4ef8-bb6d-7bb9bd380b22 (mentioned=False)",
                            "verification_method": "Re-audit AI visibility 14 days post-publication to verify brand mention."
                        }
                    ]
                }
            }
        },
        404: {
            "description": "Not Found — Analysis Job or ExtractedEvidence missing.",
            "content": {
                "application/json": {
                    "example": {"detail": "No extracted evidence found for Analysis Job 'b1ffcd88-8b0a-3ef7-aa5c-5aa8ac270900'."}
                }
            }
        }
    }
)
async def get_recommendations_for_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    service: RecommendationService = Depends(lambda: recommendation_service)
) -> List[Recommendation]:
    return await service.get_recommendations_for_job(db, job_id=job_id)
