import uuid
from typing import List
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.analysis_job import AnalysisJobResponse
from app.services.analysis_job_service import analysis_job_service, AnalysisJobService

router = APIRouter()


@router.post(
    "/projects/{project_id}/jobs",
    response_model=AnalysisJobResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Trigger a new Analysis Job for a Project",
    description="Creates and triggers a new Analysis Job in Pending state. Rejects creation if an active job is already running for the project.",
    responses={
        201: {
            "description": "Analysis Job created successfully in Pending state.",
            "content": {
                "application/json": {
                    "example": {
                        "id": "b1ffcd88-8b0a-3ef7-aa5c-5aa8ac270900",
                        "project_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
                        "status": "Pending",
                        "error_message": None,
                        "started_at": None,
                        "completed_at": None,
                        "created_at": "2026-08-07T23:45:00Z",
                        "updated_at": "2026-08-07T23:45:00Z"
                    }
                }
            }
        },
        404: {
            "description": "Not Found — Project with given UUID does not exist.",
            "content": {
                "application/json": {
                    "example": {"detail": "Project with ID 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11' not found."}
                }
            }
        },
        409: {
            "description": "Conflict — An active Analysis Job is already in progress for this project.",
            "content": {
                "application/json": {
                    "example": {"detail": "An active Analysis Job (ID: b1ffcd88-8b0a-3ef7-aa5c-5aa8ac270900) is already in progress for this project."}
                }
            }
        }
    }
)
async def create_job(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    service: AnalysisJobService = Depends(lambda: analysis_job_service)
) -> AnalysisJobResponse:
    job = await service.create_job(db, project_id=project_id)
    return AnalysisJobResponse.model_validate(job)


@router.get(
    "/projects/{project_id}/jobs",
    response_model=List[AnalysisJobResponse],
    status_code=status.HTTP_200_OK,
    summary="List Analysis Jobs for a Project",
    description="Returns a paginated list of all past and active Analysis Jobs for a project ordered by creation date descending.",
    responses={
        200: {
            "description": "List of Analysis Jobs returned successfully.",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "b1ffcd88-8b0a-3ef7-aa5c-5aa8ac270900",
                            "project_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
                            "status": "Completed",
                            "error_message": None,
                            "started_at": "2026-08-07T23:45:01Z",
                            "completed_at": "2026-08-07T23:45:10Z",
                            "created_at": "2026-08-07T23:45:00Z",
                            "updated_at": "2026-08-07T23:45:10Z"
                        }
                    ]
                }
            }
        },
        404: {"description": "Not Found — Project with given UUID does not exist."}
    }
)
async def list_jobs_for_project(
    project_id: uuid.UUID,
    skip: int = Query(0, ge=0, description="Items to skip for pagination"),
    limit: int = Query(100, ge=1, le=100, description="Max items to return"),
    db: AsyncSession = Depends(get_db),
    service: AnalysisJobService = Depends(lambda: analysis_job_service)
) -> List[AnalysisJobResponse]:
    jobs = await service.list_jobs_for_project(db, project_id=project_id, skip=skip, limit=limit)
    return [AnalysisJobResponse.model_validate(j) for j in jobs]


@router.get(
    "/jobs/{job_id}",
    response_model=AnalysisJobResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Analysis Job details",
    description="Fetches a single Analysis Job by its unique UUID identifier.",
    responses={
        200: {"description": "Analysis Job found and returned."},
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
async def get_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    service: AnalysisJobService = Depends(lambda: analysis_job_service)
) -> AnalysisJobResponse:
    job = await service.get_job(db, job_id=job_id)
    return AnalysisJobResponse.model_validate(job)


@router.post(
    "/jobs/{job_id}/cancel",
    response_model=AnalysisJobResponse,
    status_code=status.HTTP_200_OK,
    summary="Cancel an active Analysis Job",
    description="Cancels an active Analysis Job in Pending or Running state. Rejects cancellation if job is already in a terminal state (Completed, Failed, Cancelled).",
    responses={
        200: {"description": "Analysis Job cancelled successfully."},
        400: {
            "description": "Bad Request — Job is already in a terminal state.",
            "content": {
                "application/json": {
                    "example": {"detail": "Cannot transition job status from 'Completed' to 'Cancelled'."}
                }
            }
        },
        404: {"description": "Not Found — Analysis Job with given UUID does not exist."}
    }
)
async def cancel_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    service: AnalysisJobService = Depends(lambda: analysis_job_service)
) -> AnalysisJobResponse:
    job = await service.cancel_job(db, job_id=job_id)
    return AnalysisJobResponse.model_validate(job)
