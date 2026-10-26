"""Embedding provider abstraction.

A thin interface so the embedding backend is swappable (local sentence-transformers
now; a hosted embedding API later) without touching the knowledge-base service. The
concrete provider loads the model lazily and runs encoding off the event loop.
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from functools import lru_cache

from loguru import logger

from app.core.config import get_settings


class EmbeddingProvider(ABC):
    """Turns text into dense vectors."""

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Vector dimensionality."""

    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of texts."""

    async def embed_one(self, text: str) -> list[float]:
        return (await self.embed([text]))[0]


class SentenceTransformerProvider(EmbeddingProvider):
    """Local embeddings via sentence-transformers."""

    def __init__(self, model_name: str | None = None) -> None:
        self._model_name = model_name or get_settings().embedding_model
        self._model = None  # lazy
        self._dimension: int | None = None

    def _load(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            logger.info("Loading embedding model: {}", self._model_name)
            self._model = SentenceTransformer(self._model_name)
            self._dimension = self._model.get_sentence_embedding_dimension()
        return self._model

    @property
    def dimension(self) -> int:
        if self._dimension is None:
            self._load()
        assert self._dimension is not None
        return self._dimension

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return await asyncio.to_thread(self._encode, texts)

    def _encode(self, texts: list[str]) -> list[list[float]]:
        model = self._load()
        vectors = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        return vectors.tolist()


@lru_cache
def get_embedding_provider() -> EmbeddingProvider:
    """Process-wide singleton embedding provider (model is expensive to load)."""
    return SentenceTransformerProvider()
