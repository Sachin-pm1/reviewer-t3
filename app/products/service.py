"""Business logic for the products domain."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.ingestion.registry import build_connector
from app.products.models import Product, Project, Source
from app.products.repository import ProjectRepository
from app.products.schemas import ProjectCreate, SourceCreate


class ProjectService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = ProjectRepository(session)

    async def create_project(self, data: ProjectCreate) -> Project:
        """Create a project plus a default product named after the product."""
        project = Project(
            name=data.name,
            product_name=data.product_name,
            description=data.description,
        )
        await self.repo.add(project)
        await self.repo.add_product(Product(project_id=project.id, name=data.product_name))
        # Reload with relations for a complete response.
        return await self.require_project(project.id, with_relations=True)

    async def list_projects(self) -> list[Project]:
        return await self.repo.list()

    async def get_project(self, project_id: str, *, with_relations: bool = False) -> Project | None:
        return await self.repo.get(project_id, with_relations=with_relations)

    async def require_project(self, project_id: str, *, with_relations: bool = False) -> Project:
        project = await self.repo.get(project_id, with_relations=with_relations)
        if project is None:
            raise NotFoundError(f"Project {project_id!r} not found.")
        return project

    async def add_source(self, project_id: str, data: SourceCreate) -> Source:
        """Validate the connector config eagerly, then persist the source."""
        await self.require_project(project_id)
        # build_connector validates the config and raises ValidationError on bad input,
        # so misconfigured sources are rejected at creation time, not analysis time.
        build_connector(data.source_type, data.config)
        source = Source(
            project_id=project_id,
            source_type=data.source_type,
            config=data.config,
            status="configured",
        )
        return await self.repo.add_source(source)

    async def list_sources(self, project_id: str) -> list[Source]:
        await self.require_project(project_id)
        return await self.repo.list_sources(project_id)
