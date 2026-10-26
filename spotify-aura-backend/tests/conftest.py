"""Shared test configuration and fixtures.

Environment is configured *before* any app import so the cached Settings point
at an isolated temp SQLite db, and no real credentials leak into tests — same
approach as the main platform's tests/conftest.py, for the same reason:
pydantic-settings reads .env directly regardless of os.environ, so a bare
os.environ.pop() doesn't actually isolate anything.
"""

from __future__ import annotations

import os
import tempfile
from collections.abc import AsyncIterator

_TMP = tempfile.mkdtemp(prefix="spotify-aura-tests-")
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{_TMP}/test.db"
os.environ["ANTHROPIC_API_KEY"] = ""
os.environ["SPOTIFY_CLIENT_ID"] = ""
os.environ["SPOTIFY_CLIENT_SECRET"] = ""
os.environ["JWT_SECRET"] = "test-secret-not-for-production-padded-to-32-bytes-plus"
# Disabled, not just "high" — a shared ASGI client's requests across every test
# in the run would otherwise accumulate against the same apparent IP and start
# failing later tests with spurious 429s. rate_limit.py has its own dedicated
# unit tests that exercise the real limiting behavior directly.
os.environ["RATE_LIMIT_PER_MINUTE"] = "0"

import httpx  # noqa: E402
import pytest_asyncio  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: E402

from app.database import SessionLocal, init_models  # noqa: E402
from app.main import app as _app  # noqa: E402


@pytest_asyncio.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    await init_models()
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@pytest_asyncio.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    await init_models()
    transport = httpx.ASGITransport(app=_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
