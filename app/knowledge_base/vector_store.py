"""Vector store abstraction over Qdrant.

Qdrant runs in local (embedded) mode by default — a directory path, no server — and
switches to a server with a single config change. The abstract base keeps the rest of
the platform independent of Qdrant specifics.
"""

from __future__ import annotations

import asyncio
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from loguru import logger

from app.core.config import get_settings


@dataclass
class VectorRecord:
    """A vector plus its payload, ready to upsert."""

    vector: list[float]
    payload: dict
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class SearchHit:
    """A single retrieval result."""

    id: str
    score: float
    payload: dict


class VectorStore(ABC):
    @abstractmethod
    async def ensure_collection(self, dimension: int) -> None: ...

    @abstractmethod
    async def upsert(self, records: list[VectorRecord]) -> None: ...

    @abstractmethod
    async def search(
        self, vector: list[float], *, top_k: int = 5, filters: dict | None = None
    ) -> list[SearchHit]: ...


class QdrantVectorStore(VectorStore):
    """Qdrant-backed vector store (local path or server URL)."""

    def __init__(self, collection: str | None = None) -> None:
        settings = get_settings()
        self.collection = collection or settings.qdrant_collection
        self._client = self._build_client(settings)
        self._ready = False
        # Local-mode Qdrant persists to its own embedded SQLite file and is not safe
        # under concurrent access — two analyze jobs writing at once (e.g. the
        # Analyze button triggered twice) reproduced a real crash here
        # ("sqlite3.InterfaceError: bad parameter or other API misuse") from two
        # asyncio.to_thread() calls hitting it simultaneously. Every operation goes
        # through this lock so the single-writer assumption is actually enforced.
        self._lock = asyncio.Lock()

    @staticmethod
    def _build_client(settings):
        from qdrant_client import QdrantClient

        if settings.qdrant_url and settings.qdrant_url.strip():
            logger.info("Connecting to Qdrant server: {}", settings.qdrant_url)
            return QdrantClient(url=settings.qdrant_url)
        path = settings.qdrant_local_path or "./data/qdrant"
        Path(path).mkdir(parents=True, exist_ok=True)
        logger.info("Using local Qdrant store at: {}", path)
        return QdrantClient(path=path)

    async def ensure_collection(self, dimension: int) -> None:
        if self._ready:
            return
        async with self._lock:
            if self._ready:  # a concurrent caller may have already done this
                return
            await asyncio.to_thread(self._ensure_collection_sync, dimension)
            self._ready = True

    def _ensure_collection_sync(self, dimension: int) -> None:
        from qdrant_client import models

        if not self._client.collection_exists(self.collection):
            self._client.create_collection(
                collection_name=self.collection,
                vectors_config=models.VectorParams(
                    size=dimension, distance=models.Distance.COSINE
                ),
            )
            logger.info("Created Qdrant collection {!r} (dim={})", self.collection, dimension)

    async def upsert(self, records: list[VectorRecord]) -> None:
        if not records:
            return
        async with self._lock:
            await asyncio.to_thread(self._upsert_sync, records)

    def _upsert_sync(self, records: list[VectorRecord]) -> None:
        from qdrant_client import models

        points = [
            models.PointStruct(id=r.id, vector=r.vector, payload=r.payload) for r in records
        ]
        self._client.upsert(collection_name=self.collection, points=points)

    async def search(
        self, vector: list[float], *, top_k: int = 5, filters: dict | None = None
    ) -> list[SearchHit]:
        async with self._lock:
            return await asyncio.to_thread(self._search_sync, vector, top_k, filters or {})

    def _search_sync(self, vector: list[float], top_k: int, filters: dict) -> list[SearchHit]:
        from qdrant_client import models

        query_filter = None
        if filters:
            conditions = [
                models.FieldCondition(key=k, match=models.MatchValue(value=v))
                for k, v in filters.items()
            ]
            query_filter = models.Filter(must=conditions)

        results = self._client.query_points(
            collection_name=self.collection,
            query=vector,
            limit=top_k,
            query_filter=query_filter,
            with_payload=True,
        ).points
        return [
            SearchHit(id=str(p.id), score=float(p.score), payload=p.payload or {})
            for p in results
        ]


@lru_cache
def get_vector_store() -> VectorStore:
    """Process-wide singleton (local Qdrant holds a single-writer file lock)."""
    return QdrantVectorStore()
