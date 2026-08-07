import uuid
import time
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("app.service.queue")

# ─────────────────────────────────────────────────────────────────
# Redis-backed QueueService
#
# Design constraints:
#   - Drop-in replacement for asyncio.Queue-based QueueService
#   - Preserves every public method signature exactly
#   - Uses Redis LIST (RPUSH / BLPOP) as the queue primitive
#   - DLQ is a separate Redis LIST key
#   - Telemetry counters stored in Redis HASH (survive restarts)
#   - Falls back to in-memory mode if Redis is unavailable (dev/test)
# ─────────────────────────────────────────────────────────────────

QUEUE_KEY = "ai_visibility:job_queue"
DLQ_KEY   = "ai_visibility:job_dlq"
STATS_KEY = "ai_visibility:queue_stats"


class QueueService:
    """
    Redis-backed background task queue manager.
    Supports retries, dead letter queueing, and telemetry.
    Drop-in replacement for the previous asyncio.Queue implementation.
    Falls back to in-memory mode when REDIS_URL is not set (test/dev).
    """

    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self._redis = None
        self._fallback_queue: list = []           # in-memory fallback
        self._dead_letter_queue: List[Dict[str, Any]] = []
        self._processed_count: int = 0
        self._failed_count: int = 0
        self._retry_count: int = 0
        self._use_redis = False
        self._connect_redis()

    def _connect_redis(self):
        """Attempt Redis connection. Fall back silently to in-memory if unavailable."""
        try:
            from app.core.config import settings
            redis_url = getattr(settings, "REDIS_URL", None)
            if not redis_url:
                logger.warning("event=queue_redis_url_missing fallback=in_memory")
                return

            import redis as redis_lib
            self._redis = redis_lib.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=3,
                socket_timeout=3
            )
            self._redis.ping()
            self._use_redis = True
            logger.info("event=queue_redis_connected url=%s", redis_url)
        except Exception as exc:
            logger.warning("event=queue_redis_unavailable reason=%s fallback=in_memory", str(exc))
            self._redis = None
            self._use_redis = False

    async def enqueue_analysis_job(
        self,
        job_id: uuid.UUID,
        prompt: Optional[str] = None,
        provider_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Pushes an AnalysisJob task payload to the queue (Redis LIST or in-memory fallback)."""
        payload = {
            "task_id": str(uuid.uuid4()),
            "job_id": str(job_id),
            "prompt": prompt,
            "provider_name": provider_name,
            "enqueued_at": time.time(),
            "attempts": 0,
            "max_retries": self.max_retries,
        }

        if self._use_redis:
            self._redis.rpush(QUEUE_KEY, json.dumps(payload))
            queue_size = self._redis.llen(QUEUE_KEY)
        else:
            self._fallback_queue.append(payload)
            queue_size = len(self._fallback_queue)

        logger.info(
            "event=job_enqueued task_id=%s job_id=%s queue_size=%d backend=%s",
            payload["task_id"], job_id, queue_size,
            "redis" if self._use_redis else "in_memory"
        )
        return payload

    async def dequeue(self, timeout: float = 1.0) -> Optional[Dict[str, Any]]:
        """Pops a task payload from the queue (blocking pop from Redis LIST, or in-memory)."""
        if self._use_redis:
            # BLPOP blocks for `timeout` seconds then returns None
            result = self._redis.blpop(QUEUE_KEY, timeout=int(max(timeout, 1)))
            if result is None:
                return None
            _, raw = result
            return json.loads(raw)
        else:
            # In-memory fallback
            import asyncio
            try:
                await asyncio.sleep(0)          # yield to event loop
                if self._fallback_queue:
                    return self._fallback_queue.pop(0)
                await asyncio.sleep(timeout)
                return None
            except asyncio.CancelledError:
                return None

    def record_retry(self, payload: Dict[str, Any], error_msg: str):
        """Re-enqueues a task after a recoverable execution failure."""
        payload["attempts"] += 1
        self._retry_count += 1
        payload["last_error"] = error_msg
        payload["retry_at"] = time.time()

        if self._use_redis:
            self._redis.hincrby(STATS_KEY, "retry_count", 1)

        if payload["attempts"] < payload["max_retries"]:
            if self._use_redis:
                self._redis.rpush(QUEUE_KEY, json.dumps(payload))
            else:
                self._fallback_queue.append(payload)
            logger.warning(
                "event=job_retried task_id=%s job_id=%s attempt=%d error=%s",
                payload["task_id"], payload["job_id"], payload["attempts"], error_msg
            )
        else:
            self.move_to_dead_letter_queue(payload, error_msg)

    def move_to_dead_letter_queue(self, payload: Dict[str, Any], error_msg: str):
        """Moves permanently failed task payload to Dead Letter Queue."""
        self._failed_count += 1
        payload["dlq_at"] = time.time()
        payload["final_error"] = error_msg

        if self._use_redis:
            self._redis.rpush(DLQ_KEY, json.dumps(payload))
            self._redis.hincrby(STATS_KEY, "failed_count", 1)
        else:
            self._dead_letter_queue.append(payload)

        logger.error(
            "event=job_moved_to_dlq task_id=%s job_id=%s attempts=%d error=%s",
            payload["task_id"], payload["job_id"], payload["attempts"], error_msg
        )

    def record_success(self, payload: Dict[str, Any]):
        """Records successful job execution telemetry."""
        self._processed_count += 1
        exec_duration_ms = (time.time() - payload.get("enqueued_at", time.time())) * 1000

        if self._use_redis:
            self._redis.hincrby(STATS_KEY, "processed_count", 1)

        logger.info(
            "event=job_worker_completed task_id=%s job_id=%s total_duration_ms=%.2f backend=%s",
            payload["task_id"], payload["job_id"], exec_duration_ms,
            "redis" if self._use_redis else "in_memory"
        )

    def get_telemetry(self) -> Dict[str, Any]:
        """Returns background queue worker telemetry metrics."""
        if self._use_redis:
            queue_depth = self._redis.llen(QUEUE_KEY)
            dlq_depth   = self._redis.llen(DLQ_KEY)
            stats       = self._redis.hgetall(STATS_KEY)
            processed   = int(stats.get("processed_count", 0))
            failed      = int(stats.get("failed_count", 0))
            retries     = int(stats.get("retry_count", 0))
        else:
            queue_depth = len(self._fallback_queue)
            dlq_depth   = len(self._dead_letter_queue)
            processed   = self._processed_count
            failed      = self._failed_count
            retries     = self._retry_count

        return {
            "queue_depth":     queue_depth,
            "dlq_depth":       dlq_depth,
            "processed_count": processed,
            "failed_count":    failed,
            "retry_count":     retries,
            "backend":         "redis" if self._use_redis else "in_memory",
            "status":          "healthy"
        }

    def reset(self):
        """Clears all queue state. Used in tests only."""
        if self._use_redis:
            self._redis.delete(QUEUE_KEY, DLQ_KEY, STATS_KEY)
        self._fallback_queue.clear()
        self._dead_letter_queue.clear()
        self._processed_count = 0
        self._failed_count = 0
        self._retry_count = 0


queue_service = QueueService()
