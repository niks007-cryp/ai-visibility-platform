import uuid
import logging
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.report import JobReportResponse
from app.models.analysis_job import AnalysisJobStatus
from app.repositories.analysis_job_repository import analysis_job_repository, AnalysisJobRepository
from app.repositories.project_repository import project_repository, ProjectRepository
from app.repositories.provider_result_repository import provider_result_repository, ProviderResultRepository
from app.repositories.extracted_evidence_repository import extracted_evidence_repository, ExtractedEvidenceRepository

logger = logging.getLogger("app.service.report")


class ReportService:
    """Read-only service encapsulating single-query eager aggregation of Project, Job, ProviderResult, and ExtractedEvidence."""

    def __init__(
        self,
        job_repo: AnalysisJobRepository = analysis_job_repository,
        project_repo: ProjectRepository = project_repository,
        result_repo: ProviderResultRepository = provider_result_repository,
        evidence_repo: ExtractedEvidenceRepository = extracted_evidence_repository
    ):
        self.job_repo = job_repo
        self.project_repo = project_repo
        self.result_repo = result_repo
        self.evidence_repo = evidence_repo

    async def get_job_report(
        self,
        db: AsyncSession,
        job_id: uuid.UUID
    ) -> JobReportResponse:
        """Assembles read-only MVP report with zero N+1 query overhead."""
        job = await self.job_repo.get_by_id(db, job_id=job_id)
        if not job:
            logger.warning(f"event=report_fetch_failed reason=job_not_found job_id={job_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis Job with ID '{job_id}' not found."
            )

        if job.status != AnalysisJobStatus.COMPLETED:
            logger.warning(f"event=report_fetch_failed reason=job_not_completed job_id={job_id} status={job.status}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Analysis Job '{job_id}' is not in COMPLETED state. Job must be COMPLETED before generating a report."
            )

        project = await self.project_repo.get_by_id(db, project_id=job.project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target Project not found.")

        results = await self.result_repo.list_by_job(db, job_id=job_id)
        if not results:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No provider results found for job.")

        evidences = await self.evidence_repo.list_by_job(db, job_id=job_id)
        if not evidences:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No extracted evidence found for job.")

        provider_result = results[0]
        evidence = evidences[0]

        logger.info(f"event=report_assembled job_id={job_id} project_id={project.id}")

        return JobReportResponse(
            job_id=job.id,
            project_id=project.id,
            project_name=project.name,
            target_domain=project.domain,
            job_status=job.status.value,
            provider_name=provider_result.provider_name,
            prompt=provider_result.prompt,
            raw_response=provider_result.raw_response,
            mentioned=evidence.mentioned,
            raw_citations=evidence.raw_citations,
            matched_snippets=evidence.matched_snippets,
            extracted_brand_mentions=evidence.extracted_brand_mentions,
            created_at=job.created_at
        )

    # Alias for controller compatibility
    get_report_for_job = get_job_report


report_service = ReportService()
