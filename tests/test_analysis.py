"""Integration test: analyze persisted reviews + aggregate, fully offline."""

from __future__ import annotations

from app.analysis.provider.claude_service import ClaudeService
from app.analysis.service import AnalysisService
from app.ingestion.base import RawDocument
from app.products.schemas import ProjectCreate
from app.products.service import ProjectService
from app.reviews.service import ReviewService
from tests._fakes import FakeProvider

_FEEDBACK = [
    ("Offline downloads keep disappearing on my commute", 2.0),
    ("The app crashes and offline mode is broken", 1.0),
    ("I love Discover Weekly, it's incredible", 5.0),
    ("Amazing collaborative playlists, great feature", 5.0),
    ("Offline playback fails without a connection", 2.0),
]


async def test_analyze_and_overview(db_session):
    project = await ProjectService(db_session).create_project(
        ProjectCreate(name="Spotify", product_name="Spotify")
    )

    docs = [
        RawDocument(source_type="file_csv", external_id=str(i), text=text, rating=rating)
        for i, (text, rating) in enumerate(_FEEDBACK)
    ]
    await ReviewService(db_session).store_documents(project.id, None, "file_csv", docs)
    reviews = await ReviewService(db_session).list_for_project(
        project.id, only_unanalyzed=True
    )
    assert len(reviews) == len(_FEEDBACK)

    analysis = AnalysisService(db_session, claude_service=ClaudeService(FakeProvider()))
    analyzed = await analysis.analyze_reviews(project.id, "Spotify", reviews)
    assert analyzed == len(_FEEDBACK)

    overview = await analysis.build_overview(project.id, total_reviews=len(_FEEDBACK))
    assert overview.analyzed_reviews == len(_FEEDBACK)
    # Three negative + two positive in the fixture.
    assert overview.sentiment_distribution.get("negative") == 3
    assert overview.sentiment_distribution.get("positive") == 2
    # The shared negative pain point aggregates across reviews.
    assert overview.pain_points
    assert overview.pain_points[0].count == 3
    assert overview.personas
    assert overview.opportunities
