#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_aid_data.py
=================
Genera los datasets que consume la web app "¿A dónde va la ayuda exterior de España?".

Produce tres ficheros JSON en webapp/data/:
  - aid.json                -> destinos (países) de la AOD española, importes, sectores,
                               y RIESGO de corrupción estimado por flujo.
  - categories.json         -> categorías/sectores de gasto en ayuda exterior (totales).
  - consejo_ministros.json  -> acuerdos del Consejo de Ministros (martes) sobre cooperación,
                               cotejados con los desembolsos registrados.

IMPORTANTE — naturaleza de los datos
------------------------------------
Las cifras son ILUSTRATIVAS pero realistas: reproducen los patrones públicos de la
Ayuda Oficial al Desarrollo (AOD) española (AECID / FONPRODE / contribuciones
multilaterales / operaciones de deuda) y los países socios del Plan Director de la
Cooperación Española. No son la contabilidad oficial exacta. Las fuentes de referencia
para reproducirlas con datos reales se documentan en webapp/METODOLOGIA.md.

El "riesgo de corrupción" es un INDICADOR DE VULNERABILIDAD estimado (probabilidad de
malversación / desvío de fondos dada la gobernanza del país receptor y el canal/modalidad
de entrega). NO afirma que un fondo concreto haya sido robado. Ver METODOLOGIA.md.
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "webapp", "data")

# Año de referencia de las cifras (ejercicio representado)
EJERCICIO = 2025

# ---------------------------------------------------------------------------
# 1) DESTINOS GEOGRÁFICOS DE LA AOD BILATERAL ESPAÑOLA
# ---------------------------------------------------------------------------
# cpi  = Corruption Perceptions Index (Transparency International, 2023; 0=muy corrupto,
#        100=muy limpio). Señal principal de gobernanza del país receptor.
# eur  = importe ilustrativo del flujo bilateral español hacia ese país (euros).
# channel  = vía de entrega principal:
#            estado      -> Estado a Estado (cooperación gubernamental directa)
#            ong         -> ejecutado por ONGD / sociedad civil
#            multi_ear   -> multilateral con destino geográfico marcado (earmarked)
#            un_human    -> agencias de la ONU / ayuda humanitaria
#            deuda       -> operación de deuda (condonación / conversión)
# modality = modalidad del desembolso:
#            apoyo_presup -> apoyo presupuestario (dinero al presupuesto del receptor)
#            proyecto     -> proyecto con justificación de gasto
#            humanitaria  -> emergencia / humanitaria
#            especie      -> en especie / asistencia técnica
#            deuda        -> alivio de deuda
#
# sectores: reparto del importe por sector CAD/CRS (porcentaje, suma ~1.0)

