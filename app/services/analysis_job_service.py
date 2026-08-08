import uuid
import logging
import time
import asyncio
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings

from app.models.analysis_job import AnalysisJob, AnalysisJobStatus
from app.models.provider_result import ProviderResult
from app.models.extracted_evidence import ExtractedEvidence
from app.repositories.project_repository import project_repository, ProjectRepository
from app.repositories.analysis_job_repository import analysis_job_repository, AnalysisJobRepository
from app.repositories.provider_result_repository import provider_result_repository, ProviderResultRepository
from app.repositories.extracted_evidence_repository import extracted_evidence_repository, ExtractedEvidenceRepository
from app.providers.base import BaseProvider
from app.providers.gemini import GeminiProvider, GeminiNotConfiguredException, GeminiAPIException
from app.services.state_machine import JobStateMachine, InvalidStateTransitionException
from app.services.prompt_service import prompt_service, PromptService
from app.services.queue_service import queue_service, QueueService
from app.services.visibility_scorer import parse_structured_response, VisibilityScorecard

logger = logging.getLogger("app.service.analysis_job")


class AnalysisJobService:
    """
    Service layer orchestrating the single-request AI visibility analysis pipeline.

    Architecture (MVP, optimized for free-tier Gemini quota):
      1. Validate project and create job
      2. Select GeminiProvider (requires GEMINI_API_KEY)
      3. Issue ONE Gemini query_structured() call covering 8 evaluation dimensions
      4. Parse and score the structured JSON response deterministically
      5. Persist ProviderResult + ExtractedEvidence
      6. Mark job COMPLETED

    Gemini request count per audit: 1
    If Gemini fails → job = FAILED (no mock fallback, ever)
    """

    def __init__(
        self,
        job_repo: AnalysisJobRepository = analysis_job_repository,
        project_repo: ProjectRepository = project_repository,
        result_repo: ProviderResultRepository = provider_result_repository,
        evidence_repo: ExtractedEvidenceRepository = extracted_evidence_repository,
        prompts: PromptService = prompt_service,
        queue: QueueService = queue_service,
        state_machine: JobStateMachine = JobStateMachine()
    ):
        self.job_repo = job_repo
        self.project_repo = project_repo
        self.result_repo = result_repo
        self.evidence_repo = evidence_repo
        self.prompts = prompts
        self.queue = queue
        self.state_machine = state_machine

    @property
    def provider(self) -> GeminiProvider:
        """
        Returns a GeminiProvider if GEMINI_API_KEY is configured.
        Raises GeminiNotConfiguredException if not — never silently falls back to mock.
        """
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip():
            return GeminiProvider(
                api_key=settings.GEMINI_API_KEY,
                model_name=settings.GEMINI_MODEL,
            )
        raise GeminiNotConfiguredException()

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
                detail=f"Project with ID '{project_id}' not found.",
            )

        active_job = await self.job_repo.get_active_job_for_project(
            db,
            project_id=project_id,
            for_update=True
        )
        if active_job:
            now = datetime.now(timezone.utc)
            created_at = active_job.created_at
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)

            # Expire stale jobs older than 120s (generous for 1 Gemini call @ 40s timeout)
            if (now - created_at).total_seconds() > 120:
                logger.warning(
                    f"event=analysis_stale_job_cleaned project_id={project_id} stale_job_id={active_job.id}"
                )
                await self.job_repo.update_status(
                    db,
                    db_obj=active_job,
                    new_status=AnalysisJobStatus.FAILED,
                    error_message="Job timed out or abandoned",
                )
                active_job = None

        if active_job:
            logger.warning(
                f"event=analysis_create_conflict reason=concurrent_active_job "
                f"project_id={project_id} active_job_id={active_job.id}"
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"An active Analysis Job (ID: {active_job.id}) is already in progress for this project.",
            )

        job = await self.job_repo.create(db, project_id=project_id)

        # Enqueue background execution task
        await self.queue.enqueue_analysis_job(job_id=job.id)

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            f"event=analysis_created_and_enqueued project_id={project_id} "
            f"job_id={job.id} status={job.status} duration_ms={elapsed_ms:.2f}"
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
                detail=f"Analysis Job with ID '{job_id}' not found.",
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
                detail=f"Project with ID '{project_id}' not found.",
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
                target_status=target_status,
            )
        except InvalidStateTransitionException as exc:
            logger.warning(
                f"event=analysis_transition_failed reason=invalid_transition "
                f"job_id={job_id} current_status={job.status} target_status={target_status}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            )

        updated_job = await self.job_repo.update_status(
            db,
            db_obj=job,
            new_status=target_status,
            error_message=error_message,
        )
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        event_name = f"analysis_{target_status.value.lower()}"
        logger.info(
            f"event={event_name} project_id={updated_job.project_id} "
            f"job_id={updated_job.id} status={updated_job.status} duration_ms={elapsed_ms:.2f}"
        )
        return updated_job

    async def execute_job(
        self,
        db: AsyncSession,
        job_id: uuid.UUID,
        prompt: Optional[str] = None,      # kept for worker compatibility, not used
        provider: Optional[BaseProvider] = None  # kept for test injection
    ) -> ProviderResult:
        """
        Executes ONE structured Gemini API request covering 8 evaluation dimensions.

        Pipeline:
          1. Transition job → Running
          2. query_structured() → raw JSON (1 Gemini request)
          3. parse_structured_response() → VisibilityScorecard (deterministic)
          4. Persist ProviderResult (raw JSON) + ExtractedEvidence (computed metrics)
          5. Transition job → Completed

        On ANY failure: job → Failed, error surfaced. No mock fallback.
        """
        start_time = time.perf_counter()
        logger.info("event=analysis_started job_id=%s", job_id)

        job = await self.get_job(db, job_id=job_id)

        # Idempotency guards
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

        # ── Provider selection (never falls back to mock) ──────────────────────
        if provider is not None:
            # Test injection path
            gemini = provider
            gemini_key_present = True
        else:
            try:
                gemini = self.provider   # raises GeminiNotConfiguredException if no key
                gemini_key_present = True
            except GeminiNotConfiguredException as exc:
                err_msg = str(exc)
                logger.error(
                    "event=job_execution_failed job_id=%s error=GEMINI_API_KEY_not_configured", job_id
                )
                await self.transition_job_status(
                    db, job_id=job_id,
                    target_status=AnalysisJobStatus.FAILED,
                    error_message=err_msg,
                )
                raise

        logger.info(
            "event=job_execution_started job_id=%s domain=%s "
            "GEMINI_API_KEY_PRESENT=%s SELECTED_PROVIDER=%s GEMINI_REQUESTS_THIS_JOB=1",
            job_id, project.domain, gemini_key_present, gemini.name,
        )

        # ── ONE Gemini request ─────────────────────────────────────────────────
        try:
            # 40s timeout per the provider; outer here is 60s safety net
            raw_json = await asyncio.wait_for(
                gemini.query_structured(domain=project.domain),
                timeout=60.0,
            )
        except (GeminiAPIException, GeminiNotConfiguredException) as exc:
            err_msg = str(exc)
            logger.error("event=job_execution_failed job_id=%s error=%s", job_id, err_msg)
            await self.transition_job_status(
                db, job_id=job_id,
                target_status=AnalysisJobStatus.FAILED,
                error_message=err_msg,
            )
            raise
        except asyncio.TimeoutError:
            err_msg = "Analysis execution timed out after 60 seconds."
            logger.error("event=job_execution_failed job_id=%s error=%s", job_id, err_msg)
            await self.transition_job_status(
                db, job_id=job_id,
                target_status=AnalysisJobStatus.FAILED,
                error_message=err_msg,
            )
            raise GeminiAPIException(err_msg, is_retryable=True)

        # ── Deterministic scoring ──────────────────────────────────────────────
        try:
            scorecard = parse_structured_response(raw_json=raw_json, domain=project.domain)
        except ValueError as exc:
            err_msg = f"Failed to parse Gemini structured response: {exc}"
            logger.error("event=job_execution_failed job_id=%s error=%s", job_id, err_msg)
            await self.transition_job_status(
                db, job_id=job_id,
                target_status=AnalysisJobStatus.FAILED,
                error_message=err_msg,
            )
            raise GeminiAPIException(err_msg, is_retryable=False)

        # ── Persist ONE ProviderResult + ONE ExtractedEvidence ─────────────────
        # Build combined prompt string (documenting the 8 dimensions used)
        combined_prompt = (
            f"AI visibility evaluation for {project.domain} across 8 standardized dimensions: "
            f"category_recognition, brand_recognition, direct_recommendation, use_case_fit, "
            f"competitor_comparison, brand_differentiation, purchase_intent, factual_knowledge. "
            f"(Single structured Gemini request — 1 API call)"
        )

        result = await self.result_repo.create(
            db,
            job_id=job_id,
            provider_name=gemini.name,
            prompt=combined_prompt,
            raw_response=scorecard.summary_text(),
            prompt_id="STRUCTURED_VISIBILITY_V1",
            prompt_version="2.0.0",
            prompt_category="multi_dimension_structured",
        )

        # ExtractedEvidence — populated from scorecard (deterministic, not from Gemini)
        mentioned = scorecard.mentioned_count > 0
        raw_citations = scorecard.brand_evidence_snippets[:10]
        matched_snippets = [
            f"[{q.category}] {q.evidence_snippet}"
            for q in scorecard.queries
            if q.brand_mentioned and q.evidence_snippet
        ][:10]
        extracted_brand_mentions = list({
            q.category: scorecard.brand for q in scorecard.queries if q.brand_mentioned
        }.values())

        await self.evidence_repo.create(
            db,
            job_id=job_id,
            provider_result_id=result.id,
            target_domain=project.domain,
            mentioned=mentioned,
            raw_citations=raw_citations,
            matched_snippets=matched_snippets,
            extracted_brand_mentions=extracted_brand_mentions,
        )

        # ── Complete job ───────────────────────────────────────────────────────
        await self.transition_job_status(db, job_id=job_id, target_status=AnalysisJobStatus.COMPLETED)
        total_elapsed = (time.perf_counter() - start_time) * 1000

        logger.info(
            "event=job_completed job_id=%s domain=%s total_duration_ms=%.2f "
            "gemini_requests=1 visibility_score=%.4f mention_rate=%.4f",
            job_id, project.domain, total_elapsed,
            scorecard.visibility_score, scorecard.mention_rate,
        )
        return result

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
            target_status=AnalysisJobStatus.CANCELLED,
        )


analysis_job_service = AnalysisJobService()
