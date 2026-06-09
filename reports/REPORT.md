# Which of the World's Biggest Companies Becomes the *Tyrell Corporation*?
### A study of **788 real, named people** across the 12 largest tech/energy companies

**Prepared:** 2026-06-09 · **788 real, individually-sourced people** · **12 companies** · 6 metrics

> **Objective.** Predict which company is most likely to become the **Tyrell Corporation**
> of our universe — the **globally dominant megacorporation** the world cannot route
> around (dominant, *not* robot-building). Answered with a transparent **Tyrell Index**
> built from market dominance, strategic moat, and the *character* of each company's real
> people.
>
> ### 🏆 Verdict: **NVIDIA** (Tyrell Index **89.0 / 100**), ahead of Alphabet (82.0) and Apple (80.6).

---

## ⚠️ Read this first — data provenance (REAL people, two tiers)

Every one of the **788 people** is a genuine, publicly-documented individual — founders,
executives, board members, distinguished engineers, and named researchers — gathered from
SEC proxy statements, official company pages, Wikipedia, arXiv paper bylines, and reputable
press. **No invented people; no scraping of private individuals.** The data comes in two tiers:

| Tier | Count | What it is | Character scores |
|------|------:|------------|------------------|
| **Core** | 216 | Top leadership/board + marquee figures, deeply profiled (origin, education, career, documented adversity) | hand-assigned per individual biography |
| **Extended** | 572 | Additional VPs, fellows, distinguished engineers, and named researchers (e.g. paper authors) | assigned by a **consistent role-based rubric** (less granular) |

