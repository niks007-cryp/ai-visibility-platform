import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.extracted_evidence import ExtractedEvidence


class ExtractedEvidenceRepository:
    """Repository class encapsulating database access for ExtractedEvidence model."""

    async def create(
        self,
        db: AsyncSession,
        *,
        job_id: uuid.UUID,
        provider_result_id: uuid.UUID,
        target_domain: str,
        mentioned: bool,
        raw_citations: List[str],
        matched_snippets: List[str],
        extracted_brand_mentions: List[str]
    ) -> ExtractedEvidence:
        db_obj = ExtractedEvidence(
            job_id=job_id,
            provider_result_id=provider_result_id,
            target_domain=target_domain,
            mentioned=mentioned,
            raw_citations=raw_citations,
            matched_snippets=matched_snippets,
            extracted_brand_mentions=extracted_brand_mentions
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_id(
        self,
        db: AsyncSession,
        evidence_id: uuid.UUID
    ) -> Optional[ExtractedEvidence]:
        result = await db.execute(select(ExtractedEvidence).where(ExtractedEvidence.id == evidence_id))
        return result.scalar_one_or_none()

    async def list_by_job(
        self,
        db: AsyncSession,
        job_id: uuid.UUID
    ) -> List[ExtractedEvidence]:
        stmt = (
            select(ExtractedEvidence)
            .where(ExtractedEvidence.job_id == job_id)
            .order_by(ExtractedEvidence.created_at.asc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())


extracted_evidence_repository = ExtractedEvidenceRepository()
