"""Business logic for persisting ingested reviews."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.ingestion.base import RawDocument
from app.reviews.models import Review
from app.reviews.repository import ReviewRepository


class ReviewService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = ReviewRepository(session)

    async def store_documents(
        self,
        project_id: str,
        source_id: str | None,
        source_type: str,
        documents: list[RawDocument],
    ) -> list[Review]:
        """Persist new documents, skipping ones already stored (by external id)."""
        existing = await self.repo.existing_external_ids(project_id, source_type)
        new_reviews: list[Review] = []
        for doc in documents:
            if doc.external_id is not None and doc.external_id in existing:
                continue
            if doc.external_id is not None:
                existing.add(doc.external_id)
            new_reviews.append(
                Review(
                    project_id=project_id,
                    source_id=source_id,
                    source_type=source_type,
                    external_id=doc.external_id,
                    text=doc.text,
                    title=doc.title,
                    author=doc.author,
                    rating=doc.rating,
                    locale=doc.locale,
                    url=doc.url,
                    posted_at=doc.posted_at,
                    review_metadata=doc.metadata,
                )
            )
        if new_reviews:
            await self.repo.add_many(new_reviews)
        return new_reviews

    async def list_for_project(self, project_id: str, **kwargs) -> list[Review]:
        return await self.repo.list_for_project(project_id, **kwargs)

    async def count(self, project_id: str) -> int:
        return await self.repo.count(project_id)
