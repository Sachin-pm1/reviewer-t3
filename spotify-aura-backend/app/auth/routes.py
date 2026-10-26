"""Account creation, sign-in, current-user info, and per-user taste profile."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.auth.schemas import (
    SigninRequest,
    SignupRequest,
    TasteProfileIn,
    TasteProfileOut,
    TokenResponse,
    UserRead,
)
from app.auth.service import AuthService
from app.database import get_session
from app.errors import NotFoundError

router = APIRouter(prefix="/auth", tags=["auth"])
me_router = APIRouter(prefix="/me", tags=["auth"])


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    payload: SignupRequest, session: AsyncSession = Depends(get_session)
) -> TokenResponse:
    user, token = await AuthService(session).signup(payload)
    return TokenResponse(access_token=token, user=UserRead.model_validate(user))


@router.post("/signin", response_model=TokenResponse)
async def signin(
    payload: SigninRequest, session: AsyncSession = Depends(get_session)
) -> TokenResponse:
    user, token = await AuthService(session).signin(payload)
    return TokenResponse(access_token=token, user=UserRead.model_validate(user))


@router.get("/me", response_model=UserRead)
async def me(user: CurrentUser) -> UserRead:
    return UserRead.model_validate(user)


@me_router.get("/taste", response_model=TasteProfileOut)
async def get_taste(user: CurrentUser, session: AsyncSession = Depends(get_session)) -> TasteProfileOut:
    profile = await AuthService(session).get_taste(user.id)
    if profile is None:
        # Distinct from "explicitly saved all-empty" — the frontend uses this to
        # decide whether to show the taste-setup screen. Returning 200 with
        # defaults here previously made a brand-new signed-in user silently skip
        # setup (found while auditing the auth flow just added).
        raise NotFoundError("No taste profile saved yet.")
    return TasteProfileOut.model_validate(profile, from_attributes=True)


@me_router.put("/taste", response_model=TasteProfileOut)
async def set_taste(
    payload: TasteProfileIn, user: CurrentUser, session: AsyncSession = Depends(get_session)
) -> TasteProfileOut:
    profile = await AuthService(session).set_taste(user.id, payload)
    return TasteProfileOut.model_validate(profile, from_attributes=True)
