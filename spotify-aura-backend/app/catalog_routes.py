"""Real-track grounding for Discovery's mood cards.

Spotify's own search endpoint is literal keyword matching against track/
artist/album text — searching the raw phrase "rainy day acoustic chill"
mostly returns tracks whose *metadata* happens to contain those words, not
tracks that actually suit a rainy day. So instead of querying Spotify
directly with the mood text, this reuses the exact same reliable pattern as
the Companion: ask Claude for one real, specific, well-known track that
actually fits the mood, then resolve that named track against Spotify (+
iTunes fallback) via the same enrichment used everywhere else in this app.
"""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.claude import get_claude_service
from app.companion.catalog import enrich_picks
from app.companion.schemas import RawTrackPick, TrackPick

router = APIRouter(prefix="/catalog", tags=["catalog"])

_SYSTEM = (
    "You pick exactly one real, specific, existing song — never invented — that "
    "genuinely fits a described mood/moment. Prefer a well-known track that clearly "
    "matches, since this is shown as a representative preview for that moment, not a "
    "personalized discovery pick."
)


class ExperienceTrackRequest(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    mood: str = Field(min_length=1, max_length=50)
    desc: str = Field(min_length=1, max_length=300)


async def _pick_for_experience(payload: ExperienceTrackRequest) -> RawTrackPick:
    claude = get_claude_service()
    user = (
        f"Moment: {payload.title}\n"
        f"Mood: {payload.mood}\n"
        f"Description: {payload.desc}\n\n"
        "Name one real song that fits perfectly."
    )
    return await claude.generate(system=_SYSTEM, user=user, schema=RawTrackPick, max_tokens=512)


# Small in-memory cache: the experience list is a fixed set of cards, so the
# representative track for "Rainy Sunday" doesn't need to be re-picked (and
# re-billed to Claude) on every single page load.
_cache: dict[str, TrackPick] = {}


@router.post("/experience-track", response_model=TrackPick)
async def experience_track(payload: ExperienceTrackRequest) -> TrackPick:
    """A single real, mood-appropriate track for a Discovery experience card."""
    cache_key = payload.title
    if cache_key in _cache:
        return _cache[cache_key]

    raw = await _pick_for_experience(payload)
    enriched = await enrich_picks([raw])
    _cache[cache_key] = enriched[0]
    return enriched[0]
