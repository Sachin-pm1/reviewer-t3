"""LLM provider abstraction.

Every AI call in the platform flows through ``ClaudeService`` -> an ``LLMProvider``.
There are no scattered, hardcoded Anthropic calls: swap the provider and the rest of
the platform is unchanged.
"""

from app.analysis.provider.claude_service import ClaudeService, get_claude_service

__all__ = ["ClaudeService", "get_claude_service"]
