# 🇪🇸 ¿A dónde va la ayuda exterior de España? — web app

App web estática que muestra **a dónde va el dinero de la Ayuda Oficial al Desarrollo (AOD)
española**, lo **cojeta con los acuerdos del Consejo de Ministros** (los martes), pinta los
**euros sobre un mapa**, desglosa el gasto en **categorías** y asigna a cada destino una
**probabilidad estimada de corrupción** (indicador de vulnerabilidad).

### ▶️ Abrir
- **Online (GitHub Pages):** se publica automáticamente desde `webapp/` en cada push
  (workflow `.github/workflows/pages.yml`). URL del proyecto:
  **https://insa-jaume.github.io/Insa-iphone-15/**
- **Sin servidor (un solo archivo):** abre con doble clic `webapp/dist/index_standalone.html`
  (CSS + JS + datos + mapamundi embebidos, funciona offline).
- **Local:**
  ```bash
  cd webapp && python3 -m http.server 8000   # http://localhost:8000
  ```

El front-end no tiene build ni dependencias: HTML + CSS + JavaScript vanilla. El mapa se
renderiza en **SVG puro** (proyección equirectangular) sobre un GeoJSON mundial vendorizado,
sin servidores de tiles ni librerías externas.

### Qué incluye — DATOS REALES, 5 años (2020–2024)
- **📅 Selector de año** 2020–2024 (2024 preliminar).
- **🗺️ Mapa del dinero** — una burbuja por país receptor: tamaño = euros reales recibidos
  (AOD bilateral), color = riesgo de corrupción (100 − CPI del país).
- **📊 Categorías / sectores** — salud, educación, gobierno y sociedad civil, agua,
  multisectorial, humanitaria… con importes reales por año.
- **🌐 Contribuciones multilaterales** — UE, sistema ONU, Banco Mundial, bancos regionales,
  Fondo Verde del Clima… con importes reales.
- **🏛️ Consejo de Ministros (martes)** — 77 acuerdos reales de cooperación extraídos de
  [La Moncloa](https://www.lamoncloa.gob.es/consejodeministros/referencias/) (cada fila enlaza a su referencia).
- **🚨 Casos reales de fraude / control** — Tribunal de Cuentas, AIReF (FONPRODE, AECID…).
- **🧮 Riesgo de corrupción** = `100 − CPI` (Transparency International). Indicador de
  vulnerabilidad de gobernanza, **no una acusación**.

### Procedencia de los datos
Recopilados por un **operativo de 30 agentes de investigación** (5 años × 6 dimensiones)
desde fuentes oficiales — **DGPOLDES** (“Seguimiento de la AOD/TOSSD”, “Cooperación
Multilateral”), **Info@OD**, **OCDE-CAD** (DAC1/DAC2a vía API SDMX), **AECID**,
**Coordinadora de ONGD**, **La Moncloa** y **Transparency International** (CPI) — consolidados
por **5 agentes extractores** y verificados por un **agente jefe** (veredicto: APTO).
La investigación bruta queda en `scripts/aod_research_raw/` para trazabilidad.

> ⚠️ Cifras reales de fuentes oficiales. Algunas de **2024 son preliminares** (avance CAD,
> abril 2025) y, cuando solo había dato de la OCDE en USD, se convirtió a EUR (anotado en la
> procedencia). Detalle en [`webapp/METODOLOGIA.md`](webapp/METODOLOGIA.md).

```
webapp/
  index.html · css/styles.css · js/map.js · js/app.js
  data/aod_real.json                  # AOD real por año: países, sectores, multilateral, CPI, casos
  data/consejo_ministros_real.json    # 77 acuerdos reales del Consejo de Ministros
  data/world-countries.geo.json       # mapamundi vendorizado
  dist/index_standalone.html          # la app en un solo archivo (offline)
  METODOLOGIA.md
scripts/
  build_aod_real.py + coords.py       # ensambla aod_real.json desde la investigación
  scrape_consejo_ministros.py         # scraping de La Moncloa
  build_standalone.py                 # empaqueta la app en un archivo
  aod_research_raw/                   # procedencia: salidas brutas de los agentes
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
