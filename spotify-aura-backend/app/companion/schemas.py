"""Schemas for the AI Discovery Companion.

Stateless per-request: the caller holds conversation history and taste profile
client-side and resends them each turn — no persistence, no auth. This is a
focused MVP surface, not the full product.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class TasteProfile(BaseModel):
    """A lightweight, self-reported stand-in for real listening history."""

    seed_artists: list[str] = Field(default_factory=list, max_length=10)
    seed_genres: list[str] = Field(default_factory=list, max_length=10)
    novelty: int = Field(
        default=50,
        ge=0,
        le=100,
        description="0 = stay close to known taste, 100 = maximum stretch beyond it.",
    )


class CompanionTurn(BaseModel):
    role: Literal["user", "aura"]
    text: str = Field(min_length=1, max_length=2000)


class CompanionRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    history: list[CompanionTurn] = Field(default_factory=list, max_length=20)
    taste: TasteProfile = Field(default_factory=TasteProfile)


class RawTrackPick(BaseModel):
    """Claude's raw structured pick — no URLs; ``catalog.py`` resolves those afterward."""

    artist: str
    track: str
    why: str
    novelty_score: int = Field(ge=0, le=100)


class RawJourney(BaseModel):
    mood: str
    reasoning: str
    energy: int = Field(ge=0, le=100)
    picks: list[RawTrackPick] = Field(min_length=2, max_length=5)


class RawCompanionReply(BaseModel):
    """The schema Claude fills via ``messages.parse``."""

    reply: str
    journey: RawJourney | None = None


class TrackPick(BaseModel):
    artist: str
    track: str
    why: str
    novelty_score: int
    artwork_url: str | None = None
    preview_url: str | None = None
    external_url: str | None = None
    source: Literal["spotify", "itunes", None] = None


class Journey(BaseModel):
    mood: str
    reasoning: str
    energy: int
    picks: list[TrackPick]


class CompanionReply(BaseModel):
    """API response: reply text plus an optional enriched recommendation journey."""

    reply: str
    journey: Journey | None = None
