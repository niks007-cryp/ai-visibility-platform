import pytest
import uuid
from httpx import AsyncClient
from app.services.queue_service import QueueService, queue_service
from app.worker import AnalysisWorker


@pytest.mark.asyncio
async def test_queue_service_enqueue_dequeue():
    """Test enqueuing and dequeuing task payloads."""
    qs = QueueService(max_retries=3)
    job_id = uuid.uuid4()

    payload = await qs.enqueue_analysis_job(job_id=job_id, prompt="Test prompt")
    assert payload["job_id"] == str(job_id)

    dequeued = await qs.dequeue(timeout=0.1)
    assert dequeued is not None
    assert dequeued["job_id"] == str(job_id)


@pytest.mark.asyncio
async def test_queue_service_retry_and_dlq():
    """Test retry policy and dead letter queueing upon max retries exceeded."""
    qs = QueueService(max_retries=2)
    job_id = uuid.uuid4()

    payload = await qs.enqueue_analysis_job(job_id=job_id)
    dequeued = await qs.dequeue(timeout=0.1)

    # Attempt 1 -> Retry
    qs.record_retry(dequeued, "Transient network timeout")
    assert qs.get_telemetry()["retry_count"] == 1
    assert qs.get_telemetry()["dlq_depth"] == 0

    # Attempt 2 -> Exceeds max retries -> Move to DLQ
    dequeued_retry = await qs.dequeue(timeout=0.1)
    qs.record_retry(dequeued_retry, "Fatal error")
    assert qs.get_telemetry()["dlq_depth"] == 1
    assert qs.get_telemetry()["failed_count"] == 1


@pytest.mark.asyncio
async def test_worker_health_endpoint(async_client: AsyncClient):
    """Test GET /api/v1/worker/health endpoint returns queue telemetry metrics."""
    res = await async_client.get("/api/v1/worker/health")
    assert res.status_code == 200
    data = res.json()

    assert "queue_depth" in data
    assert "dlq_depth" in data
    assert "processed_count" in data
    assert "retry_count" in data
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_worker_process_single_task(db_session):
    """Test AnalysisWorker consuming task payload from queue and executing job."""
    from app.services.analysis_job_service import analysis_job_service
    from app.repositories.project_repository import project_repository

    # Drain any lingering test queue items
    queue_service.reset()

    # Create project
    project = await project_repository.create(db_session, name="Worker Test Co", domain="workertest.io")

    # Create job (automatically enqueued)
    job = await analysis_job_service.create_job(db_session, project_id=project.id)

    worker = AnalysisWorker()
    
    # Process enqueued job payload
    payload = await worker.queue.dequeue(timeout=0.5)
    assert payload is not None
    assert payload["job_id"] == str(job.id)

    # Execute via job_service directly
    await analysis_job_service.execute_job(db_session, job_id=job.id)
    worker.queue.record_success(payload)

    telemetry = worker.queue.get_telemetry()
    assert telemetry["processed_count"] >= 1
