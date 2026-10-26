"""Data-access layer for the products domain (repository pattern)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.products.models import Product, Project, Source


class ProjectRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, project: Project) -> Project:
        self.session.add(project)
        await self.session.flush()
        return project

    async def get(self, project_id: str, *, with_relations: bool = False) -> Project | None:
        stmt = select(Project).where(Project.id == project_id)
        if with_relations:
            stmt = stmt.options(
                selectinload(Project.products), selectinload(Project.sources)
            )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self) -> list[Project]:
        result = await self.session.execute(
            select(Project).order_by(Project.created_at.desc())
        )
        return list(result.scalars().all())

    async def add_product(self, product: Product) -> Product:
        self.session.add(product)
        await self.session.flush()
        return product

    async def add_source(self, source: Source) -> Source:
        self.session.add(source)
        await self.session.flush()
        return source

    async def get_source(self, source_id: str) -> Source | None:
        result = await self.session.execute(select(Source).where(Source.id == source_id))
        return result.scalar_one_or_none()

    async def list_sources(self, project_id: str) -> list[Source]:
        result = await self.session.execute(
            select(Source).where(Source.project_id == project_id).order_by(Source.created_at)
        )
        return list(result.scalars().all())
