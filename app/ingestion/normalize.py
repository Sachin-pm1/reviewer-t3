"""Normalization + chunking for the ingestion pipeline.

Normalization cleans/standardizes raw text; chunking splits long documents into
embedding-sized windows for the knowledge base. Kept dependency-free and deterministic
so it is trivial to unit-test.
"""

from __future__ import annotations

import re

from app.ingestion.base import RawDocument

_WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """Collapse whitespace and trim. Cheap, lossless cleanup."""
    return _WHITESPACE_RE.sub(" ", text or "").strip()


def is_meaningful(doc: RawDocument, *, min_chars: int = 3) -> bool:
    """Drop empty/near-empty documents that carry no analyzable signal."""
    return len(normalize_text(doc.text)) >= min_chars


def normalize_document(doc: RawDocument) -> RawDocument:
    """Return a copy of ``doc`` with normalized text/title."""
    return doc.model_copy(
        update={
            "text": normalize_text(doc.text),
            "title": normalize_text(doc.title) if doc.title else None,
        }
    )


def chunk_text(text: str, *, max_chars: int = 1000, overlap: int = 150) -> list[str]:
    """Split ``text`` into overlapping word-boundary chunks.

    Most reviews fit in a single chunk; long-form documents (interview transcripts,
    PDFs in later increments) split into several. Overlap preserves context across
    boundaries for retrieval.
    """
    text = normalize_text(text)
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]

    chunks: list[str] = []
    start = 0
    length = len(text)
    while start < length:
        end = min(start + max_chars, length)
        # Prefer to break on a space near the window end (avoid mid-word cuts).
        if end < length:
            space = text.rfind(" ", start, end)
            if space > start:
                end = space
        chunks.append(text[start:end].strip())
        if end >= length:
            break
        start = max(end - overlap, start + 1)
    return [c for c in chunks if c]
