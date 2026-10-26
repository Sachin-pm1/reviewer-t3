"""CompanionService accepts claude_service/enrich for exactly this reason —
test the real reasoning-to-enrichment pipeline with fakes standing in for
Claude and the Spotify/iTunes network calls, no real credentials needed.
"""

from __future__ import annotations

from app.companion.schemas import CompanionRequest, TasteProfile, TrackPick
from app.companion.service import CompanionService
from tests._fakes import FakeClaudeService


async def _fake_enrich(picks):
    return [
        TrackPick(
            artist=p.artist,
            track=p.track,
            why=p.why,
            novelty_score=p.novelty_score,
            artwork_url="https://example.test/art.jpg",
            preview_url="https://example.test/preview.m4a",
            external_url="https://example.test/track",
            source="spotify",
        )
        for p in picks
    ]


def _service(**kwargs) -> CompanionService:
    return CompanionService(claude_service=FakeClaudeService(**kwargs), enrich=_fake_enrich)


async def test_music_request_returns_an_enriched_journey():
    svc = _service()
    reply = await svc.respond(
        CompanionRequest(
            message="I need something for a solo night drive.",
            taste=TasteProfile(seed_artists=["Tame Impala"], seed_genres=["indie rock"], novelty=70),
        )
    )
    assert reply.journey is not None
    assert len(reply.journey.picks) == 2
    first = reply.journey.picks[0]
    assert first.artwork_url == "https://example.test/art.jpg"
    assert first.source == "spotify"
    assert first.why  # every pick carries explicit reasoning, not just a title


async def test_small_talk_has_no_journey():
    svc = _service()
    reply = await svc.respond(CompanionRequest(message="Hello, how do you work?"))
    assert reply.journey is None
    assert reply.reply


async def test_history_is_forwarded_into_the_prompt():
    # _build_prompt is a @staticmethod — call it on the class directly so this
    # doesn't need a real Claude client (CompanionService() with no args would
    # hit the real constructor, which requires ANTHROPIC_API_KEY).
    from app.companion.schemas import CompanionTurn

    prompt = CompanionService._build_prompt(
        CompanionRequest(
            message="Something calmer this time.",
            history=[CompanionTurn(role="user", text="I need motivation")],
        )
    )
    assert "Listener: I need motivation" in prompt
    assert "Listener: Something calmer this time." in prompt
