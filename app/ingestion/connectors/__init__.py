"""Concrete connectors.

Importing this package imports each connector module, whose ``@register`` decorator
adds it to the registry. To add a source: drop a new module here and import it below.
"""

from app.ingestion.connectors import app_store, file_csv, google_play, reddit  # noqa: F401

__all__ = ["app_store", "file_csv", "google_play", "reddit"]
