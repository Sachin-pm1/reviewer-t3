"""Async SQLAlchemy engine, declarative base, and session dependency.

This project had no persistence at all until accounts were added — everything
was either stateless (Companion) or in-memory (the experience-track cache).
SQLite is enough here: the only durable data is accounts and taste profiles,
both tiny, low-write tables.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from datetime import datetime, timezone
from pathlib import Path

from fastapi import Depends
from sqlalchemy import DateTime, String
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing import Annotated

from app.config import get_settings


def _new_id() -> str:
    return uuid.uuid4().hex


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_new_id)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


def _build_engine():
    url = get_settings().database_url
    if url.startswith("sqlite"):
        db_path = url.split("///", 1)[-1]
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    return create_async_engine(url, future=True, echo=False)


engine = _build_engine()
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def init_models() -> None:
    from app import models_registry  # noqa: F401 — registers models on Base.metadata

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


DbSession = Annotated[AsyncSession, Depends(get_session)]
