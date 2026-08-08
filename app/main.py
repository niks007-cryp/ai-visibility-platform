import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.core.config_guard import validate_production_configuration
from app.core.middleware import (
    RequestCorrelationMiddleware,
    SecurityHeadersMiddleware,
    global_exception_handler,
)
from app.api.v1.router import api_router
from app.api.v1.endpoints.health import (
    health_check,
    readiness_probe,
    liveness_probe,
    prometheus_metrics,
)

# Initialize structured logging
setup_logging()
logger = logging.getLogger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup validation and shutdown cleanup."""
    logger.info("event=startup service=%s version=%s environment=%s", settings.PROJECT_NAME, settings.VERSION, settings.ENVIRONMENT)
    
    # Startup Configuration Fail-Fast Guard
    validate_production_configuration()

    yield
    logger.info("event=shutdown service=%s", settings.PROJECT_NAME)


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Performance: Gzip Compression Middleware for payloads > 1KB
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Production Security & Middleware Stack
app.add_middleware(RequestCorrelationMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# CORS Middleware (Must be added last so it executes FIRST in ASGI pipeline)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handler
app.add_exception_handler(Exception, global_exception_handler)

# Root level health & readiness endpoints for container probes
app.add_api_route("/health", health_check, methods=["GET"], tags=["Health"])
app.add_api_route("/ready", readiness_probe, methods=["GET"], tags=["Health"])
app.add_api_route("/live", liveness_probe, methods=["GET"], tags=["Health"])
app.add_api_route("/metrics", prometheus_metrics, methods=["GET"], tags=["Health"])

# API v1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", include_in_schema=False)
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health"
    }
