"""Connector registry — the plugin mechanism for the Ingestion Engine.

Connectors register themselves with ``@register``; callers build them by source-type
string via :func:`build_connector`. New sources plug in without any consumer of the
registry changing.
"""

from __future__ import annotations

from app.core.errors import ValidationError
from app.ingestion.base import BaseConnector

_REGISTRY: dict[str, type[BaseConnector]] = {}


def register(connector_cls: type[BaseConnector]) -> type[BaseConnector]:
    """Class decorator registering a connector under its ``source_type``."""
    key = connector_cls.source_type
    if not key:
        raise ValueError(f"{connector_cls.__name__} must define a non-empty source_type")
    if key in _REGISTRY and _REGISTRY[key] is not connector_cls:
        raise ValueError(f"Duplicate connector source_type: {key!r}")
    _REGISTRY[key] = connector_cls
    return connector_cls


def available_source_types() -> list[str]:
    """Return the sorted list of registered source-type keys."""
    return sorted(_REGISTRY)


def get_connector_cls(source_type: str) -> type[BaseConnector]:
    """Return the connector class for ``source_type`` or raise ``ValidationError``."""
    try:
        return _REGISTRY[source_type]
    except KeyError as exc:
        raise ValidationError(
            f"Unknown source type {source_type!r}. "
            f"Available: {', '.join(available_source_types()) or '(none)'}."
        ) from exc


def build_connector(source_type: str, config: dict | None = None) -> BaseConnector:
    """Instantiate a connector after validating its config."""
    cls = get_connector_cls(source_type)
    clean_config = cls.validate_config(config or {})
    return cls(clean_config)
