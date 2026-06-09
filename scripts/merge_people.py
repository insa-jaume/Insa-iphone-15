#!/usr/bin/env python3
"""
merge_people.py
===============
Merges the hand-curated core roster (data/all_people.csv, the original 216 with
individually-assigned character scores) with the EXTENDED roster gathered by the
research agents into data/people_raw/<NN>_<slug>.csv.

For the extended people (mostly VPs, distinguished engineers, named researchers),
full biographies are usually not public, so the three character indices are
assigned by a CONSISTENT, DOCUMENTED role-based rubric rather than per-person
judgement. A `data_tier` column marks "core" vs "extended" so the two are always
distinguishable. Real disclosed compensation exists only for the core NEOs, so
extended rows have blank comp.

Re-runnable: rebuilds data/all_people.csv from the core + raw files. The core is
preserved in data/all_people_core.csv (created on first run).
"""

from __future__ import annotations

import csv
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
RAW = os.path.join(DATA, "people_raw")

CORE = os.path.join(DATA, "all_people_core.csv")
ALL = os.path.join(DATA, "all_people.csv")

FIELDS = ["company", "ticker", "name", "title", "year_joined", "origin_country",
          "origin_region", "immigrant", "role_category", "total_compensation_usd",
          "comp_fiscal_year", "documented_adversity", "potential_index",
          "mental_strength", "adversity_origin_score", "data_tier"]

# raw filename stem -> (company, ticker, hq_country)
FILE_COMPANY = {
    "01_nvidia": ("NVIDIA", "NVDA", "USA"),
    "02_apple": ("Apple", "AAPL", "USA"),
    "03_alphabet": ("Alphabet (Google)", "GOOG", "USA"),
    "04_microsoft": ("Microsoft", "MSFT", "USA"),
    "05_amazon": ("Amazon", "AMZN", "USA"),
    "06_tsmc": ("TSMC", "TSM", "Taiwan"),
    "07_broadcom": ("Broadcom", "AVGO", "USA"),
    "08_saudi_aramco": ("Saudi Aramco", "2222.SR", "Saudi Arabia"),
    "09_tesla": ("Tesla", "TSLA", "USA"),
    "10_meta_platforms": ("Meta Platforms", "META", "USA"),
    "11_spacex": ("SpaceX", "SPACEX", "USA"),
    "12_openai": ("OpenAI", "OPENAI", "USA"),
}

REGION = {
    "USA": "North America", "United States": "North America", "Canada": "North America",
    "Mexico": "Latin America", "Brazil": "Latin America", "Venezuela": "Latin America",
    "Argentina": "Latin America", "Colombia": "Latin America",
    "UK": "Europe", "United Kingdom": "Europe", "England": "Europe", "Scotland": "Europe",
    "Ireland": "Europe", "Germany": "Europe", "France": "Europe", "Spain": "Europe",
    "Italy": "Europe", "Netherlands": "Europe", "Poland": "Europe", "Russia": "Europe",
    "USSR": "Europe", "Soviet Union": "Europe", "Ukraine": "Europe", "Greece": "Europe",
    "Romania": "Europe", "Bulgaria": "Europe", "Slovakia": "Europe", "Czechoslovakia": "Europe",
    "Czech Republic": "Europe", "Switzerland": "Europe", "Sweden": "Europe", "Belgium": "Europe",
    "Austria": "Europe", "Portugal": "Europe", "Hungary": "Europe", "Norway": "Europe",
    "Denmark": "Europe", "Finland": "Europe", "Albania": "Europe", "Serbia": "Europe", "Croatia": "Europe",
    "India": "South Asia", "Pakistan": "South Asia", "Bangladesh": "South Asia", "Sri Lanka": "South Asia", "Nepal": "South Asia",
    "China": "East Asia", "Taiwan": "East Asia", "Japan": "East Asia", "South Korea": "East Asia",
    "Korea": "East Asia", "Hong Kong": "East Asia",
    "Singapore": "Southeast Asia", "Malaysia": "Southeast Asia", "Indonesia": "Southeast Asia",
    "Vietnam": "Southeast Asia", "Philippines": "Southeast Asia", "Thailand": "Southeast Asia",
    "Israel": "Middle East", "Saudi Arabia": "Middle East", "Egypt": "Middle East",
    "Iran": "Middle East", "Turkey": "Middle East", "Lebanon": "Middle East", "UAE": "Middle East", "Jordan": "Middle East",
    "South Africa": "Africa", "Nigeria": "Africa", "Kenya": "Africa", "Morocco": "Africa", "Ghana": "Africa", "Egypt ": "Africa",
    "Australia": "Oceania", "New Zealand": "Oceania",
}


def norm(name: str) -> str:
    return re.sub(r"[^a-z]", "", name.lower())


