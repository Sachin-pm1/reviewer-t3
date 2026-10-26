"""Single import point that registers every ORM model on Base.metadata.

database.init_models() imports this so create_all sees every table.
"""

from app.auth.models import TasteProfile, User  # noqa: F401
from app.memories.models import Memory  # noqa: F401
from app.spotify_connect.models import SpotifyConnection  # noqa: F401

__all__ = ["User", "TasteProfile", "SpotifyConnection", "Memory"]
