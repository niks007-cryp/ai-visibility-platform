import time
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db
from app.core.config import settings
from app.core.observability import metrics_exporter
from app.services.queue_service import queue_service

router = APIRouter()


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health Check Probe",
    description="Returns service status and dependency health."
)
async def health_check(db: AsyncSession = Depends(get_db)):
    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"

    worker_telemetry = queue_service.get_telemetry()

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "dependencies": {
            "database": db_status,
            "gemini_provider": "configured" if settings.GEMINI_API_KEY else "unconfigured",
            "worker": worker_telemetry["status"]
        }
    }


@router.get(
    "/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness Probe",
    description="Verifies database and queue worker readiness for handling production traffic."
)
async def readiness_probe(response: Response, db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {
            "status": "ready",
            "database": "connected",
            "worker": "ready",
            "timestamp": time.time()
        }
    except Exception as exc:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "not_ready", "reason": str(exc), "timestamp": time.time()}


@router.get(
    "/live",
    status_code=status.HTTP_200_OK,
    summary="Liveness Probe",
    description="Verifies application process is running."
)
async def liveness_probe():
    return {"status": "alive", "timestamp": time.time()}


@router.get(
    "/metrics",
    status_code=status.HTTP_200_OK,
    summary="Prometheus Telemetry Metrics",
    description="Exposes Prometheus telemetry metrics."
)
async def prometheus_metrics():
    metrics_text = metrics_exporter.export_text()
    return Response(content=metrics_text, media_type="text/plain")
