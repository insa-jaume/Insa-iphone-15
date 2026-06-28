"""Orquestación de la ingesta: sumario -> publicaciones -> coincidencias.

Flujo diario:
    1. Para cada boletín con adaptador, descargar el sumario del día.
    2. Para cada anuncio nuevo, descargar su texto, extraer identificadores y
       guardar la publicación (idempotente por (source, ext_id)).
    3. Buscar coincidencias con las identidades vigiladas activas y crear los
       ``Match`` pendientes de notificar.
"""
from __future__ import annotations

import logging
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import IngestLog, Match, Publication, Source, Subject
from app.search import build_index_fields, find_matches_for_subject
from app.sources.base import BulletinSource
from app.sources.registry import get_source

log = logging.getLogger("ingest")


def _get_source_row(db: Session, code: str) -> Source | None:
    return db.scalar(select(Source).where(Source.code == code))


def ingest_day(db: Session, code: str, day: date, *, force: bool = False) -> dict:
    """Ingiere un boletín para un día concreto. Idempotente.

    Devuelve estadísticas {stored, skipped, items}.
    """
    source_row = _get_source_row(db, code)
    if source_row is None:
        raise ValueError(f"Fuente desconocida: {code}")

    # ¿Ya ingerido? (salvo force)
    already = db.scalar(
        select(IngestLog).where(IngestLog.source_code == code, IngestLog.pub_date == day)
    )
    if already and already.status in ("ok", "empty") and not force:
        return {"stored": 0, "skipped": already.items, "items": already.items, "cached": True}

    adapter: BulletinSource | None = get_source(code)
    if adapter is None:
        raise ValueError(f"No hay adaptador de ingesta para {code} todavía")

    stored = skipped = 0
    status = "ok"
    detail = ""
    try:
        items = adapter.fetch_summary_items(day)
        for raw in items:
            if not raw.ext_id:
                continue
            exists = db.scalar(
                select(Publication.id).where(
                    Publication.source_id == source_row.id,
                    Publication.ext_id == raw.ext_id,
                )
            )
            if exists:
                skipped += 1
                continue

            full_text = adapter.fetch_item_text(raw)
            normalized, ids_field = build_index_fields(full_text)
            pub = Publication(
                source_id=source_row.id,
                ext_id=raw.ext_id,
                pub_date=raw.pub_date,
                section=raw.section,
                department=raw.department,
                title=raw.title[:8000],
                url_html=raw.url_html,
                url_pdf=raw.url_pdf,
                full_text=full_text,
                normalized_text=normalized,
                identifiers=ids_field,
                is_notification=raw.is_notification,
            )
            db.add(pub)
            stored += 1
            # Commit por lotes para no perder progreso en backfills largos.
            if stored % 50 == 0:
                db.commit()
        db.commit()
        if not items:
            status = "empty"
    except Exception as exc:  # noqa: BLE001 - registramos y seguimos
        db.rollback()
        status = "error"
        detail = str(exc)[:1000]
        log.exception("Error ingiriendo %s %s", code, day)
    finally:
        adapter.close()

    # Registrar el log de ingesta (idempotente).
    logrow = db.scalar(
        select(IngestLog).where(IngestLog.source_code == code, IngestLog.pub_date == day)
    )
    if logrow is None:
        logrow = IngestLog(source_code=code, pub_date=day)
        db.add(logrow)
    logrow.items = stored + skipped
    logrow.status = status
    logrow.detail = detail
    db.commit()

    return {"stored": stored, "skipped": skipped, "items": stored + skipped, "status": status}


def match_subject(db: Session, subject: Subject, *, since: date | None = None) -> int:
    """Crea los Match que falten para una identidad. Devuelve nº de nuevos."""
    found = find_matches_for_subject(db, subject, since=since)
    new = 0
    for pub, match_type, term, score in found:
        exists = db.scalar(
            select(Match.id).where(
                Match.subject_id == subject.id, Match.publication_id == pub.id
            )
        )
        if exists:
            continue
        db.add(
            Match(
                subject_id=subject.id,
                publication_id=pub.id,
                match_type=match_type,
                matched_term=term[:255],
                score=score,
            )
        )
        new += 1
    db.commit()
    return new


def match_all_active_subjects(db: Session, *, since: date | None = None) -> int:
    """Recalcula coincidencias de todas las identidades activas. Devuelve total nuevos."""
    subjects = db.scalars(select(Subject).where(Subject.active.is_(True))).all()
    total = 0
    for subject in subjects:
        total += match_subject(db, subject, since=since)
    return total
