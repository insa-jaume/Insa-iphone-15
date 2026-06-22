#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scrape_consejo_ministros.py
===========================
Descarga datos REALES del Consejo de Ministros desde La Moncloa y extrae los
acuerdos de COOPERACIÓN / AYUDA EXTERIOR (AECID, FONPRODE, ayuda humanitaria,
contribuciones multilaterales, operaciones de deuda) con sus importes en euros.

Fuente oficial: https://www.lamoncloa.gob.es/consejodeministros/referencias/

Cómo funciona
-------------
1. El listado de referencias se filtra por mes/año mediante un postback ASP.NET
   (formulario SummarySearchByDate). Recorremos el rango de meses configurado y
   recogemos las URL de cada Consejo (los slugs y formatos de fecha varían).
2. Descargamos cada referencia (con caché local en /tmp/cm_cache) y extraemos:
   - la sección "Asuntos Exteriores, Unión Europea y Cooperación" (agenda + detalle),
   - cualquier acuerdo, en cualquier sección, que mencione cooperación/ayuda y euros.
3. De cada acuerdo extraemos: fecha, título, texto, importe(s) en euros, instrumento
   (AECID/FONPRODE/Humanitaria/Multilateral/Deuda/Otros) y país receptor (si se cita).

Salida: webapp/data/consejo_ministros_real.json

Uso:
    python3 scripts/scrape_consejo_ministros.py [AAAA-MM_inicio] [AAAA-MM_fin]
    (por defecto: 2024-01 .. mes actual)
