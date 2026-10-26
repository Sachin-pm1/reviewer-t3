"""Data-access layer for reviews."""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.reviews.models import Review


class ReviewRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_many(self, reviews: Sequence[Review]) -> list[Review]:
        self.session.add_all(reviews)
        await self.session.flush()
        return list(reviews)

    async def existing_external_ids(self, project_id: str, source_type: str) -> set[str]:
        """External ids already stored for a project+source (for de-duplication)."""
        stmt = select(Review.external_id).where(
            Review.project_id == project_id,
            Review.source_type == source_type,
            Review.external_id.is_not(None),
        )
        result = await self.session.execute(stmt)
        return {row for (row,) in result.all() if row is not None}

    async def list_for_project(
        self, project_id: str, *, limit: int | None = None, only_unanalyzed: bool = False
    ) -> list[Review]:
        stmt = select(Review).where(Review.project_id == project_id)
        if only_unanalyzed:
            stmt = stmt.where(Review.analyzed.is_(False))
        stmt = stmt.order_by(Review.created_at)
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_many(self, review_ids: Sequence[str]) -> dict[str, Review]:
        if not review_ids:
            return {}
        result = await self.session.execute(
            select(Review).where(Review.id.in_(list(review_ids)))
        )
        return {r.id: r for r in result.scalars().all()}

    async def count(self, project_id: str) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(Review).where(Review.project_id == project_id)
        )
        return int(result.scalar_one())
