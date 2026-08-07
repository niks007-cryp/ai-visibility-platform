import uuid
import signal
import sys
import asyncio
import logging
from app.core.database import AsyncSessionLocal
from app.services.queue_service import queue_service, QueueService
from app.services.analysis_job_service import analysis_job_service, AnalysisJobService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] app.worker: %(message)s")
logger = logging.getLogger("app.worker")


class AnalysisWorker:
    """Standalone background worker listening on task queue, executing AnalysisJobs asynchronously."""

    def __init__(
        self,
        queue: QueueService = queue_service,
        job_service: AnalysisJobService = analysis_job_service
    ):
        self.queue = queue
        self.job_service = job_service
        self.running = True

    def stop(self, *args):
        logger.info("event=worker_shutdown_signal_received")
        self.running = False

    async def run(self):
        logger.info("event=worker_started listening_on_queue=True")
        
        while self.running:
            payload = await self.queue.dequeue(timeout=0.5)
            if not payload:
                await asyncio.sleep(0.1)
                continue

            task_id = payload["task_id"]
            job_id_str = payload["job_id"]
            job_id = uuid.UUID(job_id_str)

            logger.info("event=worker_processing_job task_id=%s job_id=%s attempt=%d", task_id, job_id_str, payload.get("attempts", 0) + 1)

            async with AsyncSessionLocal() as db:
                try:
                    await self.job_service.execute_job(
                        db,
                        job_id=job_id,
                        prompt=payload.get("prompt")
                    )
                    await db.commit()
                    self.queue.record_success(payload)
                except Exception as exc:
                    await db.rollback()
                    logger.error("event=worker_job_execution_failed task_id=%s job_id=%s error=%s", task_id, job_id_str, str(exc))
                    self.queue.record_retry(payload, str(exc))

        logger.info("event=worker_stopped_gracefully")


if __name__ == "__main__":
    worker = AnalysisWorker()
    loop = asyncio.get_event_loop()

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, worker.stop)

    try:
        loop.run_until_complete(worker.run())
    except KeyboardInterrupt:
        logger.info("event=worker_keyboard_interrupt")
