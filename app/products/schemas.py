"""Request/response schemas for the products domain."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.shared.schemas import TimestampedSchema, assume_utc_if_naive


# --- Requests ---
class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200, description="Project/workspace name.")
    product_name: str = Field(
        min_length=1, max_length=200, description="The product being analyzed, e.g. 'Spotify'."
    )
    description: str | None = Field(default=None, description="Optional context.")


class SourceCreate(BaseModel):
    source_type: str = Field(description="Registered connector type, e.g. 'file_csv'.")
    config: dict = Field(default_factory=dict, description="Connector-specific configuration.")


# --- Responses ---
class ProductRead(TimestampedSchema):
    name: str


class SourceRead(TimestampedSchema):
    project_id: str
    source_type: str
    config: dict
    status: str
    review_count: int
    last_collected_at: datetime | None

    # Outside TimestampedSchema's created_at/updated_at, so needs the same
    # naive-SQLite-datetime-is-actually-UTC fix applied separately — see
    # assume_utc_if_naive's docstring for why (this is the exact field that
    # showed "5h ago" on the Sources tab moments after a real collection ran).
    _assume_utc = field_validator("last_collected_at", mode="before")(assume_utc_if_naive)


class ProjectRead(TimestampedSchema):
    name: str
    product_name: str
    description: str | None


class ProjectDetail(ProjectRead):
    products: list[ProductRead] = Field(default_factory=list)
    sources: list[SourceRead] = Field(default_factory=list)
