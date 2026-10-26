"""Unit tests for normalization + chunking (pure functions, no I/O)."""

from __future__ import annotations

from app.ingestion.normalize import chunk_text, normalize_text


def test_normalize_collapses_whitespace():
    assert normalize_text("  hello\n\tworld  ") == "hello world"
    assert normalize_text("") == ""


def test_chunk_short_text_single_chunk():
    chunks = chunk_text("a short review")
    assert chunks == ["a short review"]


def test_chunk_long_text_splits_with_overlap():
    text = " ".join(f"word{i}" for i in range(400))  # well over 1000 chars
    chunks = chunk_text(text, max_chars=200, overlap=50)
    assert len(chunks) > 1
    # No chunk exceeds the window (allowing the trailing trim).
    assert all(len(c) <= 200 for c in chunks)
    # Overlap means consecutive chunks share some content.
    assert chunks[0].split()[-1] in chunks[1] or chunks[1].startswith(chunks[0].split()[-1])


def test_chunk_empty_text_returns_empty():
    assert chunk_text("   ") == []
