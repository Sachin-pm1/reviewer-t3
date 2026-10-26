"""Encrypt/decrypt Spotify access + refresh tokens at rest.

Fernet (AES128-CBC + HMAC) keyed by TOKEN_ENCRYPTION_KEY. A token that fails
to decrypt (key rotated since it was written, or corrupted) is treated as
"not connected" rather than crashing — the user just reconnects Spotify.
"""

from __future__ import annotations

from cryptography.fernet import Fernet, InvalidToken

from app.config import get_settings


def _fernet() -> Fernet:
    return Fernet(get_settings().token_encryption_key.encode())


def encrypt(value: str) -> str:
    return _fernet().encrypt(value.encode()).decode()


def decrypt(value: str) -> str | None:
    try:
        return _fernet().decrypt(value.encode()).decode()
    except InvalidToken:
        return None
