"""Schemas for the reports domain."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.shared.schemas import TimestampedSchema


class ReportCreate(BaseModel):
    report_type: str = Field(description="One of the registered report types, e.g. 'executive'.")


class ReportSummary(TimestampedSchema):
    project_id: str
    report_type: str
    title: str
    model: str


class ReportRead(ReportSummary):
    content_markdown: str
    data: dict