DESTINOS = [
    # --- América Latina y Caribe ---
    dict(iso="COL", name="Colombia",            lat=4.6,   lng=-74.1, cpi=40, eur=58_000_000, channel="estado",   modality="proyecto",
         sectores={"gobernanza":0.30,"paz":0.25,"desarrollo_rural":0.20,"genero":0.15,"educacion":0.10}),
    dict(iso="PER", name="Perú",                lat=-12.0, lng=-77.0, cpi=33, eur=31_000_000, channel="estado",   modality="proyecto",
         sectores={"agua":0.30,"gobernanza":0.20,"desarrollo_rural":0.20,"educacion":0.15,"salud":0.15}),
    dict(iso="BOL", name="Bolivia",             lat=-16.5, lng=-68.1, cpi=29, eur=27_000_000, channel="estado",   modality="proyecto",
         sectores={"agua":0.30,"desarrollo_rural":0.25,"salud":0.20,"gobernanza":0.15,"genero":0.10}),
    dict(iso="ECU", name="Ecuador",             lat=-0.2,  lng=-78.5, cpi=34, eur=19_000_000, channel="ong",      modality="proyecto",
         sectores={"educacion":0.30,"salud":0.25,"desarrollo_rural":0.25,"gobernanza":0.20}),
    dict(iso="HND", name="Honduras",            lat=14.1,  lng=-87.2, cpi=23, eur=24_000_000, channel="estado",   modality="proyecto",
         sectores={"seguridad_alimentaria":0.30,"gobernanza":0.25,"agua":0.20,"genero":0.15,"salud":0.10}),
    dict(iso="GTM", name="Guatemala",           lat=14.6,  lng=-90.5, cpi=23, eur=22_000_000, channel="ong",      modality="proyecto",
         sectores={"seguridad_alimentaria":0.30,"salud":0.25,"educacion":0.20,"gobernanza":0.15,"genero":0.10}),
    dict(iso="SLV", name="El Salvador",         lat=13.7,  lng=-89.2, cpi=31, eur=14_000_000, channel="ong",      modality="proyecto",
         sectores={"gobernanza":0.30,"genero":0.25,"educacion":0.25,"agua":0.20}),
    dict(iso="NIC", name="Nicaragua",           lat=12.1,  lng=-86.3, cpi=17, eur=9_000_000,  channel="ong",      modality="humanitaria",
         sectores={"humanitaria":0.40,"salud":0.30,"agua":0.30}),
    dict(iso="DOM", name="Rep. Dominicana",     lat=18.5,  lng=-69.9, cpi=35, eur=12_000_000, channel="estado",   modality="proyecto",
         sectores={"agua":0.35,"gobernanza":0.25,"educacion":0.20,"medio_ambiente":0.20}),
    dict(iso="PRY", name="Paraguay",            lat=-25.3, lng=-57.6, cpi=28, eur=11_000_000, channel="estado",   modality="proyecto",
         sectores={"desarrollo_rural":0.30,"gobernanza":0.25,"agua":0.25,"educacion":0.20}),
    dict(iso="CUB", name="Cuba",                lat=23.1,  lng=-82.4, cpi=42, eur=8_000_000,  channel="ong",      modality="humanitaria",
         sectores={"humanitaria":0.40,"seguridad_alimentaria":0.35,"salud":0.25}),
    dict(iso="HTI", name="Haití",               lat=18.6,  lng=-72.3, cpi=17, eur=10_000_000, channel="un_human", modality="humanitaria",
         sectores={"humanitaria":0.60,"salud":0.25,"agua":0.15}),
    dict(iso="VEN", name="Venezuela",           lat=10.5,  lng=-66.9, cpi=13, eur=13_000_000, channel="un_human", modality="humanitaria",
         sectores={"humanitaria":0.55,"salud":0.25,"seguridad_alimentaria":0.20}),

    # --- África ---
    dict(iso="MAR", name="Marruecos",           lat=34.0,  lng=-6.8,  cpi=38, eur=42_000_000, channel="estado",   modality="apoyo_presup",
         sectores={"agua":0.25,"educacion":0.20,"gobernanza":0.20,"desarrollo_rural":0.20,"genero":0.15}),
    dict(iso="MRT", name="Mauritania",          lat=18.1,  lng=-15.9, cpi=30, eur=21_000_000, channel="estado",   modality="proyecto",
         sectores={"seguridad_alimentaria":0.30,"agua":0.25,"pesca":0.20,"salud":0.15,"gobernanza":0.10}),
    dict(iso="SEN", name="Senegal",             lat=14.7,  lng=-17.5, cpi=43, eur=33_000_000, channel="estado",   modality="proyecto",
         sectores={"desarrollo_rural":0.30,"agua":0.25,"educacion":0.20,"migracion":0.15,"genero":0.10}),
    dict(iso="MLI", name="Malí",                lat=12.6,  lng=-8.0,  cpi=28, eur=14_000_000, channel="un_human", modality="humanitaria",
         sectores={"humanitaria":0.45,"seguridad_alimentaria":0.30,"salud":0.25}),
    dict(iso="NER", name="Níger",               lat=13.5,  lng=2.1,   cpi=32, eur=12_000_000, channel="un_human", modality="humanitaria",
         sectores={"humanitaria":0.45,"seguridad_alimentaria":0.30,"agua":0.25}),
    dict(iso="ETH", name="Etiopía",             lat=9.0,   lng=38.7,  cpi=37, eur=16_000_000, channel="un_human", modality="humanitaria",
         sectores={"humanitaria":0.50,"seguridad_alimentaria":0.30,"salud":0.20}),
    dict(iso="MOZ", name="Mozambique",          lat=-25.9, lng=32.6,  cpi=25, eur=20_000_000, channel="estado",   modality="proyecto",
         sectores={"salud":0.30,"educacion":0.25,"agua":0.20,"desarrollo_rural":0.15,"gobernanza":0.10}),
    dict(iso="GNQ", name="Guinea Ecuatorial",   lat=3.8,   lng=8.8,   cpi=17, eur=6_000_000,  channel="estado",   modality="especie",
         sectores={"educacion":0.40,"salud":0.35,"gobernanza":0.25}),
    dict(iso="NGA", name="Nigeria",             lat=9.1,   lng=7.4,   cpi=25, eur=7_000_000,  channel="un_human", modality="humanitaria",
         sectores={"humanitaria":0.55,"salud":0.25,"genero":0.20}),
    dict(iso="CPV", name="Cabo Verde",          lat=14.9,  lng=-23.5, cpi=64, eur=9_000_000,  channel="estado",   modality="proyecto",
         sectores={"agua":0.30,"medio_ambiente":0.25,"educacion":0.25,"gobernanza":0.20}),
    dict(iso="DZA", name="Argelia (camp. saharauis)", lat=27.7, lng=-8.1, cpi=36, eur=11_000_000, channel="un_human", modality="humanitaria",
         sectores={"humanitaria":0.60,"seguridad_alimentaria":0.25,"salud":0.15}),
    dict(iso="TUN", name="Túnez",               lat=36.8,  lng=10.2,  cpi=40, eur=8_000_000,  channel="estado",   modality="proyecto",
         sectores={"gobernanza":0.30,"migracion":0.25,"educacion":0.25,"genero":0.20}),

    # --- Oriente Próximo / Mediterráneo ---
    dict(iso="PSE", name="Territorios Palestinos", lat=31.9, lng=35.2, cpi=30, eur=26_000_000, channel="un_human", modality="humanitaria",
         sectores={"humanitaria":0.45,"salud":0.20,"educacion":0.20,"gobernanza":0.15}),
    dict(iso="JOR", name="Jordania",            lat=31.9,  lng=35.9,  cpi=46, eur=10_000_000, channel="un_human", modality="humanitaria",
         sectores={"humanitaria":0.50,"educacion":0.30,"agua":0.20}),
    dict(iso="LBN", name="Líbano",              lat=33.9,  lng=35.5,  cpi=24, eur=9_000_000,  channel="un_human", modality="humanitaria",
         sectores={"humanitaria":0.55,"salud":0.25,"educacion":0.20}),
    dict(iso="SYR", name="Siria",               lat=33.5,  lng=36.3,  cpi=13, eur=12_000_000, channel="un_human", modality="humanitaria",
         sectores={"humanitaria":0.70,"salud":0.20,"agua":0.10}),

    # --- Otros (humanitario) ---
    dict(iso="UKR", name="Ucrania",             lat=50.4,  lng=30.5,  cpi=36, eur=18_000_000, channel="un_human", modality="humanitaria",
         sectores={"humanitaria":0.60,"salud":0.20,"gobernanza":0.20}),
    dict(iso="PHL", name="Filipinas",           lat=14.6,  lng=121.0, cpi=34, eur=6_000_000,  channel="ong",      modality="proyecto",
         sectores={"medio_ambiente":0.35,"desarrollo_rural":0.30,"educacion":0.20,"genero":0.15}),
    dict(iso="AFG", name="Afganistán",          lat=34.5,  lng=69.2,  cpi=20, eur=7_000_000,  channel="un_human", modality="humanitaria",
         sectores={"humanitaria":0.65,"salud":0.20,"genero":0.15}),
]

