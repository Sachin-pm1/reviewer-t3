"""Real Spotify user login (Authorization Code flow) — connect, status,
disconnect, and the bundled real-data overview that powers Dashboard, Music
DNA, Life Chapters, Insights, Memories, and Wrapped once a user connects."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.config import get_settings
from app.database import get_session
from app.errors import FeatureUnavailableError
from app.spotify_connect import client as spotify
from app.spotify_connect.schemas import SpotifyAuthorizeResponse, SpotifyOverview, SpotifyStatus
from app.spotify_connect.service import (
    SpotifyConnectService,
    consume_pending_state,
    create_pending_state,
)

router = APIRouter(prefix="/auth/spotify", tags=["spotify-connect"])
me_router = APIRouter(prefix="/me/spotify", tags=["spotify-connect"])


@router.get("/login", response_model=SpotifyAuthorizeResponse)
async def login(user: CurrentUser) -> SpotifyAuthorizeResponse:
    settings = get_settings()
    if not settings.has_spotify_credentials:
        raise FeatureUnavailableError("Spotify isn't configured on this deployment yet.")
    state = create_pending_state(user.id)
    return SpotifyAuthorizeResponse(authorize_url=spotify.build_authorize_url(state))


@router.get("/callback")
async def callback(
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    session: AsyncSession = Depends(get_session),
) -> RedirectResponse:
    settings = get_settings()
    frontend = settings.frontend_base_url

    if error or not code or not state:
        logger.warning("Spotify callback missing code/state or carried an error: error={}", error)
        return RedirectResponse(f"{frontend}/settings?spotify=error")

    user_id = consume_pending_state(state)
    if user_id is None:
        logger.warning("Spotify callback state not found/expired — server restarted mid-flow, or a stale/replayed link.")
        return RedirectResponse(f"{frontend}/settings?spotify=error")

    try:
        await SpotifyConnectService(session).handle_callback(user_id, code)
    except Exception:
        await session.rollback()
        logger.exception("Spotify OAuth callback failed while exchanging the code / saving the connection")
        return RedirectResponse(f"{frontend}/settings?spotify=error")

    return RedirectResponse(f"{frontend}/settings?spotify=connected")


@me_router.get("/status", response_model=SpotifyStatus)
async def status(user: CurrentUser, session: AsyncSession = Depends(get_session)) -> SpotifyStatus:
    return await SpotifyConnectService(session).status(user.id)


@me_router.get("/overview", response_model=SpotifyOverview)
async def overview(
    user: CurrentUser, session: AsyncSession = Depends(get_session)
) -> SpotifyOverview:
    return await SpotifyConnectService(session).overview(user.id)


@me_router.post("/disconnect", status_code=204)
async def disconnect(user: CurrentUser, session: AsyncSession = Depends(get_session)) -> None:
    await SpotifyConnectService(session).disconnect(user.id)
