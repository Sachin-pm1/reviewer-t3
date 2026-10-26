"""ORM model persisting a structured insight for one review."""

from __future__ import annotations

from sqlalchemy import JSON, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class ReviewInsightRecord(Base):
    __tablename__ = "review_insights"

    review_id: Mapped[str] = mapped_column(
        ForeignKey("reviews.id", ondelete="CASCADE"), index=True, unique=True
    )
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), index=True
    )
    model: Mapped[str] = mapped_column(String(64))

    sentiment: Mapped[str] = mapped_column(String(16), index=True)
    emotion: Mapped[str] = mapped_column(String(64))
    user_intent: Mapped[str] = mapped_column(Text)
    topic: Mapped[str] = mapped_column(String(200), index=True)
    pain_point: Mapped[str | None] = mapped_column(Text, default=None)
    root_cause: Mapped[str | None] = mapped_column(Text, default=None)
    feature_request: Mapped[str | None] = mapped_column(Text, default=None)
    severity: Mapped[str] = mapped_column(String(16), index=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    persona: Mapped[str] = mapped_column(String(200), index=True)
    business_impact: Mapped[str] = mapped_column(String(16), index=True)
    suggested_opportunity: Mapped[str | None] = mapped_column(Text, default=None)

    raw: Mapped[dict] = mapped_column(JSON, default=dict)