# ---------------------------------------------------------------------------
# 2) MODELO DE RIESGO DE CORRUPCIÓN (indicador de vulnerabilidad)
# ---------------------------------------------------------------------------
# Riesgo = combinación ponderada de:
#   (a) Gobernanza del receptor   -> (100 - CPI)           peso 0.50
#   (b) Riesgo de la modalidad    -> tabla MODALIDAD_RIESGO peso 0.30
#   (c) Riesgo del canal de entrega-> tabla CANAL_RIESGO    peso 0.20
# Resultado normalizado a 0..100. Mayor = más vulnerable a desvío.
#
# Lógica: el dinero entregado como apoyo presupuestario a un Estado con baja
# gobernanza y por vía gubernamental directa es el MÁS vulnerable; la ayuda
# humanitaria canalizada por agencias de la ONU con justificación es la MENOS
# vulnerable (independientemente de lo corrupto que sea el país).

W_GOBERNANZA = 0.50
W_MODALIDAD  = 0.30
W_CANAL      = 0.20

MODALIDAD_RIESGO = {  # 0..100
    "apoyo_presup": 95,   # dinero al presupuesto del receptor: máxima fungibilidad
    "deuda":        70,   # alivio de deuda: libera recursos, poca trazabilidad de destino
    "proyecto":     45,   # proyecto con justificación de gasto
    "especie":      30,   # en especie / asistencia técnica
    "humanitaria":  25,   # emergencia con control humanitario
}

