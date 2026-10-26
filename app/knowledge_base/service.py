"""Knowledge-base service: index reviews and retrieve relevant chunks (RAG).

Indexing chunks each review, embeds the chunks, and upserts them into the vector store
with payload metadata (project, review id, source, rating). Retrieval embeds a query
and returns the most similar chunks scoped to a project — the context the copilot and
analysis layers ground their answers on.
"""

from __future__ import annotations

from dataclasses import dataclass

from loguru import logger

from app.ingestion.normalize import chunk_text
from app.knowledge_base.embeddings import EmbeddingProvider, get_embedding_provider
from app.knowledge_base.vector_store import (
    SearchHit,
    VectorRecord,
    VectorStore,
    get_vector_store,
)
from app.reviews.models import Review


@dataclass
class RetrievedChunk:
    """A retrieved KB chunk with provenance, used for citations."""

    text: str
    score: float
    review_id: str
    source_type: str
    rating: float | None


class KnowledgeBaseService:
    """Chunk/embed/store reviews and retrieve relevant context for a project."""

    def __init__(
        self,
        embedding_provider: EmbeddingProvider | None = None,
        vector_store: VectorStore | None = None,
    ) -> None:
        self.embeddings = embedding_provider or get_embedding_provider()
        self.store = vector_store or get_vector_store()

    async def index_reviews(self, reviews: list[Review]) -> int:
        """Chunk, embed, and upsert reviews. Returns the number of chunks indexed."""
        if not reviews:
            return 0

        texts: list[str] = []
        payloads: list[dict] = []
        for review in reviews:
            for chunk_index, chunk in enumerate(chunk_text(review.text)):
                texts.append(chunk)
                payloads.append(
                    {
                        "project_id": review.project_id,
                        "review_id": review.id,
                        "source_type": review.source_type,
                        "rating": review.rating,
                        "chunk_index": chunk_index,
                        "text": chunk,
                    }
                )
        if not texts:
            return 0

        await self.store.ensure_collection(self.embeddings.dimension)
        vectors = await self.embeddings.embed(texts)
        records = [
            VectorRecord(vector=vec, payload=payload)
            for vec, payload in zip(vectors, payloads, strict=True)
        ]
        await self.store.upsert(records)
        logger.info("Indexed {} chunks from {} reviews", len(records), len(reviews))
        return len(records)

    async def retrieve(
        self, project_id: str, query: str, *, top_k: int = 6
    ) -> list[RetrievedChunk]:
        """Return the most relevant chunks for ``query`` within a project."""
        await self.store.ensure_collection(self.embeddings.dimension)
        query_vector = await self.embeddings.embed_one(query)
        hits: list[SearchHit] = await self.store.search(
            query_vector, top_k=top_k, filters={"project_id": project_id}
        )
        return [
            RetrievedChunk(
                text=hit.payload.get("text", ""),
                score=hit.score,
                review_id=hit.payload.get("review_id", ""),
                source_type=hit.payload.get("source_type", ""),
                rating=hit.payload.get("rating"),
            )
            for hit in hits
        ]
