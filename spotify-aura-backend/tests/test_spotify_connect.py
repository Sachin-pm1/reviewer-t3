"""Real Spotify user login (Authorization Code flow).

HTTP-layer tests cover the parts reachable without a real Spotify redirect:
auth gating, the not-connected shapes, and the callback's error paths. The
service-layer tests below them are the important part — they exercise the
actual token-exchange → encrypt-and-store → refresh-before-expiry pipeline
with Spotify's network calls monkeypatched, the same "test the real function,
fake the network seam" pattern as test_catalog_enrichment.py.
"""

from __future__ import annotations

import itertools
from datetime import datetime, timedelta, timezone

from app.auth.models import User
from app.spotify_connect import service as connect_service
from app.spotify_connect.service import (
    SpotifyConnectService,
    consume_pending_state,
    create_pending_state,
)

_email_counter = itertools.count()


def _unique_email() -> str:
    return f"oauth-listener{next(_email_counter)}@example.com"


async def _signed_up_token(client) -> str:
    resp = await client.post(
        "/auth/signup", json={"email": _unique_email(), "password": "correcthorse123"}
    )
    return resp.json()["access_token"]


# ---------------------------------------------------------------------------
# HTTP layer
# ---------------------------------------------------------------------------


async def test_status_not_connected_by_default(client):
    token = await _signed_up_token(client)
    resp = await client.get("/me/spotify/status", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json() == {
        "connected": False,
        "display_name": None,
        "spotify_user_id": None,
        "connected_at": None,
    }


async def test_status_requires_auth(client):
    resp = await client.get("/me/spotify/status")
    assert resp.status_code == 401


async def test_login_returns_503_when_spotify_not_configured(client):
    # conftest.py sets SPOTIFY_CLIENT_ID/SECRET to "" for test isolation.
    token = await _signed_up_token(client)
    resp = await client.get("/auth/spotify/login", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 503
    assert resp.json()["error"]["code"] == "feature_unavailable"


async def test_login_requires_auth(client):
    resp = await client.get("/auth/spotify/login")
    assert resp.status_code == 401


async def test_overview_not_connected_returns_empty_shape(client):
    token = await _signed_up_token(client)
    resp = await client.get("/me/spotify/overview", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["connected"] is False
    assert body["top_artists"] == []
    assert body["top_tracks"] == []
    assert body["recently_played"] == []


async def test_disconnect_when_not_connected_is_a_noop(client):
    token = await _signed_up_token(client)
    resp = await client.post(
        "/me/spotify/disconnect", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 204


async def test_callback_missing_code_redirects_to_error(client):
    resp = await client.get(
        "/auth/spotify/callback", params={"state": "whatever"}, follow_redirects=False
    )
    assert resp.status_code == 307
    assert resp.headers["location"].endswith("/settings?spotify=error")


async def test_callback_unknown_state_redirects_to_error(client):
    resp = await client.get(
        "/auth/spotify/callback",
        params={"code": "somecode", "state": "never-issued"},
        follow_redirects=False,
    )
    assert resp.status_code == 307
    assert resp.headers["location"].endswith("/settings?spotify=error")


# ---------------------------------------------------------------------------
# Pending state store (CSRF protection + account linking across the redirect)
# ---------------------------------------------------------------------------


def test_pending_state_is_one_time_use():
    state = create_pending_state("user-123")
    assert consume_pending_state(state) == "user-123"
    assert consume_pending_state(state) is None  # already consumed


def test_pending_state_unknown_returns_none():
    assert consume_pending_state("not-a-real-state") is None


# ---------------------------------------------------------------------------
# Service layer — real logic, monkeypatched Spotify network calls
# ---------------------------------------------------------------------------


def _token_body(*, access="access-1", refresh="refresh-1", expires_in=3600, scope="user-top-read"):
    return {
        "access_token": access,
        "refresh_token": refresh,
        "expires_in": expires_in,
        "scope": scope,
    }


def _profile(*, spotify_id="spotify-user-1", display_name="Test Listener", product="premium"):
    return {"id": spotify_id, "display_name": display_name, "product": product}


async def _fake_exchange_code(code):
    return _token_body()


async def _fake_fetch_me(token):
    return _profile()


def _patch_connect(monkeypatch):
    """Every test below connects first — patch the exchange_code/fetch_me seam
    each of them shares, and let individual tests patch the rest as needed."""
    monkeypatch.setattr(connect_service.spotify, "exchange_code", _fake_exchange_code)
    monkeypatch.setattr(connect_service.spotify, "fetch_me", _fake_fetch_me)


async def _make_user(db_session) -> User:
    user = User(email=_unique_email(), password_hash="unused-in-these-tests")
    db_session.add(user)
    await db_session.flush()
    return user


async def test_handle_callback_stores_encrypted_tokens_and_profile(db_session, monkeypatch):
    _patch_connect(monkeypatch)

    user = await _make_user(db_session)
    svc = SpotifyConnectService(db_session)
    await svc.handle_callback(user.id, "auth-code-xyz")

    connection = await svc._get_connection(user.id)
    assert connection is not None
    assert connection.spotify_user_id == "spotify-user-1"
    assert connection.display_name == "Test Listener"
    # Tokens are never stored in plaintext.
    assert connection.access_token_encrypted != "access-1"
    assert connection.refresh_token_encrypted != "refresh-1"

    status = await svc.status(user.id)
    assert status.connected is True
    assert status.display_name == "Test Listener"


async def test_valid_access_token_reuses_unexpired_token_without_refreshing(db_session, monkeypatch):
    _patch_connect(monkeypatch)

    async def _fail_if_called(refresh_token):
        raise AssertionError("refresh_access_token should not be called for an unexpired token")

    monkeypatch.setattr(connect_service.spotify, "refresh_access_token", _fail_if_called)

    user = await _make_user(db_session)
    svc = SpotifyConnectService(db_session)
    await svc.handle_callback(user.id, "auth-code-xyz")

    connection = await svc._get_connection(user.id)
    access_token = await svc._valid_access_token(connection)
    assert access_token == "access-1"


async def test_valid_access_token_refreshes_when_expired(db_session, monkeypatch):
    _patch_connect(monkeypatch)

    user = await _make_user(db_session)
    svc = SpotifyConnectService(db_session)
    await svc.handle_callback(user.id, "auth-code-xyz")

    connection = await svc._get_connection(user.id)
    # Force expiry into the past so the refresh branch is exercised.
    connection.expires_at = datetime.now(timezone.utc) - timedelta(minutes=5)
    await db_session.flush()

    async def fake_refresh(refresh_token):
        assert refresh_token == "refresh-1"  # decrypted correctly
        return {"access_token": "access-2", "expires_in": 3600}

    monkeypatch.setattr(connect_service.spotify, "refresh_access_token", fake_refresh)

    access_token = await svc._valid_access_token(connection)
    assert access_token == "access-2"
    # Refresh token carries over unchanged since Spotify didn't send a new one.
    from app.spotify_connect.crypto import decrypt

    assert decrypt(connection.refresh_token_encrypted) == "refresh-1"


async def test_overview_assembles_real_data_and_top_genres(db_session, monkeypatch):
    _patch_connect(monkeypatch)

    user = await _make_user(db_session)
    svc = SpotifyConnectService(db_session)
    await svc.handle_callback(user.id, "auth-code-xyz")

    async def fake_fetch_top(token, kind, *, time_range, limit):
        if kind == "artists":
            return [
                {"name": "Artist A", "genres": ["indie rock", "dream pop"], "images": [], "popularity": 70},
                {"name": "Artist B", "genres": ["dream pop"], "images": [], "popularity": 60},
            ]
        return [
            {
                "name": "Track 1",
                "artists": [{"name": "Artist A"}],
                "album": {"images": []},
                "external_urls": {"spotify": "https://open.spotify.com/track/1"},
                "preview_url": None,
                "popularity": 55,
            }
        ]

    async def fake_recently_played(token, *, limit):
        return [
            {
                "played_at": "2026-07-01T10:00:00Z",
                "track": {
                    "name": "Track 1",
                    "artists": [{"name": "Artist A"}],
                    "album": {"images": []},
                    "external_urls": {},
                    "preview_url": None,
                    "popularity": 55,
                },
            }
        ]

    monkeypatch.setattr(connect_service.spotify, "fetch_top", fake_fetch_top)
    monkeypatch.setattr(connect_service.spotify, "fetch_recently_played", fake_recently_played)

    overview = await svc.overview(user.id)

    assert overview.connected is True
    assert overview.display_name == "Test Listener"
    assert overview.product == "premium"
    assert [a.name for a in overview.top_artists] == ["Artist A", "Artist B"]
    assert overview.top_tracks[0].name == "Track 1"
    assert overview.top_tracks[0].artist == "Artist A"
    assert overview.recently_played[0].played_at == "2026-07-01T10:00:00Z"
    # "dream pop" appears on both artists, so it should rank first.
    assert overview.top_genres[0] == "dream pop"


async def test_disconnect_removes_the_connection_row(db_session, monkeypatch):
    _patch_connect(monkeypatch)

    user = await _make_user(db_session)
    svc = SpotifyConnectService(db_session)
    await svc.handle_callback(user.id, "auth-code-xyz")
    assert await svc._get_connection(user.id) is not None

    await svc.disconnect(user.id)
    assert await svc._get_connection(user.id) is None


async def test_decrypt_returns_none_for_garbage_ciphertext():
    from app.spotify_connect.crypto import decrypt

    assert decrypt("not-a-real-fernet-token") is None