CANAL_RIESGO = {  # 0..100
    "estado":    90,   # Estado a Estado: pasa por la administración del receptor
    "deuda":     65,
    "multi_ear": 45,   # multilateral marcado
    "ong":       35,   # ONGD con auditoría
    "un_human":  20,   # agencias ONU / humanitario
}

def riesgo_corrupcion(d):
    gob = 100 - d["cpi"]                       # (a)
    mod = MODALIDAD_RIESGO[d["modality"]]      # (b)
    can = CANAL_RIESGO[d["channel"]]           # (c)
    score = W_GOBERNANZA * gob + W_MODALIDAD * mod + W_CANAL * can
    return round(score, 1)

def nivel(score):
    if score >= 70: return "muy_alto"
    if score >= 55: return "alto"
    if score >= 40: return "medio"
    return "bajo"

# ---------------------------------------------------------------------------
# 3) CONTRIBUCIONES MULTILATERALES (no geográficas) — para el total y categorías
# ---------------------------------------------------------------------------
# Estas no se pintan en el mapa como burbuja país, pero cuentan en el total y en
# las categorías. Reflejan que la mayor parte de la AOD española es multilateral
# (UE, organismos ONU, bancos de desarrollo).
MULTILATERAL = [
    dict(name="Unión Europea (FED / presupuesto)", eur=1_350_000_000, sector="multilateral"),
    dict(name="Organismos ONU (PMA, ACNUR, UNICEF, OMS…)", eur=320_000_000, sector="multilateral"),
    dict(name="Bancos de desarrollo (BM, BID, BAfD)", eur=290_000_000, sector="multilateral"),
    dict(name="Fondos climáticos y medioambientales", eur=180_000_000, sector="medio_ambiente"),
    dict(name="Operaciones de deuda (condonación/conversión)", eur=95_000_000, sector="deuda"),
    dict(name="Costes refugiados en España (in-donor)", eur=410_000_000, sector="in_donor"),
]

# Etiquetas legibles de sectores
SECTORES_LABEL = {
    "humanitaria": "Ayuda humanitaria y emergencia",
    "salud": "Salud y población",
    "educacion": "Educación",
    "gobernanza": "Gobernanza y sociedad civil",
    "agua": "Agua y saneamiento",
    "desarrollo_rural": "Agricultura y desarrollo rural",
    "seguridad_alimentaria": "Seguridad alimentaria",
    "medio_ambiente": "Medio ambiente y clima",
    "genero": "Igualdad de género",
    "paz": "Construcción de paz",
    "migracion": "Migración y movilidad",
    "pesca": "Pesca y recursos marinos",
    "multilateral": "Contribuciones multilaterales",
    "deuda": "Operaciones de deuda",
    "in_donor": "Costes en país donante",
}

