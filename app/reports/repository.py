"""Data-access for reports."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.reports.models import Report


class ReportRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, report: Report) -> Report:
        self.session.add(report)
        await self.session.flush()
        return report

    async def get(self, report_id: str) -> Report | None:
        return await self.session.get(Report, report_id)

    async def list_for_project(self, project_id: str) -> list[Report]:
        result = await self.session.execute(
            select(Report)
            .where(Report.project_id == project_id)
            .order_by(Report.created_at.desc())
        )
        return list(result.scalars().all())
