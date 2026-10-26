"""Schemas for the RAG copilot."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.shared.schemas import TimestampedSchema


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, description="Question about the product's feedback.")
    top_k: int = Field(default=6, ge=1, le=20, description="How many excerpts to retrieve.")


class ChatSource(BaseModel):
    index: int
    text: str
    score: float
    review_id: str
    source_type: str
    rating: float | None = None


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: list[ChatSource] = Field(default_factory=list)


class ChatHistoryItem(TimestampedSchema):
    """A past copilot exchange, for restoring the conversation on reload."""

    question: str
    answer: str
    sources: list[ChatSource] = Field(default_factory=list)
