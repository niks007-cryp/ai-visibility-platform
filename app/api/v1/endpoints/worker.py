from typing import Dict, Any
from fastapi import APIRouter, Depends, status

from app.services.queue_service import queue_service, QueueService

router = APIRouter()


@router.get(
    "/worker/health",
    status_code=status.HTTP_200_OK,
    summary="Worker & Queue Health Telemetry",
    description="Returns background worker status, queue depth, dead-letter queue depth, and retry metrics.",
    responses={
        200: {
            "description": "Worker telemetry retrieved successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "queue_depth": 0,
                        "dlq_depth": 0,
                        "processed_count": 12,
                        "failed_count": 0,
                        "retry_count": 0,
                        "status": "healthy"
                    }
                }
            }
        }
    }
)
async def get_worker_health(
    service: QueueService = Depends(lambda: queue_service)
) -> Dict[str, Any]:
    return service.get_telemetry()