The `data_tier` column in `data/all_people.csv` marks which is which. Source lists per
company: **`reports/PROFILES.md`** (core) and **`data/people_raw/`** (extended, with each
person's education/prior-company/notable facts).

| Field | Status |
|-------|--------|
| Names, titles, origins, careers | ✅ **Real, sourced** |
| **Total compensation** (41 people) | ✅ **Real** — actual disclosed figures for *named executive officers* |
| The 3 **character** indices | 🟨 **Interpretive** — from documented biography (core) or role rubric (extended); not measurements |
| Strategic-moat scores | 🟨 **Editorial**, from public facts |

**Honest limits.** "100 per company" is the *target*, not a guarantee: the verifiable public
ceiling varies hugely. Research-heavy firms reach it (OpenAI 116, Apple 91, Meta 82, NVIDIA
79); firms that disclose few names land lower (SpaceX 34, Aramco 36, TSMC 37) — and I did
**not** fabricate to hit a quota. Compensation is public only for named executive officers;
everyone else (and the private firms / non-US disclosers) is blank, not guessed.

---

## 1. The 12 companies

| Rank | Company | Country | Ownership | Value ($T) | People documented |
|-----:|---------|---------|-----------|-----------:|------------------:|
| 1 | NVIDIA | 🇺🇸 USA | Public | 5.053 | 79 |
| 2 | Apple | 🇺🇸 USA | Public | 4.428 | 91 |
| 3 | Alphabet (Google) | 🇺🇸 USA | Public | 4.404 | 75 |
| 4 | Microsoft | 🇺🇸 USA | Public | 3.058 | 75 |
| 5 | Amazon | 🇺🇸 USA | Public | 2.637 | 77 |
| 6 | TSMC | 🇹🇼 Taiwan | Public | 2.213 | 37 |
| 7 | Broadcom | 🇺🇸 USA | Public | 1.877 | 41 |
| 8 | Saudi Aramco | 🇸🇦 Saudi Arabia | Public | 1.750 | 36 |
| 9 | Tesla | 🇺🇸 USA | Public | 1.535 | 45 |
| 10 | Meta Platforms | 🇺🇸 USA | Public | 1.485 | 82 |
| 11 | SpaceX 🔒 | 🇺🇸 USA | Private | 1.250 | 34 |
| 12 | OpenAI 🔒 | 🇺🇸 USA | Private | 0.852 | 116 |

Full per-company tables: `data/people/`; combined: `data/all_people.csv` (788 rows).

---

## 2. The six metrics & the character rubric

Three **fact** metrics (role/seniority · disclosed compensation · origin & tenure) + three
**character** metrics (potential · adversity-of-origin · mental strength).

**Character rubric** (core = per-biography within these bands; extended = by role):
- **Adversity-of-origin** — refugee / fled persecution / working-class / housing-project →
  **80–95**; immigrant or first-generation → **60–80**; ordinary professional family →
  **40–55**; privileged/dynastic → **20–35**.
- **Mental strength** — survived a near-death company crisis / public ousting-and-comeback /
  combat veteran → **85–95**; long high-pressure founder/CEO tenure → **78–90**; senior →
  **62–78**.
- **Potential** — iconic founder-CEO / Nobel-Turing-level → **90–100**; division CEO /
  co-founder / top researcher → **78–90**; C-suite → **68–84**; established director → **58–80**.

These are **interpretive assessments of public figures**, not psychometric measurements.

---

## 3. Company summary

| Company | People | % immigrant¹ | % w/ documented adversity | Potential | Mental | Adversity-origin | Median disclosed comp |
|---------|------:|------------:|--------------------------:|----------:|-------:|-----------------:|----------------------:|
| NVIDIA | 79 | 46% | 29% | 76.3 | 75.3 | 56.5 | $21.4M |
| Apple | 91 | 26% | 13% | 77.2 | 74.9 | 49.3 | $27.1M |
| Alphabet | 75 | **65%** | 29% | 78.0 | 75.6 | **58.5** | $38.6M |
| Microsoft | 75 | 57% | 27% | 77.3 | 75.6 | 54.6 | $28.3M |
| Amazon | 77 | 38% | 18% | 77.8 | 75.6 | 53.8 | $25.7M |
| TSMC | 37 | 36% | 14% | 79.3 | 76.0 | 52.2 | $74M* |
| Broadcom | 41 | 40% | 12% | 77.4 | 74.9 | 50.4 | $28.4M |
| Saudi Aramco | 36 | **12%** | 8% | 79.4 | 75.9 | 48.8 | n/d |
| Tesla | 45 | 55% | 20% | 77.5 | 75.5 | 52.5 | $0.4M† |
| Meta | 82 | 51% | 20% | 77.9 | 75.4 | 53.9 | $23.6M |
| SpaceX | 34 | 18% | 18% | 78.5 | **76.5** | 49.5 | n/d (private) |
| OpenAI | 116 | 37% | 14% | 77.6 | 74.8 | 51.3 | n/d (private) |

¹ Immigrant share among people with a *known* origin (many extended researchers' origins
aren't public). \* TSMC: only C.C. Wei's pay is public (~$74M). † Tesla's three NEOs are Musk
($0), Zhu ($376k), Taneja ($139.5M). n/d = not disclosed. Full table:
`data/company_people_summary.csv`.

---

## 4. Visuals

![Tyrell Index](figures/tyrell_index.png)

| | |
|---|---|
| ![Immigrant share](figures/pct_immigrant.png) | ![Adversity of origin](figures/adversity_origin_mean.png) |
| ![Potential](figures/potential_mean.png) | ![Mental strength](figures/mental_mean.png) |

![Origin region mix](figures/origin_region_mix.png)
![Disclosed compensation](figures/disclosed_comp.png)

---

## 5. THE TYRELL INDEX

Pillars: **dominance** (0.34, valuation ÷ largest × 100) · **strategic moat** (0.34) ·
**potential** (0.14) · **mental strength** (0.10) · **builder origins** (0.08). Because every
firm's leadership scores high on character, those pillars bunch tightly — so **dominance and
moat drive the ranking**, exactly right for a *global-dominance* prediction.

| Rank | Company | **Tyrell Index** | Dominance | Moat | Potential | Mental | Builder |
|-----:|---------|----------------:|----------:|-----:|----------:|-------:|--------:|
| **1** | **NVIDIA** | **89.0** | 100.0 | 95 | 76.3 | 75.3 | 56.5 |
| 2 | Alphabet | 82.0 | 87.2 | 86 | 78.0 | 75.6 | 58.5 |
| 3 | Apple | 80.6 | 87.6 | 84 | 77.2 | 74.9 | 49.3 |
| 4 | Microsoft | 72.2 | 60.5 | 85 | 77.3 | 75.6 | 54.6 |
| 5 | Amazon | 68.4 | 52.2 | 82 | 77.8 | 75.6 | 53.8 |
| 6 | TSMC | 68.4 | 43.8 | 90 | 79.3 | 76.0 | 52.2 |
| 7 | SpaceX 🔒 | 60.2 | 24.7 | 86 | 78.5 | 76.5 | 49.5 |
| 8 | OpenAI 🔒 | 58.8 | 16.9 | 90 | 77.6 | 74.8 | 51.3 |
| 9 | Saudi Aramco | 58.2 | 34.6 | 70 | 79.4 | 75.9 | 48.8 |
| 10 | Meta | 57.9 | 29.4 | 74 | 77.9 | 75.4 | 53.9 |
| 11 | Broadcom | 57.4 | 37.1 | 66 | 77.4 | 74.9 | 50.4 |
| 12 | Tesla | 51.6 | 30.4 | 55 | 77.5 | 75.5 | 52.5 |

Full table: `data/tyrell_index.csv`.

### Verdict
**NVIDIA** is the most likely Tyrell Corporation — the only company topping *both*
heavyweight pillars: largest in the study **and** owner of the era's critical chokepoint, AI
compute. **Alphabet** and **Apple** follow on dominance + moat; **OpenAI** and **SpaceX** have
elite people but are held back by smaller (private) valuations — dominance in waiting. The
verdict has held across every version of this study (synthetic → real → expanded).

---

## 6. What the real data shows

1. **Big Tech runs on immigrants — and the bigger the sample, the clearer it gets.** Across
   788 people, **34.5%** of those with a known origin are immigrants; among the technical
   ranks it is far higher: **Alphabet 65%, Microsoft 57%, Tesla 55%, Meta 51%, NVIDIA 46%**.
   The lowest are **Saudi Aramco (12%)** — a national champion — and **SpaceX (18%)**, whose
   export-controlled (ITAR) work skews to US persons. Nearly every founder/CEO here is an
   immigrant (Huang, Nadella, Pichai, Musk, Tan, Morris Chang).
2. **The self-made story sits at the very top.** Documented hardship/humble origins
   concentrate among the founders and CEOs — Huang (bathroom-cleaning immigrant), Cook
   (working-class Alabama), Brin (Soviet refugee), Tan (Penang scholarship), plus directors
   like Ursula Burns (housing project) and Rafael Reif (refugee family). Below the top, most
   leaders' origins are comfortable or simply undocumented.
3. **Real pay is wildly unequal — and founders take little.** Of the 41 with public pay, the
   top package is **Hock Tan (Broadcom) $205.3M**, then **Nadella $96.5M**, **Cook $74.6M**,
   and **Tesla CFO Vaibhav Taneja $139.5M**. Founder-operators take little cash: **Musk $0**,
   **Bezos $1.68M**, **Jassy $1.60M**.
4. **Character barely separates the firms** — every one is led by exceptional people, so mean
   potential (76–79) and mental strength (75–77) bunch tightly. That is *why* dominance and
   moat decide the Tyrell race.
5. **The verdict is robust:** in a world where compute is power, the company that owns the
   compute — **NVIDIA** — becomes Tyrell.

---

## 7. Caveats

- **Two-tier character scoring:** the 216 core people are scored per-biography; the 572
  extended people are scored by role rubric (so their individual scores are coarse). Both are
  interpretive, not measurements.
- **The roster is publicly-documented people**, weighted to leadership and well-known
  technical figures, and includes some notable *former* members. It is not a random or
  complete employee sample; N varies **34–116** by company.
- **Compensation** is real but exists only for named executive officers; a blank means "not
  disclosed," not "unpaid."
- Many extended people's origin/year-joined aren't public and are blank; immigrant % is
  computed over known-origin people only.
- Valuations are a June-2026 snapshot.

---

## 8. Reproduce

```bash
pip install numpy pandas matplotlib
python3 scripts/merge_people.py    # core (216) + data/people_raw/ -> data/all_people.csv (788)
python3 scripts/analyze_people.py  # summaries, Tyrell Index, charts
```

Sources: **`reports/PROFILES.md`** (core people) and **`data/people_raw/`** (extended people).
