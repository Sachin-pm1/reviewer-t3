from __future__ import annotations

from pydantic import BaseModel


class SpotifyAuthorizeResponse(BaseModel):
    authorize_url: str


class SpotifyStatus(BaseModel):
    connected: bool
    display_name: str | None = None
    spotify_user_id: str | None = None
    connected_at: str | None = None


class SpotifyArtist(BaseModel):
    name: str
    genres: list[str] = []
    image_url: str | None = None
    external_url: str | None = None
    popularity: int | None = None


class SpotifyTrack(BaseModel):
    name: str
    artist: str
    album_image: str | None = None
    external_url: str | None = None
    preview_url: str | None = None
    popularity: int | None = None
    played_at: str | None = None  # only set for recently-played items


class SpotifyOverview(BaseModel):
    connected: bool
    display_name: str | None = None
    product: str | None = None
    top_artists: list[SpotifyArtist] = []
    top_tracks: list[SpotifyTrack] = []
    recently_played: list[SpotifyTrack] = []
    top_genres: list[str] = []
