"""HTTP routes for browsing ingested reviews."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.products.service import ProjectService
from app.reviews.schemas import ReviewRead
from app.reviews.service import ReviewService

router = APIRouter(prefix="/projects", tags=["reviews"])


@router.get("/{project_id}/reviews", response_model=list[ReviewRead])
async def list_reviews(
    project_id: str,
    limit: int = Query(default=50, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
) -> list[ReviewRead]:
    """List ingested reviews for a project (most recent first by insertion order)."""
    await ProjectService(session).require_project(project_id)
    reviews = await ReviewService(session).list_for_project(project_id, limit=limit)
    return [ReviewRead.model_validate(r) for r in reviews]
