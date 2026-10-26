"""Manual per-day memory notes — independent of the Spotify connection."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.database import get_session
from app.memories.schemas import MemoryIn, MemoryOut
from app.memories.service import MemoryService

router = APIRouter(prefix="/me/memories", tags=["memories"])


@router.get("", response_model=list[MemoryOut])
async def list_memories(
    user: CurrentUser, session: AsyncSession = Depends(get_session)
) -> list[MemoryOut]:
    memories = await MemoryService(session).list_for_user(user.id)
    return [MemoryOut.model_validate(m) for m in memories]


@router.post("", response_model=MemoryOut, status_code=201)
async def upsert_memory(
    payload: MemoryIn, user: CurrentUser, session: AsyncSession = Depends(get_session)
) -> MemoryOut:
    memory = await MemoryService(session).upsert(user.id, payload)
    return MemoryOut.model_validate(memory)


@router.delete("/{memory_id}", status_code=204)
async def delete_memory(
    memory_id: str, user: CurrentUser, session: AsyncSession = Depends(get_session)
) -> None:
    await MemoryService(session).delete(user.id, memory_id)
