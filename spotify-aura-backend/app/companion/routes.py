"""HTTP route for the AI Discovery Companion (Part 4 MVP)."""

from __future__ import annotations

from fastapi import APIRouter

from app.companion.schemas import CompanionReply, CompanionRequest
from app.companion.service import get_companion_service

router = APIRouter(prefix="/companion", tags=["companion"])


@router.post("/chat", response_model=CompanionReply)
async def companion_chat(payload: CompanionRequest) -> CompanionReply:
    """Have one turn of conversation with the discovery companion."""
    return await get_companion_service().respond(payload)
