import uuid
import logging
from datetime import datetime, timezone
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.evaluation import EvaluationSummary, ConfidenceLevel, ContradictionDetail
from app.repositories.analysis_job_repository import analysis_job_repository, AnalysisJobRepository
from app.repositories.provider_result_repository import provider_result_repository, ProviderResultRepository
from app.repositories.extracted_evidence_repository import extracted_evidence_repository, ExtractedEvidenceRepository

logger = logging.getLogger("app.service.evaluation")


class EvaluationService:
    """Service layer calculating multi-prompt execution consistency and confidence level from factual evidence."""

    def __init__(
        self,
        job_repo: AnalysisJobRepository = analysis_job_repository,
        result_repo: ProviderResultRepository = provider_result_repository,
        evidence_repo: ExtractedEvidenceRepository = extracted_evidence_repository
    ):
        self.job_repo = job_repo
        self.result_repo = result_repo
        self.evidence_repo = evidence_repo

    async def get_evaluation_summary(
        self,
        db: AsyncSession,
        job_id: uuid.UUID
    ) -> EvaluationSummary:
        """Calculates multi-prompt execution consistency and contradiction detection for an Analysis Job."""
        job = await self.job_repo.get_by_id(db, job_id=job_id)
        if not job:
            logger.warning(f"event=evaluation_failed reason=job_not_found job_id={job_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis Job with ID '{job_id}' not found."
            )

        results = await self.result_repo.list_by_job(db, job_id=job_id)
        evidences = await self.evidence_repo.list_by_job(db, job_id=job_id)

        if not results or not evidences:
            logger.warning(f"event=evaluation_failed reason=results_or_evidence_missing job_id={job_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No execution results or extracted evidence found for job '{job_id}'."
            )

        total_prompts = len(results)
        successful_executions = len(results)

        # Build lookup from provider_result_id to evidence & result
        result_map = {r.id: r for r in results}
        mentioned_count = sum(1 for e in evidences if e.mentioned)
        mention_rate = round(mentioned_count / total_prompts, 2) if total_prompts > 0 else 0.0

        provider_count = len({r.provider_name for r in results})
        prompt_categories = sorted(list({r.prompt_category for r in results if r.prompt_category}))

        # Calculate consistency percentage: percentage of executions that match the majority mention outcome
        majority_count = max(mentioned_count, total_prompts - mentioned_count)
        consistency_pct = round((majority_count / total_prompts) * 100.0, 1) if total_prompts > 0 else 0.0

        # Confidence Level mapping
        if consistency_pct >= 95.0:
            confidence = ConfidenceLevel.HIGH
        elif consistency_pct >= 80.0:
            confidence = ConfidenceLevel.MEDIUM
        else:
            confidence = ConfidenceLevel.LOW

        # Detect contradictions across prompt variations
        contradictions: List[ContradictionDetail] = []
        if 0 < mentioned_count < total_prompts:
            mentioned_evidences = [e for e in evidences if e.mentioned]
            omitted_evidences = [e for e in evidences if not e.mentioned]

            for m_ev in mentioned_evidences:
                m_res = result_map.get(m_ev.provider_result_id)
                for o_ev in omitted_evidences:
                    o_res = result_map.get(o_ev.provider_result_id)
                    m_p_id = m_res.prompt_id if m_res and m_res.prompt_id else "UNKNOWN"
                    m_cat = m_res.prompt_category if m_res and m_res.prompt_category else "UNKNOWN"
                    o_p_id = o_res.prompt_id if o_res and o_res.prompt_id else "UNKNOWN"
                    o_cat = o_res.prompt_category if o_res and o_res.prompt_category else "UNKNOWN"

                    contradictions.append(
                        ContradictionDetail(
                            mentioned_prompt_id=m_p_id,
                            mentioned_prompt_category=m_cat,
                            omitted_prompt_id=o_p_id,
                            omitted_prompt_category=o_cat,
                            description=(
                                f"Contradiction detected: Brand was recommended under prompt '{m_p_id}' ({m_cat}), "
                                f"but omitted under prompt '{o_p_id}' ({o_cat})."
                            )
                        )
                    )

        logger.info(
            f"event=evaluation_calculated job_id={job_id} consistency={consistency_pct}% confidence={confidence} contradictions={len(contradictions)}"
        )

        return EvaluationSummary(
            job_id=job.id,
            total_prompts=total_prompts,
            successful_executions=successful_executions,
            mentioned_count=mentioned_count,
            mention_rate=mention_rate,
            provider_count=provider_count,
            prompt_categories_tested=prompt_categories,
            consistency_percentage=consistency_pct,
            confidence_level=confidence,
            contradictions=contradictions,
            generated_at=datetime.now(timezone.utc)
        )


evaluation_service = EvaluationService()
