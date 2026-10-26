"""Data-access for stored insights."""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.analysis.models import ReviewInsightRecord
from app.reviews.models import Review


class InsightRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_many(self, records: Sequence[ReviewInsightRecord]) -> None:
        self.session.add_all(list(records))
        await self.session.flush()

    async def count_for_project(self, project_id: str) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(ReviewInsightRecord)
            .where(ReviewInsightRecord.project_id == project_id)
        )
        return int(result.scalar_one())

    async def list_with_review_text(
        self, project_id: str
    ) -> list[tuple[ReviewInsightRecord, str]]:
        """Insights joined to their review text (for aggregation + examples)."""
        stmt = (
            select(ReviewInsightRecord, Review.text)
            .join(Review, Review.id == ReviewInsightRecord.review_id)
            .where(ReviewInsightRecord.project_id == project_id)
        )
        result = await self.session.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]
