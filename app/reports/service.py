"""Report service — orchestrates evidence gathering + agent generation + persistence."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import get_agent
from app.analysis.provider.claude_service import ClaudeService, get_claude_service
from app.analysis.service import AnalysisService
from app.core.errors import NotFoundError, ValidationError
from app.products.service import ProjectService
from app.reports.models import Report
from app.reports.repository import ReportRepository
from app.reviews.service import ReviewService


class ReportService:
    def __init__(
        self, session: AsyncSession, claude_service: ClaudeService | None = None
    ) -> None:
        self.session = session
        self.repo = ReportRepository(session)
        self.claude = claude_service or get_claude_service()

    async def generate(self, project_id: str, report_type: str) -> Report:
        """Generate a report grounded on the project's analyzed insights."""
        project = await ProjectService(self.session).require_project(project_id)
        agent = get_agent(report_type)  # validates the type early

        total = await ReviewService(self.session).count(project_id)
        overview = await AnalysisService(self.session).build_overview(project_id, total)
        if overview.analyzed_reviews == 0:
            raise ValidationError(
                "No analyzed insights yet — run POST /projects/{id}/analyze first."
            )

        # Representative excerpts as grounding evidence for the agent.
        sample = await ReviewService(self.session).list_for_project(project_id, limit=25)
        evidence = [r.text for r in sample]

        document, markdown = await agent.run(
            self.claude, overview, project.product_name, evidence
        )
        report = Report(
            project_id=project_id,
            report_type=report_type,
            title=f"{agent.title}: {project.product_name}",
            model=self.claude.model,
            content_markdown=markdown,
            data=document.model_dump(),
        )
        return await self.repo.add(report)

    async def list_for_project(self, project_id: str) -> list[Report]:
        await ProjectService(self.session).require_project(project_id)
        return await self.repo.list_for_project(project_id)

    async def require_report(self, report_id: str) -> Report:
        report = await self.repo.get(report_id)
        if report is None:
            raise NotFoundError(f"Report {report_id!r} not found.")
        return report
