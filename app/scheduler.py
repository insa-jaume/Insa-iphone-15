"""Proceso 'worker': ingesta diaria automática + envío de avisos.

Se ejecuta como servicio independiente (ver docker-compose). Cada día a la hora
configurada descarga los boletines del día, recalcula coincidencias y envía los
avisos pendientes.

Uso: python -m app.scheduler
"""
from __future__ import annotations

import logging
from datetime import date, timedelta

from apscheduler.schedulers.blocking import BlockingScheduler

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.ingest import ingest_day, match_all_active_subjects
from app.models import *  # noqa: F401,F403
from app.notifier import notify_pending
from app.seed import seed_sources
from app.sources.registry import available_codes

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("scheduler")


def daily_job() -> None:
    """Ingiere el boletín de hoy (y reintenta ayer por si se publicó tarde)."""
    today = date.today()
    days = [today, today - timedelta(days=1)]
    codes = available_codes()
    with SessionLocal() as db:
        for day in days:
            for code in codes:
                try:
                    stats = ingest_day(db, code, day)
                    log.info("Ingesta %s %s: %s", code, day, stats)
                except Exception:  # noqa: BLE001
                    log.exception("Error ingiriendo %s %s", code, day)
        new = match_all_active_subjects(db, since=today - timedelta(days=7))
        log.info("Nuevas coincidencias: %s", new)
        sent = notify_pending(db)
        log.info("Usuarios notificados: %s", sent)


def main() -> None:
    # Asegura esquema y fuentes en arranque.
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_sources(db)

    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(daily_job, "cron", hour=settings.ingest_daily_hour, minute=0, id="daily")
    log.info("Worker iniciado. Ingesta diaria a las %02d:00 UTC.", settings.ingest_daily_hour)
    # Ejecuta una pasada al arrancar para no esperar al primer cron.
    try:
        daily_job()
    except Exception:  # noqa: BLE001
        log.exception("Fallo en la pasada inicial")
    scheduler.start()


if __name__ == "__main__":
    main()
