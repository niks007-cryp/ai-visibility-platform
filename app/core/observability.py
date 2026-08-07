import os
import time
import json
import logging
import socket
from typing import Dict, Any, Optional

from app.core.config import settings

logger = logging.getLogger("app.core.observability")


class JSONFormatter(logging.Formatter):
    """Structured JSON Log Formatter enriching logs with request_id, user_id, job_id, and telemetry metrics."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "environment": settings.ENVIRONMENT,
            "service_version": settings.VERSION,
            "hostname": socket.gethostname(),
        }

        # Extra context fields
        for field in ("request_id", "correlation_id", "user_id", "project_id", "job_id", "provider", "duration_ms"):
            val = getattr(record, field, None)
            if val is not None:
                log_obj[field] = val

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj)


class PrometheusMetricsExporter:
    """Prometheus telemetry counter and gauge metric recorder."""

    def __init__(self):
        self.http_requests_count = 0
        self.auth_failures_count = 0
        self.rate_limit_hits_count = 0
        self.provider_queries_count = 0

    def record_http_request(self):
        self.http_requests_count += 1

    def record_auth_failure(self):
        self.auth_failures_count += 1

    def record_rate_limit_hit(self):
        self.rate_limit_hits_count += 1

    def record_provider_query(self):
        self.provider_queries_count += 1

    def export_text(self) -> str:
        return (
            "# HELP http_requests_total Total HTTP requests handled\n"
            "# TYPE http_requests_total counter\n"
            f'http_requests_total {self.http_requests_count}\n'
            "# HELP auth_failures_total Total authentication failures\n"
            "# TYPE auth_failures_total counter\n"
            f'auth_failures_total {self.auth_failures_count}\n'
            "# HELP rate_limit_hits_total Total rate limit hits\n"
            "# TYPE rate_limit_hits_total counter\n"
            f'rate_limit_hits_total {self.rate_limit_hits_count}\n'
            "# HELP provider_queries_total Total AI provider queries executed\n"
            "# TYPE provider_queries_total counter\n"
            f'provider_queries_total {self.provider_queries_count}\n'
            "# HELP app_info Application metadata\n"
            "# TYPE app_info gauge\n"
            f'app_info{{version="{settings.VERSION}",env="{settings.ENVIRONMENT}"}} 1\n'
        )


metrics_exporter = PrometheusMetricsExporter()
