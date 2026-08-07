import uuid
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.analysis_job import AnalysisJob, AnalysisJobStatus


class AnalysisJobRepository:
    """Repository class encapsulating database access for AnalysisJob model."""

    async def create(
        self,
        db: AsyncSession,
        *,
        project_id: uuid.UUID
    ) -> AnalysisJob:
        db_obj = AnalysisJob(
            project_id=project_id,
            status=AnalysisJobStatus.PENDING
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_id(
        self,
        db: AsyncSession,
        job_id: uuid.UUID
    ) -> Optional[AnalysisJob]:
        result = await db.execute(select(AnalysisJob).where(AnalysisJob.id == job_id))
        return result.scalar_one_or_none()

    async def get_active_job_for_project(
        self,
        db: AsyncSession,
        project_id: uuid.UUID,
        for_update: bool = False
    ) -> Optional[AnalysisJob]:
        """Queries for any active (Pending or Running) job for a project.
        
        Optionally applies row-level locking (with_for_update) to prevent race conditions.
        """
        stmt = (
            select(AnalysisJob)
            .where(
                AnalysisJob.project_id == project_id,
                AnalysisJob.status.in_([AnalysisJobStatus.PENDING, AnalysisJobStatus.RUNNING])
            )
        )
        if for_update:
            stmt = stmt.with_for_update()

        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_project(
        self,
        db: AsyncSession,
        project_id: uuid.UUID,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[AnalysisJob]:
        stmt = (
            select(AnalysisJob)
            .where(AnalysisJob.project_id == project_id)
            .order_by(AnalysisJob.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def update_status(
        self,
        db: AsyncSession,
        *,
        db_obj: AnalysisJob,
        new_status: AnalysisJobStatus,
        error_message: Optional[str] = None
    ) -> AnalysisJob:
        now = datetime.now(timezone.utc)
        db_obj.status = new_status

        if new_status == AnalysisJobStatus.RUNNING and not db_obj.started_at:
            db_obj.started_at = now
        elif new_status in (AnalysisJobStatus.COMPLETED, AnalysisJobStatus.FAILED, AnalysisJobStatus.CANCELLED):
            db_obj.completed_at = now
            if new_status == AnalysisJobStatus.FAILED and error_message:
                db_obj.error_message = error_message

        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj


analysis_job_repository = AnalysisJobRepository()
