"""Crea las tablas y siembra las fuentes. Idempotente.

Uso: python -m scripts.init_db
"""
from __future__ import annotations

from app.database import Base, SessionLocal, engine
from app.models import *  # noqa: F401,F403  (registra los modelos en Base.metadata)
from app.seed import seed_sources


def main() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        created = seed_sources(db)
    print(f"Base de datos lista. Fuentes nuevas sembradas: {created}")


if __name__ == "__main__":
    main()
