"""Google Play Store reviews connector.

Pulls public app reviews via ``google-play-scraper`` (no credentials required). The
scraper is synchronous, so calls run in a worker thread to stay async-friendly.

Config keys:
    app_id (str, required):  Play package id, e.g. "com.spotify.music".
    count (int):             Max reviews to fetch. Default 200.
    lang (str):              Language. Default "en".
    country (str):           Country. Default "us".
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

from app.core.errors import ValidationError
from app.ingestion.base import BaseConnector, RawDocument
from app.ingestion.registry import register


@register
class GooglePlayConnector(BaseConnector):
    source_type = "google_play"

    @classmethod
    def validate_config(cls, config: dict) -> dict:
        config = dict(config or {})
        if not config.get("app_id"):
            raise ValidationError(
                "google_play source requires an 'app_id' (e.g. 'com.spotify.music')."
            )
        config.setdefault("count", 200)
        config.setdefault("lang", "en")
        config.setdefault("country", "us")
        return config

    async def collect(self) -> AsyncIterator[RawDocument]:
        cfg = self.config
        rows = await asyncio.to_thread(
            _fetch_reviews,
            app_id=cfg["app_id"],
            count=int(cfg["count"]),
            lang=cfg["lang"],
            country=cfg["country"],
        )
        for row in rows:
            content = (row.get("content") or "").strip()
            if not content:
                continue
            yield RawDocument(
                source_type=self.source_type,
                external_id=row.get("reviewId"),
                text=content,
                author=row.get("userName"),
                rating=_to_float(row.get("score")),
                posted_at=row.get("at"),
                metadata={
                    "app_id": cfg["app_id"],
                    "thumbs_up": row.get("thumbsUpCount"),
                    "app_version": row.get("reviewCreatedVersion"),
                },
            )


def _fetch_reviews(*, app_id: str, count: int, lang: str, country: str) -> list[dict]:
    """Synchronous fetch (runs in a thread). Imported lazily so the dep is optional."""
    try:
        from google_play_scraper import Sort, reviews
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise ValidationError(
            "google-play-scraper is not installed. Run `pip install google-play-scraper`."
        ) from exc

    result, _token = reviews(
        app_id,
        lang=lang,
        country=country,
        sort=Sort.NEWEST,
        count=count,
    )
    return result or []


def _to_float(value) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None
