# 🇪🇸 ¿A dónde va la ayuda exterior de España? — web app

App web estática que muestra **a dónde va el dinero de la Ayuda Oficial al Desarrollo (AOD)
española**, lo **cojeta con los acuerdos del Consejo de Ministros** (los martes), pinta los
**euros sobre un mapa**, desglosa el gasto en **categorías** y asigna a cada destino una
**probabilidad estimada de corrupción** (indicador de vulnerabilidad).

### ▶️ Abrir
```bash
python3 scripts/build_aid_data.py            # genera webapp/data/*.json
cd webapp && python3 -m http.server 8000     # http://localhost:8000
```
Sin build ni dependencias: HTML + CSS + JavaScript vanilla. El mapa se renderiza en **SVG
puro** (proyección equirectangular) sobre un GeoJSON mundial vendorizado, sin servidores de
tiles ni librerías externas.

### Qué incluye
- **🗺️ Mapa del dinero** — una burbuja por país: tamaño = euros, color = riesgo de corrupción.
- **📊 Categorías de gasto** — humanitaria, salud, agua, gobernanza, multilateral, deuda…
- **🏛️ Cotejo con el Consejo de Ministros** — cada acuerdo (FONPRODE/AECID/humanitaria/deuda)
  marcado como *coincide · parcial · sin rastro* frente al desembolso.
- **🧮 Riesgo de corrupción** — `0,50·(100−CPI) + 0,30·modalidad + 0,20·canal`. Es un
  **indicador de vulnerabilidad**, no una acusación. Detalle en
  [`webapp/METODOLOGIA.md`](webapp/METODOLOGIA.md).

> ⚠️ **Cifras ilustrativas** que reproducen patrones públicos de la AOD española (no es la
> contabilidad oficial exacta). Fuentes para datos reales — Info@OD/DGPOLDES, AECID,
> OCDE-CAD, La Moncloa (Consejo de Ministros), Transparency International (CPI) — en la
> metodología.

```
webapp/
  index.html              # la app
  css/styles.css
  js/map.js               # mapa SVG (proyección + render de países)
  js/app.js               # carga de datos, KPIs, detalle, categorías, tabla del Consejo
  data/aid.json           # destinos, importes, sectores y riesgo (generado)
  data/categories.json    # totales por sector (generado)
  data/consejo_ministros.json  # acuerdos cotejados (generado)
  data/world-countries.geo.json # mapamundi vendorizado
  METODOLOGIA.md          # modelo de riesgo, cotejo y fuentes
scripts/build_aid_data.py # genera los datos + calcula el riesgo (reproducible)
```

---

# Which Big Company Becomes the *Tyrell Corporation*? — a real-people study

A study of the **12 largest tech/energy companies** (10 largest public by market cap +
private **OpenAI** and **SpaceX**), profiling **788 real, individually-sourced people**
— founders, executives, board members, distinguished engineers, and named researchers —
across **6 metrics**, then predicting which company is most likely to become the **globally
dominant megacorporation** (the "Tyrell Corporation" — meaning *dominant*).

### 🏆 Answer: **NVIDIA** — Tyrell Index **89.0 / 100**, ahead of Alphabet (82.0) and Apple (80.6).

> ✅ **Real people, two tiers.** All 788 are genuine, publicly-documented individuals (SEC
> proxies, official pages, Wikipedia, arXiv paper bylines, press). **216 "core"** leaders are
> deeply profiled with per-biography character scores; **572 "extended"** VPs/engineers/
> researchers are scored by a consistent role rubric (`data_tier` column marks which). The
> three character metrics are **interpretive**, not psychometric measurements. **Disclosed
> compensation** (41 named executive officers) is real. No invented people; no scraping of
> private individuals. Per-company counts range 34–116 — I did not fabricate to hit a target.

## 📑 Start here → [reports/REPORT.md](reports/REPORT.md)

Full report: the 12 companies, the 6 metrics + rubric, summary tables, charts, the
**Tyrell Index** verdict, and conclusions. Sourcing appendix: **[reports/PROFILES.md](reports/PROFILES.md)**.

## The 6 metrics
**Facts:** role/seniority · disclosed compensation (NEOs only) · origin & tenure.
**Character (from documented bios):** potential · adversity-of-origin · mental strength.

## What the real data shows
- **Big Tech runs on immigrants** — 34.5% of all known-origin people; in the technical
  ranks it's far higher (Alphabet 65%, Microsoft 57%, Tesla 55%, Meta 51%, NVIDIA 46%).
  Nearly every founder/CEO is an immigrant (Huang, Nadella, Pichai, Musk, Tan, Chang).
  Least immigrant: Aramco 12% (national champion), SpaceX 18% (ITAR/export control).
- **The self-made story is real and concentrated at the top** — Huang (bathroom-cleaning
  immigrant), Cook (working-class Alabama), Brin (Soviet refugee), Tan (Penang
  scholarship), Ursula Burns (housing project), Rafael Reif (refugee family).
- **Real pay is wildly unequal** — Hock Tan $205.3M, Nadella $96.5M, Cook $74.6M; yet
  founders take little cash (Musk $0, Bezos $1.68M). Private firms/Aramco disclose nothing.
- **Verdict is robust** — in a world where compute is power, the company that owns the
  compute (**NVIDIA**) becomes Tyrell.

## Layout
```
data/
  companies.csv                  # the 12 companies (real; 10 public + 2 private)
  all_people.csv                 # 788 real people, 6 metrics  ← the dataset
  all_people_core.csv            # the 216 deeply-profiled "core" people
  people_raw/01..12_*.csv        # extended rosters as gathered (with extra bio facts)
  people/01_nvidia.csv … 12_openai.csv   # final split per company
  company_people_summary.csv, origin_region_breakdown.csv, tyrell_index.csv, headline_stats.json
scripts/
  merge_people.py                # core + people_raw -> all_people.csv (dedupe + role-score)
  analyze_people.py              # summaries, origin breakdown, Tyrell Index, charts
reports/
  REPORT.md                      # ← the deliverable
  PROFILES.md                    # sourcing & methodology appendix (core people)
  figures/*.png
```

## Reproduce
```bash
pip install numpy pandas matplotlib
python3 scripts/merge_people.py
python3 scripts/analyze_people.py
```
