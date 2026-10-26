"""Real-catalog enrichment: Spotify first, iTunes fills the one gap Spotify leaves.

Claude's reasoning is the product; this module just attaches real artwork,
preview audio, and a canonical link so the MVP shows real songs instead of
placeholder cards. Spotify (via Client Credentials — app-only, no user login)
is the primary source since this is a Spotify product. The one real wrinkle:
Spotify stopped returning ``preview_url`` for apps created after their
November 2024 policy change unless the app has extended-quota approval, so a
freshly-registered app frequently gets a correct track match with a null
preview. When that happens, iTunes (no auth needed) is queried purely to
backfill the 30-second clip — the artwork and canonical link stay Spotify's.
Any lookup failure degrades to an unenriched pick rather than failing the
request.
"""

from __future__ import annotations

import asyncio

import httpx
from loguru import logger

from app.companion.schemas import RawTrackPick, TrackPick
from app.spotify_client import SpotifyClient, get_spotify_client

_ITUNES_SEARCH_URL = "https://itunes.apple.com/search"
_TIMEOUT = httpx.Timeout(5.0)


async def _itunes_lookup(client: httpx.AsyncClient, artist: str, track: str) -> dict | None:
    try:
        resp = await client.get(
            _ITUNES_SEARCH_URL,
            params={"term": f"{artist} {track}", "media": "music", "entity": "song", "limit": 1},
        )
        resp.raise_for_status()
        results = resp.json().get("results") or []
        return results[0] if results else None
    except (httpx.HTTPError, ValueError) as exc:
        logger.debug("iTunes lookup failed for {} - {}: {}", artist, track, exc)
        return None


def _largest_image(images: list[dict]) -> str | None:
    if not images:
        return None
    return max(images, key=lambda img: img.get("width") or 0).get("url")


async def _enrich_one(
    client: httpx.AsyncClient, spotify: SpotifyClient, raw: RawTrackPick
) -> TrackPick:
    spotify_hit = await spotify.search_track(client, raw.artist, raw.track)

    if spotify_hit:
        preview_url = spotify_hit.get("preview_url")
        artwork_url = _largest_image(spotify_hit.get("album", {}).get("images", []))
        external_url = spotify_hit.get("external_urls", {}).get("spotify")

        if not preview_url:
            # Spotify matched the track but (per the Nov 2024 policy change) didn't
            # return a preview clip for this app tier — borrow just that from iTunes.
            itunes_hit = await _itunes_lookup(client, raw.artist, raw.track)
            if itunes_hit:
                preview_url = itunes_hit.get("previewUrl")

        return TrackPick(
            artist=raw.artist,
            track=raw.track,
            why=raw.why,
            novelty_score=raw.novelty_score,
            artwork_url=artwork_url,
            preview_url=preview_url,
            external_url=external_url,
            source="spotify",
        )

    # Spotify had no match at all (rare for a real, released track) — fall back
    # to iTunes entirely rather than leaving the pick completely unenriched.
    itunes_hit = await _itunes_lookup(client, raw.artist, raw.track)
    if not itunes_hit:
        return TrackPick(
            artist=raw.artist, track=raw.track, why=raw.why, novelty_score=raw.novelty_score
        )

    artwork = itunes_hit.get("artworkUrl100")
    if artwork:
        artwork = artwork.replace("100x100bb", "512x512bb")
    return TrackPick(
        artist=raw.artist,
        track=raw.track,
        why=raw.why,
        novelty_score=raw.novelty_score,
        artwork_url=artwork,
        preview_url=itunes_hit.get("previewUrl"),
        external_url=itunes_hit.get("trackViewUrl"),
        source="itunes",
    )


async def enrich_picks(picks: list[RawTrackPick]) -> list[TrackPick]:
    """Resolve each raw pick against Spotify (+ iTunes as needed), concurrently."""
    spotify = get_spotify_client()
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        return await asyncio.gather(*(_enrich_one(client, spotify, p) for p in picks))
