import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.provider_result import ProviderResult


class ProviderResultRepository:
    """Repository class encapsulating database access for ProviderResult model."""

    async def create(
        self,
        db: AsyncSession,
        *,
        job_id: uuid.UUID,
        provider_name: str,
        prompt: str,
        raw_response: str,
        prompt_id: Optional[str] = None,
        prompt_version: Optional[str] = None,
        prompt_category: Optional[str] = None
    ) -> ProviderResult:
        db_obj = ProviderResult(
            job_id=job_id,
            provider_name=provider_name,
            prompt=prompt,
            raw_response=raw_response,
            prompt_id=prompt_id,
            prompt_version=prompt_version,
            prompt_category=prompt_category
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_id(
        self,
        db: AsyncSession,
        result_id: uuid.UUID
    ) -> Optional[ProviderResult]:
        result = await db.execute(select(ProviderResult).where(ProviderResult.id == result_id))
        return result.scalar_one_or_none()

    async def list_by_job(
        self,
        db: AsyncSession,
        job_id: uuid.UUID
    ) -> List[ProviderResult]:
        stmt = (
            select(ProviderResult)
            .where(ProviderResult.job_id == job_id)
            .order_by(ProviderResult.created_at.asc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())


provider_result_repository = ProviderResultRepository()
