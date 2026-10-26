"""Application error types and FastAPI exception handlers.

Same shape as the parent repo's app/core/errors.py: domain errors map to a
consistent JSON envelope so callers never see a raw stack trace.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger


class AppError(Exception):
    """Base class for expected, handled application errors."""

    status_code: int = 500
    code: str = "internal_error"

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"


class ValidationError(AppError):
    status_code = 422
    code = "validation_error"


class ConflictError(AppError):
    status_code = 409
    code = "conflict"


class UnauthorizedError(AppError):
    status_code = 401
    code = "unauthorized"


class FeatureUnavailableError(AppError):
    """A capability is correctly wired but its prerequisites (an API key) are missing."""

    status_code = 503
    code = "feature_unavailable"


def _error_payload(code: str, message: str) -> dict:
    return {"error": {"code": code, "message": message}}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        if exc.status_code >= 500:
            logger.error("AppError [{}]: {}", exc.code, exc.message)
        else:
            logger.info("AppError [{}]: {}", exc.code, exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(exc.code, exc.message),
        )

    @app.exception_handler(Exception)
    async def _handle_unexpected(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception: {}", exc)
        return JSONResponse(
            status_code=500,
            content=_error_payload("internal_error", "An unexpected error occurred."),
        )
