"""ORM model for ingested reviews.

A ``Review`` is a normalized :class:`~app.ingestion.base.RawDocument` persisted against
a project + source. ``indexed`` / ``analyzed`` flags let the pipeline be idempotent and
resumable.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, Boolean, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Review(Base):
    __tablename__ = "reviews"

    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), index=True
    )
    source_id: Mapped[str | None] = mapped_column(
        ForeignKey("sources.id", ondelete="SET NULL"), default=None, index=True
    )
    source_type: Mapped[str] = mapped_column(String(64), index=True)
    external_id: Mapped[str | None] = mapped_column(String(255), default=None)

    text: Mapped[str] = mapped_column(Text)
    title: Mapped[str | None] = mapped_column(Text, default=None)
    author: Mapped[str | None] = mapped_column(String(255), default=None)
    rating: Mapped[float | None] = mapped_column(Float, default=None)
    locale: Mapped[str | None] = mapped_column(String(16), default=None)
    url: Mapped[str | None] = mapped_column(Text, default=None)
    posted_at: Mapped[datetime | None] = mapped_column(default=None)
    review_metadata: Mapped[dict] = mapped_column("metadata", JSON, default=dict)

    indexed: Mapped[bool] = mapped_column(Boolean, default=False)
    analyzed: Mapped[bool] = mapped_column(Boolean, default=False)
