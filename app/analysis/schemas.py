"""Pydantic schemas for analysis: the structured insight + aggregate dashboards.

``ReviewInsight`` is the contract Claude must fill for every review — it is passed to
``messages.parse`` as the output schema, so the model's response is validated against
it and never trusted as free-form text.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Sentiment = Literal["positive", "neutral", "negative", "mixed"]
Severity = Literal["low", "medium", "high", "critical"]
Impact = Literal["low", "medium", "high"]


class ReviewInsight(BaseModel):
    """Structured insight extracted from a single review (the LLM output schema)."""

    model_config = ConfigDict(extra="ignore")

    sentiment: Sentiment = Field(description="Overall sentiment of the feedback.")
    emotion: str = Field(description="Dominant emotion, e.g. 'frustration', 'delight'.")
    user_intent: str = Field(description="What the user was trying to do / express.")
    topic: str = Field(description="Concise topic label, e.g. 'Offline playback'.")
    pain_point: str | None = Field(default=None, description="The core problem, if any.")
    root_cause: str | None = Field(default=None, description="Likely underlying cause, if inferable.")
    feature_request: str | None = Field(default=None, description="Requested feature, if any.")
    severity: Severity = Field(description="Severity of the issue for the user.")
    confidence: float = Field(ge=0.0, le=1.0, description="Model confidence 0..1.")
    persona: str = Field(description="Short user persona label, e.g. 'Daily commuter'.")
    business_impact: Impact = Field(description="Estimated impact on the business.")
    suggested_opportunity: str | None = Field(
        default=None, description="A concrete product opportunity this implies."
    )


# --- Aggregated dashboard schemas (read models for /insights) ---
class CountedItem(BaseModel):
    label: str
    count: int
    examples: list[str] = Field(default_factory=list)


class PainPointSummary(CountedItem):
    severity_mix: dict[str, int] = Field(default_factory=dict)


class PersonaSummary(CountedItem):
    top_pain_points: list[str] = Field(default_factory=list)


class OpportunitySummary(CountedItem):
    impact_mix: dict[str, int] = Field(default_factory=dict)


class InsightsOverview(BaseModel):
    project_id: str
    total_reviews: int
    analyzed_reviews: int
    sentiment_distribution: dict[str, int] = Field(default_factory=dict)
    top_topics: list[CountedItem] = Field(default_factory=list)
    pain_points: list[PainPointSummary] = Field(default_factory=list)
    personas: list[PersonaSummary] = Field(default_factory=list)
    opportunities: list[OpportunitySummary] = Field(default_factory=list)
