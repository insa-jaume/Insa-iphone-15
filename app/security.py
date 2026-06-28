"""Autenticación: hash de contraseñas y sesión firmada por cookie."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from app.config import settings

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
_ALGO = "HS256"
SESSION_COOKIE = "session"
_SESSION_DAYS = 30


def hash_password(password: str) -> str:
    return _pwd.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _pwd.verify(password, password_hash)
    except ValueError:
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
