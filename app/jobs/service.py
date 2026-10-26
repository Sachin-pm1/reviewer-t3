"""Job service + the Analyze lifecycle orchestrator.

``run_analyze_job`` is the end-to-end pipeline: ingest every source -> persist reviews
-> build the knowledge base -> run Claude analysis. It runs in the background with its
own DB sessions and writes progress to the ``CollectionJob`` row so callers can poll
``GET /jobs/{id}``.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.analysis.service import AnalysisService
from app.core.config import get_settings
from app.core.logging import bind_correlation_id
from app.database.session import session_scope
from app.ingestion.pipeline import ingest
from app.jobs.models import CollectionJob, JobStatus
from app.knowledge_base.service import KnowledgeBaseService
from app.products.models import Source
from app.products.service import ProjectService
from app.reviews.service import ReviewService


class JobService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_analyze_job(self, project_id: str) -> tuple[CollectionJob, bool]:
        """Start an analyze job, or hand back the one already running for this
        project. Two concurrent jobs for the same project both write to the same
        shared local Qdrant store at once, which isn't safe (see
        knowledge_base/vector_store.py) — this is the other half of that fix: never
        let a second one start rather than only surviving it after the fact.

        Returns ``(job, is_new)`` — callers must only schedule the background
        ``run_analyze_job`` task when ``is_new`` is true, or a reused job would get
        a second, concurrent execution scheduled against the same row.
        """
        await ProjectService(self.session).require_project(project_id)

        active = await self._active_job(project_id)
        if active is not None:
            return active, False

        job = CollectionJob(project_id=project_id, type="analyze", status=JobStatus.PENDING)
        self.session.add(job)
        await self.session.flush()
        return job, True

    async def _active_job(self, project_id: str) -> CollectionJob | None:
        stmt = (
            select(CollectionJob)
            .where(
                CollectionJob.project_id == project_id,
                CollectionJob.type == "analyze",
                CollectionJob.status.in_([JobStatus.PENDING, JobStatus.RUNNING]),
            )
            .order_by(CollectionJob.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get(self, job_id: str) -> CollectionJob | None:
        return await self.session.get(CollectionJob, job_id)


async def _update_job(job_id: str, **fields) -> None:
    """Persist a partial update to the job row in its own committed transaction."""
    async with session_scope() as session:
        job = await session.get(CollectionJob, job_id)
        if job is None:
            return
        for key, value in fields.items():
            setattr(job, key, value)


async def run_analyze_job(job_id: str, max_reviews_per_source: int | None = None) -> None:
    """Background entrypoint: ingest -> persist -> index -> analyze."""
    bind_correlation_id(f"job:{job_id[:8]}")
    logger.info("Analyze job starting")

    # Resolve the project id up front. BackgroundTasks can start before the request's
    # own commit of the just-created job row is visible to this task's own session
    # (observed in practice on SQLite) — retry briefly rather than assume it's there.
    project_id: str | None = None
    for attempt in range(5):
        async with session_scope() as session:
            job = await session.get(CollectionJob, job_id)
            if job is not None:
                project_id = job.project_id
                break
        await asyncio.sleep(0.2 * (attempt + 1))

    if project_id is None:
        logger.error("Job {} never became visible to the worker — marking failed.", job_id)
        await _update_job(
            job_id,
            status=JobStatus.FAILED,
            stage="failed",
            error="Job row was not visible to the background worker after retrying.",
        )
        return

    try:
        ingested, indexed_chunks = await _ingest_and_index(
            job_id, project_id, max_reviews_per_source
        )
        analyzed, note = await _analyze(job_id, project_id)

        result = {
            "reviews_ingested": ingested,
            "chunks_indexed": indexed_chunks,
            "reviews_analyzed": analyzed,
        }
        if note:
            result["note"] = note
        await _update_job(
            job_id,
            status=JobStatus.COMPLETED,
            stage="done",
            result=result,
        )
        logger.info("Analyze job complete: {}", result)
    except Exception as exc:  # noqa: BLE001 - record any failure on the job
        logger.exception("Analyze job failed: {}", exc)
        await _update_job(job_id, status=JobStatus.FAILED, stage="failed", error=str(exc))


async def _ingest_and_index(
    job_id: str, project_id: str, max_reviews_per_source: int | None
) -> tuple[int, int]:
    await _update_job(job_id, status=JobStatus.RUNNING, stage="ingesting")
    kb = KnowledgeBaseService()
    total_new = 0
    indexed_chunks = 0

    async with session_scope() as session:
        project = await ProjectService(session).require_project(project_id, with_relations=True)
        sources = [(s.id, s.source_type, s.config) for s in project.sources]

    # Each source gets its own short, immediately-committed transaction rather than
    # one held open across the whole loop. SQLite allows only one writer at a time;
    # holding a write transaction open while _update_job's progress pings (and the
    # embedding step) run on separate connections reproduces a real
    # "database is locked" error under an actual multi-hundred-review pull.
    for source_id, source_type, config in sources:
        docs = [
            doc async for doc in ingest(source_type, config, limit=max_reviews_per_source)
        ]

        async with session_scope() as session:
            new_reviews = await ReviewService(session).store_documents(
                project_id, source_id, source_type, docs
            )
            source = await session.get(Source, source_id)
            source.review_count += len(new_reviews)
            source.last_collected_at = datetime.now(timezone.utc)
            source.status = "collected"

        await _update_job(job_id, stage="indexing")
        indexed_chunks += await kb.index_reviews(new_reviews)
        total_new += len(new_reviews)

    return total_new, indexed_chunks


async def _analyze(job_id: str, project_id: str) -> tuple[int, str | None]:
    if not get_settings().has_anthropic_key:
        logger.warning("ANTHROPIC_API_KEY not set — skipping AI analysis stage.")
        await _update_job(job_id, stage="analysis_skipped")
        return 0, "AI analysis skipped: ANTHROPIC_API_KEY is not set."

    await _update_job(job_id, stage="analyzing")
    # NOTE: this session stays open across the whole concurrent-analysis gather below,
    # and `progress` (called from inside it) writes via a *separate* connection — the
    # same shape that caused a reproduced "database is locked" error in
    # _ingest_and_index. It's lower-risk here because no writes happen on this session
    # until the final `add_many` after the gather completes (only SELECTs beforehand,
    # which don't take an exclusive SQLite lock), but it hasn't been exercised against
    # a real ANTHROPIC_API_KEY end-to-end. If this ever throws "database is locked" in
    # practice, apply the same fix: fetch reviews as plain data, run analysis outside
    # any open write session, persist in one short transaction at the end.
    async with session_scope() as session:
        project = await ProjectService(session).require_project(project_id)
        reviews = await ReviewService(session).list_for_project(
            project_id, only_unanalyzed=True
        )
        await _update_job(job_id, total=len(reviews), processed=0)

        async def progress(done: int, total: int) -> None:
            if done == total or done % 5 == 0:
                await _update_job(job_id, processed=done, total=total)

        analyzed = await AnalysisService(session).analyze_reviews(
            project_id, project.product_name, reviews, progress=progress
        )
    return analyzed, None