# ---------------------------------------------------------------------------
# 4) ACUERDOS DEL CONSEJO DE MINISTROS (martes) — cotejo con desembolsos
# ---------------------------------------------------------------------------
# Cada entrada representa un acuerdo de cooperación adoptado en un Consejo de
# Ministros (los martes). "cotejado" indica si el acuerdo aparece reflejado en
# los desembolsos registrados del país/sector correspondiente.
#   match = "ok"        -> importe acordado ≈ desembolso registrado
#   match = "parcial"   -> ejecutado parcialmente / pendiente de justificar
#   match = "sin_rastro"-> acordado pero sin desembolso trazable todavía
CONSEJO = [
    dict(fecha="2025-01-14", instrumento="FONPRODE", iso="SEN", titulo="Crédito FONPRODE para agua y saneamiento en Senegal", eur=20_000_000, match="ok"),
    dict(fecha="2025-01-28", instrumento="AECID",    iso="HND", titulo="Subvención AECID seguridad alimentaria Honduras", eur=8_000_000, match="parcial"),
    dict(fecha="2025-02-11", instrumento="Humanitaria", iso="SYR", titulo="Ayuda humanitaria de emergencia Siria (terremoto/conflicto)", eur=6_000_000, match="ok"),
    dict(fecha="2025-02-25", instrumento="Deuda",     iso="MRT", titulo="Conversión de deuda por desarrollo con Mauritania", eur=15_000_000, match="sin_rastro"),
    dict(fecha="2025-03-11", instrumento="Multilateral", iso=None, titulo="Contribución al Programa Mundial de Alimentos (PMA)", eur=40_000_000, match="ok"),
    dict(fecha="2025-03-25", instrumento="AECID",    iso="COL", titulo="Programa de paz y reincorporación en Colombia", eur=12_000_000, match="ok"),
    dict(fecha="2025-04-08", instrumento="FONPRODE", iso="MAR", titulo="Apoyo presupuestario sectorial educación Marruecos", eur=18_000_000, match="parcial"),
    dict(fecha="2025-04-22", instrumento="Humanitaria", iso="PSE", titulo="Ayuda humanitaria Territorios Palestinos (UNRWA)", eur=14_000_000, match="ok"),
    dict(fecha="2025-05-13", instrumento="AECID",    iso="BOL", titulo="Programa de agua y saneamiento rural en Bolivia", eur=10_000_000, match="ok"),
    dict(fecha="2025-05-27", instrumento="Multilateral", iso=None, titulo="Aportación al Fondo Verde para el Clima", eur=35_000_000, match="ok"),
    dict(fecha="2025-06-10", instrumento="FONPRODE", iso="GNQ", titulo="Cooperación técnica Guinea Ecuatorial", eur=6_000_000, match="sin_rastro"),
    dict(fecha="2025-06-24", instrumento="Humanitaria", iso="UKR", titulo="Ayuda humanitaria a Ucrania", eur=12_000_000, match="ok"),
    dict(fecha="2025-09-09", instrumento="AECID",    iso="MOZ", titulo="Programa de salud materno-infantil Mozambique", eur=9_000_000, match="parcial"),
    dict(fecha="2025-09-23", instrumento="Deuda",     iso="CUB", titulo="Reestructuración de deuda con Cuba", eur=8_000_000, match="sin_rastro"),
    dict(fecha="2025-10-14", instrumento="Multilateral", iso=None, titulo="Contribución a ACNUR para crisis de refugiados", eur=28_000_000, match="ok"),
    dict(fecha="2025-10-28", instrumento="AECID",    iso="PER", titulo="Programa de gobernanza democrática Perú", eur=7_000_000, match="ok"),
    dict(fecha="2025-11-11", instrumento="FONPRODE", iso="DZA", titulo="Ayuda a la población saharaui (campamentos de Tinduf)", eur=11_000_000, match="ok"),
    dict(fecha="2025-11-25", instrumento="Humanitaria", iso="HTI", titulo="Respuesta humanitaria en Haití", eur=6_000_000, match="parcial"),
    dict(fecha="2025-12-16", instrumento="AECID",    iso="GTM", titulo="Programa de salud y nutrición Guatemala", eur=8_000_000, match="ok"),
]

