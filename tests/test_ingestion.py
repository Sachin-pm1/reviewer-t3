"""Tests for the ingestion engine: connectors, registry, pipeline."""

from __future__ import annotations

import pytest

from app.core.errors import ValidationError
from app.ingestion.connectors.app_store import _entry_to_document, _parse_updated
from app.ingestion.pipeline import ingest
from app.ingestion.registry import available_source_types, build_connector


def test_registry_contains_increment1_connectors():
    types = available_source_types()
    assert "file_csv" in types
    assert "google_play" in types
    assert "app_store" in types
    assert "reddit" in types


def test_build_unknown_connector_raises():
    with pytest.raises(ValidationError):
        build_connector("does_not_exist", {})


def test_csv_connector_requires_existing_path():
    with pytest.raises(ValidationError):
        build_connector("file_csv", {"path": "/nope/missing.csv"})


def test_google_play_requires_app_id():
    with pytest.raises(ValidationError):
        build_connector("google_play", {})


def test_app_store_requires_app_id():
    with pytest.raises(ValidationError):
        build_connector("app_store", {})


def test_app_store_defaults():
    connector = build_connector("app_store", {"app_id": "324684580"})
    assert connector.config["country"] == "us"
    assert connector.config["max_pages"] == 5


def test_app_store_entry_parsing_maps_real_feed_shape():
    # Shape matches Apple's actual customer-reviews RSS/JSON feed, confirmed live
    # against Spotify's real App Store listing (id 324684580) before wiring this up.
    entry = {
        "author": {"name": {"label": "a real reviewer"}},
        "updated": {"label": "2026-07-01T14:38:11-07:00"},
        "im:rating": {"label": "1"},
        "im:version": {"label": "9.1.60"},
        "id": {"label": "14251135530"},
        "title": {"label": "Horrible App"},
        "content": {"label": "Too many freaking ads", "attributes": {"type": "text"}},
        "link": {"attributes": {"href": "https://itunes.apple.com/us/review?id=324684580"}},
    }
    doc = _entry_to_document(entry, app_id="324684580")
    assert doc is not None
    assert doc.external_id == "14251135530"
    assert doc.text == "Too many freaking ads"
    assert doc.rating == 1.0
    assert doc.author == "a real reviewer"
    assert doc.posted_at == _parse_updated("2026-07-01T14:38:11-07:00")


def test_app_store_entry_missing_rating_is_skipped():
    # The feed occasionally mixes in non-review entries with no rating/content.
    entry = {"title": {"label": "not a review"}}
    assert _entry_to_document(entry, app_id="324684580") is None


def test_reddit_requires_query():
    with pytest.raises(ValidationError):
        build_connector("reddit", {})


def test_reddit_requires_credentials_even_with_a_query():
    # conftest forces REDDIT_CLIENT_ID/SECRET empty, so this should fail clearly and
    # immediately (source-creation time) rather than deep into an analyze job.
    with pytest.raises(ValidationError, match="credentials"):
        build_connector("reddit", {"query": "discover new music"})


async def test_csv_ingestion_yields_normalized_docs(sample_csv_path):
    docs = [
        doc
        async for doc in ingest(
            "file_csv",
            {
                "path": sample_csv_path,
                "text_column": "text",
                "rating_column": "rating",
                "id_column": "id",
            },
        )
    ]
    assert len(docs) == 20
    first = docs[0]
    assert first.source_type == "file_csv"
    assert first.external_id == "1"
    assert first.rating == 2.0
    assert "offline" in first.text.lower()
    # Normalization collapsed any stray whitespace.
    assert "  " not in first.text


async def test_ingest_respects_limit(sample_csv_path):
    docs = [doc async for doc in ingest("file_csv", {"path": sample_csv_path}, limit=5)]
    assert len(docs) == 5
