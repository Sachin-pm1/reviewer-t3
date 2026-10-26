"""Discovery Companion: a conversational agent that deliberately recommends music
beyond the listener's stated taste, with explainable reasoning attached to every pick.

This is the Part 4 MVP. Traditional collaborative-filtering recommenders can only
rank catalog items by similarity/engagement; they cannot hold a natural-language
negotiation about *why* a listener wants something different right now, nor
explain in plain language why an unfamiliar pick still fits. That negotiation +
explanation loop is the thing this service exists to demonstrate.
"""

from __future__ import annotations

from typing import Awaitable, Callable

from app.claude import ClaudeService, get_claude_service
from app.companion.catalog import enrich_picks
from app.companion.schemas import (
    CompanionReply,
    CompanionRequest,
    Journey,
    RawCompanionReply,
    RawTrackPick,
    TrackPick,
)

Enricher = Callable[[list[RawTrackPick]], Awaitable[list[TrackPick]]]

_SYSTEM = (
    "You are Aura, an AI music discovery companion inside a streaming app. Your one job "
    "is to fight algorithmic staleness: most recommendation systems maximize short-term "
    "engagement by resurfacing songs and artists the listener already loves, which quietly "
    "traps people in a loop of repeat listening. You do the opposite — you hold a real "
    "conversation, understand what the listener wants right now, and deliberately "
    "recommend real, specific tracks that stretch beyond their stated taste in a way that "
    "still makes sense for the moment.\n\n"
    "You are given the listener's self-reported taste profile (seed artists/genres) and a "
    "0-100 novelty dial: 0 means stay close to what they already like, 100 means push as "
    "far outside their comfort zone as still makes sense. Calibrate every pick to that dial.\n\n"
    "For every track you recommend:\n"
    "- It must be a real, specific, existing song by a real artist. Never invent a title.\n"
    "- Explain why in one concrete sentence naming the specific sonic, lyrical, or cultural "
    "thread connecting it to what they already like — never a generic 'you'll love this'.\n"
    "- Prefer lesser-known tracks and artists over the most obvious choice — the goal is "
    "discovery, not another hit they've certainly already heard.\n"
    "- Give an honest novelty_score (0-100) for how far this specific pick sits from their "
    "stated taste.\n\n"
    "If the message is small talk or a question about how you work rather than a request "
    "for music, reply conversationally and leave journey null."
)


class CompanionService:
    def __init__(
        self,
        claude_service: ClaudeService | None = None,
        enrich: Enricher | None = None,
    ) -> None:
        self.claude = claude_service or get_claude_service()
        self._enrich = enrich or enrich_picks

    async def respond(self, request: CompanionRequest) -> CompanionReply:
        raw = await self.claude.generate(
            system=_SYSTEM,
            user=self._build_prompt(request),
            schema=RawCompanionReply,
            max_tokens=2048,
        )

        journey = None
        if raw.journey:
            picks = await self._enrich(raw.journey.picks)
            journey = Journey(
                mood=raw.journey.mood,
                reasoning=raw.journey.reasoning,
                energy=raw.journey.energy,
                picks=picks,
            )

        return CompanionReply(reply=raw.reply, journey=journey)

    @staticmethod
    def _build_prompt(request: CompanionRequest) -> str:
        taste = request.taste
        profile_lines = [
            "Taste profile:",
            f"- Seed artists they already love: {', '.join(taste.seed_artists) or '(none given)'}",
            f"- Seed genres they already love: {', '.join(taste.seed_genres) or '(none given)'}",
            f"- Novelty dial: {taste.novelty}/100",
            "",
        ]
        parts = list(profile_lines)
        if request.history:
            parts.append("Recent conversation:")
            parts += [
                f"{'Listener' if turn.role == 'user' else 'Aura'}: {turn.text}"
                for turn in request.history[-6:]
            ]
            parts.append("")
        parts.append(f"Listener: {request.message}")
        return "\n".join(parts)


def get_companion_service() -> CompanionService:
    return CompanionService()
