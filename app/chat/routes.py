"""HTTP route for the RAG copilot."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.chat.schemas import ChatHistoryItem, ChatRequest, ChatResponse
from app.chat.service import ChatService
from app.database.session import get_session

router = APIRouter(prefix="/projects", tags=["chat"])


@router.post("/{project_id}/chat", response_model=ChatResponse)
async def chat(
    project_id: str,
    payload: ChatRequest,
    session: AsyncSession = Depends(get_session),
) -> ChatResponse:
    """Ask the AI copilot a question grounded in the project's feedback (with citations)."""
    return await ChatService(session).ask(
        project_id, payload.question, top_k=payload.top_k
    )


@router.get("/{project_id}/chat", response_model=list[ChatHistoryItem])
async def chat_history(
    project_id: str,
    session: AsyncSession = Depends(get_session),
) -> list[ChatHistoryItem]:
    """Past copilot exchanges for a project, oldest first."""
    records = await ChatService(session).history(project_id)
    return [ChatHistoryItem.model_validate(r) for r in records]
