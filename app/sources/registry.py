"""Registro de adaptadores de ingesta disponibles (code -> clase)."""
from __future__ import annotations

from app.sources.base import BulletinSource
from app.sources.boe import BoeSource, BormeSource

_REGISTRY: dict[str, type[BulletinSource]] = {
    BoeSource.code: BoeSource,
    BormeSource.code: BormeSource,
}


def get_source(code: str) -> BulletinSource | None:
    cls = _REGISTRY.get(code)
    return cls() if cls else None


def available_codes() -> list[str]:
    return list(_REGISTRY.keys())
