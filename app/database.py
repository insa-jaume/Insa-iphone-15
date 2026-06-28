"""Configuración de SQLAlchemy: engine, sesión y base declarativa."""
from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, future=True)


class Base(DeclarativeBase):
    pass


def get_db() -> Iterator[Session]:
    """Dependencia FastAPI: abre y cierra una sesión por petición."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
