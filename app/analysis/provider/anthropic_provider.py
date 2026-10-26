"""Anthropic implementation of :class:`LLMProvider`.

This is the *only* module that imports the Anthropic SDK or references the API key.
Per-review insights use ``messages.parse`` so responses are validated against the
Pydantic schema; transient failures (429 / 5xx / connection) retry with backoff.
"""

from __future__ import annotations

from typing import TypeVar

import anthropic
from loguru import logger
from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from app.analysis.provider.base import LLMProvider
from app.core.config import get_settings
from app.core.errors import FeatureUnavailableError

T = TypeVar("T", bound=BaseModel)


def _is_retryable(exc: BaseException) -> bool:
    """Retry rate limits, server errors, and connection blips — not 4xx client errors."""
    if isinstance(exc, (anthropic.RateLimitError, anthropic.APIConnectionError)):
        return True
    if isinstance(exc, anthropic.APIStatusError):
        return exc.status_code >= 500
    return False


_retry = retry(
    retry=retry_if_exception(_is_retryable),
    wait=wait_exponential(multiplier=1, min=1, max=20),
    stop=stop_after_attempt(4),
    reraise=True,
)


class AnthropicProvider(LLMProvider):
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.has_anthropic_key:
            # Surfaced as 503 by the API layer when an AI endpoint is hit.
            raise FeatureUnavailableError(
                "ANTHROPIC_API_KEY is not set — AI analysis and chat are unavailable. "
                "Set it in your environment / .env to enable these features."
            )
        self._model = settings.anthropic_model
        # Pass the key explicitly rather than letting the SDK auto-read os.environ:
        # pydantic-settings loads .env into Settings without exporting it to
        # os.environ, so a key that only lives in .env (not a real shell export) is
        # invisible to the SDK's own detection — reproduced directly, has_anthropic_key
        # was true while every real call failed with "Could not resolve authentication
        # method." Settings is the single source of truth; give it to the client.
        self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    @property
    def model(self) -> str:
        return self._model

    @_retry
    async def parse(
        self, *, system: str, user: str, schema: type[T], max_tokens: int = 1024
    ) -> T:
        try:
            response = await self._client.messages.parse(
                model=self._model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}],
                output_format=schema,
            )
        except PydanticValidationError as exc:
            # messages.parse() raises this itself when the response text isn't valid
            # JSON for `schema` — in practice this means Claude's output got cut off
            # mid-string because max_tokens was too small for the full document
            # (reproduced directly generating an executive report). Previously
            # unhandled: it crashed straight through every layer as a raw 500.
            logger.warning(
                "Structured output failed to validate against {} (likely truncated "
                "by max_tokens={}): {}",
                schema.__name__,
                max_tokens,
                exc,
            )
            raise FeatureUnavailableError(
                "The model's structured response was incomplete or malformed — this "
                "usually means it ran out of output tokens mid-document. Try again, "
                "or shorten the input."
            ) from exc
        if response.stop_reason == "refusal" or response.parsed_output is None:
            raise FeatureUnavailableError(
                "The model declined to analyze this content or returned no structured output."
            )
        return response.parsed_output

    @_retry
    async def complete(self, *, system: str, user: str, max_tokens: int = 1500) -> str:
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        if response.stop_reason == "refusal":
            logger.warning("Claude refused the chat request.")
            return "I'm unable to answer that request."
        return "".join(
            block.text for block in response.content if getattr(block, "type", None) == "text"
        ).strip()
