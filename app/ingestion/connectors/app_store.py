"""Apple App Store reviews connector.

Pulls public app reviews via Apple's customer-reviews RSS/JSON feed (no credentials
required, no scraping library needed — it's a documented-by-convention public
endpoint Apple itself serves for this purpose). Confirmed working directly against
Spotify's real App Store listing before wiring this up.

Config keys:
    app_id (str, required):  Numeric Apple app id, e.g. "324684580" for Spotify.
                              Find it in the App Store URL: apps.apple.com/us/app/x/id324684580
    country (str):           Apple storefront country code. Default "us".
    max_pages (int):         Pages to fetch, 50 reviews/page. Default 5 (250 reviews).
                              Apple caps this feed at 10 pages regardless.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from datetime import datetime

import httpx
from loguru import logger

from app.core.errors import ValidationError
from app.ingestion.base import BaseConnector, RawDocument
from app.ingestion.registry import register

_FEED_URL = "https://itunes.apple.com/{country}/rss/customerreviews/page={page}/id={app_id}/sortby=mostrecent/json"
_MAX_PAGES_HARD_CAP = 10  # Apple returns 400 beyond this regardless of config.
# Confirmed empirically (not a guess): this feed intermittently returns a
# 200 with zero `entry` items for a page that has real reviews on it — the
# very next request for the *same* page, seconds later, comes back with a
# full page of entries. A page genuinely past the end of the feed also
# returns zero entries, so this can't distinguish "really done" from "Apple
# glitched" — it just retries a couple of times before accepting "done".
_EMPTY_PAGE_RETRIES = 2
_EMPTY_PAGE_RETRY_DELAY_SECONDS = 1.5


@register
class AppStoreConnector(BaseConnector):
    source_type = "app_store"

    @classmethod
    def validate_config(cls, config: dict) -> dict:
        config = dict(config or {})
        if not config.get("app_id"):
            raise ValidationError(
                "app_store source requires an 'app_id' (the numeric App Store id, "
                "e.g. '324684580' for Spotify — found in the App Store URL)."
            )
        config.setdefault("country", "us")
        config.setdefault("max_pages", 5)
        return config

    async def collect(self) -> AsyncIterator[RawDocument]:
        cfg = self.config
        app_id = str(cfg["app_id"])
        country = cfg.get("country", "us")
        max_pages = min(int(cfg.get("max_pages", 5)), _MAX_PAGES_HARD_CAP)

        async with httpx.AsyncClient(timeout=10.0) as client:
            for page in range(1, max_pages + 1):
                entries = await _fetch_page(client, app_id=app_id, country=country, page=page)
                if not entries:
                    break
                for entry in entries:
                    doc = _entry_to_document(entry, app_id=app_id)
                    if doc is not None:
                        yield doc


async def _fetch_page(
    client: httpx.AsyncClient, *, app_id: str, country: str, page: int
) -> list[dict]:
    url = _FEED_URL.format(country=country, page=page, app_id=app_id)
    for attempt in range(_EMPTY_PAGE_RETRIES + 1):
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            entries = resp.json().get("feed", {}).get("entry", []) or []
        except (httpx.HTTPError, ValueError) as exc:
            logger.warning("App Store feed page {} failed for app_id={}: {}", page, app_id, exc)
            return []
        if entries:
            return entries
        if attempt < _EMPTY_PAGE_RETRIES:
            logger.debug(
                "App Store feed page {} for app_id={} came back empty (attempt {}/{}) — "
                "retrying, since this feed is known to intermittently 200 with no entries "
                "on a page that has real reviews.",
                page, app_id, attempt + 1, _EMPTY_PAGE_RETRIES + 1,
            )
            await asyncio.sleep(_EMPTY_PAGE_RETRY_DELAY_SECONDS)
    return []


def _entry_to_document(entry: dict, *, app_id: str) -> RawDocument | None:
    # The feed mixes review entries with the occasional non-review entry (missing
    # a rating/content) — skip anything that isn't a real review.
    content = entry.get("content", {}).get("label", "").strip()
    rating_label = entry.get("im:rating", {}).get("label")
    if not content or rating_label is None:
        return None

    return RawDocument(
        source_type="app_store",
        external_id=entry.get("id", {}).get("label"),
        text=content,
        title=entry.get("title", {}).get("label"),
        author=entry.get("author", {}).get("name", {}).get("label"),
        rating=_to_float(rating_label),
        url=entry.get("link", {}).get("attributes", {}).get("href"),
        posted_at=_parse_updated(entry.get("updated", {}).get("label")),
        metadata={"app_id": app_id, "app_version": entry.get("im:version", {}).get("label")},
    )


def _to_float(value) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _parse_updated(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None