# ---------------------------------------------------------------------------
# BUILD
# ---------------------------------------------------------------------------
def build():
    # --- aid.json (destinos) ---
    destinos = []
    for d in DESTINOS:
        score = riesgo_corrupcion(d)
        destinos.append({
            "iso": d["iso"],
            "name": d["name"],
            "lat": d["lat"],
            "lng": d["lng"],
            "eur": d["eur"],
            "cpi": d["cpi"],
            "channel": d["channel"],
            "modality": d["modality"],
            "sectores": d["sectores"],
            "riesgo": score,
            "nivel": nivel(score),
        })
    destinos.sort(key=lambda x: -x["eur"])

    total_bilateral = sum(d["eur"] for d in destinos)
    total_multi = sum(m["eur"] for m in MULTILATERAL)
    total = total_bilateral + total_multi

    # ponderación de riesgo por euro (solo bilateral geográfico)
    riesgo_ponderado = sum(d["eur"] * d["riesgo"] for d in destinos) / total_bilateral

    aid = {
        "ejercicio": EJERCICIO,
        "moneda": "EUR",
        "total_aod": total,
        "total_bilateral_geografico": total_bilateral,
        "total_multilateral": total_multi,
        "riesgo_medio_ponderado": round(riesgo_ponderado, 1),
        "destinos": destinos,
        "multilateral": MULTILATERAL,
        "modelo_riesgo": {
            "pesos": {"gobernanza": W_GOBERNANZA, "modalidad": W_MODALIDAD, "canal": W_CANAL},
            "modalidad_riesgo": MODALIDAD_RIESGO,
            "canal_riesgo": CANAL_RIESGO,
        },
    }

    # --- categories.json (sectores) ---
    cat_tot = {}
    for d in destinos:
        for s, frac in d["sectores"].items():
            cat_tot[s] = cat_tot.get(s, 0) + d["eur"] * frac
    for m in MULTILATERAL:
        cat_tot[m["sector"]] = cat_tot.get(m["sector"], 0) + m["eur"]
    categorias = [
        {"sector": s, "label": SECTORES_LABEL.get(s, s), "eur": round(v)}
        for s, v in sorted(cat_tot.items(), key=lambda kv: -kv[1])
    ]
    categories = {"ejercicio": EJERCICIO, "total": round(sum(cat_tot.values())), "categorias": categorias}

    # --- consejo_ministros.json (cotejo) ---
    by_iso = {d["iso"]: d for d in destinos}
    items = []
    for c in CONSEJO:
        riesgo = by_iso[c["iso"]]["riesgo"] if c["iso"] in by_iso else None
        items.append({**c, "riesgo": riesgo})
    consejo = {
        "ejercicio": EJERCICIO,
        "nota": "Acuerdos de cooperación adoptados en Consejo de Ministros (martes), cotejados con desembolsos registrados.",
        "resumen": {
            "ok": sum(1 for c in CONSEJO if c["match"] == "ok"),
            "parcial": sum(1 for c in CONSEJO if c["match"] == "parcial"),
            "sin_rastro": sum(1 for c in CONSEJO if c["match"] == "sin_rastro"),
        },
        "acuerdos": items,
    }

    os.makedirs(OUT, exist_ok=True)
    for fname, obj in [("aid.json", aid), ("categories.json", categories), ("consejo_ministros.json", consejo)]:
        path = os.path.join(OUT, fname)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
        print(f"  escrito {fname}: {os.path.getsize(path):,} bytes")

    print(f"\nResumen ejercicio {EJERCICIO}:")
    print(f"  AOD total (ilustrativa):      {total:,.0f} €")
    print(f"  Bilateral geográfica:         {total_bilateral:,.0f} €")
    print(f"  Multilateral:                 {total_multi:,.0f} €")
    print(f"  Riesgo medio ponderado/€:     {riesgo_ponderado:.1f}/100")

if __name__ == "__main__":
    build()
