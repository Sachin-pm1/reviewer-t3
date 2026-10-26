"""The Ingestion Engine.

Every input — a CSV file, an app-store listing, a forum, an API — is modelled as a
:class:`~app.ingestion.base.BaseConnector` that yields uniform
:class:`~app.ingestion.base.RawDocument` objects. The rest of the platform only ever
sees ``RawDocument``\\ s, so it stays completely source-agnostic. Adding a new source
means writing one connector and registering it; no core code changes.
"""

# Importing the connectors package triggers their @register decorators so the
# registry is populated as soon as the ingestion package is imported.
from app.ingestion import connectors  # noqa: F401
