"""Shared Pydantic schema primitives."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, field_validator


class ORMModel(BaseModel):
    """Base schema for response models read from ORM objects."""

    model_config = ConfigDict(from_attributes=True)


def assume_utc_if_naive(value: object) -> object:
    """Attach UTC tzinfo to a naive datetime; pass everything else through.

    Every datetime this app writes originates from ``datetime.now(timezone.utc)``
    (see app.database.base._utcnow and the call sites of Source.last_collected_at),
    but SQLite has no real timezone-aware column type, so SQLAlchemy reads them back
    as naive datetimes that are UTC in every way except the label. Serialized as-is,
    the JSON has no "Z"/offset, and JS's `new Date(...)` then parses timezone-less
    ISO strings as *local* time in the browser — a report generated seconds ago read
    "5h ago" for an IST user (UTC+5:30), and a source collected minutes ago showed the
    same "5h ago" on the Sources tab (last_collected_at has the identical shape but
    lives outside TimestampedSchema, so it needed this applied separately).
    Postgres round-trips real tz-aware values, so this only ever fires on the
    naive-but-actually-UTC case; already-aware datetimes pass through untouched.
    """
    if isinstance(value, datetime) and value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


class TimestampedSchema(ORMModel):
    """Mixin exposing the common id + timestamp fields."""

    id: str
    created_at: datetime
    updated_at: datetime

    _assume_utc_if_naive = field_validator("created_at", "updated_at", mode="before")(
        assume_utc_if_naive
    )
