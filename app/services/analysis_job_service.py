import uuid
import logging
import time
import asyncio
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis_job import AnalysisJob, AnalysisJobStatus
from app.models.provider_result import ProviderResult
from app.models.extracted_evidence import ExtractedEvidence
from app.repositories.project_repository import project_repository, ProjectRepository
from app.repositories.analysis_job_repository import analysis_job_repository, AnalysisJobRepository
from app.repositories.provider_result_repository import provider_result_repository, ProviderResultRepository
from app.repositories.extracted_evidence_repository import extracted_evidence_repository, ExtractedEvidenceRepository
from app.providers.base import BaseProvider
from app.providers.mock import mock_provider
from app.providers.gemini import gemini_provider, GeminiNotConfiguredException
from app.services.state_machine import JobStateMachine, InvalidStateTransitionException
from app.services.evidence_pipeline import evidence_pipeline, EvidencePipeline
from app.services.prompt_service import prompt_service, PromptService
from app.services.queue_service import queue_service, QueueService

logger = logging.getLogger("app.service.analysis_job")


class AnalysisJobService:
    """Service layer orchestrating business logic, prompt evaluation framework, provider execution, evidence extraction, and state transitions."""

    def __init__(
        self,
        job_repo: AnalysisJobRepository = analysis_job_repository,
        project_repo: ProjectRepository = project_repository,
        result_repo: ProviderResultRepository = provider_result_repository,
        evidence_repo: ExtractedEvidenceRepository = extracted_evidence_repository,
        provider: BaseProvider = mock_provider,
        pipeline: EvidencePipeline = evidence_pipeline,
        prompts: PromptService = prompt_service,
        queue: QueueService = queue_service,
        state_machine: JobStateMachine = JobStateMachine()
    ):
        self.job_repo = job_repo
        self.project_repo = project_repo
        self.result_repo = result_repo
        self.evidence_repo = evidence_repo
        self.provider = provider
        self.pipeline = pipeline
        self.prompts = prompts
        self.queue = queue
        self.state_machine = state_machine

    async def create_job(
        self,
        db: AsyncSession,
        project_id: uuid.UUID
    ) -> AnalysisJob:
        start_time = time.perf_counter()

        project = await self.project_repo.get_by_id(db, project_id=project_id)
        if not project:
            logger.warning(f"event=analysis_create_failed reason=project_not_found project_id={project_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID '{project_id}' not found."
            )

        active_job = await self.job_repo.get_active_job_for_project(
            db,
            project_id=project_id,
            for_update=True
        )
        if active_job:
            logger.warning(
                f"event=analysis_create_conflict reason=concurrent_active_job project_id={project_id} active_job_id={active_job.id}"
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"An active Analysis Job (ID: {active_job.id}) is already in progress for this project."
            )

        job = await self.job_repo.create(db, project_id=project_id)
        
        # Enqueue background execution task
        await self.queue.enqueue_analysis_job(job_id=job.id)

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        logger.info(
            f"event=analysis_created_and_enqueued project_id={project_id} job_id={job.id} status={job.status} duration_ms={elapsed_ms:.2f}"
        )
        return job

    async def get_job(
        self,
        db: AsyncSession,
        job_id: uuid.UUID
    ) -> AnalysisJob:
        job = await self.job_repo.get_by_id(db, job_id=job_id)
        if not job:
            logger.warning(f"event=analysis_fetch_failed reason=job_not_found job_id={job_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis Job with ID '{job_id}' not found."
            )
        return job

    async def list_jobs_for_project(
        self,
        db: AsyncSession,
        project_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[AnalysisJob]:
        project = await self.project_repo.get_by_id(db, project_id=project_id)
        if not project:
            logger.warning(f"event=analysis_list_failed reason=project_not_found project_id={project_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID '{project_id}' not found."
            )

        return await self.job_repo.list_by_project(db, project_id=project_id, skip=skip, limit=limit)

    async def transition_job_status(
        self,
        db: AsyncSession,
        job_id: uuid.UUID,
        target_status: AnalysisJobStatus,
        error_message: Optional[str] = None
    ) -> AnalysisJob:
        start_time = time.perf_counter()
        job = await self.get_job(db, job_id=job_id)

        try:
            self.state_machine.validate_transition(
                current_status=job.status,
                target_status=target_status
            )
        except InvalidStateTransitionException as exc:
            logger.warning(
                f"event=analysis_transition_failed reason=invalid_transition job_id={job_id} current_status={job.status} target_status={target_status}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc)
            )

        updated_job = await self.job_repo.update_status(
            db,
            db_obj=job,
            new_status=target_status,
            error_message=error_message
        )
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        event_name = f"analysis_{target_status.value.lower()}"
        logger.info(
            f"event={event_name} project_id={updated_job.project_id} job_id={updated_job.id} status={updated_job.status} duration_ms={elapsed_ms:.2f}"
        )
        return updated_job

    async def execute_job(
        self,
        db: AsyncSession,
        job_id: uuid.UUID,
        prompt: Optional[str] = None,
        provider: Optional[BaseProvider] = None
    ) -> ProviderResult:
        """Executes an Analysis Job across Prompt Evaluation Catalog templates and records ProviderResults and ExtractedEvidence."""
        start_time = time.perf_counter()
        logger.info("event=analysis_started job_id=%s timestamp=%.2f", job_id, start_time)

        job = await self.get_job(db, job_id=job_id)
        if job.status == AnalysisJobStatus.COMPLETED:
            logger.info("event=execute_job_skipped reason=already_completed job_id=%s", job_id)
            existing_results = await self.result_repo.list_by_job(db, job_id=job_id)
            return existing_results[0] if existing_results else None

        if job.status == AnalysisJobStatus.FAILED:
            logger.info("event=execute_job_skipped reason=already_failed job_id=%s", job_id)
            return None

        if job.status != AnalysisJobStatus.RUNNING:
            await self.transition_job_status(db, job_id=job_id, target_status=AnalysisJobStatus.RUNNING)

        project = await self.project_repo.get_by_id(db, project_id=job.project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

        target_provider = provider or self.provider
        active_prompts = self.prompts.list_active_prompts()
        primary_result: Optional[ProviderResult] = None

        logger.info(
            "event=job_execution_started job_id=%s domain=%s prompts_count=%d",
            job_id, project.domain, len(active_prompts)
        )

        async def _run_analysis():
            nonlocal primary_result
            for p_template in active_prompts:
                formatted_prompt = prompt or p_template.template.format(domain=project.domain)

                p_start = time.perf_counter()
                logger.info("event=provider_call_started job_id=%s prompt_id=%s", job_id, p_template.id)

                try:
                    output = await target_provider.query(prompt=formatted_prompt, domain=project.domain)
                except Exception as p_err:
                    logger.warning("event=provider_query_failed error=%s fallback_to_mock job_id=%s", p_err, job_id)
                    output = await mock_provider.query(prompt=formatted_prompt, domain=project.domain)

                p_elapsed = (time.perf_counter() - p_start) * 1000
                logger.info(
                    "event=gemini_response_received job_id=%s provider=%s elapsed_ms=%.2f",
                    job_id, output.provider_name, p_elapsed
                )

                db_start = time.perf_counter()
                logger.info("event=database_persistence_started job_id=%s", job_id)

                result = await self.result_repo.create(
                    db,
                    job_id=job_id,
                    provider_name=output.provider_name,
                    prompt=output.prompt,
                    raw_response=output.raw_response,
                    prompt_id=p_template.id,
                    prompt_version=p_template.version,
                    prompt_category=p_template.category.value
                )

                if primary_result is None:
                    primary_result = result

                evidence_payload = self.pipeline.process(raw_text=output.raw_response, target_domain=project.domain)
                await self.evidence_repo.create(
                    db,
                    job_id=job_id,
                    provider_result_id=result.id,
                    target_domain=project.domain,
                    **evidence_payload
                )

                db_elapsed = (time.perf_counter() - db_start) * 1000
                logger.info("event=database_persistence_completed job_id=%s elapsed_ms=%.2f", job_id, db_elapsed)

        try:
            await asyncio.wait_for(_run_analysis(), timeout=25.0)
        except (Exception, asyncio.TimeoutError) as exc:
            err_msg = "Analysis execution timed out after 25s." if isinstance(exc, asyncio.TimeoutError) else str(exc)
            logger.error("event=job_execution_failed job_id=%s error=%s", job_id, err_msg)
            await self.transition_job_status(
                db,
                job_id=job_id,
                target_status=AnalysisJobStatus.FAILED,
                error_message=err_msg
            )
            raise exc

        await self.transition_job_status(db, job_id=job_id, target_status=AnalysisJobStatus.COMPLETED)
        total_elapsed = (time.perf_counter() - start_time) * 1000
        logger.info("event=job_completed job_id=%s total_duration_ms=%.2f", job_id, total_elapsed)
        return primary_result

    async def get_evidence_for_job(
        self,
        db: AsyncSession,
        job_id: uuid.UUID
    ) -> List[ExtractedEvidence]:
        await self.get_job(db, job_id=job_id)
        return await self.evidence_repo.list_by_job(db, job_id=job_id)

    async def cancel_job(
        self,
        db: AsyncSession,
        job_id: uuid.UUID
    ) -> AnalysisJob:
        return await self.transition_job_status(
            db,
            job_id=job_id,
            target_status=AnalysisJobStatus.CANCELLED
        )


analysis_job_service = AnalysisJobService()
