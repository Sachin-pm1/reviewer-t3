"""app.companion.catalog.enrich_picks() is the most important untested logic in
this project — the Spotify-primary/iTunes-fallback branching is exactly the
kind of thing that's easy to get backwards under real network conditions and
never notice until a demo. Tests the real function with its two network seams
(SpotifyClient.search_track, the iTunes lookup) monkeypatched, not a
stand-in copy of the logic.
"""

from __future__ import annotations

from app.companion import catalog
from app.companion.schemas import RawTrackPick

_RAW = RawTrackPick(artist="Real Artist", track="Real Track", why="fits the mood", novelty_score=50)


class _FakeSpotifyClient:
    def __init__(self, hit: dict | None):
        self._hit = hit

    async def search_track(self, client, artist, track):
        return self._hit


def _spotify_hit(*, preview_url: str | None) -> dict:
    return {
        "preview_url": preview_url,
        "album": {"images": [{"url": "https://spotify.test/small.jpg", "width": 64},
                              {"url": "https://spotify.test/large.jpg", "width": 640}]},
        "external_urls": {"spotify": "https://open.spotify.com/track/abc"},
    }


def _itunes_hit() -> dict:
    return {
        "previewUrl": "https://itunes.test/preview.m4a",
        "artworkUrl100": "https://itunes.test/art/100x100bb.jpg",
        "trackViewUrl": "https://music.apple.com/track/abc",
    }


async def test_spotify_hit_with_preview_uses_spotify_for_everything(monkeypatch):
    monkeypatch.setattr(
        catalog, "get_spotify_client",
        lambda: _FakeSpotifyClient(_spotify_hit(preview_url="https://spotify.test/preview.mp3")),
    )
    monkeypatch.setattr(catalog, "_itunes_lookup", None)  # must never be called

    picks = await catalog.enrich_picks([_RAW])
    pick = picks[0]

    assert pick.source == "spotify"
    assert pick.preview_url == "https://spotify.test/preview.mp3"
    assert pick.artwork_url == "https://spotify.test/large.jpg"  # picks the widest image
    assert pick.external_url == "https://open.spotify.com/track/abc"


async def test_spotify_hit_without_preview_borrows_just_the_preview_from_itunes(monkeypatch):
    monkeypatch.setattr(
        catalog, "get_spotify_client",
        lambda: _FakeSpotifyClient(_spotify_hit(preview_url=None)),
    )

    async def fake_itunes_lookup(client, artist, track):
        return _itunes_hit()

    monkeypatch.setattr(catalog, "_itunes_lookup", fake_itunes_lookup)

    picks = await catalog.enrich_picks([_RAW])
    pick = picks[0]

    assert pick.source == "spotify"
    assert pick.preview_url == "https://itunes.test/preview.m4a"  # borrowed
    assert pick.artwork_url == "https://spotify.test/large.jpg"  # stays Spotify's
    assert pick.external_url == "https://open.spotify.com/track/abc"  # stays Spotify's


async def test_no_spotify_match_falls_back_to_itunes_entirely(monkeypatch):
    monkeypatch.setattr(catalog, "get_spotify_client", lambda: _FakeSpotifyClient(None))

    async def fake_itunes_lookup(client, artist, track):
        return _itunes_hit()

    monkeypatch.setattr(catalog, "_itunes_lookup", fake_itunes_lookup)

    picks = await catalog.enrich_picks([_RAW])
    pick = picks[0]

    assert pick.source == "itunes"
    assert pick.preview_url == "https://itunes.test/preview.m4a"
    assert pick.artwork_url == "https://itunes.test/art/512x512bb.jpg"  # upgraded from 100x100
    assert pick.external_url == "https://music.apple.com/track/abc"


async def test_both_sources_miss_returns_an_unenriched_pick_not_an_error(monkeypatch):
    monkeypatch.setattr(catalog, "get_spotify_client", lambda: _FakeSpotifyClient(None))

    async def fake_itunes_lookup(client, artist, track):
        return None

    monkeypatch.setattr(catalog, "_itunes_lookup", fake_itunes_lookup)

    picks = await catalog.enrich_picks([_RAW])
    pick = picks[0]

    assert pick.artist == "Real Artist"
    assert pick.track == "Real Track"
    assert pick.source is None
    assert pick.artwork_url is None
    assert pick.preview_url is None


async def test_enriches_multiple_picks_concurrently(monkeypatch):
    monkeypatch.setattr(
        catalog, "get_spotify_client",
        lambda: _FakeSpotifyClient(_spotify_hit(preview_url="https://spotify.test/preview.mp3")),
    )
    monkeypatch.setattr(catalog, "_itunes_lookup", None)

    raw_picks = [
        RawTrackPick(artist="A", track="1", why="x", novelty_score=10),
        RawTrackPick(artist="B", track="2", why="y", novelty_score=20),
        RawTrackPick(artist="C", track="3", why="z", novelty_score=30),
    ]
    picks = await catalog.enrich_picks(raw_picks)
    assert [p.artist for p in picks] == ["A", "B", "C"]  # order preserved
    assert all(p.source == "spotify" for p in picks)
