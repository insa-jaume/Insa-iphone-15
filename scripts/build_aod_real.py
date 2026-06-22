#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_aod_real.py
=================
Ensambla los datos REALES de la AOD española (5 años) que producen los agentes
extractores en /tmp/aod_extract/ y genera webapp/data/aod_real.json, que consume
la web app (mapa multi-año, KPIs, categorías y riesgo de corrupción por país).

Entradas (escritas por los 5 agentes extractores):
  /tmp/aod_extract/totales.json      {"2023":{total_eur,pct_rnb,bilateral_eur,multilateral_eur,aecid_eur,fonprode_eur,preliminar,confianza,fuentes[]},...}
  /tmp/aod_extract/paises.json       {"2023":[{iso,name,eur},...],...}
  /tmp/aod_extract/sectores.json     {"2023":[{sector,label,eur|pct},...],...}
  /tmp/aod_extract/multilateral.json {"2023":[{name,eur},...],...}
  /tmp/aod_extract/gobernanza.json   {"cpi":{"COL":40,...},"casos":[{anio,titulo,fuente,resumen},...]}

También copia los JSON de investigación crudos a scripts/aod_research_raw/ (procedencia).
"""

import os, re, json, glob, shutil, datetime
from coords import COORDS, NAME2ISO

HERE = os.path.dirname(os.path.abspath(__file__))
EXTRACT = "/tmp/aod_extract"
RESEARCH = "/tmp/aod_research"
OUT = os.path.join(HERE, "..", "webapp", "data", "aod_real.json")
RAW_COPY = os.path.join(HERE, "aod_research_raw")

ANIOS = [2020, 2021, 2022, 2023, 2024]

def load(path, default):
    try:
        return json.load(open(path, encoding="utf-8"))
    except Exception as e:
        print(f"  !! no pude leer {path}: {e}")
        return default

def iso_of(entry):
    iso = (entry.get("iso") or "").upper()
    if iso and len(iso) == 3:
        return iso
    name = (entry.get("name") or "").strip().lower()
    return NAME2ISO.get(name)

def nivel(score):
    if score >= 70: return "muy_alto"
    if score >= 55: return "alto"
    if score >= 40: return "medio"
    return "bajo"

def main():
    totales = load(f"{EXTRACT}/totales.json", {})
    paises = load(f"{EXTRACT}/paises.json", {})
    sectores = load(f"{EXTRACT}/sectores.json", {})
    multi = load(f"{EXTRACT}/multilateral.json", {})
    gob = load(f"{EXTRACT}/gobernanza.json", {"cpi": {}, "casos": []})
    cpi = {k.upper(): v for k, v in gob.get("cpi", {}).items()}

    por_anio = {}
    for y in ANIOS:
        ys = str(y)
        t = totales.get(ys, {})
        # países con coords + riesgo (CPI real)
        dests = []
        for e in paises.get(ys, []):
            iso = iso_of(e)
            if not iso or iso not in COORDS:
                continue
            eur = e.get("eur")
            c = cpi.get(iso)
            riesgo = round(100 - c, 1) if c is not None else None
            dests.append({
                "iso": iso, "name": e.get("name", iso),
                "lat": COORDS[iso][0], "lng": COORDS[iso][1],
                "eur": eur, "cpi": c,
                "riesgo": riesgo, "nivel": nivel(riesgo) if riesgo is not None else "n_d",
            })
        dests = [d for d in dests if d["eur"]]
        dests.sort(key=lambda x: -(x["eur"] or 0))

        secs = []
        for s in sectores.get(ys, []):
            secs.append({"sector": s.get("sector"), "label": s.get("label") or s.get("sector"),
                         "eur": s.get("eur"), "pct": s.get("pct")})

        mlist = [{"name": m.get("name"), "eur": m.get("eur")} for m in multi.get(ys, []) if m.get("name")]

        # riesgo medio ponderado por euro (solo países con riesgo e importe)
        num = sum((d["eur"] or 0) * d["riesgo"] for d in dests if d["riesgo"] is not None)
        den = sum((d["eur"] or 0) for d in dests if d["riesgo"] is not None)
        riesgo_pond = round(num / den, 1) if den else None

        por_anio[ys] = {
            "total_eur": t.get("total_eur"), "pct_rnb": t.get("pct_rnb"),
            "bilateral_eur": t.get("bilateral_eur"), "multilateral_eur": t.get("multilateral_eur"),
            "aecid_eur": t.get("aecid_eur"), "fonprode_eur": t.get("fonprode_eur"),
            "preliminar": t.get("preliminar", False), "confianza": t.get("confianza"),
            "fuentes": t.get("fuentes", []),
            "riesgo_medio_ponderado": riesgo_pond,
            "paises": dests, "sectores": secs, "multilateral": mlist,
        }

    obj = {
        "titulo": "AOD española — datos reales por año",
        "generado": datetime.datetime.now().isoformat(timespec="seconds"),
        "moneda": "EUR",
        "anios": ANIOS,
        "nota_riesgo": "El riesgo de corrupción por país = 100 − CPI (Índice de Percepción "
                       "de la Corrupción de Transparency International). Es un indicador de "
                       "vulnerabilidad de gobernanza del receptor, no una acusación.",
        "por_anio": por_anio,
        "gobernanza": {"cpi": cpi, "casos": gob.get("casos", [])},
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(obj, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"Escrito {OUT} ({os.path.getsize(OUT):,} bytes)")

    # procedencia: copiar investigación cruda al repo
    os.makedirs(RAW_COPY, exist_ok=True)
    n = 0
    for f in glob.glob(f"{RESEARCH}/*.json"):
        shutil.copy(f, os.path.join(RAW_COPY, os.path.basename(f))); n += 1
    for f in glob.glob(f"{EXTRACT}/*.json"):
        shutil.copy(f, os.path.join(RAW_COPY, "extract_" + os.path.basename(f))); n += 1
    print(f"Copiados {n} ficheros de procedencia a {RAW_COPY}")

    # resumen
    for y in ANIOS:
        d = por_anio[str(y)]
        print(f"  {y}: total={d['total_eur']}  %RNB={d['pct_rnb']}  "
              f"paises={len(d['paises'])} sectores={len(d['sectores'])} multi={len(d['multilateral'])} "
              f"riesgoPond={d['riesgo_medio_ponderado']}")

if __name__ == "__main__":
    main()
