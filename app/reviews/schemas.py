"""Response schemas for the reviews domain."""

from __future__ import annotations

from app.shared.schemas import TimestampedSchema


class ReviewRead(TimestampedSchema):
    project_id: str
    source_type: str
    external_id: str | None
    author: str | None
    rating: float | None
    text: str
    analyzed: bool
