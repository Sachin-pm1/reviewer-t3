from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.memories.models import Memory
from app.memories.schemas import MemoryIn


class MemoryService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_for_user(self, user_id: str) -> list[Memory]:
        result = await self.session.execute(
            select(Memory).where(Memory.user_id == user_id).order_by(Memory.date)
        )
        return list(result.scalars().all())

    async def upsert(self, user_id: str, payload: MemoryIn) -> Memory:
        """One memory per user per date — re-saving the same date edits it."""
        result = await self.session.execute(
            select(Memory).where(Memory.user_id == user_id, Memory.date == payload.date)
        )
        memory = result.scalar_one_or_none()
        if memory is None:
            memory = Memory(user_id=user_id, date=payload.date)
            self.session.add(memory)
        memory.note = payload.note
        memory.mood = payload.mood
        await self.session.flush()
        return memory

    async def delete(self, user_id: str, memory_id: str) -> None:
        memory = await self.session.get(Memory, memory_id)
        if memory is not None and memory.user_id == user_id:
            await self.session.delete(memory)
            await self.session.flush()
