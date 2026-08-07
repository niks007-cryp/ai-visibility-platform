import time
import logging
from typing import Dict, List
from fastapi import Request, HTTPException, status

logger = logging.getLogger("app.core.rate_limiter")


class RateLimiter:
    """In-memory sliding window rate limiter enforcing IP-based request quotas."""

    def __init__(self):
        # Maps key (e.g. "auth_login:127.0.0.1") to list of request timestamps
        self._requests: Dict[str, List[float]] = {}

    def check_rate_limit(
        self,
        request: Request,
        key_prefix: str = "global",
        max_requests: int = 60,
        window_seconds: int = 60
    ):
        """Validates client request rate against limit threshold. Raises 429 if exceeded."""
        client_ip = request.client.host if request.client else "127.0.0.1"
        key = f"{key_prefix}:{client_ip}"
        now = time.time()
        window_start = now - window_seconds

        # Clean old timestamps outside current window
        if key not in self._requests:
            self._requests[key] = []

        timestamps = [ts for ts in self._requests[key] if ts > window_start]
        self._requests[key] = timestamps

        if len(timestamps) >= max_requests:
            logger.warning(
                "event=rate_limit_exceeded key=%s count=%d max=%d client_ip=%s",
                key, len(timestamps), max_requests, client_ip
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {max_requests} requests per {window_seconds} seconds allowed.",
                headers={"Retry-After": str(window_seconds)}
            )

        self._requests[key].append(now)

    def reset(self):
        """Clears all tracked rate limit records (used in tests)."""
        self._requests.clear()


rate_limiter = RateLimiter()
