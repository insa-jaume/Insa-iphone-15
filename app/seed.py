"""Siembra/actualiza la tabla de fuentes a partir del catálogo."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Source
from app.sources.catalog import CATALOG


def seed_sources(db: Session) -> int:
    created = 0
    for code, name, scope, region, homepage, implemented in CATALOG:
        row = db.scalar(select(Source).where(Source.code == code))
        if row is None:
            db.add(
                Source(
                    code=code,
                    name=name,
                    scope=scope,
                    region=region,
                    homepage=homepage,
                    implemented=implemented,
                    active=implemented,
                )
            )
            created += 1
        else:
            # Mantener metadatos al día sin pisar el flag 'active' del operador.
            row.name = name
            row.scope = scope
            row.region = region
            row.homepage = homepage
            row.implemented = implemented
    db.commit()
    return created
