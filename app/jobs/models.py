"""ORM model for background jobs."""

from __future__ import annotations

from enum import StrEnum

from sqlalchemy import JSON, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class JobStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class CollectionJob(Base):
    __tablename__ = "collection_jobs"

    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), index=True
    )
    type: Mapped[str] = mapped_column(String(32), default="analyze")
    status: Mapped[str] = mapped_column(String(16), default=JobStatus.PENDING, index=True)
    stage: Mapped[str] = mapped_column(String(32), default="queued")
    processed: Mapped[int] = mapped_column(Integer, default=0)
    total: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str | None] = mapped_column(Text, default=None)
    result: Mapped[dict] = mapped_column(JSON, default=dict)

    @property
    def progress(self) -> float:
        """Completion fraction 0..1 (0 when total unknown)."""
        return round(self.processed / self.total, 4) if self.total else 0.0
