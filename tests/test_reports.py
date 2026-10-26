"""Report generation tests (offline, fake provider)."""

from __future__ import annotations

import pytest

from app.agents.base import available_report_types
from app.analysis.provider.claude_service import ClaudeService
from app.analysis.service import AnalysisService
from app.core.errors import ValidationError
from app.ingestion.base import RawDocument
from app.products.schemas import ProjectCreate
from app.products.service import ProjectService
from app.reports.service import ReportService
from app.reviews.service import ReviewService
from tests._fakes import FakeProvider

_FEEDBACK = [
    ("Offline downloads keep disappearing on my commute", 2.0),
    ("The app crashes and offline mode is broken", 1.0),
    ("I love Discover Weekly, it's incredible", 5.0),
]


async def _analyzed_project(db_session):
    project = await ProjectService(db_session).create_project(
        ProjectCreate(name="Spotify", product_name="Spotify")
    )
    docs = [
        RawDocument(source_type="file_csv", external_id=str(i), text=t, rating=r)
        for i, (t, r) in enumerate(_FEEDBACK)
    ]
    await ReviewService(db_session).store_documents(project.id, None, "file_csv", docs)
    reviews = await ReviewService(db_session).list_for_project(
        project.id, only_unanalyzed=True
    )
    await AnalysisService(db_session, claude_service=ClaudeService(FakeProvider())).analyze_reviews(
        project.id, "Spotify", reviews
    )
    return project


def test_report_types_registered():
    types = available_report_types()
    assert {"executive", "prd", "roadmap"} <= set(types)


async def test_generate_executive_report(db_session):
    project = await _analyzed_project(db_session)
    service = ReportService(db_session, claude_service=ClaudeService(FakeProvider()))

    report = await service.generate(project.id, "executive")
    assert report.report_type == "executive"
    assert report.model == "fake-model"
    assert "# Executive Product Intelligence Report" in report.content_markdown
    assert "## Validated Pain Points" in report.content_markdown
    assert "## Product Roadmap" in report.content_markdown
    # Structured payload is persisted alongside the rendered markdown.
    assert report.data["executive_summary"]
    assert report.data["opportunity_ranking"]


async def test_generate_prd_and_roadmap(db_session):
    project = await _analyzed_project(db_session)
    service = ReportService(db_session, claude_service=ClaudeService(FakeProvider()))

    prd = await service.generate(project.id, "prd")
    assert prd.report_type == "prd"
    assert "# PRD:" in prd.content_markdown
    assert "## User Stories" in prd.content_markdown

    roadmap = await service.generate(project.id, "roadmap")
    assert roadmap.report_type == "roadmap"
    assert "Initiatives" in roadmap.content_markdown

    listed = await service.list_for_project(project.id)
    assert len(listed) == 2
    fetched = await service.require_report(prd.id)
    assert fetched.id == prd.id


async def test_unknown_report_type_raises(db_session):
    project = await _analyzed_project(db_session)
    service = ReportService(db_session, claude_service=ClaudeService(FakeProvider()))
    with pytest.raises(ValidationError):
        await service.generate(project.id, "nonsense")


async def test_report_requires_analysis_first(db_session):
    project = await ProjectService(db_session).create_project(
        ProjectCreate(name="Empty", product_name="Empty")
    )
    service = ReportService(db_session, claude_service=ClaudeService(FakeProvider()))
    with pytest.raises(ValidationError):
        await service.generate(project.id, "executive")
