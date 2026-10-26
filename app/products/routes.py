"""HTTP routes for projects and sources."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.ingestion.registry import available_source_types
from app.products.schemas import (
    ProjectCreate,
    ProjectDetail,
    ProjectRead,
    SourceCreate,
    SourceRead,
)
from app.products.service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectDetail, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate, session: AsyncSession = Depends(get_session)
) -> ProjectDetail:
    project = await ProjectService(session).create_project(payload)
    return ProjectDetail.model_validate(project)


@router.get("", response_model=list[ProjectRead])
async def list_projects(session: AsyncSession = Depends(get_session)) -> list[ProjectRead]:
    projects = await ProjectService(session).list_projects()
    return [ProjectRead.model_validate(p) for p in projects]


@router.get("/{project_id}", response_model=ProjectDetail)
async def get_project(
    project_id: str, session: AsyncSession = Depends(get_session)
) -> ProjectDetail:
    project = await ProjectService(session).require_project(project_id, with_relations=True)
    return ProjectDetail.model_validate(project)


@router.post(
    "/{project_id}/sources",
    response_model=SourceRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_source(
    project_id: str,
    payload: SourceCreate,
    session: AsyncSession = Depends(get_session),
) -> SourceRead:
    source = await ProjectService(session).add_source(project_id, payload)
    return SourceRead.model_validate(source)


@router.get("/{project_id}/sources", response_model=list[SourceRead])
async def list_sources(
    project_id: str, session: AsyncSession = Depends(get_session)
) -> list[SourceRead]:
    sources = await ProjectService(session).list_sources(project_id)
    return [SourceRead.model_validate(s) for s in sources]


# Convenience: surface which connectors are installed/registered.
catalog_router = APIRouter(tags=["catalog"])


@catalog_router.get("/source-types", response_model=list[str])
async def list_source_types() -> list[str]:
    return available_source_types()
