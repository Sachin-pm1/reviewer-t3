"""Reddit discussions connector.

Searches a subreddit via PRAW (the official Reddit API wrapper). Public
unauthenticated access to reddit.com/*.json now returns 403 — Reddit locked this down
after their 2023 API changes (confirmed directly against this project) — so this
connector needs real, free OAuth credentials. See the README for how to get them.

Config keys:
    query (str, required):  Search terms, e.g. "discover new music".
    subreddit (str):         Subreddit to search. Default "spotify".
    limit (int):             Max posts to fetch. Default 100.
    sort (str):              relevance | hot | top | new | comments. Default "relevance".
    time_filter (str):       all | day | hour | month | week | year. Default "year".
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from datetime import datetime, timezone

from app.core.config import get_settings
from app.core.errors import ValidationError
from app.ingestion.base import BaseConnector, RawDocument
from app.ingestion.registry import register


@register
class RedditConnector(BaseConnector):
    source_type = "reddit"

    @classmethod
    def validate_config(cls, config: dict) -> dict:
        config = dict(config or {})
        if not config.get("query"):
            raise ValidationError("reddit source requires a 'query' to search for.")
        config.setdefault("subreddit", "spotify")
        config.setdefault("limit", 100)
        config.setdefault("sort", "relevance")
        config.setdefault("time_filter", "year")
        # Fail at source-creation time, not deep into an analyze job — same principle
        # as file_csv checking the path exists eagerly.
        if not get_settings().has_reddit_credentials:
            raise ValidationError(
                "Reddit credentials are not configured. Set REDDIT_CLIENT_ID and "
                "REDDIT_CLIENT_SECRET (free, ~2 minutes at reddit.com/prefs/apps — "
                "see README) in your environment / .env to use this connector."
            )
        return config

    async def collect(self) -> AsyncIterator[RawDocument]:
        cfg = self.config
        posts = await asyncio.to_thread(
            _search_reddit,
            query=cfg["query"],
            subreddit=cfg["subreddit"],
            limit=int(cfg["limit"]),
            sort=cfg["sort"],
            time_filter=cfg["time_filter"],
        )
        for post in posts:
            text = "\n\n".join(filter(None, [post["title"], post["selftext"]])).strip()
            if not text:
                continue
            yield RawDocument(
                source_type=self.source_type,
                external_id=post["id"],
                text=text,
                title=post["title"],
                author=post["author"],
                url=post["permalink"],
                posted_at=post["created_at"],
                metadata={
                    "subreddit": cfg["subreddit"],
                    "score": post["score"],
                    "num_comments": post["num_comments"],
                },
            )


def _search_reddit(
    *, query: str, subreddit: str, limit: int, sort: str, time_filter: str
) -> list[dict]:
    """Synchronous fetch (runs in a thread). Imported lazily so the dep is optional."""
    try:
        import praw
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise ValidationError("praw is not installed. Run `pip install praw`.") from exc

    settings = get_settings()
    reddit = praw.Reddit(
        client_id=settings.reddit_client_id,
        client_secret=settings.reddit_client_secret,
        user_agent=settings.reddit_user_agent,
    )
    results = []
    for submission in reddit.subreddit(subreddit).search(
        query, sort=sort, time_filter=time_filter, limit=limit
    ):
        results.append(
            {
                "id": submission.id,
                "title": submission.title or "",
                "selftext": submission.selftext or "",
                "author": str(submission.author) if submission.author else None,
                "permalink": f"https://reddit.com{submission.permalink}",
                "score": submission.score,
                "num_comments": submission.num_comments,
                "created_at": datetime.fromtimestamp(submission.created_utc, tz=timezone.utc),
            }
        )
    return results
