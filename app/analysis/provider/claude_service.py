"""ClaudeService — the single gateway every AI call goes through.

It owns the prompts and delegates the actual model call to an ``LLMProvider``. The
provider is created lazily so constructing the service never requires the API key;
only *using* it does (which then yields a clean 503 if the key is missing).
"""

from __future__ import annotations

from typing import TypeVar

from pydantic import BaseModel

from app.analysis.provider.base import LLMProvider
from app.analysis.schemas import ReviewInsight
from app.knowledge_base.service import RetrievedChunk

T = TypeVar("T", bound=BaseModel)

_ANALYZE_SYSTEM = (
    "You are a senior product analyst. Given a single piece of user feedback about a "
    "software product, extract a precise, structured insight. Be specific and avoid "
    "generic labels. If a field genuinely does not apply (e.g. no pain point in praise), "
    "leave the optional field null. Keep topic/persona labels short and reusable so "
    "similar feedback groups together."
)

_CHAT_SYSTEM = (
    "You are an AI product-intelligence copilot. Answer the user's question about a "
    "product using ONLY the provided customer-feedback excerpts as evidence. Cite "
    "excerpts inline as [1], [2], etc. If the excerpts don't contain the answer, say so "
    "plainly rather than inventing facts. Be concise, concrete, and useful to a product team."
)


class ClaudeService:
    def __init__(self, provider: LLMProvider | None = None) -> None:
        self._provider = provider

    @property
    def provider(self) -> LLMProvider:
        if self._provider is None:
            # Imported here to avoid importing the Anthropic SDK at module load.
            from app.analysis.provider.anthropic_provider import AnthropicProvider

            self._provider = AnthropicProvider()
        return self._provider

    @property
    def model(self) -> str:
        return self.provider.model

    async def analyze_review(
        self, *, text: str, product_name: str, rating: float | None = None
    ) -> ReviewInsight:
        """Extract a schema-validated :class:`ReviewInsight` from one review."""
        rating_line = f"Star rating: {rating}\n" if rating is not None else ""
        user = (
            f"Product: {product_name}\n"
            f"{rating_line}"
            f"Feedback:\n\"\"\"\n{text}\n\"\"\"\n\n"
            "Extract the structured insight."
        )
        return await self.provider.parse(
            system=_ANALYZE_SYSTEM, user=user, schema=ReviewInsight
        )

    async def generate(
        self, *, system: str, user: str, schema: type[T], max_tokens: int = 4096
    ) -> T:
        """Generate a larger schema-validated document (reports, PRDs, roadmaps)."""
        return await self.provider.parse(
            system=system, user=user, schema=schema, max_tokens=max_tokens
        )

    async def answer(
        self, *, question: str, product_name: str, context: list[RetrievedChunk]
    ) -> str:
        """Answer a copilot question grounded on retrieved feedback excerpts."""
        if not context:
            excerpts = "(no relevant feedback found)"
        else:
            excerpts = "\n\n".join(
                f"[{i}] (source: {c.source_type}, rating: {c.rating}) {c.text}"
                for i, c in enumerate(context, start=1)
            )
        user = (
            f"Product: {product_name}\n\n"
            f"Customer feedback excerpts:\n{excerpts}\n\n"
            f"Question: {question}"
        )
        return await self.provider.complete(system=_CHAT_SYSTEM, user=user)


def get_claude_service() -> ClaudeService:
    """Default ClaudeService with the Anthropic provider (created on first use)."""
    return ClaudeService()
