"""The only module that imports the Anthropic SDK or reads the API key.

Structured output via messages.parse, same as the parent repo's
AnthropicProvider — see that file's history for why truncated/malformed JSON
needs an explicit catch rather than being left to crash raw.
"""

from __future__ import annotations

from typing import TypeVar

import anthropic
from loguru import logger
from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from app.config import get_settings
from app.errors import FeatureUnavailableError

T = TypeVar("T", bound=BaseModel)


def _is_retryable(exc: BaseException) -> bool:
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


class ClaudeService:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.has_anthropic_key:
            raise FeatureUnavailableError(
                "ANTHROPIC_API_KEY is not set — set it in .env to enable the Companion."
            )
        self._model = settings.anthropic_model
        self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    @property
    def model(self) -> str:
        return self._model

    @_retry
    async def generate(
        self, *, system: str, user: str, schema: type[T], max_tokens: int = 2048
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
            logger.warning(
                "Structured output failed to validate against {} (likely truncated): {}",
                schema.__name__,
                exc,
            )
            raise FeatureUnavailableError(
                "The model's structured response was incomplete or malformed. Try again."
            ) from exc
        if response.stop_reason == "refusal" or response.parsed_output is None:
            raise FeatureUnavailableError(
                "The model declined to analyze this content or returned no structured output."
            )
        return response.parsed_output


_instance: ClaudeService | None = None


def get_claude_service() -> ClaudeService:
    global _instance
    if _instance is None:
        _instance = ClaudeService()
    return _instance
