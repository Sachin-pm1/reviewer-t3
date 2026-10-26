"""The ingestion pipeline: collect -> normalize -> filter.

Given a source type + config, this drives the matching connector and yields clean,
meaningful :class:`RawDocument` objects ready to be persisted as reviews and indexed
into the knowledge base. Chunking happens later (in the KB service) so reviews are
stored whole.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from loguru import logger

from app.ingestion.base import RawDocument
from app.ingestion.normalize import is_meaningful, normalize_document
from app.ingestion.registry import build_connector


async def ingest(
    source_type: str, config: dict | None = None, *, limit: int | None = None
) -> AsyncIterator[RawDocument]:
    """Yield normalized, meaningful documents from a single source.

    Args:
        source_type: Registered connector key (e.g. ``"file_csv"``).
        config: Connector-specific configuration.
        limit: Optional cap on the number of documents yielded.
    """
    connector = build_connector(source_type, config)
    seen_external_ids: set[str] = set()
    emitted = 0

    logger.info("Ingesting from source_type={}", source_type)
    async for raw in connector.collect():
        doc = normalize_document(raw)
        if not is_meaningful(doc):
            continue
        # De-duplicate within a single run when the source provides stable ids.
        if doc.external_id is not None:
            if doc.external_id in seen_external_ids:
                continue
            seen_external_ids.add(doc.external_id)

        yield doc
        emitted += 1
        if limit is not None and emitted >= limit:
            break

    logger.info("Ingestion complete: source_type={} emitted={}", source_type, emitted)
