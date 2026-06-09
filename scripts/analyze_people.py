#!/usr/bin/env python3
"""
analyze_people.py
=================
Analyses the REAL, sourced notable-people dataset (data/all_people.csv) for the
12 companies, and computes the Tyrell Index (who becomes the dominant global
megacorp).

Data provenance:
  - The people, titles, origins, biographies and disclosed compensation are
    REAL and individually sourced (see reports/PROFILES.md).
  - The three character indices (potential, mental_strength, adversity_origin)
    are INTERPRETIVE assessments derived from each person's documented public
    biography via one consistent rubric (see reports/REPORT.md). They are not
    psychometric measurements.

Outputs: per-company CSVs (data/people/), company summary, origin breakdown,
Tyrell Index, and charts in reports/figures/.
"""

from __future__ import annotations

import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
FIG = os.path.join(ROOT, "reports", "figures")
PEOPLE_DIR = os.path.join(DATA, "people")
os.makedirs(FIG, exist_ok=True)
os.makedirs(PEOPLE_DIR, exist_ok=True)

CHAR = ["potential_index", "mental_strength", "adversity_origin_score"]

companies = pd.read_csv(os.path.join(DATA, "companies.csv"))
order = companies["company"].tolist()
short = {"Alphabet (Google)": "Alphabet", "Saudi Aramco": "Aramco", "Meta Platforms": "Meta"}
labels = [short.get(c, c) for c in order]

df = pd.read_csv(os.path.join(DATA, "all_people.csv"))
df["company"] = pd.Categorical(df["company"], categories=order, ordered=True)

# Split per-company files (slug from companies.csv rank/name).
slug = {r["company"]: f"{r['rank']:02d}_" + r["company"].split(" (")[0].replace(" ", "_").replace(".", "").lower()
        for _, r in companies.iterrows()}
for c in order:
    sub = df[df["company"] == c]
    sub.to_csv(os.path.join(PEOPLE_DIR, slug[c] + ".csv"), index=False)
print(f"wrote {len(order)} per-company files to data/people/ ({len(df)} people total)")

g = df.groupby("company", observed=True)


# --------------------------------------------------------------------------
# 1. Company summary
# --------------------------------------------------------------------------
summary = pd.DataFrame({
    "people_documented": g.size(),
    "pct_immigrant": (g["immigrant"].apply(lambda s: (s == "Yes").mean() * 100)).round(1),
    "pct_documented_adversity": (g["documented_adversity"].apply(
        lambda s: (~s.str.startswith("none")).mean() * 100)).round(1),
    "potential_mean": g["potential_index"].mean().round(1),
    "mental_mean": g["mental_strength"].mean().round(1),
    "adversity_origin_mean": g["adversity_origin_score"].mean().round(1),
    "disclosed_comp_count": g["total_compensation_usd"].apply(lambda s: s.notna().sum()),
    "median_disclosed_comp": g["total_compensation_usd"].median().round(0),
}).reindex(order)
summary = summary.merge(
    companies.set_index("company")[["valuation_usd_trillions", "ownership", "sector"]],
    left_index=True, right_index=True)
summary.to_csv(os.path.join(DATA, "company_people_summary.csv"))
print(summary.to_string())


# --------------------------------------------------------------------------
# 2. Origin-region breakdown
# --------------------------------------------------------------------------
region_tab = (df.groupby(["company", "origin_region"], observed=True).size()
              .unstack(fill_value=0).reindex(order))
region_pct = (region_tab.div(region_tab.sum(axis=1), axis=0) * 100).round(1)
region_pct.to_csv(os.path.join(DATA, "origin_region_breakdown.csv"))


# --------------------------------------------------------------------------
# 3. Charts
# --------------------------------------------------------------------------
def barchart(values, title, ylabel, fname, fmt=None, color="#3b6ea5"):
    fig, ax = plt.subplots(figsize=(11, 5))
    bars = ax.bar(labels, values, color=color)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_ylabel(ylabel)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=35, ha="right")
    for b, v in zip(bars, values):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height(),
                fmt(v) if fmt else f"{v}", ha="center", va="bottom", fontsize=8)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, fname), dpi=110)
    plt.close(fig)
    print("wrote", fname)


barchart(summary["pct_immigrant"], "Share of notable people who are immigrants (%)",
         "%", "pct_immigrant.png", fmt=lambda v: f"{v:.0f}%", color="#1f7a4d")
barchart(summary["potential_mean"], "Mean POTENTIAL index (biographically assessed)",
         "score", "potential_mean.png", fmt=lambda v: f"{v:.1f}", color="#6a3d9a")
barchart(summary["mental_mean"], "Mean MENTAL STRENGTH (biographically assessed)",
         "score", "mental_mean.png", fmt=lambda v: f"{v:.1f}", color="#c0392b")
barchart(summary["adversity_origin_mean"], "Mean ADVERSITY-OF-ORIGIN (biographically assessed)",
         "score", "adversity_origin_mean.png", fmt=lambda v: f"{v:.1f}", color="#a6611a")

# Origin-region stacked bar
fig, ax = plt.subplots(figsize=(13, 6))
bottom = np.zeros(len(order))
cmap = plt.get_cmap("tab10")
for i, reg in enumerate(region_pct.columns):
    ax.bar(labels, region_pct[reg].values, bottom=bottom, label=reg, color=cmap(i % 10))
    bottom += region_pct[reg].values
ax.set_title("Where the notable people come from — origin region by company (%)",
             fontsize=13, fontweight="bold")
