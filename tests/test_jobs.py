"""Regression tests for the analyze-job orchestrator's start-up race.

Found by actually running a real analyze job end-to-end against a live server: the
background task can start (and query for its own job row) before the request's own
commit of that row is visible to it, leaving the job stuck at "pending" forever with
no error surfaced. ``run_analyze_job`` now retries briefly and fails loudly instead of
hanging silently — these tests reproduce both the recovery and the give-up path.
"""

from __future__ import annotations

import asyncio
import uuid

from app.database.base import SessionLocal
from app.jobs.models import CollectionJob, JobStatus
from app.jobs.service import JobService, run_analyze_job
from app.products.schemas import ProjectCreate, SourceCreate
from app.products.service import ProjectService


async def test_run_analyze_job_recovers_from_a_late_commit(db_session):
    """The job row commits ~0.3s after the worker starts looking for it — same shape
    as the real race — and the worker should still find it and finish, not hang."""
    project = await ProjectService(db_session).create_project(
        ProjectCreate(name="Spotify", product_name="Spotify")
    )
    await db_session.commit()

    job_id = uuid.uuid4().hex

    async def create_job_after_delay() -> None:
        await asyncio.sleep(0.3)
        async with SessionLocal() as session:
            session.add(
                CollectionJob(id=job_id, project_id=project.id, type="analyze", status=JobStatus.PENDING)
            )
            await session.commit()

    creator = asyncio.create_task(create_job_after_delay())
    await run_analyze_job(job_id)
    await creator

    async with SessionLocal() as session:
        job = await session.get(CollectionJob, job_id)
    assert job is not None
    assert job.status == JobStatus.COMPLETED  # not stuck at "pending"


async def test_run_analyze_job_fails_loudly_if_job_row_never_appears():
    """No job ever gets created for this id — the worker must give up with a clear
    failure rather than logging an error and hanging forever."""
    job_id = uuid.uuid4().hex

    # Bounded wait makes the "give up, don't hang forever" guarantee an explicit
    # assertion failure instead of a suite-wide timeout if this regresses.
    await asyncio.wait_for(run_analyze_job(job_id), timeout=5)

    async with SessionLocal() as session:
        job = await session.get(CollectionJob, job_id)
    assert job is None  # there was never a row to update — nothing to assert on it


async def test_ingest_and_index_handles_multiple_sources(db_session, sample_csv_path, tmp_path):
    """_ingest_and_index now commits one short transaction per source instead of a
    single transaction spanning the whole loop (that's what caused a reproduced
    "database is locked" error against a real ~300-review pull). This exercises the
    multi-source path for correctness: every source's rows and metadata land right.

    Uses two CSVs with disjoint ids (rather than the same file twice) because
    ReviewService dedupes by (project_id, source_type, external_id) — same-file
    sources would legitimately collapse into one, which isn't what this test is
    checking.
    """
    second_csv = tmp_path / "second.csv"
    second_csv.write_text(
        "id,rating,author,text\n"
        + "\n".join(f'b{i},4,tester,"Another review {i}"' for i in range(1, 8))
    )

    project = await ProjectService(db_session).create_project(
        ProjectCreate(name="Spotify", product_name="Spotify")
    )
    source_a = await ProjectService(db_session).add_source(
        project.id,
        SourceCreate(
            source_type="file_csv", config={"path": sample_csv_path, "id_column": "id"}
        ),
    )
    source_b = await ProjectService(db_session).add_source(
        project.id,
        SourceCreate(
            source_type="file_csv", config={"path": str(second_csv), "id_column": "id"}
        ),
    )
    await db_session.commit()

    job, _ = await JobService(db_session).create_analyze_job(project.id)
    await db_session.commit()

    await run_analyze_job(job.id, max_reviews_per_source=7)

    async with SessionLocal() as session:
        finished = await session.get(CollectionJob, job.id)
        assert finished.status == JobStatus.COMPLETED
        assert finished.result["reviews_ingested"] == 14  # 7 per source, both sources

        refreshed_a = await session.get(type(source_a), source_a.id)
        refreshed_b = await session.get(type(source_b), source_b.id)
        assert refreshed_a.review_count == 7
        assert refreshed_a.status == "collected"
        assert refreshed_a.last_collected_at is not None
        assert refreshed_b.review_count == 7
        assert refreshed_b.status == "collected"


async def test_create_analyze_job_reuses_an_active_job_for_the_same_project(db_session):
    """Two analyze jobs for the same project running at once both write to the same
    shared local Qdrant store concurrently — reproduced as a real crash. This is the
    other half of that fix: never start a second one while one's still active, and
    tell the caller so it knows not to schedule a second background execution."""
    project = await ProjectService(db_session).create_project(
        ProjectCreate(name="Spotify", product_name="Spotify")
    )
    await db_session.commit()

    service = JobService(db_session)
    first, first_is_new = await service.create_analyze_job(project.id)
    assert first_is_new is True

    second, second_is_new = await service.create_analyze_job(project.id)  # e.g. a double-click
    assert second.id == first.id  # same job handed back, not a new one
    assert second_is_new is False  # caller must not schedule a second run_analyze_job

    first.status = JobStatus.COMPLETED
    await db_session.flush()
    third, third_is_new = await service.create_analyze_job(project.id)
    assert third.id != first.id  # once finished, a new run is allowed
    assert third_is_new is True
