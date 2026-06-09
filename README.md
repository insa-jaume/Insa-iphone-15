# Which Big-Tech Giant Becomes the *Tyrell Corporation*?

A study of the **10 largest public companies by market cap** (June 2026) that models
**1,000 key employees each** (10,000 total) across **6 metrics** — then predicts which
company is most likely to become the **globally dominant megacorporation** (the
"Tyrell Corporation" of our universe — meaning *dominant*, not robot-building).

### 🏆 Answer: **NVIDIA** — Tyrell Index **91.9 / 100**, ahead of Alphabet (73.3) and Apple (66.4).

> ⚠️ **Data honesty.** The *company list* is real and sourced. The *per-employee data
> is synthetic* — no public dataset of any company's "1,000 most important employees"
> with personal performance, pay, **potential, origins, or mental strength** exists
> (and character/origins are unmeasurable anyway). The data is generated from
> distributions **calibrated to public, company-level characteristics**, so it is
> realistic in shape but is **not** about real individuals. Fully reproducible. See
> the report for full provenance.

## 📑 Start here → [reports/REPORT.md](reports/REPORT.md)

The full report: objective, the 6 metrics, comparison tables, 12 charts, the **Tyrell
Index** verdict with reasoning and sensitivity, and cross-company conclusions.

## The 6 metrics

**Performance:** performance score · total compensation · tenure.
**Character (deep):** **potential** (growth ceiling) · **adversity-of-origin** (where
they come from, quantified) · **mental strength** (resilience/grit).

## The Tyrell Index

Five pillars → one 0–100 score predicting durable global dominance:
**dominance now** (market cap, 0.34) · **strategic moat** (control of a global
chokepoint, 0.34) · **workforce potential** (0.14) · **mental strength** (0.10) ·
**builder origins** (0.08). NVIDIA wins by topping the two heavyweight pillars at once
— biggest company *and* owner of the AI-compute chokepoint.

## Layout

```
data/
  companies.csv                  # the 10 companies (REAL, sourced)
  employees/01_nvidia.csv … 10_meta.csv   # 1,000 employees each (synthetic, 6 metrics)
  all_employees.csv              # combined 10,000-row table
  company_metrics_summary.csv    # per-company aggregates
  origin_region_breakdown.csv    # "where they come from" by company
  tyrell_index.csv               # the dominance ranking
  headline_stats.json            # correlations + headline numbers
scripts/
  generate_data.py               # builds the dataset (seed 20260609)
  analyze.py                     # aggregates, correlations, Tyrell Index, charts
reports/
  REPORT.md                      # ← the deliverable
  figures/*.png                  # 12 charts
```

## Reproduce

```bash
pip install numpy pandas matplotlib
python3 scripts/generate_data.py
python3 scripts/analyze.py
```
