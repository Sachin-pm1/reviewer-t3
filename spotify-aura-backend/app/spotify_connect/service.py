"""Orchestrates the Authorization Code round trip and the real-data overview.

The `_pending` state store exists purely to survive the redirect round trip:
this app's own session is a Bearer JWT, which a top-level browser navigation
to accounts.spotify.com and back cannot carry. So /auth/spotify/login mints a
one-time opaque `state`, remembers which of *our* accounts asked for it, and
the callback route resolves `state` back to that account — the same
in-memory, short-TTL pattern already used for the experience-track cache in
catalog_routes.py, just for a different purpose (CSRF protection + account
linking instead of avoiding a repeat Claude call).
"""

from __future__ import annotations

import time
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.errors import FeatureUnavailableError
from app.spotify_connect import client as spotify
from app.spotify_connect.crypto import decrypt, encrypt
from app.spotify_connect.models import SpotifyConnection
from app.spotify_connect.schemas import SpotifyArtist, SpotifyOverview, SpotifyStatus, SpotifyTrack

_PENDING_TTL_SECONDS = 600
_pending: dict[str, tuple[str, float]] = {}


def create_pending_state(user_id: str) -> str:
    _prune_expired()
    state = uuid.uuid4().hex
    _pending[state] = (user_id, time.monotonic())
    return state


def consume_pending_state(state: str) -> str | None:
    """One-time use: the state is removed whether or not it's still valid."""
    entry = _pending.pop(state, None)
    if entry is None:
        return None
    user_id, created = entry
    if time.monotonic() - created > _PENDING_TTL_SECONDS:
        return None
    return user_id


def _prune_expired() -> None:
    cutoff = time.monotonic() - _PENDING_TTL_SECONDS
    for state in [s for s, (_, created) in _pending.items() if created < cutoff]:
        _pending.pop(state, None)


def _ensure_utc(dt: datetime) -> datetime:
    """SQLite drops tzinfo on round-trip — assume naive means UTC (it always is here)."""
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _largest_image(images: list[dict]) -> str | None:
    if not images:
        return None
    return max(images, key=lambda img: img.get("width") or 0).get("url")


def _to_track(t: dict, *, played_at: str | None = None) -> SpotifyTrack:
    return SpotifyTrack(
        name=t.get("name", ""),
        artist=", ".join(a["name"] for a in t.get("artists", [])),
        album_image=_largest_image(t.get("album", {}).get("images", [])),
        external_url=t.get("external_urls", {}).get("spotify"),
        preview_url=t.get("preview_url"),
        popularity=t.get("popularity"),
        played_at=played_at,
    )


class SpotifyConnectService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _get_connection(self, user_id: str) -> SpotifyConnection | None:
        result = await self.session.execute(
            select(SpotifyConnection).where(SpotifyConnection.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def handle_callback(self, user_id: str, code: str) -> None:
        token_body = await spotify.exchange_code(code)
        profile = await spotify.fetch_me(token_body["access_token"])
        expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=token_body.get("expires_in", 3600)
        )

        connection = await self._get_connection(user_id)
        if connection is None:
            connection = SpotifyConnection(user_id=user_id)
            self.session.add(connection)

        connection.spotify_user_id = profile.get("id", "")
        connection.display_name = profile.get("display_name")
        connection.access_token_encrypted = encrypt(token_body["access_token"])
        connection.refresh_token_encrypted = encrypt(token_body["refresh_token"])
        connection.scope = token_body.get("scope", "")
        connection.expires_at = expires_at
        await self.session.flush()

    async def status(self, user_id: str) -> SpotifyStatus:
        connection = await self._get_connection(user_id)
        if connection is None:
            return SpotifyStatus(connected=False)
        return SpotifyStatus(
            connected=True,
            display_name=connection.display_name,
            spotify_user_id=connection.spotify_user_id,
            connected_at=connection.created_at.isoformat(),
        )

    async def disconnect(self, user_id: str) -> None:
        connection = await self._get_connection(user_id)
        if connection is not None:
            await self.session.delete(connection)
            await self.session.flush()

    async def _valid_access_token(self, connection: SpotifyConnection) -> str:
        now = datetime.now(timezone.utc)
        access_token = decrypt(connection.access_token_encrypted)
        if access_token and now < _ensure_utc(connection.expires_at) - timedelta(seconds=60):
            return access_token

        refresh_token = decrypt(connection.refresh_token_encrypted)
        if refresh_token is None:
            raise FeatureUnavailableError(
                "Your Spotify connection needs to be re-authorized.",
                code="spotify_reconnect_required",
            )
        body = await spotify.refresh_access_token(refresh_token)
        connection.access_token_encrypted = encrypt(body["access_token"])
        if body.get("refresh_token"):
            connection.refresh_token_encrypted = encrypt(body["refresh_token"])
        connection.expires_at = now + timedelta(seconds=body.get("expires_in", 3600))
        await self.session.flush()
        return body["access_token"]

    async def overview(self, user_id: str) -> SpotifyOverview:
        connection = await self._get_connection(user_id)
        if connection is None:
            return SpotifyOverview(connected=False)

        access_token = await self._valid_access_token(connection)

        me = await spotify.fetch_me(access_token)
        top_artists_raw = await spotify.fetch_top(
            access_token, "artists", time_range="medium_term", limit=10
        )
        top_tracks_raw = await spotify.fetch_top(
            access_token, "tracks", time_range="medium_term", limit=10
        )
        recent_raw = await spotify.fetch_recently_played(access_token, limit=20)

        top_artists = [
            SpotifyArtist(
                name=a["name"],
                genres=a.get("genres", []),
                image_url=_largest_image(a.get("images", [])),
                external_url=a.get("external_urls", {}).get("spotify"),
                popularity=a.get("popularity"),
            )
            for a in top_artists_raw
        ]
        top_tracks = [_to_track(t) for t in top_tracks_raw]
        recently_played = [
            _to_track(item["track"], played_at=item.get("played_at")) for item in recent_raw
        ]

        genre_counts: dict[str, int] = {}
        for artist in top_artists:
            for genre in artist.genres:
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
        top_genres = sorted(genre_counts, key=lambda g: genre_counts[g], reverse=True)[:6]

        return SpotifyOverview(
            connected=True,
            display_name=me.get("display_name"),
            product=me.get("product"),
            top_artists=top_artists,
            top_tracks=top_tracks,
            recently_played=recently_played,
            top_genres=top_genres,
        )
