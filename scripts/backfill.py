"""Backfill: ingiere un rango de fechas para los boletines con adaptador.

Uso:
    python -m scripts.backfill 2024-01-01 2024-12-31
    python -m scripts.backfill 2024-01-01 2024-12-31 BOE
    python -m scripts.backfill 2010-01-01 2026-06-28 BOE BORME

Recorre día a día (es intensivo: un día de BOE puede tener cientos de anuncios,
cada uno con una descarga de texto). Es idempotente: se puede reanudar.
"""
from __future__ import annotations

import sys
from datetime import date, timedelta

from app.database import SessionLocal
from app.ingest import ingest_day, match_all_active_subjects
from app.sources.registry import available_codes


def _parse(d: str) -> date:
    y, m, day = (int(x) for x in d.split("-"))
    return date(y, m, day)


def main(argv: list[str]) -> None:
    if len(argv) < 2:
        print(__doc__)
        sys.exit(1)
    start = _parse(argv[0])
    end = _parse(argv[1])
    codes = argv[2:] or available_codes()

    print(f"Backfill {start} -> {end} para {codes}")
    day = start
    while day <= end:
        with SessionLocal() as db:
            for code in codes:
                try:
                    stats = ingest_day(db, code, day)
                    if stats.get("stored"):
                        print(f"  {day} {code}: +{stats['stored']} nuevas")
                except Exception as exc:  # noqa: BLE001
                    print(f"  {day} {code}: ERROR {exc}")
        day += timedelta(days=1)

    print("Recalculando coincidencias de identidades activas...")
    with SessionLocal() as db:
        total = match_all_active_subjects(db)
    print(f"Backfill completado. Nuevas coincidencias: {total}")


if __name__ == "__main__":
    main(sys.argv[1:])