ax.set_ylabel("% of documented people")
ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels, rotation=35, ha="right")
ax.legend(bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=8)
ax.set_ylim(0, 100)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "origin_region_mix.png"), dpi=110)
plt.close(fig)
print("wrote origin_region_mix.png")

# Disclosed compensation (real NEO pay) — boxplot of disclosed values per company
fig, ax = plt.subplots(figsize=(12, 5.5))
comp_by_co, comp_labels = [], []
for c, lab in zip(order, labels):
    vals = df.loc[(df["company"] == c) & df["total_compensation_usd"].notna(),
                  "total_compensation_usd"] / 1e6
    if len(vals) > 0:
        comp_by_co.append(vals.values)
        comp_labels.append(f"{lab}\n(n={len(vals)})")
ax.boxplot(comp_by_co, tick_labels=comp_labels, showfliers=True)
ax.set_title("Disclosed executive compensation (real, $M) — companies with NEO disclosure",
             fontsize=12, fontweight="bold")
ax.set_ylabel("total comp ($M)")
ax.tick_params(axis="x", labelsize=8)
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "disclosed_comp.png"), dpi=110)
plt.close(fig)
print("wrote disclosed_comp.png")


# --------------------------------------------------------------------------
# 4. THE TYRELL INDEX (global-dominance prediction)
# --------------------------------------------------------------------------
STRATEGIC_MOAT = {
    "NVIDIA": 95, "TSMC": 90, "OpenAI": 90, "Alphabet (Google)": 86, "SpaceX": 86,
    "Microsoft": 85, "Apple": 84, "Amazon": 82, "Meta Platforms": 74,
    "Saudi Aramco": 70, "Broadcom": 66, "Tesla": 55,
}
WEIGHTS = {"dominance": 0.34, "moat": 0.34, "potential": 0.14, "mental": 0.10, "builder": 0.08}


def scale_0_100(s):
    lo, hi = s.min(), s.max()
    return pd.Series(50.0, index=s.index) if hi == lo else ((s - lo) / (hi - lo) * 100).round(1)


tyrell = pd.DataFrame(index=order)
val = companies.set_index("company").reindex(order)["valuation_usd_trillions"]
# Dominance: scaled relative to the most valuable company (absolute, not min-max,
# so small firms aren't artificially pushed to 0).
tyrell["dominance"] = (val / val.max() * 100).round(1)
tyrell["moat"] = pd.Series(STRATEGIC_MOAT).reindex(order)
# Character pillars are already 0-100 indices -> use the company mean directly.
# (Min-max rescaling here would amplify the compressed between-company spread
# into misleading 0-100 swings.)
tyrell["potential"] = summary["potential_mean"]
tyrell["mental"] = summary["mental_mean"]
tyrell["builder"] = summary["adversity_origin_mean"]
tyrell["tyrell_index"] = sum(tyrell[k] * w for k, w in WEIGHTS.items()).round(1)
tyrell = tyrell.sort_values("tyrell_index", ascending=False)
tyrell["rank"] = range(1, len(tyrell) + 1)
tyrell.to_csv(os.path.join(DATA, "tyrell_index.csv"))
print("\n=== TYRELL INDEX (real-people version) ===")
print(tyrell.to_string())

fig, ax = plt.subplots(figsize=(13, 6))
t_lab = [short.get(c, c) for c in tyrell.index]
bottom = np.zeros(len(tyrell))
pillar_colors = {"dominance": "#2c3e50", "moat": "#8e44ad", "potential": "#2980b9",
                 "mental": "#c0392b", "builder": "#d68910"}
for k, w in WEIGHTS.items():
    ax.bar(t_lab, (tyrell[k] * w).values, bottom=bottom, label=f"{k} (w={w})", color=pillar_colors[k])
    bottom += (tyrell[k] * w).values
for i, v in enumerate(tyrell["tyrell_index"].values):
    ax.text(i, bottom[i], f"{v:.1f}", ha="center", va="bottom", fontsize=9, fontweight="bold")
ax.set_title("THE TYRELL INDEX — which company becomes the dominant global megacorp?",
             fontsize=13, fontweight="bold")
ax.set_ylabel("weighted score (0-100)")
ax.set_xticks(range(len(t_lab)))
ax.set_xticklabels(t_lab, rotation=35, ha="right")
ax.legend(loc="upper right", fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "tyrell_index.png"), dpi=110)
plt.close(fig)
print("wrote tyrell_index.png")


# --------------------------------------------------------------------------
# 5. Headline numbers
# --------------------------------------------------------------------------
disclosed = df[df["total_compensation_usd"].notna()]
headline = {
    "people_documented": int(len(df)),
    "companies": len(order),
    "people_with_disclosed_comp": int(len(disclosed)),
    "overall_pct_immigrant": round((df["immigrant"] == "Yes").mean() * 100, 1),
    "highest_disclosed_comp": [disclosed.loc[disclosed["total_compensation_usd"].idxmax(), "name"],
                               int(disclosed["total_compensation_usd"].max())],
    "tyrell_winner": [tyrell.index[0], float(tyrell["tyrell_index"].iloc[0])],
    "tyrell_top5": {c: float(v) for c, v in tyrell["tyrell_index"].head(5).items()},
    "most_immigrant_company": [summary["pct_immigrant"].idxmax(), float(summary["pct_immigrant"].max())],
    "highest_adversity_company": [summary["adversity_origin_mean"].idxmax(),
                                  float(summary["adversity_origin_mean"].max())],
}
with open(os.path.join(DATA, "headline_stats.json"), "w") as f:
    json.dump(headline, f, indent=2, default=str)
print("\n=== HEADLINE ===")
print(json.dumps(headline, indent=2, default=str))
