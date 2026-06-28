"""Motor de coincidencias entre identidades vigiladas y publicaciones.

Dos estrategias:

* **Por identificador** (DNI/NIE/CIF): máxima precisión. Se busca el
  identificador normalizado como *token* dentro del campo ``identifiers`` de la
  publicación (que solo contiene identificadores fiscales válidos extraídos del
  texto). Prácticamente sin falsos positivos -> score 100.

* **Por nombre/razón social**: apoyo. Se busca el nombre normalizado como
  subcadena dentro del texto normalizado. Puede dar falsos positivos
  (homónimos), por eso se marca con score menor y "revisión recomendada".

Para volúmenes grandes en producción conviene un índice GIN/pg_trgm sobre
``normalized_text`` y ``identifiers`` (ver README). El código es compatible con
SQLite (tests) y PostgreSQL.
"""
from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import MatchType, Publication, Subject
from app.normalize import extract_identifiers, normalize_name

# Longitud mínima de nombre para permitir búsqueda por nombre (evita ruido).
MIN_NAME_LEN = 6


def build_index_fields(full_text: str) -> tuple[str, str]:
    """A partir del texto completo, calcula (texto_normalizado, identificadores).

    ``identifiers`` se almacena con espacios de relleno (" ID1 ID2 ") para poder
    hacer coincidencia exacta de token con LIKE '% ID %'.
    """
    normalized = normalize_name(full_text)
    ids = extract_identifiers(full_text)
    ids_field = (" " + " ".join(sorted(ids)) + " ") if ids else ""
    return normalized, ids_field


def find_matches_for_subject(
    db: Session,
    subject: Subject,
    *,
    since: date | None = None,
    limit: int | None = None,
) -> list[tuple[Publication, MatchType, str, int]]:
    """Busca publicaciones que coinciden con la identidad vigilada.

    Devuelve tuplas (publicación, tipo, término, score). Combina identificador y
    nombre, evitando duplicar la misma publicación (gana el identificador).
    """
    results: dict[int, tuple[Publication, MatchType, str, int]] = {}

    # --- 1) Coincidencia por identificador ---
    if subject.normalized_id:
        token = f" {subject.normalized_id} "
        stmt = select(Publication).where(Publication.identifiers.like(f"%{token}%"))
        if since is not None:
            stmt = stmt.where(Publication.pub_date >= since)
        stmt = stmt.order_by(Publication.pub_date.desc())
        if limit:
            stmt = stmt.limit(limit)
        for pub in db.scalars(stmt):
            results[pub.id] = (pub, MatchType.identifier, subject.normalized_id, 100)

    # --- 2) Coincidencia por nombre ---
    if subject.monitor_name and subject.normalized_name and len(subject.normalized_name) >= MIN_NAME_LEN:
        name = subject.normalized_name
        stmt = select(Publication).where(Publication.normalized_text.like(f"%{name}%"))
        if since is not None:
            stmt = stmt.where(Publication.pub_date >= since)
        stmt = stmt.order_by(Publication.pub_date.desc())
        if limit:
            stmt = stmt.limit(limit)
        for pub in db.scalars(stmt):
            if pub.id in results:
                continue  # ya casó por identificador (más fiable)
            results[pub.id] = (pub, MatchType.name, subject.display_name, 60)

    ordered = sorted(results.values(), key=lambda r: r[0].pub_date, reverse=True)
    return ordered


def free_text_search(
    db: Session, query: str, *, limit: int = 50
) -> list[Publication]:
    """Búsqueda libre (uso administrativo/diagnóstico) por identificador o texto."""
    q = query.strip()
    ids = extract_identifiers(q)
    stmt = select(Publication)
    if ids:
        token = f" {next(iter(ids))} "
        stmt = stmt.where(Publication.identifiers.like(f"%{token}%"))
    else:
        stmt = stmt.where(Publication.normalized_text.like(f"%{normalize_name(q)}%"))
    stmt = stmt.order_by(Publication.pub_date.desc()).limit(limit)
    return list(db.scalars(stmt))
