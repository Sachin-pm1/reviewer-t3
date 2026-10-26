"""HTTP routes: trigger an analyze job and poll its status."""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.database.session import get_session
from app.jobs.schemas import AnalyzeOptions, JobRead
from app.jobs.service import JobService, run_analyze_job

# Trigger lives under /projects/{id}/analyze; status under /jobs/{id}.
analyze_router = APIRouter(prefix="/projects", tags=["jobs"])
jobs_router = APIRouter(prefix="/jobs", tags=["jobs"])


@analyze_router.post(
    "/{project_id}/analyze", response_model=JobRead, status_code=status.HTTP_202_ACCEPTED
)
async def start_analyze(
    project_id: str,
    background_tasks: BackgroundTasks,
    options: AnalyzeOptions | None = None,
    session: AsyncSession = Depends(get_session),
) -> JobRead:
    """Kick off the full lifecycle (ingest -> KB -> analyze) as a background job.

    If one's already running for this project, hands that back instead of starting
    a second — two concurrent runs would both write to the same shared local Qdrant
    store at once, which isn't safe (see knowledge_base/vector_store.py).
    """
    job, is_new = await JobService(session).create_analyze_job(project_id)
    job_view = JobRead.model_validate(job)
    max_reviews = options.max_reviews_per_source if options else None
    # Commit explicitly rather than relying on get_session()'s post-yield commit:
    # BackgroundTasks can start (and this app's worker queries the row on its own
    # session) before a Depends() dependency's post-yield teardown has actually run
    # on this FastAPI/Starlette version — reproduced directly, the job row was
    # invisible to the worker for seconds after the response was already sent.
    await session.commit()
    if is_new:
        background_tasks.add_task(run_analyze_job, job.id, max_reviews)
    return job_view


@jobs_router.get("/{job_id}", response_model=JobRead)
async def get_job(job_id: str, session: AsyncSession = Depends(get_session)) -> JobRead:
    job = await JobService(session).get(job_id)
    if job is None:
        raise NotFoundError(f"Job {job_id!r} not found.")
    return JobRead.model_validate(job)