"""

import os, re, sys, json, time, html, datetime
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "webapp", "data", "consejo_ministros_real.json")
CACHE = "/tmp/cm_cache"
BASE = "https://www.lamoncloa.gob.es/consejodeministros/referencias/Paginas/index.aspx"
PFX = "ctl00$PlaceHolderMain$DisplayMode$sumarioPaginado$SummarySearchByDate$EditModePanel$"
UA = {"User-Agent": "Mozilla/5.0 (compatible; aid-tracker/1.0; research)"}

# ---------------------------------------------------------------------------
# Países receptores típicos de la cooperación española (nombre -> ISO3)
# ---------------------------------------------------------------------------
PAISES = {
    "Colombia":"COL","Perú":"PER","Peru":"PER","Bolivia":"BOL","Ecuador":"ECU",
    "Honduras":"HND","Guatemala":"GTM","El Salvador":"SLV","Nicaragua":"NIC",
    "República Dominicana":"DOM","Paraguay":"PRY","Cuba":"CUB","Venezuela":"VEN",
    "Haití":"HTI","Haiti":"HTI","Uruguay":"URY","México":"MEX","Mexico":"MEX",
    "Marruecos":"MAR","Mauritania":"MRT","Senegal":"SEN","Malí":"MLI","Mali":"MLI",
    "Níger":"NER","Niger":"NER","Etiopía":"ETH","Etiopia":"ETH","Mozambique":"MOZ",
    "Guinea Ecuatorial":"GNQ","Nigeria":"NGA","Cabo Verde":"CPV","Argelia":"DZA",
    "Túnez":"TUN","Tunez":"TUN","Egipto":"EGY","Angola":"AGO","Camerún":"CMR",
    "Territorios Palestinos":"PSE","Palestina":"PSE","Palestinos":"PSE",
    "Jordania":"JOR","Líbano":"LBN","Libano":"LBN","Siria":"SYR","Irak":"IRQ",
    "Yemen":"YEM","Ucrania":"UKR","Filipinas":"PHL","Afganistán":"AFG",
    "Afganistan":"AFG","Sudán":"SDN","Sudan":"SDN","Somalia":"SOM","Chad":"TCD",
    "Burkina Faso":"BFA","Gambia":"GMB","Guinea":"GIN","saharaui":"DZA",
}

# ---------------------------------------------------------------------------
def session():
    s = requests.Session(); s.headers.update(UA); return s

def hidden(name, txt):
    m = re.search(r'id="%s"[^>]*value="([^"]*)"' % re.escape(name), txt)
    return m.group(1) if m else ""

def list_month(s, month, year):
    """Devuelve las URLs de referencias de un mes/año vía postback."""
    t = s.get(BASE, timeout=30).text
    data = {
        "__EVENTTARGET": "", "__EVENTARGUMENT": "",
        "__VIEWSTATE": hidden("__VIEWSTATE", t),
        "__VIEWSTATEGENERATOR": hidden("__VIEWSTATEGENERATOR", t),
        "__EVENTVALIDATION": hidden("__EVENTVALIDATION", t),
        PFX + "ddlMonth": str(month), PFX + "ddlYear": str(year),
        PFX + "btnSearch": "Buscar",
    }
    r = s.post(BASE, data=data, timeout=30)
    return sorted(set(re.findall(
        r'/consejodeministros/referencias/Paginas/[0-9]{4}/[0-9A-Za-z-]+\.aspx', r.text)))

def fetch(s, path):
    """Descarga una referencia con caché local."""
    os.makedirs(CACHE, exist_ok=True)
    key = os.path.join(CACHE, path.strip("/").replace("/", "_"))
    if os.path.exists(key) and os.path.getsize(key) > 1000:
        return open(key, encoding="utf-8", errors="replace").read()
    url = "https://www.lamoncloa.gob.es" + path
    for attempt in range(3):
        try:
            r = s.get(url, timeout=40)
            if r.status_code == 200 and len(r.text) > 1000:
                open(key, "w", encoding="utf-8").write(r.text)
                return r.text
        except requests.RequestException:
            pass
        time.sleep(2 * (attempt + 1))
    return ""

def clean(s):
    s = re.sub(r'(?is)<[^>]+>', ' ', s)
    s = html.unescape(s)
    return re.sub(r'\s+', ' ', s).strip()

def fecha_from_path(path):
    """Extrae la fecha del slug. Formatos vistos: YYYYMMDD-, DDMMYYYY-, refcYYYYMMDD,
    YYMMDD- (bajo carpeta /AAAA/)."""
    mfold = re.search(r'/(\d{4})/', path)
    folder = mfold.group(1) if mfold else None
    fname = path.rsplit("/", 1)[-1]
    digits = re.search(r'(\d{6,8})', fname)
    if not digits:
        return None
    d = digits.group(1)
    if len(d) == 8:
        if d[:4] in ("20", "19") or d[:4] == folder or d[:2] == "20":
            return f"{d[:4]}-{d[4:6]}-{d[6:8]}"        # YYYYMMDD
        return f"{d[4:8]}-{d[2:4]}-{d[0:2]}"            # DDMMYYYY
    if len(d) == 6:                                     # YYMMDD
        return f"20{d[:2]}-{d[2:4]}-{d[4:6]}"
    return None

EUR_RE = re.compile(
    r'([0-9]{1,3}(?:\.[0-9]{3})*(?:,[0-9]+)?|[0-9]+(?:,[0-9]+)?)\s*(millones?|mill\.)?\s*(?:de\s+)?euros',
    re.I)

def parse_eur(text):
    """Devuelve la lista de importes en euros encontrados en el texto."""
    out = []
    for m in EUR_RE.finditer(text):
        num = m.group(1).replace(".", "").replace(",", ".")
        try:
            v = float(num)
        except ValueError:
            continue
        if m.group(2):  # "millones"
            v *= 1_000_000
        out.append(round(v))
    return out

# --- Señales FUERTES y específicas de ayuda exterior / cooperación ---
# Solo se acepta un acuerdo si su propio texto casa con alguna de estas (evita arrastrar
# defensa, hidrógeno, líneas ICO, educación, etc. de otras secciones del Consejo).
STRONG_KW = re.compile(
    r'\bAECID\b'
    r'|\bFONPRODE\b'
    r'|ayuda humanitaria|acci[oó]n humanitaria|crisis humanitaria|emergencia humanitaria'
    r'|cooperaci[oó]n (?:internacional |espa[ñn]ola )?(?:al |para el )?desarrollo'
    r'|cooperaci[oó]n al desarrollo'
    r'|(?:contribuci[oó]n|aportaci[oó]n|cuota)[^.]{0,80}'
      r'(?:Naciones Unidas|Programa Mundial de Alimentos|\bPMA\b|ACNUR|UNICEF|UNRWA|'
      r'\bOMS\b|\bOIM\b|Cruz Roja|fondo fiduciario|fiduciario|Fondo Verde|'
      r'Banco (?:Mundial|Africano|Interamericano)|organismo[s]? internacional)'
    r'|(?:condonaci[oó]n|conversi[oó]n|alivio|reestructuraci[oó]n) de (?:la )?deuda'
    r'|Fondo para la Promoci[oó]n del Desarrollo'
    r'|Fondo Verde para el Clima'
    r'|ayuda oficial al desarrollo|\bAOD\b',
    re.I)

# Excluir títulos que NO son ayuda (nombramientos, tratados, declaraciones, bios…)
EXCLUDE_KW = re.compile(
    r'^\s*(?:ACUERDO por el que se (?:designa|nombra)|Embajador|Embajada|'
    r'Tratado|Convenci[oó]n sobre|credenciales|c[oó]nsul|nombramiento|cese|toma de razón|'
    r'D\.?ª?\.?\s+[A-ZÁÉÍÓÚ]|Do[ñn]a?\s+[A-Z]|DECLARACI[OÓ]N INSTITUCIONAL)',
    re.I)

# Señal de "es un acuerdo de ayuda" presente en el propio TÍTULO (para conservar
# acuerdos sin importe explícito, p.ej. marcos de asociación país-España).
TITLE_AID = re.compile(
    r'\bAECID\b|\bFONPRODE\b|contribuci[oó]n|aportaci[oó]n|ayuda humanitaria|'
    r'acci[oó]n humanitaria|cooperaci[oó]n|marco de asociaci[oó]n|fondo|deuda|desarrollo',
    re.I)

# Excluir el Fondo de la asignación tributaria (IRPF "interés social"): gasto social
# interno, no ayuda exterior, aunque mencione cooperación al desarrollo.
EXCLUDE_BLOB = re.compile(
    r'asignaci[oó]n tributaria|actividades de inter[eé]s social|fondo de contingencia|'
    r'metrolog[ií]a|Comit[eé] Federal|\bPSOE\b|licenciad[oa] en|nacid[oa] en (?:el a[ñn]o|19|20)',
    re.I)

# Para acuerdos SIN importe: solo se conservan si el título es inequívocamente de ayuda.
STRICT_TITLE_AID = re.compile(
    r'\bAECID\b|\bFONPRODE\b|marco de asociaci[oó]n|ayuda humanitaria|acci[oó]n humanitaria|'
    r'contribuci[oó]n (?:voluntaria|de Espa[ñn]a|al )|cooperaci[oó]n (?:al |para el )?desarrollo',
    re.I)

# Cabeceras de ministerio que a veces quedan como "título" de un bloque: descartarlas.
MINISTRY_HEAD = re.compile(
    r'^(Asuntos Exteriores|Hacienda|Industria|Presidencia|Trabajo|Educaci[oó]n|'
    r'Para la Transformaci[oó]n|Defensa|Interior|Justicia|Sanidad|Agricultura|'
    r'Transportes|Cultura|Ciencia|Inclusi[oó]n|Derechos Sociales|Pol[ií]tica Territorial|'
    r'Econom[ií]a|Vivienda|Juventud|Igualdad)\b', re.I)

# Keep para clasificación (mantiene compatibilidad)
AID_KW = STRONG_KW

def instrumento(text):
    t = text.lower()
    if re.search(r'(condonaci|conversi|alivio|reestructuraci)[^.]{0,30}deuda', t): return "Deuda"
    if "fonprode" in t or "fondo para la promoción del desarrollo" in t: return "FONPRODE"
    if "aecid" in t or "agencia española de cooperación" in t: return "AECID"
    if "ayuda humanitaria" in t or "acción humanitaria" in t or "emergencia humanitaria" in t:
        return "Humanitaria"
    if any(k in t for k in ["contribuci", "aportaci", "cuota", "pma", "programa mundial",
                            "acnur", "unicef", "unrwa", "fondo verde", "fiduciario",
                            "organismo internacional", "naciones unidas", "banco mundial",
                            "banco africano", "banco interamericano", "oms", "oim", "fnuap"]):
        return "Multilateral"
    if "marco de asociaci" in t: return "Marco país"
    return "Cooperación"

def match_pais(text):
    for nombre, iso in PAISES.items():
        if re.search(r'\b' + re.escape(nombre) + r'\b', text):
            return iso, nombre
    return None, None

# Términos INEQUÍVOCOS de ayuda exterior: válidos aunque el acuerdo aparezca en la
# sección de OTRO ministerio (Hacienda, Economía…). Deben aparecer en el TÍTULO, no
# en el detalle (en el detalle, palabras como "cooperación" o "humanitaria" aparecen
# también en asuntos internos: empleo, salvamento marítimo, economía circular…).
NARROW_KW = re.compile(
    r'\bAECID\b|\bFONPRODE\b|\bUNRWA\b|\bACNUR\b|\bUNICEF\b|\bFIDA\b|\bFNUAP\b|'
    r'Programa Mundial de Alimentos|marco de asociaci[oó]n para el desarrollo|'
    r'cooperaci[oó]n internacional para el desarrollo',
    re.I)

def _units(body):
    """Extrae unidades (título, detalle) de un fragmento HTML: bloques h4 y li."""
    out = []
    for tm, dm in re.findall(r'(?is)<h4[^>]*>(.*?)</h4>(.*?)(?=<h4|<h3|$)', body):
        out.append((clean(tm), clean(dm)))
    for li in re.findall(r'(?is)<li[^>]*>(.*?)</li>', body):
        t = clean(li)
        if 15 <= len(t) <= 300:
            out.append((t, ""))
    return out

def extract_items(htmltext, fecha, path):
    """Extrae acuerdos de cooperación/ayuda exterior de una referencia.

    Estrategia en dos niveles para evitar arrastrar asuntos internos (deuda de las
    CC.AA., empleo, salvamento marítimo, economía circular…):
      1) Dentro de la sección "Asuntos Exteriores, Unión Europea y Cooperación" se
         acepta cualquier unidad con señal FUERTE de ayuda (STRONG_KW).
      2) Fuera de esa sección, solo se aceptan unidades con términos INEQUÍVOCOS
         (NARROW_KW: AECID, FONPRODE, UNRWA, ayuda humanitaria, marco de asociación…).
    """
    raw = re.sub(r'(?is)<script.*?</script>', '', htmltext)
    raw = re.sub(r'(?is)<style.*?</style>', '', raw)
    items, seen = [], set()

    candidatos = []  # (titulo, detalle, en_maec)
    parts = re.split(r'(?is)<h3[^>]*>(.*?)</h3>', raw)
    # parts: [pre, head1, body1, head2, body2, ...]; 'pre' no tiene cabecera -> no MAEC
    bloques = [("", parts[0])] if parts else []
    for i in range(1, len(parts), 2):
        bloques.append((clean(parts[i]), parts[i + 1] if i + 1 < len(parts) else ""))
    for head, body in bloques:
        en_maec = ("Exteriores" in head) or ("Cooperaci" in head)
        for t, d in _units(body):
            candidatos.append((t, d, en_maec))

    for title, detail, en_maec in candidatos:
        blob = (title + " " + detail).strip()
        if not blob:
            continue
        # Si el "título" es en realidad la cabecera del ministerio, derivar uno real
        # de la primera frase del detalle; si no hay detalle, descartar.
        if MINISTRY_HEAD.match(title):
            if not detail:
                continue
            title = re.split(r'(?<=[a-z0-9)])\.\s', detail, 1)[0][:160]
        if EXCLUDE_KW.search(title):         # nombramientos, tratados, bios, declaraciones
            continue
        if EXCLUDE_BLOB.search(blob):        # fondo IRPF / asuntos internos colados
            continue
        # Dentro de Exteriores -> señal fuerte; fuera -> solo términos inequívocos.
        if en_maec:
            if not STRONG_KW.search(blob):
                continue
        else:
            # Fuera de Exteriores: el término inequívoco debe estar en el TÍTULO.
            if not NARROW_KW.search(title):
                continue
        euros = parse_eur(blob)
        # acuerdos sin importe: conservar solo si el TÍTULO es inequívocamente de ayuda
        if not euros and not STRICT_TITLE_AID.search(title):
            continue
        add_item(items, seen, fecha, path, title, detail, blob)

    # Dedupe: un mismo acuerdo aparece como título de agenda y como bloque detallado.
    # Agrupamos por (fecha, instrumento, importe) y nos quedamos con el más informativo.
    dedup = {}
    for it in items:
        k = (it["fecha"], it["instrumento"], it["eur"], it["iso"])
        cur = dedup.get(k)
        if cur is None or _score_item(it) > _score_item(cur):
            dedup[k] = it
    return list(dedup.values())

def _score_item(it):
    """Cuanto mayor, más informativo (tiene detalle, país y título largo)."""
    return (1 if it["detalle"] else 0) * 1000 + (1 if it["iso"] else 0) * 500 + len(it["titulo"])

def add_item(items, seen, fecha, path, title, detail, blob):
    key = (fecha, title[:90])
    if key in seen:
        return
    seen.add(key)
    euros = parse_eur(blob)
    # País: priorizar título y comienzo del detalle (evita arrastrar países citados
    # de pasada al final de un texto largo).
    iso, nombre = match_pais(title + " " + detail[:220])
    items.append({
        "fecha": fecha,
        "instrumento": instrumento(blob),
        "titulo": title[:300],
        "detalle": detail[:600],
        "eur": max(euros) if euros else None,
        "eur_todos": euros,
        "iso": iso,
        "pais": nombre,
        "url": "https://www.lamoncloa.gob.es" + path,
    })

# ---------------------------------------------------------------------------
def main():
    today = datetime.date.today()
    ini = sys.argv[1] if len(sys.argv) > 1 else "2024-01"
    fin = sys.argv[2] if len(sys.argv) > 2 else f"{today.year:04d}-{today.month:02d}"
    y0, m0 = map(int, ini.split("-")); y1, m1 = map(int, fin.split("-"))

    s = session()
    meses = []
    y, m = y0, m0
    while (y, m) <= (y1, m1):
        meses.append((y, m))
        m += 1
        if m > 12: m = 1; y += 1

    all_paths = []
    for (y, m) in meses:
        try:
            L = list_month(s, m, y)
        except requests.RequestException as e:
            print(f"  !! {y}-{m:02d}: {e}"); continue
        print(f"  {y}-{m:02d}: {len(L)} referencias")
        all_paths += L
        time.sleep(0.4)
    all_paths = sorted(set(all_paths))
    print(f"\nTotal referencias: {len(all_paths)}")

    items = []
    n_con_cifra = 0
    for p in all_paths:
        fecha = fecha_from_path(p)
        htmltext = fetch(s, p)
        if not htmltext:
            print(f"  !! no descargada: {p}"); continue
        it = extract_items(htmltext, fecha, p)
        items += it
        time.sleep(0.15)
    items.sort(key=lambda x: (x["fecha"] or "", x["titulo"]))
    n_con_cifra = sum(1 for x in items if x["eur"])

    # resumen por instrumento y por país
    por_inst, por_pais = {}, {}
    total_eur = 0
    for x in items:
        por_inst[x["instrumento"]] = por_inst.get(x["instrumento"], 0) + (x["eur"] or 0)
        if x["iso"]:
            por_pais[x["iso"]] = por_pais.get(x["iso"], 0) + (x["eur"] or 0)
        total_eur += (x["eur"] or 0)

    obj = {
        "fuente": "La Moncloa — Consejo de Ministros (referencias)",
        "url_fuente": "https://www.lamoncloa.gob.es/consejodeministros/referencias/",
        "descargado": datetime.datetime.now().isoformat(timespec="seconds"),
        "rango": {"desde": ini, "hasta": fin},
        "n_referencias": len(all_paths),
        "n_acuerdos": len(items),
        "n_acuerdos_con_importe": n_con_cifra,
        "total_eur_identificado": total_eur,
        "por_instrumento": por_inst,
        "por_pais": por_pais,
        "acuerdos": items,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(obj, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\nEscrito {OUT}")
    print(f"  acuerdos cooperación: {len(items)}  (con importe: {n_con_cifra})")
    print(f"  total € identificado: {total_eur:,.0f}")
    print(f"  por instrumento: {por_inst}")

if __name__ == "__main__":
    main()
