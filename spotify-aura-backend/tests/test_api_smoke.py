"""API smoke tests via ASGI transport — offline (no ANTHROPIC_API_KEY/Spotify
credentials in the test env, see conftest.py), so these only cover the paths
that don't need a real network call: health, and the clean-503 contract for
AI endpoints when their prerequisites are missing.
"""

from __future__ import annotations


async def test_health_reports_ai_and_spotify_disabled(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["ai_enabled"] is False
    assert body["spotify_enabled"] is False


async def test_companion_chat_without_key_is_503_not_a_crash(client):
    resp = await client.post("/companion/chat", json={"message": "surprise me"})
    assert resp.status_code == 503
    assert resp.json()["error"]["code"] == "feature_unavailable"


async def test_experience_track_without_key_is_503_not_a_crash(client):
    resp = await client.post(
        "/catalog/experience-track",
        json={"title": "Rainy Sunday", "mood": "Cozy", "desc": "Blankets and chai."},
    )
    assert resp.status_code == 503
