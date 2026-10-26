"""Async SQLAlchemy engine, declarative base, and schema bootstrap.

Local-first: the default engine is async SQLite. Switching to Postgres is purely a
``DATABASE_URL`` change — no code here assumes a particular backend. ``init_models``
creates tables for the local/dev path; production would use Alembic migrations.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import DateTime, String, func
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.core.config import get_settings


def _new_id() -> str:
    """Generate a short, URL-safe, sortable-enough unique id."""
    return uuid.uuid4().hex


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """Declarative base with common id + timestamp columns for every table."""

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_new_id)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )


def _build_engine() -> AsyncEngine:
    settings = get_settings()
    url = settings.database_url
    connect_args: dict = {}
    # Ensure the SQLite data directory exists before the engine opens the file, and
    # give writers a generous busy timeout (the background job uses parallel sessions).
    if url.startswith("sqlite"):
        db_path = url.split("///", 1)[-1]
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        connect_args["timeout"] = 30
    return create_async_engine(url, future=True, echo=False, connect_args=connect_args)


engine: AsyncEngine = _build_engine()
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def init_models() -> None:
    """Create all tables (dev/local path). Imports models for metadata registration."""
    # Import here so every model registers on Base.metadata before create_all.
    from app import models_registry  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
