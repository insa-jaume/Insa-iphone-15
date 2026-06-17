# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A **data-analysis study**, not an application. It profiles **788 real, individually-sourced
people** (founders, executives, board members, distinguished engineers, named researchers)
across the **12 largest tech/energy companies**, scores them on 6 metrics, and computes a
**"Tyrell Index"** predicting which company is most likely to become the globally dominant
megacorporation. The deliverable is the prose report in `reports/REPORT.md`; everything else
(scripts, CSVs, figures) exists to produce and support it.

## Commands

```bash
pip install numpy pandas matplotlib   # only dependencies

python3 scripts/merge_people.py       # step 1: build data/all_people.csv
python3 scripts/analyze_people.py     # step 2: summaries, Tyrell Index, charts
```

There are no tests, linters, or build steps. **The two scripts must run in order** —
`analyze_people.py` reads `data/all_people.csv`, which `merge_people.py` produces.

## Data pipeline (read this before editing data or scripts)

The dataset has **two tiers**, tracked by the `data_tier` column in every people CSV:

- **core** (216): top leadership/board, deeply profiled. Character scores are
  **hand-assigned per individual biography**. The canonical source of truth is
  `data/all_people_core.csv` (a one-time snapshot of the original `all_people.csv`).
- **extended** (572): additional VPs/fellows/engineers/researchers gathered into
  `data/people_raw/<NN>_<slug>.csv`. Character scores are assigned by a **consistent
  role-based rubric** (the `role_of` / `POTENTIAL` / `MENTAL_BASE` / `score` functions in
  `merge_people.py`), not per-person judgement. Extended rows have blank compensation.

Flow:
```
data/all_people_core.csv  +  data/people_raw/*.csv
        └────── merge_people.py (dedupe by company+name, role-score extended) ──────┐
                                                                                     ▼
                                                                       data/all_people.csv   ← the dataset
                                                                                     │
                                                            analyze_people.py        ▼
   data/people/<NN>_<slug>.csv (per-company split) · company_people_summary.csv ·
   origin_region_breakdown.csv · tyrell_index.csv · headline_stats.json · reports/figures/*.png
```

Key consequences:
- **`data/all_people.csv` is generated** — do not hand-edit it. To change core people, edit
  `data/all_people_core.csv`; to change extended people, edit the relevant
  `data/people_raw/` file. Then re-run both scripts.
- `merge_people.py` is **re-runnable and idempotent**: it preserves the core snapshot on
  first run and rebuilds `all_people.csv` from core + raw each time.
- `data/people/*.csv` are also generated (by `analyze_people.py`); don't edit them directly.

## The 6 metrics and the Tyrell Index

- **Factual** (real, sourced): role/seniority, disclosed compensation (NEOs only — see SEC
  proxies), origin & tenure.
- **Character** (`potential_index`, `mental_strength`, `adversity_origin_score`):
  **interpretive** assessments from documented public biographies via one rubric — *not*
  psychometric measurements. Always preserve this framing in any prose or comments.
- **Tyrell Index** (`analyze_people.py`, section 4): weighted blend of `dominance` (market
  cap relative to the largest company), a hand-set `STRATEGIC_MOAT` dict, and the three
  character pillars. Weights live in the `WEIGHTS` dict. Changing weights, moat values, or
  scaling changes the verdict — update the conclusions in `reports/REPORT.md` to match.

## Conventions

- Companies are keyed by their full `company` string (e.g. `"Alphabet (Google)"`); the
  `short` dict in `analyze_people.py` maps to display labels. Company ordering everywhere
  follows the `rank` order in `data/companies.csv`.
- Per-company file slugs are derived as `<rank:02d>_<name-lowercased-no-spaces>` — keep
  `FILE_COMPANY` in `merge_people.py` and the slug logic in `analyze_people.py` consistent.
- New origin countries must be added to the `REGION` map in `merge_people.py`, or they fall
  through to `"Other"`.
- Charts use `matplotlib` with the `Agg` backend (headless); all figures write to
  `reports/figures/`.

## Integrity rules (this project's whole premise)

The study's credibility rests on **no fabricated people and no invented facts**. When adding
or editing roster data: use only genuine, publicly-documented individuals with real
sourcing; never scrape or invent private individuals; keep disclosed compensation limited to
real NEO figures; and preserve the `data_tier` distinction so hand-scored and rubric-scored
people stay separable. Document core-person sourcing in `reports/PROFILES.md`.
