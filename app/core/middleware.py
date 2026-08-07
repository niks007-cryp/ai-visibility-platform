import uuid
import time
import logging
from datetime import datetime, timezone
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("app.middleware")


class RequestCorrelationMiddleware(BaseHTTPMiddleware):
    """Middleware attaching request_id and correlation_id to request state and response headers."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()
        
        # Read or generate request_id & correlation_id
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        correlation_id = request.headers.get("X-Correlation-ID") or request_id

        request.state.request_id = request_id
        request.state.correlation_id = correlation_id

        response = await call_next(request)

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        # Attach tracking headers to response
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Correlation-ID"] = correlation_id

        logger.info(
            "event=http_request method=%s path=%s status=%d latency_ms=%.2f request_id=%s",
            request.method, request.url.path, response.status_code, elapsed_ms, request_id
        )

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware adding standard security hardening headers to all HTTP responses."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler converting unhandled exceptions into standard error envelope."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    logger.error("event=unhandled_exception request_id=%s error=%s", request_id, str(exc), exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "request_id": request_id,
            "error": "InternalServerError",
            "message": "An unhandled internal server error occurred.",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )
