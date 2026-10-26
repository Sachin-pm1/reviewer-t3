"""Tests for ClaudeService using a fake provider (no network)."""

from __future__ import annotations

from app.analysis.provider.claude_service import ClaudeService
from app.knowledge_base.service import RetrievedChunk
from tests._fakes import FakeProvider


async def test_analyze_review_returns_validated_insight():
    svc = ClaudeService(provider=FakeProvider())
    insight = await svc.analyze_review(text="I love Discover Weekly", product_name="Spotify")
    assert insight.sentiment == "positive"
    assert insight.confidence == 0.9
    assert svc.model == "fake-model"


async def test_analyze_review_detects_negative():
    svc = ClaudeService(provider=FakeProvider())
    insight = await svc.analyze_review(
        text="Offline downloads keep disappearing", product_name="Spotify"
    )
    assert insight.sentiment == "negative"
    assert insight.pain_point


async def test_answer_grounds_on_context():
    svc = ClaudeService(provider=FakeProvider())
    chunk = RetrievedChunk(
        text="offline mode is broken",
        score=0.92,
        review_id="r1",
        source_type="file_csv",
        rating=1.0,
    )
    answer = await svc.answer(
        question="Why are users unhappy?", product_name="Spotify", context=[chunk]
    )
    assert "[1]" in answer
