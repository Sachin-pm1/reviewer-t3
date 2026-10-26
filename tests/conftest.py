"""Shared test configuration and fixtures.

Environment is configured *before* any app import so the cached Settings point at an
isolated temp SQLite db + temp Qdrant path, and no real Anthropic key leaks into tests.
"""

from __future__ import annotations

import os
import tempfile
from collections.abc import AsyncIterator

# --- Isolate the test environment BEFORE importing app modules ---
_TMP = tempfile.mkdtemp(prefix="aipi-tests-")
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{_TMP}/test.db"
os.environ["QDRANT_PATH"] = f"{_TMP}/qdrant"
# Explicit empty strings, not pop() — pydantic-settings falls back to reading a real
# .env file directly when a var is merely absent from os.environ, so real credentials
# sitting in .env (for local dev) would otherwise leak into "offline" test runs.
os.environ["ANTHROPIC_API_KEY"] = ""
os.environ["REDDIT_CLIENT_ID"] = ""
os.environ["REDDIT_CLIENT_SECRET"] = ""
# Disabled, not just "high" — the shared ASGI test client's requests across every
# test in the run would otherwise accumulate against the same apparent IP and start
# failing later tests with spurious 429s. app/core/rate_limit.py has its own
# dedicated, isolated unit tests that exercise the real limiting behavior.
os.environ["RATE_LIMIT_PER_MINUTE"] = "0"

import httpx  # noqa: E402
import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: E402

import app.ingestion  # noqa: E402,F401 - registers connectors (lifespan does this normally)
from app.database.base import SessionLocal, init_models  # noqa: E402
from app.main import app as _app  # noqa: E402

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE_CSV = os.path.join(PROJECT_ROOT, "data", "sample_spotify_reviews.csv")


@pytest_asyncio.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    """A committed-on-success async session against the temp SQLite database."""
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
    """An ASGI-transport client against the real app — offline, no sockets."""
    await init_models()
    transport = httpx.ASGITransport(app=_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
def sample_csv_path() -> str:
    return SAMPLE_CSV
