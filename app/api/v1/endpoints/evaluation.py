import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.evaluation import EvaluationSummary
from app.services.evaluation_service import evaluation_service, EvaluationService

router = APIRouter()


@router.get(
    "/jobs/{job_id}/evaluation",
    response_model=EvaluationSummary,
    status_code=status.HTTP_200_OK,
    summary="Get Multi-Prompt Execution Evaluation Summary",
    description="Calculates multi-prompt execution consistency percentage, confidence level (HIGH/MEDIUM/LOW), and detects contradictions for an Analysis Job.",
    responses={
        200: {
            "description": "Evaluation summary calculated and returned successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "job_id": "b1ffcd88-8b0a-3ef7-aa5c-5aa8ac270900",
                        "total_prompts": 4,
                        "successful_executions": 4,
                        "mentioned_count": 4,
                        "mention_rate": 1.0,
                        "provider_count": 1,
                        "prompt_categories_tested": ["BUYING", "COMPARISON", "DIRECT", "USE_CASE"],
                        "consistency_percentage": 100.0,
                        "confidence_level": "HIGH",
                        "contradictions": [],
                        "generated_at": "2026-08-07T23:59:00Z"
                    }
                }
            }
        },
        404: {
            "description": "Not Found — Analysis Job or ProviderResult records missing.",
            "content": {
                "application/json": {
                    "example": {"detail": "No execution results or extracted evidence found for job 'b1ffcd88-8b0a-3ef7-aa5c-5aa8ac270900'."}
                }
            }
        }
    }
)
async def get_evaluation_summary(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    service: EvaluationService = Depends(lambda: evaluation_service)
) -> EvaluationSummary:
    return await service.get_evaluation_summary(db, job_id=job_id)