def role_of(title: str) -> str:
    t = title.lower()
    if "co-founder" in t or "cofounder" in t:
        return "Co-founder"
    if "founder" in t and ("ceo" in t or "chief executive" in t):
        return "Founder/CEO"
    if ("independent director" in t or "lead director" in t or t.strip() == "director"
            or "board" in t):
        return "Director"
    if "chair" in t:
        return "Chair"
    if "chief financial" in t or t.strip() == "cfo" or " cfo" in t:
        return "CFO"
    if "chief scientist" in t or "chief ai scientist" in t or "chief research" in t:
        return "Chief Scientist"
    if "chief technolog" in t or t.strip() == "cto" or " cto" in t:
        return "CTO"
    if "ceo" in t or "chief executive" in t:
        return "Division-CEO"
    if any(k in t for k in ["fellow", "distinguished engineer", "scientist", "researcher",
                            "research", "principal engineer", "architect"]):
        return "Tech Leader"
    if any(k in t for k in ["president", "coo", "cmo", "cpo", "chro", "general counsel",
                            "chief", "svp", "evp", "senior vice president", "executive vice president"]):
        return "C-suite"
    if any(k in t for k in ["vp", "vice president", "head of", "gm", "general manager",
                            "director"]):
        return "C-suite"
    return "Tech Leader"


POTENTIAL = {"Founder/CEO": 92, "Co-founder": 84, "Division-CEO": 84, "Chair": 80,
             "CTO": 80, "Chief Scientist": 82, "CFO": 78, "C-suite": 76,
             "Tech Leader": 76, "Director": 72}
MENTAL_BASE = {"Founder/CEO": 84, "Co-founder": 80, "Division-CEO": 80, "Chair": 76,
               "CTO": 76, "Chief Scientist": 76, "CFO": 74, "C-suite": 74,
               "Tech Leader": 74, "Director": 72}


def has_adversity(s: str) -> bool:
    s = (s or "").strip().lower()
    return bool(s) and not s.startswith("none")


def score(role: str, immigrant: str, adversity: bool):
    pot = POTENTIAL.get(role, 74)
    mental = min(95, MENTAL_BASE.get(role, 74) + (6 if adversity else 0))
    if adversity:
        adv = 78
    elif immigrant == "Yes":
        adv = 60
    else:
        adv = 45
    return pot, mental, adv


def load_core():
    with open(ALL if not os.path.exists(CORE) else CORE) as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r.setdefault("data_tier", "core")
        r["data_tier"] = "core"
    return rows


def main():
    # Preserve the original hand-curated roster once.
    if not os.path.exists(CORE):
        with open(ALL) as f:
            original = f.read()
        with open(CORE, "w") as f:
            f.write(original)
        print(f"saved core snapshot -> {CORE}")

    core = load_core()
    seen = {(r["company"], norm(r["name"])) for r in core}
    combined = list(core)
    added = {}

    for stem, (company, ticker, hq) in FILE_COMPANY.items():
        path = os.path.join(RAW, stem + ".csv")
        if not os.path.exists(path):
            continue
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = (row.get("name") or "").strip()
                if not name or norm(name) in {n for c, n in seen if c == company}:
                    continue
                key = (company, norm(name))
                if key in seen:
                    continue
                seen.add(key)
                origin = (row.get("origin_country") or "").strip()
                region = REGION.get(origin, "Unknown" if not origin else "Other")
                if not origin:
                    immigrant = "Unknown"
                elif origin in (hq, "United States" if hq == "USA" else hq):
                    immigrant = "No"
                else:
                    immigrant = "Yes"
                title = (row.get("title") or "").strip()
                role = role_of(title)
                adv_note = (row.get("documented_adversity") or "none documented").strip()
                adv = has_adversity(adv_note)
                pot, mental, advs = score(role, immigrant, adv)
                combined.append({
                    "company": company, "ticker": ticker, "name": name, "title": title,
                    "year_joined": (row.get("year_joined") or "").strip(),
                    "origin_country": origin, "origin_region": region,
                    "immigrant": immigrant, "role_category": role,
                    "total_compensation_usd": "", "comp_fiscal_year": "",
                    "documented_adversity": adv_note if adv else "none documented",
                    "potential_index": pot, "mental_strength": mental,
                    "adversity_origin_score": advs, "data_tier": "extended",
                })
                added[company] = added.get(company, 0) + 1

    with open(ALL, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in combined:
            w.writerow({k: r.get(k, "") for k in FIELDS})

    print(f"total people: {len(combined)} (core {len(core)} + extended {sum(added.values())})")
    for c, n in added.items():
        print(f"  +{n:3d}  {c}")


if __name__ == "__main__":
    main()
