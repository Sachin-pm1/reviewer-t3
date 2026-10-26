"""Data-access for copilot chat sessions."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.chat.models import ChatSession


class ChatRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, record: ChatSession) -> ChatSession:
        self.session.add(record)
        await self.session.flush()
        return record

    async def list_for_project(self, project_id: str) -> list[ChatSession]:
        result = await self.session.execute(
            select(ChatSession)
            .where(ChatSession.project_id == project_id)
            .order_by(ChatSession.created_at.asc())
        )
        return list(result.scalars().all())
