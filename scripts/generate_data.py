#!/usr/bin/env python3
"""
generate_data.py
================
Generates the employee dataset analysed in this project.

IMPORTANT — DATA PROVENANCE
---------------------------
The list of the 10 largest companies by market capitalisation is REAL,
publicly sourced data (see ``data/companies.csv`` and the report).

The per-employee records are NOT real. No company publishes a roster of its
"1000 most important employees" together with personal performance,
compensation and tenure figures — that information does not exist in any
public form, and publishing real individuals' performance/pay would be a
privacy violation anyway.

This script therefore produces a **synthetic** dataset whose statistical
*distributions* are calibrated to publicly known, company-level
characteristics (sector, pay scale, typical seniority mix, turnover/tenure
patterns). It is intended for methodology, tooling and analysis purposes —
the individuals are fictional and any resemblance to real people is
coincidental.

Reproducible: a fixed RNG seed is used so the dataset regenerates identically.
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass, field

import numpy as np

SEED = 20260609
EMPLOYEES_PER_COMPANY = 1000
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
EMP_DIR = os.path.join(OUT_DIR, "employees")

rng = np.random.default_rng(SEED)


# --------------------------------------------------------------------------
# Real, sourced company facts (market cap snapshot: companiesmarketcap.com,
# June 2026). Market cap in USD trillions.
# --------------------------------------------------------------------------
@dataclass
class Company:
    rank: int
    name: str
    ticker: str
    country: str
    sector: str
    market_cap_usd_tn: float
    slug: str
    # synthetic-distribution calibration parameters -------------------------
    comp_median: float          # median total annual comp (USD) of the senior cohort
    comp_sigma: float           # lognormal sigma (pay dispersion)
    tenure_mean: float          # mean tenure (years)
    tenure_sd: float
    perf_mean: float            # mean performance score (0-100)
    perf_sd: float
    name_locale: str            # which name pool to weight toward
    departments: dict = field(default_factory=dict)


# Department weighting reflects each firm's centre of gravity.
TECH_DEPTS = {
    "Engineering": 0.34, "Research & AI": 0.14, "Product": 0.10, "Operations": 0.09,
    "Sales & GTM": 0.10, "Design": 0.05, "Finance": 0.05, "Marketing": 0.05,
    "Legal & Policy": 0.04, "People/HR": 0.04,
}
SEMI_DEPTS = {
    "Engineering": 0.30, "Fab/Manufacturing": 0.22, "Research & AI": 0.10,
    "Operations": 0.12, "Sales & GTM": 0.08, "Finance": 0.05, "Quality": 0.05,
    "Supply Chain": 0.04, "Legal & Policy": 0.02, "People/HR": 0.02,
}
ENERGY_DEPTS = {
    "Upstream/Engineering": 0.30, "Operations": 0.20, "Refining & Chemicals": 0.14,
    "Research & Tech": 0.08, "Finance": 0.07, "HSE/Safety": 0.07,
    "Supply Chain": 0.06, "Sales & Trading": 0.04, "Legal & Policy": 0.02, "People/HR": 0.02,
}
AUTO_DEPTS = {
    "Engineering": 0.30, "Manufacturing": 0.22, "Autonomy & AI": 0.12,
    "Operations": 0.10, "Sales & Service": 0.09, "Energy/Charging": 0.06,
    "Design": 0.04, "Finance": 0.03, "Legal & Policy": 0.02, "People/HR": 0.02,
}

COMPANIES = [
    Company(1, "NVIDIA", "NVDA", "USA", "Semiconductors / AI", 5.053, "nvidia",
            comp_median=415_000, comp_sigma=0.55, tenure_mean=6.2, tenure_sd=4.0,
            perf_mean=80, perf_sd=10, name_locale="us_mixed", departments=TECH_DEPTS),
    Company(2, "Apple", "AAPL", "USA", "Consumer Electronics", 4.428, "apple",
            comp_median=350_000, comp_sigma=0.52, tenure_mean=8.0, tenure_sd=4.6,
            perf_mean=78, perf_sd=10, name_locale="us_mixed", departments=TECH_DEPTS),
    Company(3, "Alphabet (Google)", "GOOG", "USA", "Internet / AI", 4.404, "alphabet",
            comp_median=380_000, comp_sigma=0.54, tenure_mean=6.8, tenure_sd=4.1,
            perf_mean=79, perf_sd=10, name_locale="us_mixed", departments=TECH_DEPTS),
    Company(4, "Microsoft", "MSFT", "USA", "Software / Cloud", 3.058, "microsoft",
            comp_median=340_000, comp_sigma=0.50, tenure_mean=7.4, tenure_sd=4.3,
            perf_mean=78, perf_sd=9, name_locale="us_mixed", departments=TECH_DEPTS),
    Company(5, "Amazon", "AMZN", "USA", "E-commerce / Cloud", 2.637, "amazon",
            comp_median=315_000, comp_sigma=0.58, tenure_mean=4.8, tenure_sd=3.4,
            perf_mean=76, perf_sd=11, name_locale="us_mixed", departments=TECH_DEPTS),
    Company(6, "TSMC", "TSM", "Taiwan", "Semiconductor Foundry", 2.213, "tsmc",
            comp_median=155_000, comp_sigma=0.48, tenure_mean=9.0, tenure_sd=4.8,
            perf_mean=80, perf_sd=8, name_locale="taiwan", departments=SEMI_DEPTS),
    Company(7, "Broadcom", "AVGO", "USA", "Semiconductors / Software", 1.877, "broadcom",
            comp_median=330_000, comp_sigma=0.56, tenure_mean=6.5, tenure_sd=4.2,
            perf_mean=77, perf_sd=10, name_locale="us_mixed", departments=SEMI_DEPTS),
    Company(8, "Saudi Aramco", "2222.SR", "Saudi Arabia", "Oil & Gas", 1.750, "saudi_aramco",
            comp_median=185_000, comp_sigma=0.50, tenure_mean=11.5, tenure_sd=5.6,
            perf_mean=79, perf_sd=8, name_locale="saudi", departments=ENERGY_DEPTS),
    Company(9, "Tesla", "TSLA", "USA", "Automotive / Energy", 1.535, "tesla",
            comp_median=275_000, comp_sigma=0.62, tenure_mean=3.9, tenure_sd=2.9,
            perf_mean=75, perf_sd=12, name_locale="us_mixed", departments=AUTO_DEPTS),
    Company(10, "Meta Platforms", "META", "USA", "Social / AI", 1.485, "meta",
            comp_median=400_000, comp_sigma=0.57, tenure_mean=4.5, tenure_sd=3.2,
            perf_mean=78, perf_sd=11, name_locale="us_mixed", departments=TECH_DEPTS),
]


# --------------------------------------------------------------------------
# Synthetic name pools (clearly fictional; locale-weighted for realism).
# --------------------------------------------------------------------------
FIRST = {
    "us_mixed": ["James", "Mary", "Wei", "Priya", "David", "Maria", "Chen", "Aisha",
                 "Michael", "Linda", "Raj", "Sofia", "John", "Emily", "Hiroshi", "Fatima",
                 "Daniel", "Olivia", "Ahmed", "Grace", "Kevin", "Nina", "Carlos", "Yuki",
                 "Samuel", "Hannah", "Arjun", "Elena", "Thomas", "Zoe"],
    "taiwan":   ["Wei", "Mei", "Jian", "Hui", "Cheng", "Yu", "Hao", "Ling", "Chih",
                 "Shu", "Ming", "Fang", "Jun", "Xin", "Bo", "Ying", "Kai", "Wen",
                 "Zhi", "Ting", "Yi", "Han", "Chun", "Li", "Po", "Jia", "Sheng", "Qing"],
    "saudi":    ["Mohammed", "Aisha", "Abdullah", "Fatima", "Khalid", "Noura", "Faisal",
                 "Sara", "Saud", "Layla", "Omar", "Huda", "Tariq", "Maryam", "Yousef",
                 "Reem", "Bandar", "Hessa", "Ziad", "Amal", "Nasser", "Lina", "Salem",
                 "Dana", "Majed", "Rana", "Hamad", "Jana"],
}
LAST = {
    "us_mixed": ["Smith", "Johnson", "Lee", "Patel", "Garcia", "Nguyen", "Brown",
                 "Khan", "Wang", "Martinez", "Davis", "Kim", "Chen", "Lopez", "Wilson",
                 "Singh", "Anderson", "Tanaka", "Rossi", "Cohen", "Murphy", "Reyes",
                 "Schmidt", "Ali", "Okafor", "Petrov", "Silva", "Yamamoto", "Hassan", "Park"],
    "taiwan":   ["Chen", "Lin", "Huang", "Chang", "Lee", "Wang", "Wu", "Liu", "Tsai",
                 "Yang", "Hsu", "Cheng", "Kuo", "Hsieh", "Chou", "Tseng", "Lu", "Yeh",
                 "Chiang", "Pan", "Hung", "Su", "Liao", "Chao", "Fang", "Shen"],
    "saudi":    ["Al-Saud", "Al-Otaibi", "Al-Qahtani", "Al-Ghamdi", "Al-Harbi",
                 "Al-Shehri", "Al-Dossari", "Al-Zahrani", "Al-Mutairi", "Al-Rashid",
                 "Al-Subaie", "Al-Anazi", "Al-Maliki", "Al-Juhani", "Al-Amri",
                 "Al-Faraj", "Al-Sulaiman", "Al-Nasser", "Bin Laden", "Al-Hassan"],
}

# Seniority mix — this cohort is the "1000 most important", so it is skewed
# heavily toward senior individual contributors and leadership.
LEVELS = ["Senior", "Staff", "Principal", "Director", "Senior Director",
          "VP", "SVP", "C-Suite"]
LEVEL_WEIGHTS = np.array([0.30, 0.24, 0.18, 0.12, 0.08, 0.055, 0.018, 0.007])
# multiplicative effect of level on compensation
LEVEL_COMP_MULT = {"Senior": 0.72, "Staff": 0.95, "Principal": 1.25, "Director": 1.55,
                   "Senior Director": 1.95, "VP": 2.6, "SVP": 3.6, "C-Suite": 6.0}


# ==========================================================================
# CHARACTER METRICS
# --------------------------------------------------------------------------
# Three "character" dimensions are modelled for every employee. Each is a
# 0-100 index built from named sub-traits, so the score is interpretable:
#
#   1. POTENTIAL        — growth ceiling: learning agility, drive/ambition,
#                         and promotion trajectory (level reached vs tenure).
#   2. ORIGIN / ROOTS   — "where they come from": a descriptive origin region
#                         and socioeconomic background, summarised numerically
#                         as an ADVERSITY-OF-ORIGIN score (higher = more
#                         self-made / further travelled from the starting line).
#   3. MENTAL STRENGTH  — resilience, stress tolerance and grit.
#
# Deliberate, defensible correlations are baked in: overcoming a harder start
# tends to build mental strength, and mental strength feeds potential. These
# are MODELLING CHOICES, not measurements — see the provenance note. Ascribing
# "character" and "origins" to (fictional) individuals is pure illustration.
# ==========================================================================

# Origin-region mix per name-locale (roughly mirrors each firm's hiring base).
ORIGIN_REGIONS = ["North America", "Latin America", "Europe", "Middle East",
                  "Africa", "South Asia", "East Asia", "Southeast Asia", "Oceania"]
ORIGIN_PROFILES = {
    "us_mixed": [0.44, 0.05, 0.08, 0.03, 0.025, 0.21, 0.12, 0.03, 0.015],
    "taiwan":   [0.04, 0.00, 0.01, 0.00, 0.005, 0.02, 0.88, 0.045, 0.00],
    "saudi":    [0.01, 0.00, 0.02, 0.78, 0.05, 0.10, 0.005, 0.035, 0.00],
}

# Socioeconomic background of origin and its base adversity weight (0-100,
# higher = started further back). first-generation-professional adds to it.
SOCIO = ["Working class", "Lower-middle", "Middle", "Upper-middle", "Affluent"]
SOCIO_WEIGHTS = [0.18, 0.25, 0.30, 0.18, 0.09]
SOCIO_ADVERSITY = {"Working class": 82, "Lower-middle": 66, "Middle": 52,
                   "Upper-middle": 38, "Affluent": 25}
FIRST_GEN_PROB = {"Working class": 0.80, "Lower-middle": 0.55, "Middle": 0.30,
                  "Upper-middle": 0.12, "Affluent": 0.05}

# Per-company culture tilt on mental strength (aggressive / high-churn cultures
# select for higher grit). Keyed by ticker stem.
MENTAL_MEAN = {"NVDA": 72, "AAPL": 68, "GOOG": 68, "MSFT": 67, "AMZN": 73,
               "TSM": 71, "AVGO": 70, "2222": 69, "TSLA": 75, "META": 71}
# Per-company ambition tilt feeding potential.
AMBITION_MEAN = {"NVDA": 74, "AAPL": 69, "GOOG": 72, "MSFT": 68, "AMZN": 73,
                 "TSM": 70, "AVGO": 69, "2222": 67, "TSLA": 76, "META": 73}

LEVEL_TRAJECTORY = {"Senior": 45, "Staff": 55, "Principal": 65, "Director": 72,
                    "Senior Director": 78, "VP": 85, "SVP": 92, "C-Suite": 98}


def generate_character(c: Company, levels, tenure, perf):
    """Return (potential, origin_region, socio, first_gen, adversity, mental)."""
    n = len(levels)
    stem = c.ticker.split(".")[0]

    # --- Origin / roots ---------------------------------------------------
    region = rng.choice(ORIGIN_REGIONS, size=n, p=np.array(ORIGIN_PROFILES[c.name_locale]))
    socio = rng.choice(SOCIO, size=n, p=SOCIO_WEIGHTS)
    first_gen = np.array([rng.random() < FIRST_GEN_PROB[s] for s in socio])
    adversity = np.array([SOCIO_ADVERSITY[s] for s in socio], dtype=float)
    adversity += first_gen * 9.0 + rng.normal(0, 7, n)
    adversity = np.clip(adversity, 0, 100).round(1)

    # --- Mental strength (resilience + stress tolerance + grit) -----------
    # Centred on the company culture mean; a harder start and stronger
    # performance tilt it up (mild positive coupling, mean-preserving).
    mental = (rng.normal(MENTAL_MEAN[stem], 9, n)
              + 0.15 * (adversity - 55)
              + 0.10 * (perf - 78))           # high performers a touch grittier
    mental = np.clip(mental + rng.normal(0, 3, n), 0, 100).round(1)

    # --- Potential (learning agility + ambition + trajectory + a bit of grit)
    learning = rng.normal(70, 12, n)
    ambition = rng.normal(AMBITION_MEAN[stem], 12, n)
    # trajectory: reached a high level fast (relative to tenure) => high potential
    traj = np.array([LEVEL_TRAJECTORY[l] for l in levels], dtype=float)
    traj = traj - 1.4 * np.clip(tenure - 5, 0, None)   # slow climbers score lower
    potential = (0.34 * learning + 0.28 * ambition + 0.22 * np.clip(traj, 0, 100)
                 + 0.16 * mental)
    potential = np.clip(potential + rng.normal(0, 4, n), 0, 100).round(1)

    return (potential, region, socio,
            np.where(first_gen, "Yes", "No"), adversity, mental)



def make_names(locale: str, n: int) -> list[str]:
    first = rng.choice(FIRST[locale], size=n)
    last = rng.choice(LAST[locale], size=n)
    return [f"{f} {l}" for f, l in zip(first, last)]


def generate_company(c: Company) -> list[dict]:
    n = EMPLOYEES_PER_COMPANY
    names = make_names(c.name_locale, n)
    depts = list(c.departments.keys())
    dept_p = np.array(list(c.departments.values()))
    dept_p = dept_p / dept_p.sum()
    departments = rng.choice(depts, size=n, p=dept_p)
    levels = rng.choice(LEVELS, size=n, p=LEVEL_WEIGHTS)

    # Metric 1: Performance score (0-100), clipped normal, mild lift with level.
    level_perf_lift = np.array([{"Senior": 0, "Staff": 1, "Principal": 2, "Director": 3,
                                 "Senior Director": 3.5, "VP": 4, "SVP": 4.5,
                                 "C-Suite": 5}[l] for l in levels])
    perf = rng.normal(c.perf_mean, c.perf_sd, n) + level_perf_lift
    perf = np.clip(perf, 30, 100).round(1)

    # Metric 2: Total annual compensation (USD).
    base = rng.lognormal(mean=np.log(c.comp_median), sigma=c.comp_sigma, size=n)
    mult = np.array([LEVEL_COMP_MULT[l] for l in levels])
    # high performers earn somewhat more (correlation ~ mild)
    perf_factor = 1 + (perf - c.perf_mean) / 100.0
    comp = (base * mult * perf_factor).round(-2).astype(int)

    # Metric 3: Tenure (years) — gamma-ish, non-negative; senior levels skew longer.
    level_tenure_lift = np.array([{"Senior": 0, "Staff": 0.5, "Principal": 1.5,
                                   "Director": 2.5, "Senior Director": 3.5, "VP": 4.5,
                                   "SVP": 5.5, "C-Suite": 6.5}[l] for l in levels])
    tenure = rng.gamma(shape=(c.tenure_mean / c.tenure_sd) ** 2,
                       scale=c.tenure_sd ** 2 / c.tenure_mean, size=n) + level_tenure_lift
    tenure = np.clip(tenure, 0.2, 40).round(1)

    # Character metrics (depend on level / tenure / performance).
    potential, region, socio, first_gen, adversity, mental = \
        generate_character(c, levels, tenure, perf)

    rows = []
    for i in range(n):
        rows.append({
            "employee_id": f"{c.ticker.split('.')[0]}-{i+1:04d}",
            "name": names[i],
            "company": c.name,
            "ticker": c.ticker,
            "department": departments[i],
            "level": levels[i],
            # --- performance metrics ---
            "performance_score": perf[i],
            "total_compensation_usd": int(comp[i]),
            "tenure_years": tenure[i],
            # --- character metrics ---
            "potential_index": potential[i],
            "origin_region": region[i],
            "socioeconomic_origin": socio[i],
            "first_generation_professional": first_gen[i],
            "adversity_origin_score": adversity[i],
            "mental_strength": mental[i],
        })
    return rows


def main() -> None:
    os.makedirs(EMP_DIR, exist_ok=True)

    # companies.csv (the real, sourced data)
    comp_path = os.path.join(OUT_DIR, "companies.csv")
    with open(comp_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["rank", "company", "ticker", "country", "sector", "market_cap_usd_trillions"])
        for c in COMPANIES:
            w.writerow([c.rank, c.name, c.ticker, c.country, c.sector, c.market_cap_usd_tn])
    print(f"wrote {comp_path}")

    fieldnames = ["employee_id", "name", "company", "ticker", "department", "level",
                  "performance_score", "total_compensation_usd", "tenure_years",
                  "potential_index", "origin_region", "socioeconomic_origin",
                  "first_generation_professional", "adversity_origin_score",
                  "mental_strength"]
    all_rows = []
    for c in COMPANIES:
        rows = generate_company(c)
        all_rows.extend(rows)
        path = os.path.join(EMP_DIR, f"{c.rank:02d}_{c.slug}.csv")
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(rows)
        print(f"wrote {path} ({len(rows)} employees)")

    all_path = os.path.join(OUT_DIR, "all_employees.csv")
    with open(all_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(all_rows)
    print(f"wrote {all_path} ({len(all_rows)} employees total)")


if __name__ == "__main__":
    main()
