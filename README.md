# Which Big Company Becomes the *Tyrell Corporation*? — a real-people study

A study of the **12 largest tech/energy companies** (10 largest public by market cap +
private **OpenAI** and **SpaceX**), profiling **216 real, individually-sourced leaders**
— founders, executives, board members, and marquee technical leaders — across **6
metrics**, then predicting which company is most likely to become the **globally
dominant megacorporation** (the "Tyrell Corporation" — meaning *dominant*).

### 🏆 Answer: **NVIDIA** — Tyrell Index **88.7 / 100**, ahead of Alphabet (82.6) and Apple (81.0).

> ✅ **This version is real.** Names, titles, origins, careers and **disclosed executive
> compensation** are genuine and individually sourced (SEC proxies, official pages,
> Wikipedia, press — see `reports/PROFILES.md`). The three **character** metrics
> (potential, mental strength, adversity-of-origin) are **interpretive assessments
> derived from each person's documented public biography** via one consistent rubric —
> not psychometric measurements. No invented people, no scraped private individuals.

## 📑 Start here → [reports/REPORT.md](reports/REPORT.md)

Full report: the 12 companies, the 6 metrics + rubric, summary tables, charts, the
**Tyrell Index** verdict, and conclusions. Sourcing appendix: **[reports/PROFILES.md](reports/PROFILES.md)**.

## The 6 metrics
**Facts:** role/seniority · disclosed compensation (NEOs only) · origin & tenure.
**Character (from documented bios):** potential · adversity-of-origin · mental strength.

## What the real data shows
- **Big Tech is run by immigrants** — 28.7% of all documented leaders; the top firms
  are immigrant-founded-or-led (Huang, Nadella, Pichai, Musk, Tan, Morris Chang). Most
  immigrant leaderships: Tesla 55%, Alphabet 48%, OpenAI 46%; least: Aramco 11%.
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
  all_people.csv                 # 216 real people, 6 metrics  ← the dataset
  people/01_nvidia.csv … 12_openai.csv   # split per company
  company_people_summary.csv, origin_region_breakdown.csv, tyrell_index.csv, headline_stats.json
scripts/
  analyze_people.py              # summaries, origin breakdown, Tyrell Index, charts
reports/
  REPORT.md                      # ← the deliverable
  PROFILES.md                    # sourcing & methodology appendix (sources per company)
  figures/*.png
```

## Reproduce
```bash
pip install numpy pandas matplotlib
python3 scripts/analyze_people.py
```
