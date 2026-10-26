"""HTTP routes for analysis dashboards (read models)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.analysis.schemas import InsightsOverview
from app.analysis.service import AnalysisService
from app.database.session import get_session
from app.products.service import ProjectService
from app.reviews.service import ReviewService

router = APIRouter(prefix="/projects", tags=["analysis"])


@router.get("/{project_id}/insights", response_model=InsightsOverview)
async def get_insights(
    project_id: str, session: AsyncSession = Depends(get_session)
) -> InsightsOverview:
    """Aggregated pain points, personas, opportunities, topics, and sentiment.

    Reads previously-stored insights — does not call the model. Run ``/analyze`` first.
    """
    project = await ProjectService(session).require_project(project_id)
    total_reviews = await ReviewService(session).count(project_id)
    return await AnalysisService(session).build_overview(project_id, total_reviews)
