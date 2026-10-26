"""Regression test for the local-Qdrant concurrency crash.

Reproduced against a real running instance: two analyze jobs writing to the shared
local Qdrant store at the same time crashed with
``sqlite3.InterfaceError: bad parameter or other API misuse`` inside qdrant_client's
own embedded persistence layer. QdrantVectorStore now serializes every operation
through an asyncio.Lock — this proves that lock actually holds under real concurrency,
without touching a real Qdrant client (local mode holds an exclusive file lock, so a
second real client on the same path can't even open — this tests the locking logic
directly instead).
"""

from __future__ import annotations

import asyncio
import time

from app.knowledge_base.vector_store import QdrantVectorStore, VectorRecord


async def test_concurrent_upserts_are_serialized_not_interleaved():
    store = QdrantVectorStore.__new__(QdrantVectorStore)  # skip real client construction
    store._lock = asyncio.Lock()
    calls = {"concurrent": 0, "max_concurrent": 0}

    def fake_upsert_sync(records):
        calls["concurrent"] += 1
        calls["max_concurrent"] = max(calls["max_concurrent"], calls["concurrent"])
        time.sleep(0.05)  # long enough that real overlap would reliably show up
        calls["concurrent"] -= 1

    store._upsert_sync = fake_upsert_sync
    record = VectorRecord(vector=[0.1, 0.2], payload={})

    await asyncio.gather(*(store.upsert([record]) for _ in range(5)))

    assert calls["max_concurrent"] == 1


async def test_concurrent_ensure_collection_only_builds_once():
    store = QdrantVectorStore.__new__(QdrantVectorStore)
    store._lock = asyncio.Lock()
    store._ready = False
    build_count = {"n": 0}

    def fake_ensure_sync(dimension):
        build_count["n"] += 1
        time.sleep(0.02)

    store._ensure_collection_sync = fake_ensure_sync

    await asyncio.gather(*(store.ensure_collection(384) for _ in range(5)))

    assert build_count["n"] == 1  # not once per concurrent caller
    assert store._ready is True
