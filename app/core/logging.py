"""Structured logging with Loguru and per-request/job correlation IDs.

A correlation id is stored in a :class:`contextvars.ContextVar` so every log line
emitted while handling a request — or running a background job — can be traced back
to its origin without threading an id through every function signature.
"""

from __future__ import annotations

import logging
import sys
from contextvars import ContextVar

from loguru import logger

from app.core.config import get_settings

# Correlation id for the current request / job. "-" when outside any context.
correlation_id: ContextVar[str] = ContextVar("correlation_id", default="-")


def bind_correlation_id(value: str) -> None:
    """Set the correlation id for the current execution context."""
    correlation_id.set(value)


def _patch_record(record: dict) -> None:
    """Inject the current correlation id into every log record."""
    record["extra"].setdefault("correlation_id", correlation_id.get())


class _InterceptHandler(logging.Handler):
    """Route stdlib logging (uvicorn, sqlalchemy, anthropic, ...) through Loguru."""

    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover - glue
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def configure_logging() -> None:
    """Configure Loguru as the single logging sink for the whole application."""
    settings = get_settings()

    logger.remove()
    logger.configure(patcher=_patch_record)
    logger.add(
        sys.stderr,
        level=settings.log_level.upper(),
        backtrace=False,
        diagnose=False,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>cid={extra[correlation_id]}</cyan> | "
            "<level>{message}</level>"
        ),
    )

    # Bridge stdlib loggers into Loguru.
    logging.basicConfig(handlers=[_InterceptHandler()], level=0, force=True)
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "sqlalchemy.engine"):
        logging.getLogger(name).handlers = [_InterceptHandler()]
        logging.getLogger(name).propagate = False
