"""Test doubles so AI/catalog-dependent services can be unit tested offline —
same idea as the main platform's tests/_fakes.py: a deterministic stand-in
with the same call shape as the real thing, no network involved.
"""

from __future__ import annotations

from typing import TypeVar

from pydantic import BaseModel

from app.companion.schemas import RawCompanionReply, RawJourney, RawTrackPick

T = TypeVar("T", bound=BaseModel)


class FakeClaudeService:
    """Implements the same call shape as app.claude.ClaudeService.generate()."""

    def __init__(self, reply: RawCompanionReply | None = None) -> None:
        self._reply = reply

    @property
    def model(self) -> str:
        return "fake-model"

    async def generate(self, *, system: str, user: str, schema: type[T], max_tokens: int = 2048) -> T:
        if schema is RawCompanionReply:
            if self._reply is not None:
                return schema.model_validate(self._reply.model_dump())
            lowered = user.lower()
            if "how do you work" in lowered or "hello" in lowered:
                return schema.model_validate(
                    RawCompanionReply(
                        reply="I'm Aura — tell me a mood and I'll stretch your playlist.",
                        journey=None,
                    ).model_dump()
                )
            return schema.model_validate(
                RawCompanionReply(
                    reply="Let's push past your usual rotation.",
                    journey=RawJourney(
                        mood="Adventurous",
                        reasoning="Leans into the taste profile's energy with unfamiliar artists.",
                        energy=65,
                        picks=[
                            RawTrackPick(
                                artist="Fake Artist A",
                                track="Fake Track A",
                                why="Shares the seed artists' production but from an unexplored scene.",
                                novelty_score=70,
                            ),
                            RawTrackPick(
                                artist="Fake Artist B",
                                track="Fake Track B",
                                why="Same tempo as the seed genres, different cultural lineage.",
                                novelty_score=55,
                            ),
                        ],
                    ),
                ).model_dump()
            )
        raise AssertionError(f"FakeClaudeService has no stub for schema {schema!r}")
