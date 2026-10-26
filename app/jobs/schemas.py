"""Schemas for jobs."""

from __future__ import annotations

from pydantic import BaseModel

from app.shared.schemas import TimestampedSchema


class JobRead(TimestampedSchema):
    project_id: str
    type: str
    status: str
    stage: str
    processed: int
    total: int
    progress: float
    error: str | None
    result: dict


class AnalyzeOptions(BaseModel):
    """Optional knobs for an analyze run."""

    max_reviews_per_source: int | None = None
