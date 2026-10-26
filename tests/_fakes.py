"""Test doubles — a deterministic LLM provider so AI paths run offline."""

from __future__ import annotations

from typing import TypeVar

from pydantic import BaseModel

from app.agents.schemas import (
    ExecutiveReport,
    Initiative,
    OpportunityItem,
    PainPointItem,
    PersonaItem,
    PRDDocument,
    RoadmapDocument,
    RoadmapPhase,
    RoadmapStage,
    UserStory,
)
from app.analysis.provider.base import LLMProvider
from app.analysis.schemas import ReviewInsight

T = TypeVar("T", bound=BaseModel)


def _fake_document(schema: type[BaseModel]) -> BaseModel:
    """Build a minimal valid instance for a report schema (offline stand-in)."""
    if schema is ExecutiveReport:
        return ExecutiveReport(
            executive_summary="Users love discovery but offline playback is broken.",
            problem_statement="Offline downloads disappear, undermining Premium value.",
            validated_pain_points=[
                PainPointItem(
                    label="Offline downloads disappear",
                    evidence_summary="Repeated reports of vanished downloads on commute.",
                    severity="high",
                )
            ],
            personas=[
                PersonaItem(
                    name="Daily commuter",
                    description="Listens offline during travel.",
                    key_needs=["Reliable offline playback"],
                )
            ],
            jobs_to_be_done=["Listen to saved music without a connection"],
            root_cause_analysis="Sync regression after a recent update.",
            business_impact="Churn risk among Premium subscribers.",
            opportunity_ranking=[
                OpportunityItem(
                    title="Fix offline sync",
                    rationale="Directly addresses the top pain point.",
                    impact="high",
                    effort="medium",
                )
            ],
            success_metrics=["Offline playback failure rate < 1%"],
            recommended_mvp="Reliable offline download + verification.",
            product_roadmap=[
                RoadmapPhase(phase="Now", focus="Reliability", items=["Fix offline sync"])
            ],
            risks=["Regression in download storage"],
            recommendations=["Prioritize offline reliability this quarter"],
        )
    if schema is PRDDocument:
        return PRDDocument(
            title="Reliable Offline Playback",
            overview="Ensure downloaded content always plays offline.",
            goals=["Eliminate vanished downloads"],
            non_goals=["Lossless audio"],
            user_stories=[
                UserStory(
                    as_a="commuter",
                    i_want="my downloads to persist",
                    so_that="I can listen on the subway",
                )
            ],
            functional_requirements=["Verify downloads on app start"],
            success_metrics=["<1% offline failures"],
            open_questions=["Which storage layer regressed?"],
        )
    if schema is RoadmapDocument:
        return RoadmapDocument(
            title="Spotify Reliability Roadmap",
            summary="Sequence reliability and discovery work by impact.",
            phases=[
                RoadmapStage(
                    phase="Now",
                    timeframe="This quarter",
                    objectives=["Fix offline playback"],
                    initiatives=[
                        Initiative(title="Fix offline sync", priority="P0", effort="medium")
                    ],
                )
            ],
        )
    raise AssertionError(f"FakeProvider has no stub for schema {schema!r}")


class FakeProvider(LLMProvider):
    """Returns predictable structured insights + answers without any network call."""

    @property
    def model(self) -> str:
        return "fake-model"

    async def parse(
        self, *, system: str, user: str, schema: type[T], max_tokens: int = 1024
    ) -> T:
        if schema is not ReviewInsight:
            return schema.model_validate(_fake_document(schema).model_dump())

        lowered = user.lower()
        positive = any(w in lowered for w in ("love", "great", "incredible", "amazing"))
        insight = ReviewInsight(
            sentiment="positive" if positive else "negative",
            emotion="delight" if positive else "frustration",
            user_intent="enjoy music" if positive else "report a problem",
            topic="Discovery" if positive else "Offline playback",
            pain_point=None if positive else "Offline downloads disappear",
            root_cause=None if positive else "Sync bug after update",
            feature_request=None,
            severity="low" if positive else "high",
            confidence=0.9,
            persona="Music explorer" if positive else "Daily commuter",
            business_impact="low" if positive else "high",
            suggested_opportunity=None if positive else "Fix offline sync reliability",
        )
        return schema.model_validate(insight.model_dump())

    async def complete(self, *, system: str, user: str, max_tokens: int = 1500) -> str:
        return "Users are unhappy mainly about broken offline playback [1]."
