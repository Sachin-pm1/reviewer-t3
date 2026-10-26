"""Regression test: a real report-generation call against real data (858 analyzed
reviews) produced a Claude response that got cut off mid-JSON — messages.parse()
raises a bare pydantic ValidationError in that case, which was never caught anywhere
and crashed straight through as an unhandled 500. Exercises AnthropicProvider.parse()
directly with a stubbed SDK client (no network, no real key) since that's the one
layer FakeProvider intentionally never touches.
"""

from __future__ import annotations

import pytest
from pydantic import BaseModel, ValidationError

from app.analysis.provider.anthropic_provider import AnthropicProvider
from app.core.errors import FeatureUnavailableError


class _Schema(BaseModel):
    field: str


def _real_validation_error() -> ValidationError:
    """A genuine pydantic ValidationError, shaped like what messages.parse() raises
    on truncated JSON — not just any exception standing in for one."""
    try:
        _Schema.model_validate_json('{"field": "this string never closes')
    except ValidationError as exc:
        return exc
    raise AssertionError("expected model_validate_json to raise")  # pragma: no cover


def _provider_with_stubbed_client(parse_side_effect):
    provider = AnthropicProvider.__new__(AnthropicProvider)  # skip __init__: no key/SDK needed
    provider._model = "fake-model"

    class _FakeMessages:
        async def parse(self, **kwargs):
            return parse_side_effect(**kwargs)

    class _FakeClient:
        messages = _FakeMessages()

    provider._client = _FakeClient()
    return provider


async def test_truncated_structured_output_raises_a_clean_typed_error():
    def raise_truncated(**kwargs):
        raise _real_validation_error()

    provider = _provider_with_stubbed_client(raise_truncated)

    with pytest.raises(FeatureUnavailableError, match="incomplete or malformed"):
        await provider.parse(system="s", user="u", schema=_Schema, max_tokens=10)


async def test_successful_parse_is_unaffected():
    class _FakeResponse:
        stop_reason = "end_turn"
        parsed_output = _Schema(field="ok")

    def raise_nothing(**kwargs):
        return _FakeResponse()

    provider = _provider_with_stubbed_client(raise_nothing)

    result = await provider.parse(system="s", user="u", schema=_Schema, max_tokens=10)
    assert result.field == "ok"
