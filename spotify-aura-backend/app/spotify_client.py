"""Real Spotify catalog access via the Client Credentials flow.

App-only auth — no user login, no redirect, just this app's own Client
ID/Secret proving who it is. That's sufficient for catalog search (track
metadata, artwork, canonical link); it does not grant access to any
listener's personal data, which this MVP never touches.

One real limitation this module works around: Spotify stopped returning
``preview_url`` for apps created after their November 2024 policy change
unless the app has extended quota approval. A freshly-registered app like
this one gets real artwork and a real track match, but frequently gets
``preview_url: null``. ``app/companion/catalog.py`` compensates by asking
iTunes for a preview clip specifically when Spotify doesn't have one — the
recommendation and the track match are still 100% Spotify's real catalog,
only the audio snippet itself sometimes has to come from elsewhere.
"""

from __future__ import annotations

import asyncio
import time

import httpx
from loguru import logger

from app.config import get_settings

_TOKEN_URL = "https://accounts.spotify.com/api/token"
_SEARCH_URL = "https://api.spotify.com/v1/search"
_TIMEOUT = httpx.Timeout(5.0)


class SpotifyClient:
    def __init__(self) -> None:
        settings = get_settings()
        self._client_id = settings.spotify_client_id
        self._client_secret = settings.spotify_client_secret
        self._token: str | None = None
        self._token_expires_at: float = 0.0
        self._lock = asyncio.Lock()

    async def _get_token(self, client: httpx.AsyncClient) -> str:
        async with self._lock:
            if self._token and time.monotonic() < self._token_expires_at - 30:
                return self._token
            resp = await client.post(
                _TOKEN_URL,
                data={"grant_type": "client_credentials"},
                auth=(self._client_id, self._client_secret),
            )
            resp.raise_for_status()
            body = resp.json()
            self._token = body["access_token"]
            self._token_expires_at = time.monotonic() + body.get("expires_in", 3600)
            return self._token

    async def _search(
        self, client: httpx.AsyncClient, query: str, limit: int
    ) -> list[dict]:
        token = await self._get_token(client)
        resp = await client.get(
            _SEARCH_URL,
            params={"q": query, "type": "track", "limit": limit},
            headers={"Authorization": f"Bearer {token}"},
        )
        if resp.status_code == 401:
            # Token expired/invalid mid-lifetime — clear and retry once.
            self._token = None
            token = await self._get_token(client)
            resp = await client.get(
                _SEARCH_URL,
                params={"q": query, "type": "track", "limit": limit},
                headers={"Authorization": f"Bearer {token}"},
            )
        resp.raise_for_status()
        return resp.json().get("tracks", {}).get("items", [])

    async def search_track(
        self, client: httpx.AsyncClient, artist: str, track: str
    ) -> dict | None:
        """Best-effort exact-ish search for one known artist+track. None on failure."""
        try:
            items = await self._search(client, f"track:{track} artist:{artist}", limit=1)
            return items[0] if items else None
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            logger.debug("Spotify lookup failed for {} - {}: {}", artist, track, exc)
            return None


_instance = SpotifyClient()


def get_spotify_client() -> SpotifyClient:
    return _instance
