import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.project import Project


class ProjectRepository:
    """Repository class encapsulating database access for Project model."""

    async def create(
        self,
        db: AsyncSession,
        *,
        name: str,
        domain: str,
        owner_id: Optional[uuid.UUID] = None
    ) -> Project:
        db_obj = Project(
            name=name,
            domain=domain,
            owner_id=owner_id
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_id(
        self,
        db: AsyncSession,
        project_id: uuid.UUID
    ) -> Optional[Project]:
        result = await db.execute(select(Project).where(Project.id == project_id))
        return result.scalar_one_or_none()

    async def get_by_domain(
        self,
        db: AsyncSession,
        domain: str,
        owner_id: Optional[uuid.UUID] = None
    ) -> Optional[Project]:
        stmt = select(Project).where(Project.domain == domain)
        if owner_id:
            stmt = stmt.where(Project.owner_id == owner_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        owner_id: Optional[uuid.UUID] = None
    ) -> List[Project]:
        stmt = select(Project).order_by(Project.created_at.desc())
        if owner_id:
            stmt = stmt.where(Project.owner_id == owner_id)
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def delete(
        self,
        db: AsyncSession,
        project_id: uuid.UUID
    ) -> bool:
        project = await self.get_by_id(db, project_id=project_id)
        if not project:
            return False
        await db.delete(project)
        await db.flush()
        return True


project_repository = ProjectRepository()
