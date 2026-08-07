import uuid
import logging
import time
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.schemas.project import ProjectCreate
from app.repositories.project_repository import project_repository, ProjectRepository
from app.core.domain_extractor import DomainExtractor

logger = logging.getLogger("app.service.project")


class ProjectService:
    """Service layer encapsulating domain normalization, duplicate checks, ownership isolation, and CRUD operations."""

    def __init__(
        self,
        repository: ProjectRepository = project_repository,
        extractor: DomainExtractor = DomainExtractor()
    ):
        self.repository = repository
        self.extractor = extractor

    async def create_project(
        self,
        db: AsyncSession,
        payload: ProjectCreate,
        owner_id: Optional[uuid.UUID] = None
    ) -> Project:
        start_time = time.perf_counter()

        name_str = payload.name.strip()
        normalized_domain = self.extractor.extract_domain(payload.url)

        existing = await self.repository.get_by_domain(db, domain=normalized_domain, owner_id=owner_id)
        if existing:
            logger.warning(
                f"event=project_create_failed reason=duplicate_domain domain={normalized_domain} owner_id={owner_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A project for domain '{normalized_domain}' already exists."
            )

        project = await self.repository.create(
            db,
            name=name_str,
            domain=normalized_domain,
            owner_id=owner_id
        )
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        logger.info(
            f"event=project_created project_id={project.id} domain={project.domain} owner_id={owner_id} duration_ms={elapsed_ms:.2f}"
        )
        return project

    async def get_project(
        self,
        db: AsyncSession,
        project_id: uuid.UUID,
        owner_id: Optional[uuid.UUID] = None
    ) -> Project:
        project = await self.repository.get_by_id(db, project_id=project_id)
        if not project:
            logger.warning(f"event=project_fetch_failed reason=not_found project_id={project_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID '{project_id}' not found."
            )

        if owner_id and project.owner_id and project.owner_id != owner_id:
            logger.warning(f"event=project_access_denied project_id={project_id} owner_id={owner_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this project."
            )

        return project

    async def list_projects(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        owner_id: Optional[uuid.UUID] = None
    ) -> List[Project]:
        return await self.repository.list_all(db, skip=skip, limit=limit, owner_id=owner_id)

    async def delete_project(
        self,
        db: AsyncSession,
        project_id: uuid.UUID,
        owner_id: Optional[uuid.UUID] = None
    ) -> bool:
        await self.get_project(db, project_id=project_id, owner_id=owner_id)
        return await self.repository.delete(db, project_id=project_id)


project_service = ProjectService()
