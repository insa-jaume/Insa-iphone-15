"""Autenticación: hash de contraseñas y sesión firmada por cookie."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.config import settings

_ALGO = "HS256"
SESSION_COOKIE = "session"
_SESSION_DAYS = 30


def _to_bytes(password: str) -> bytes:
    # bcrypt solo considera los primeros 72 bytes; truncamos explícitamente.
    return password.encode("utf-8")[:72]


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_to_bytes(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(_to_bytes(password), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_session_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": str(user_id), "iat": now, "exp": now + timedelta(days=_SESSION_DAYS)}
    return jwt.encode(payload, settings.secret_key, algorithm=_ALGO)


def read_session_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[_ALGO])
        return int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        return None
