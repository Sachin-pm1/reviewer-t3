"""The provider interface every LLM backend implements."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMProvider(ABC):
    """Backend-agnostic LLM operations used by the platform."""

    @property
    @abstractmethod
    def model(self) -> str:
        """Identifier of the underlying model."""

    @abstractmethod
    async def parse(
        self, *, system: str, user: str, schema: type[T], max_tokens: int = 1024
    ) -> T:
        """Return a schema-validated structured object for ``user`` given ``system``."""

    @abstractmethod
    async def complete(self, *, system: str, user: str, max_tokens: int = 1500) -> str:
        """Return a plain-text completion (used for the RAG copilot)."""
