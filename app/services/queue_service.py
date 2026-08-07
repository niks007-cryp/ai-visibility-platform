import uuid
import time
import asyncio
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("app.service.queue")


class QueueService:
    """Async background task queue manager supporting retries, dead letter queueing, and telemetry."""

    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self._primary_queue: asyncio.Queue = asyncio.Queue()
        self._dead_letter_queue: List[Dict[str, Any]] = []
        self._processed_count: int = 0
        self._failed_count: int = 0
        self._retry_count: int = 0

    async def enqueue_analysis_job(
        self,
        job_id: uuid.UUID,
        prompt: Optional[str] = None,
        provider_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Pushes an AnalysisJob task payload to the background execution queue."""
        payload = {
            "task_id": str(uuid.uuid4()),
            "job_id": str(job_id),
            "prompt": prompt,
            "provider_name": provider_name,
            "enqueued_at": time.time(),
            "attempts": 0,
            "max_retries": self.max_retries,
        }
        await self._primary_queue.put(payload)
        logger.info(
            "event=job_enqueued task_id=%s job_id=%s queue_size=%d",
            payload["task_id"], job_id, self._primary_queue.qsize()
        )
        return payload

    async def dequeue(self, timeout: float = 1.0) -> Optional[Dict[str, Any]]:
        """Pops a task payload from the primary execution queue."""
        try:
            return await asyncio.wait_for(self._primary_queue.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None

    def record_retry(self, payload: Dict[str, Any], error_msg: str):
        """Re-enqueues a task after a recoverable execution failure."""
        payload["attempts"] += 1
        self._retry_count += 1
        payload["last_error"] = error_msg
        payload["retry_at"] = time.time()

        if payload["attempts"] < payload["max_retries"]:
            self._primary_queue.put_nowait(payload)
            logger.warning(
                "event=job_retried task_id=%s job_id=%s attempt=%d error=%s",
                payload["task_id"], payload["job_id"], payload["attempts"], error_msg
            )
        else:
            self.move_to_dead_letter_queue(payload, error_msg)

    def move_to_dead_letter_queue(self, payload: Dict[str, Any], error_msg: str):
        """Moves permanently failed task payload to Dead Letter Queue (DLQ)."""
        self._failed_count += 1
        payload["dlq_at"] = time.time()
        payload["final_error"] = error_msg
        self._dead_letter_queue.append(payload)
        logger.error(
            "event=job_moved_to_dlq task_id=%s job_id=%s attempts=%d error=%s",
            payload["task_id"], payload["job_id"], payload["attempts"], error_msg
        )

    def record_success(self, payload: Dict[str, Any]):
        """Records successful job execution telemetry."""
        self._processed_count += 1
        exec_duration_ms = (time.time() - payload.get("enqueued_at", time.time())) * 1000
        logger.info(
            "event=job_worker_completed task_id=%s job_id=%s total_duration_ms=%.2f",
            payload["task_id"], payload["job_id"], exec_duration_ms
        )

    def get_telemetry(self) -> Dict[str, Any]:
        """Returns background queue worker telemetry metrics."""
        return {
            "queue_depth": self._primary_queue.qsize(),
            "dlq_depth": len(self._dead_letter_queue),
            "processed_count": self._processed_count,
            "failed_count": self._failed_count,
            "retry_count": self._retry_count,
            "status": "healthy"
        }


queue_service = QueueService()
