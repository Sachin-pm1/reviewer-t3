"""FastAPI application factory and wiring.

Brings the modular monolith together: configures logging, creates tables on startup
(local/dev path), registers connectors, installs a correlation-id middleware and the
JSON error handlers, and mounts every domain router.
"""

from __future__ import annotations

import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.analysis.routes import router as analysis_router
from app.chat.routes import router as chat_router
from app.core.config import get_settings
from app.core.errors import register_exception_handlers
from app.core.logging import bind_correlation_id, configure_logging
from app.core.rate_limit import check_rate_limit
from app.database.base import init_models
from app.jobs.routes import analyze_router, jobs_router
from app.products.routes import catalog_router
from app.products.routes import router as products_router
from app.reports.routes import (
    project_reports_router,
    report_catalog_router,
    reports_router,
)
from app.reviews.routes import router as reviews_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    settings = get_settings()

    # Importing these packages runs the registration side-effects:
    #   - ingestion connectors register on the connector registry
    #   - report agents register on the agent registry
    import app.agents  # noqa: F401
    import app.ingestion  # noqa: F401

    await init_models()

    logger.info(
        "Started {} (env={}, model={}, ai={})",
        settings.app_name,
        settings.environment,
        settings.anthropic_model,
        "enabled" if settings.has_anthropic_key else "disabled (no ANTHROPIC_API_KEY)",
    )
    yield
    logger.info("Shutting down")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description=(
            "Product-agnostic AI Product Intelligence Platform: ingest customer "
            "feedback from any source, build a RAG knowledge base, and generate "
            "structured product insights with Claude."
        ),
        lifespan=lifespan,
    )

    # One BaseHTTPMiddleware layer, not two — see check_rate_limit's docstring for
    # why a second stacked @app.middleware("http") caused a real, reproduced bug.
    @app.middleware("http")
    async def correlation_id_middleware(request: Request, call_next):
        blocked = check_rate_limit(request)
        if blocked is not None:
            return blocked
        cid = request.headers.get("X-Correlation-ID") or uuid.uuid4().hex[:12]
        bind_correlation_id(cid)
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = cid
        return response

    # Allow the standalone Next.js frontend (and other browser clients) to call the
    # API directly. The frontend can also proxy through Next, in which case this is
    # simply unused — configured via CORS_ORIGINS.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Correlation-ID"],
    )

    register_exception_handlers(app)

    # Routers.
    app.include_router(products_router)
    app.include_router(catalog_router)
    app.include_router(analyze_router)
    app.include_router(jobs_router)
    app.include_router(analysis_router)
    app.include_router(chat_router)
    app.include_router(project_reports_router)
    app.include_router(reports_router)
    app.include_router(report_catalog_router)
    app.include_router(reviews_router)

    @app.get("/health", tags=["meta"])
    async def health() -> dict:
        return {
            "status": "ok",
            "app": settings.app_name,
            "model": settings.anthropic_model,
            "ai_enabled": settings.has_anthropic_key,
        }

    return app


app = create_app()
