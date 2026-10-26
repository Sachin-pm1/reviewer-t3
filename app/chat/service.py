"""RAG copilot service: retrieve relevant feedback, then answer with Claude."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.analysis.provider.claude_service import ClaudeService, get_claude_service
from app.chat.models import ChatSession
from app.chat.repository import ChatRepository
from app.chat.schemas import ChatResponse, ChatSource
from app.knowledge_base.service import KnowledgeBaseService
from app.products.service import ProjectService


class ChatService:
    def __init__(
        self,
        session: AsyncSession,
        kb_service: KnowledgeBaseService | None = None,
        claude_service: ClaudeService | None = None,
    ) -> None:
        self.session = session
        self.repo = ChatRepository(session)
        self.kb = kb_service or KnowledgeBaseService()
        self.claude = claude_service or get_claude_service()

    async def ask(self, project_id: str, question: str, *, top_k: int = 6) -> ChatResponse:
        project = await ProjectService(self.session).require_project(project_id)

        chunks = await self.kb.retrieve(project_id, question, top_k=top_k)
        answer = await self.claude.answer(
            question=question, product_name=project.product_name, context=chunks
        )

        sources = [
            ChatSource(
                index=i,
                text=c.text,
                score=c.score,
                review_id=c.review_id,
                source_type=c.source_type,
                rating=c.rating,
            )
            for i, c in enumerate(chunks, start=1)
        ]

        record = await self.repo.add(
            ChatSession(
                project_id=project_id,
                question=question,
                answer=answer,
                sources=[s.model_dump() for s in sources],
            )
        )

        return ChatResponse(session_id=record.id, answer=answer, sources=sources)

    async def history(self, project_id: str) -> list[ChatSession]:
        """Past exchanges for a project, oldest first — restores the conversation on reload."""
        await ProjectService(self.session).require_project(project_id)
        return await self.repo.list_for_project(project_id)
