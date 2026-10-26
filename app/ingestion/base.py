"""Core ingestion contracts: ``RawDocument`` and ``BaseConnector``.

These two types are the heart of the platform's extensibility. Everything downstream
(normalization, knowledge base, analysis) consumes ``RawDocument`` and never needs to
know where the data came from.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from datetime import datetime

from pydantic import BaseModel, Field


class RawDocument(BaseModel):
    """A single unit of feedback as emitted by a connector, before normalization.

    Connectors map their source-specific shape into this common envelope. ``text`` is
    the only strictly required signal; everything else is best-effort metadata.
    """

    source_type: str = Field(description="Connector type that produced this, e.g. 'google_play'.")
    external_id: str | None = Field(
        default=None, description="Stable id within the source, for de-duplication."
    )
    text: str = Field(description="The raw feedback text.")
    title: str | None = Field(default=None, description="Optional title/subject.")
    author: str | None = Field(default=None, description="Author/handle, if available.")
    rating: float | None = Field(default=None, description="Star/score rating, if available.")
    locale: str | None = Field(default=None, description="Language/region, e.g. 'en'.")
    url: str | None = Field(default=None, description="Permalink to the original item.")
    posted_at: datetime | None = Field(default=None, description="When it was posted.")
    metadata: dict = Field(default_factory=dict, description="Arbitrary source-specific extras.")


class BaseConnector(ABC):
    """Abstract base every data-source connector implements.

    A connector is constructed with a free-form ``config`` dict (validated by the
    concrete subclass) and exposes a single async generator, :meth:`collect`, that
    yields :class:`RawDocument` objects.
    """

    #: Unique source-type key. Set by subclasses; used by the registry and persisted
    #: on each Source row. Example: ``"google_play"``.
    source_type: str = ""

    def __init__(self, config: dict | None = None) -> None:
        self.config = config or {}

    @abstractmethod
    async def collect(self) -> AsyncIterator[RawDocument]:
        """Yield raw documents from the source.

        Implemented as an ``async def`` generator in subclasses.
        """
        raise NotImplementedError
        yield  # pragma: no cover - makes the abstract method an async generator type

    @classmethod
    def validate_config(cls, config: dict) -> dict:
        """Validate/normalize a source config. Override to enforce required keys.

        Returns the (possibly cleaned) config. Raise
        :class:`app.core.errors.ValidationError` on invalid input.
        """
        return config or {}
