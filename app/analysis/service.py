"""Analysis service: run Claude over reviews and aggregate the results.

``analyze_reviews`` runs per-review structured extraction concurrently (bounded by a
semaphore), persists each insight, and marks the review analyzed. ``build_overview``
turns the stored insights into the dashboard read-model the API serves.
"""

from __future__ import annotations

import asyncio
from collections import Counter, defaultdict
from collections.abc import Awaitable, Callable

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.analysis.models import ReviewInsightRecord
from app.analysis.provider.claude_service import ClaudeService, get_claude_service
from app.analysis.repository import InsightRepository
from app.analysis.schemas import (
    CountedItem,
    InsightsOverview,
    OpportunitySummary,
    PainPointSummary,
    PersonaSummary,
)
from app.core.config import get_settings
from app.reviews.models import Review

ProgressCallback = Callable[[int, int], Awaitable[None]]


class AnalysisService:
    def __init__(
        self, session: AsyncSession, claude_service: ClaudeService | None = None
    ) -> None:
        self.session = session
        self.repo = InsightRepository(session)
        self.claude = claude_service or get_claude_service()

    async def analyze_reviews(
        self,
        project_id: str,
        product_name: str,
        reviews: list[Review],
        *,
        progress: ProgressCallback | None = None,
    ) -> int:
        """Analyze a batch of reviews concurrently. Returns the number analyzed."""
        if not reviews:
            return 0

        concurrency = max(1, get_settings().analysis_concurrency)
        semaphore = asyncio.Semaphore(concurrency)
        done = 0
        total = len(reviews)
        records: list[ReviewInsightRecord] = []
        lock = asyncio.Lock()

        async def worker(review: Review) -> None:
            nonlocal done
            async with semaphore:
                try:
                    insight = await self.claude.analyze_review(
                        text=review.text,
                        product_name=product_name,
                        rating=review.rating,
                    )
                except Exception as exc:  # one bad review must not sink the batch
                    logger.warning("Analysis failed for review {}: {}", review.id, exc)
                    return
                record = ReviewInsightRecord(
                    review_id=review.id,
                    project_id=project_id,
                    model=self.claude.model,
                    sentiment=insight.sentiment,
                    emotion=insight.emotion,
                    user_intent=insight.user_intent,
                    topic=insight.topic,
                    pain_point=insight.pain_point,
                    root_cause=insight.root_cause,
                    feature_request=insight.feature_request,
                    severity=insight.severity,
                    confidence=insight.confidence,
                    persona=insight.persona,
                    business_impact=insight.business_impact,
                    suggested_opportunity=insight.suggested_opportunity,
                    raw=insight.model_dump(),
                )
                review.analyzed = True
                async with lock:
                    records.append(record)
                    done += 1
                    if progress is not None:
                        await progress(done, total)

        await asyncio.gather(*(worker(r) for r in reviews))
        await self.repo.add_many(records)
        logger.info("Analyzed {}/{} reviews for project {}", len(records), total, project_id)
        return len(records)

    async def build_overview(self, project_id: str, total_reviews: int) -> InsightsOverview:
        """Aggregate stored insights into the dashboard overview."""
        rows = await self.repo.list_with_review_text(project_id)

        sentiment: Counter[str] = Counter()
        topic_counts: Counter[str] = Counter()
        topic_examples: dict[str, list[str]] = defaultdict(list)
        pain_counts: Counter[str] = Counter()
        pain_severity: dict[str, Counter[str]] = defaultdict(Counter)
        pain_examples: dict[str, list[str]] = defaultdict(list)
        persona_counts: Counter[str] = Counter()
        persona_pains: dict[str, Counter[str]] = defaultdict(Counter)
        opp_counts: Counter[str] = Counter()
        opp_impact: dict[str, Counter[str]] = defaultdict(Counter)
        opp_examples: dict[str, list[str]] = defaultdict(list)

        for record, review_text in rows:
            snippet = _snippet(review_text)
            sentiment[record.sentiment] += 1

            if record.topic:
                topic_counts[record.topic] += 1
                _add_example(topic_examples[record.topic], snippet)

            if record.pain_point:
                pain_counts[record.pain_point] += 1
                pain_severity[record.pain_point][record.severity] += 1
                _add_example(pain_examples[record.pain_point], snippet)

            if record.persona:
                persona_counts[record.persona] += 1
                if record.pain_point:
                    persona_pains[record.persona][record.pain_point] += 1

            if record.suggested_opportunity:
                opp_counts[record.suggested_opportunity] += 1
                opp_impact[record.suggested_opportunity][record.business_impact] += 1
                _add_example(opp_examples[record.suggested_opportunity], snippet)

        return InsightsOverview(
            project_id=project_id,
            total_reviews=total_reviews,
            analyzed_reviews=len(rows),
            sentiment_distribution=dict(sentiment),
            top_topics=[
                CountedItem(label=label, count=count, examples=topic_examples[label])
                for label, count in topic_counts.most_common(10)
            ],
            pain_points=[
                PainPointSummary(
                    label=label,
                    count=count,
                    examples=pain_examples[label],
                    severity_mix=dict(pain_severity[label]),
                )
                for label, count in pain_counts.most_common(10)
            ],
            personas=[
                PersonaSummary(
                    label=label,
                    count=count,
                    top_pain_points=[p for p, _ in persona_pains[label].most_common(3)],
                )
                for label, count in persona_counts.most_common(10)
            ],
            opportunities=[
                OpportunitySummary(
                    label=label,
                    count=count,
                    examples=opp_examples[label],
                    impact_mix=dict(opp_impact[label]),
                )
                for label, count in opp_counts.most_common(10)
            ],
        )


def _snippet(text: str, *, max_len: int = 160) -> str:
    text = (text or "").strip()
    return text if len(text) <= max_len else text[: max_len - 1].rstrip() + "…"


def _add_example(bucket: list[str], snippet: str, *, limit: int = 3) -> None:
    if snippet and snippet not in bucket and len(bucket) < limit:
        bucket.append(snippet)
