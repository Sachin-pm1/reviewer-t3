"""Spotify Authorization Code flow: real user login, real personal data.

Distinct from app/spotify_client.py (Client Credentials — app-only, catalog
search only, used everywhere else in this app). This module exchanges a
user's consent for an access+refresh token pair scoped to *their own*
account, and calls the handful of `/v1/me/*` endpoints that require a real
user session: profile, top artists/tracks, and recently played. Unless the
Spotify app has been granted extended quota, only Spotify accounts explicitly
added under the app's Dashboard → User Management can complete this flow.
"""

from __future__ import annotations

import urllib.parse

import httpx
from loguru import logger

from app.config import get_settings

_AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
_TOKEN_URL = "https://accounts.spotify.com/api/token"
_API_BASE = "https://api.spotify.com/v1"
_TIMEOUT = httpx.Timeout(8.0)

# The minimal real scopes needed to power Dashboard/DNA/Chapters/Insights/
# Memories/Wrapped with genuine personal data. Deliberately excludes
# playback-control and library-modification scopes this app never needs.
SCOPES = "user-read-email user-read-private user-top-read user-read-recently-played"


class SpotifyAuthError(Exception):
    """Raised when the Authorization Code exchange, refresh, or a `/me` call fails."""


def build_authorize_url(state: str) -> str:
    settings = get_settings()
    params = {
        "client_id": settings.spotify_client_id,
        "response_type": "code",
        "redirect_uri": settings.spotify_redirect_uri,
        "scope": SCOPES,
        "state": state,
    }
    return f"{_AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"


async def exchange_code(code: str) -> dict:
    """Trade a one-time authorization code for an access+refresh token pair."""
    settings = get_settings()
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.post(
            _TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.spotify_redirect_uri,
            },
            auth=(settings.spotify_client_id, settings.spotify_client_secret),
        )
    if resp.status_code != 200:
        logger.warning("Spotify code exchange failed: {} {}", resp.status_code, resp.text)
        raise SpotifyAuthError("Spotify rejected the authorization code.")
    return resp.json()


async def refresh_access_token(refresh_token: str) -> dict:
    settings = get_settings()
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.post(
            _TOKEN_URL,
            data={"grant_type": "refresh_token", "refresh_token": refresh_token},
            auth=(settings.spotify_client_id, settings.spotify_client_secret),
        )
    if resp.status_code != 200:
        logger.warning("Spotify token refresh failed: {} {}", resp.status_code, resp.text)
        raise SpotifyAuthError("Could not refresh the Spotify session — reconnect required.")
    return resp.json()


async def _get(access_token: str, path: str, *, params: dict | None = None) -> dict:
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.get(
            f"{_API_BASE}{path}",
            params=params,
            headers={"Authorization": f"Bearer {access_token}"},
        )
    if resp.status_code == 401:
        raise SpotifyAuthError("Spotify session expired.")
    if resp.status_code >= 400:
        logger.warning("Spotify GET {} failed: {} {}", path, resp.status_code, resp.text)
    resp.raise_for_status()
    return resp.json()


async def fetch_me(access_token: str) -> dict:
    return await _get(access_token, "/me")


async def fetch_top(access_token: str, kind: str, *, time_range: str, limit: int) -> list[dict]:
    body = await _get(
        access_token, f"/me/top/{kind}", params={"time_range": time_range, "limit": limit}
    )
    return body.get("items", [])


async def fetch_recently_played(access_token: str, *, limit: int) -> list[dict]:
    body = await _get(access_token, "/me/player/recently-played", params={"limit": limit})
    return body.get("items", [])
