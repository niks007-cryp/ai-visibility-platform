import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.report import JobReportResponse
from app.services.report_service import report_service, ReportService

router = APIRouter()


@router.get(
    "/jobs/{job_id}/report",
    response_model=JobReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Get MVP Analysis Job Report",
    description="Assembles existing Project, AnalysisJob, ProviderResult, and ExtractedEvidence into a unified frontend-ready report payload.",
    responses={
        200: {
            "description": "MVP Report assembled and returned successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "job_id": "b1ffcd88-8b0a-3ef7-aa5c-5aa8ac270900",
                        "project_id": "a0ffcd77-7a0a-2ef6-994b-4aa7ac160800",
                        "project_name": "Acme Software",
                        "target_domain": "acmesoftware.io",
                        "job_status": "Completed",
                        "provider_name": "gemini",
                        "prompt": "What are the best software tools for visual workflow pipelines?",
                        "raw_response": "Acme Software is a top choice for visual workflow automation.",
                        "mentioned": True,
                        "raw_citations": ["https://g2.com/products/acmesoftware"],
                        "matched_snippets": ["Acme Software is a top choice for visual workflow automation."],
                        "extracted_brand_mentions": ["Acme", "Zapier"],
                        "created_at": "2026-08-07T23:59:00Z"
                    }
                }
            }
        },
        400: {
            "description": "Bad Request — Job is not in COMPLETED state.",
            "content": {
                "application/json": {
                    "example": {"detail": "Cannot generate report for job in 'Running' state. Job must be COMPLETED."}
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
async def get_job_report(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    service: ReportService = Depends(lambda: report_service)
) -> JobReportResponse:
    return await service.get_report_for_job(db, job_id=job_id)
