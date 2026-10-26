"""HTTP routes for report generation and retrieval."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import available_report_types
from app.database.session import get_session
from app.reports.schemas import ReportCreate, ReportRead, ReportSummary
from app.reports.service import ReportService

# Generation/listing under the project; single-report fetch under /reports.
project_reports_router = APIRouter(prefix="/projects", tags=["reports"])
reports_router = APIRouter(prefix="/reports", tags=["reports"])
report_catalog_router = APIRouter(tags=["catalog"])


@report_catalog_router.get("/report-types", response_model=list[str])
async def list_report_types() -> list[str]:
    return available_report_types()


@project_reports_router.post(
    "/{project_id}/reports", response_model=ReportRead, status_code=status.HTTP_201_CREATED
)
async def generate_report(
    project_id: str,
    payload: ReportCreate,
    session: AsyncSession = Depends(get_session),
) -> ReportRead:
    """Generate an executive report / PRD / roadmap from the project's insights."""
    report = await ReportService(session).generate(project_id, payload.report_type)
    return ReportRead.model_validate(report)


@project_reports_router.get("/{project_id}/reports", response_model=list[ReportSummary])
async def list_reports(
    project_id: str, session: AsyncSession = Depends(get_session)
) -> list[ReportSummary]:
    reports = await ReportService(session).list_for_project(project_id)
    return [ReportSummary.model_validate(r) for r in reports]


@reports_router.get("/{report_id}", response_model=ReportRead)
async def get_report(
    report_id: str, session: AsyncSession = Depends(get_session)
) -> ReportRead:
    report = await ReportService(session).require_report(report_id)
    return ReportRead.model_validate(report)
