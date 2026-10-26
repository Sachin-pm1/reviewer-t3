from __future__ import annotations

import re
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class MemoryIn(BaseModel):
    date: str = Field(min_length=10, max_length=10)
    note: str = Field(min_length=1, max_length=2000)
    mood: str | None = Field(default=None, max_length=50)

    @field_validator("date")
    @classmethod
    def _validate_date(cls, value: str) -> str:
        if not _DATE_RE.match(value):
            raise ValueError("date must be in YYYY-MM-DD format")
        return value


class MemoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    date: str
    note: str
    mood: str | None
    created_at: datetime

    @field_validator("created_at", mode="before")
    @classmethod
    def _assume_utc_if_naive(cls, value: object) -> object:
        # Same SQLite-drops-tzinfo-on-round-trip fix as UserRead.created_at.
        if isinstance(value, datetime) and value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
