"""CSV file connector.

Reads reviews/feedback from a CSV file on disk. Works completely offline, which makes
it the default way to run a real analysis on day one. Column names are configurable so
it adapts to whatever export the user has.

Config keys:
    path (str, required):   Path to the CSV file.
    text_column (str):      Column holding the feedback text. Default "text".
    rating_column (str):    Optional column holding a numeric rating.
    author_column (str):    Optional column holding the author.
    title_column (str):     Optional column holding a title/subject.
    id_column (str):        Optional column holding a stable id.
    encoding (str):         File encoding. Default "utf-8".
"""

from __future__ import annotations

import csv
from collections.abc import AsyncIterator
from pathlib import Path

from app.core.errors import ValidationError
from app.ingestion.base import BaseConnector, RawDocument
from app.ingestion.registry import register


@register
class CsvFileConnector(BaseConnector):
    source_type = "file_csv"

    @classmethod
    def validate_config(cls, config: dict) -> dict:
        config = dict(config or {})
        path = config.get("path")
        if not path:
            raise ValidationError("file_csv source requires a 'path' to the CSV file.")
        if not Path(path).is_file():
            raise ValidationError(f"CSV file not found: {path}")
        config.setdefault("text_column", "text")
        config.setdefault("encoding", "utf-8")
        return config

    async def collect(self) -> AsyncIterator[RawDocument]:
        cfg = self.config
        path = cfg["path"]
        text_col = cfg.get("text_column", "text")
        rating_col = cfg.get("rating_column")
        author_col = cfg.get("author_column")
        title_col = cfg.get("title_column")
        id_col = cfg.get("id_column")
        encoding = cfg.get("encoding", "utf-8")

        with open(path, newline="", encoding=encoding) as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames is None or text_col not in reader.fieldnames:
                raise ValidationError(
                    f"CSV is missing the text column {text_col!r}. "
                    f"Found columns: {reader.fieldnames}"
                )
            for index, row in enumerate(reader):
                text = (row.get(text_col) or "").strip()
                if not text:
                    continue
                rating = _to_float(row.get(rating_col)) if rating_col else None
                yield RawDocument(
                    source_type=self.source_type,
                    external_id=(row.get(id_col) if id_col else None) or f"row-{index}",
                    text=text,
                    title=row.get(title_col) if title_col else None,
                    author=row.get(author_col) if author_col else None,
                    rating=rating,
                    metadata={"source_path": str(path), "row_index": index},
                )


def _to_float(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
