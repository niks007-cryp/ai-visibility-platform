import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth_deps import get_optional_current_user
from app.core.domain_extractor import DomainExtractor
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.services.project_service import project_service, ProjectService

router = APIRouter()


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Target Domain Project",
    description="Registers a target web domain project. Normalizes URL and assigns ownership to current user."
)
async def create_project(
    payload: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
    service: ProjectService = Depends(lambda: project_service)
) -> ProjectResponse:
    owner_id = current_user.id if current_user else None
    return await service.create_project(db, payload=payload, owner_id=owner_id)


@router.get(
    "",
    response_model=List[ProjectResponse],
    status_code=status.HTTP_200_OK,
    summary="List Projects",
    description="Lists domain projects owned by current user."
)
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
    service: ProjectService = Depends(lambda: project_service)
) -> List[ProjectResponse]:
    owner_id = current_user.id if current_user else None
    return await service.list_projects(db, skip=skip, limit=limit, owner_id=owner_id)


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Project Details",
    description="Fetches project details by ID verifying owner access rights."
)
async def get_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
    service: ProjectService = Depends(lambda: project_service)
) -> ProjectResponse:
    owner_id = current_user.id if current_user else None
    return await service.get_project(db, project_id=project_id, owner_id=owner_id)


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Project",
    description="Updates project metadata."
)
async def update_project(
    project_id: uuid.UUID,
    payload: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
    service: ProjectService = Depends(lambda: project_service)
) -> ProjectResponse:
    owner_id = current_user.id if current_user else None
    project = await service.get_project(db, project_id=project_id, owner_id=owner_id)
    if payload.name:
        project.name = payload.name.strip()
    if payload.url:
        project.domain = DomainExtractor.extract_domain(payload.url)
    await db.flush()
    await db.refresh(project)
    return project


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Project",
    description="Deletes target project by ID."
)
async def delete_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
    service: ProjectService = Depends(lambda: project_service)
):
    owner_id = current_user.id if current_user else None
    await service.delete_project(db, project_id=project_id, owner_id=owner_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
