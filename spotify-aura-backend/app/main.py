"""FastAPI application factory for the standalone Spotify Aura Companion MVP."""

from __future__ import annotations

import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.auth.routes import me_router, router as auth_router
from app.catalog_routes import router as catalog_router
from app.companion.routes import router as companion_router
from app.config import get_settings
from app.database import init_models
from app.errors import register_exception_handlers
from app.memories.routes import router as memories_router
from app.rate_limit import check_rate_limit
from app.spotify_connect.routes import me_router as spotify_me_router, router as spotify_auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    await init_models()
    logger.info(
        "Started spotify-aura-backend (model={}, ai={}, spotify={})",
        settings.anthropic_model,
        "enabled" if settings.has_anthropic_key else "disabled (no ANTHROPIC_API_KEY)",
        "enabled" if settings.has_spotify_credentials else "disabled (falls back to iTunes only)",
    )
    yield
    logger.info("Shutting down")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Spotify Aura — Discovery Companion",
        version="0.1.0",
        description="Standalone AI-native music discovery MVP (Part 4).",
        lifespan=lifespan,
    )

    @app.middleware("http")
    async def correlation_id_middleware(request: Request, call_next):
        blocked = check_rate_limit(request)
        if blocked is not None:
            return blocked
        cid = request.headers.get("X-Correlation-ID") or uuid.uuid4().hex[:12]
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = cid
        return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Correlation-ID"],
    )

    register_exception_handlers(app)
    app.include_router(auth_router)
    app.include_router(me_router)
    app.include_router(spotify_auth_router)
    app.include_router(spotify_me_router)
    app.include_router(memories_router)
    app.include_router(companion_router)
    app.include_router(catalog_router)

    @app.get("/health", tags=["meta"])
    async def health() -> dict:
        return {
            "status": "ok",
            "model": settings.anthropic_model,
            "ai_enabled": settings.has_anthropic_key,
            "spotify_enabled": settings.has_spotify_credentials,
        }

    return app


app = create_app()
