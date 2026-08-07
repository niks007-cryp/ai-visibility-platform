import uuid
import logging
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.recommendation import Recommendation
from app.repositories.analysis_job_repository import analysis_job_repository, AnalysisJobRepository
from app.repositories.extracted_evidence_repository import extracted_evidence_repository, ExtractedEvidenceRepository
from app.services.recommendation_engine import recommendation_rule_engine, RecommendationRuleEngine

logger = logging.getLogger("app.service.recommendation")


class RecommendationService:
    """Service layer orchestrating deterministic recommendation generation from ExtractedEvidence."""

    def __init__(
        self,
        job_repo: AnalysisJobRepository = analysis_job_repository,
        evidence_repo: ExtractedEvidenceRepository = extracted_evidence_repository,
        engine: RecommendationRuleEngine = recommendation_rule_engine
    ):
        self.job_repo = job_repo
        self.evidence_repo = evidence_repo
        self.engine = engine

    async def get_recommendations_for_job(
        self,
        db: AsyncSession,
        job_id: uuid.UUID
    ) -> List[Recommendation]:
        """Fetches ExtractedEvidence for job and evaluates deterministic recommendation rules."""
        # 1. Verify job exists
        job = await self.job_repo.get_by_id(db, job_id=job_id)
        if not job:
            logger.warning(f"event=recommendations_failed reason=job_not_found job_id={job_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis Job with ID '{job_id}' not found."
            )

        # 2. Fetch ExtractedEvidence
        evidences = await self.evidence_repo.list_by_job(db, job_id=job_id)
        if not evidences:
            logger.warning(f"event=recommendations_failed reason=evidence_not_found job_id={job_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No extracted evidence found for Analysis Job '{job_id}'."
            )

        evidence = evidences[0]
        recommendations = self.engine.generate_recommendations(evidence)

        logger.info(f"event=recommendations_generated job_id={job_id} count={len(recommendations)}")
        return recommendations


recommendation_service = RecommendationService()
