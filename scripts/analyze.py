#!/usr/bin/env python3
"""
analyze.py
==========
Reads data/all_employees.csv and analyses SIX employee metrics across the
10 companies:

  performance metrics : performance_score, total_compensation_usd, tenure_years
  character  metrics  : potential_index, adversity_origin_score, mental_strength
                        (+ descriptive origin_region / socioeconomic_origin)

Writes data/company_metrics_summary.csv, data/origin_region_breakdown.csv,
data/headline_stats.json and charts into reports/figures/.
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
os.makedirs(FIG, exist_ok=True)

PERF_METRICS = ["performance_score", "total_compensation_usd", "tenure_years"]
CHAR_METRICS = ["potential_index", "adversity_origin_score", "mental_strength"]
ALL_METRICS = PERF_METRICS + CHAR_METRICS

companies = pd.read_csv(os.path.join(DATA, "companies.csv"))
order = companies["company"].tolist()
short = {"Alphabet (Google)": "Alphabet", "Saudi Aramco": "Aramco", "Meta Platforms": "Meta"}
labels = [short.get(c, c) for c in order]

df = pd.read_csv(os.path.join(DATA, "all_employees.csv"))
df["company"] = pd.Categorical(df["company"], categories=order, ordered=True)
g = df.groupby("company", observed=True)


# --------------------------------------------------------------------------
# 1. Per-company summary table (performance + character)
# --------------------------------------------------------------------------
summary = pd.DataFrame({
    "headcount": g.size(),
    "perf_mean": g["performance_score"].mean().round(1),
    "comp_median_usd": g["total_compensation_usd"].median().round(0).astype(int),
    "tenure_median_yrs": g["tenure_years"].median().round(1),
    "potential_mean": g["potential_index"].mean().round(1),
    "pct_high_potential": (g["potential_index"].apply(lambda s: (s >= 75).mean() * 100)).round(1),
    "adversity_origin_mean": g["adversity_origin_score"].mean().round(1),
    "pct_first_gen": (g["first_generation_professional"].apply(lambda s: (s == "Yes").mean() * 100)).round(1),
    "mental_strength_mean": g["mental_strength"].mean().round(1),
    "pct_high_mental": (g["mental_strength"].apply(lambda s: (s >= 80).mean() * 100)).round(1),
}).reindex(order)
summary = summary.merge(companies.set_index("company")[["valuation_usd_trillions", "sector"]],
                        left_index=True, right_index=True)
summary.to_csv(os.path.join(DATA, "company_metrics_summary.csv"))
print(summary.to_string())


# --------------------------------------------------------------------------
# 2. Origin-region breakdown per company
# --------------------------------------------------------------------------
region_tab = (df.groupby(["company", "origin_region"], observed=True).size()
              .unstack(fill_value=0).reindex(order))
region_pct = (region_tab.div(region_tab.sum(axis=1), axis=0) * 100).round(1)
region_pct.to_csv(os.path.join(DATA, "origin_region_breakdown.csv"))
print("\nOrigin region mix (%):")
print(region_pct.to_string())


# --------------------------------------------------------------------------
# 3. Correlations across all six metrics (pooled)
# --------------------------------------------------------------------------
pooled_corr = df[ALL_METRICS].corr().round(3)
print("\nPooled correlation matrix:")
print(pooled_corr.to_string())


# --------------------------------------------------------------------------
# 4. Charts
# --------------------------------------------------------------------------
def barchart(values, title, ylabel, fname, fmt=None, color="#3b6ea5"):
    fig, ax = plt.subplots(figsize=(10, 5))
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


# performance charts
barchart(summary["comp_median_usd"], "Median total annual compensation (USD)",
         "USD", "comp_median.png", fmt=lambda v: f"${v/1000:.0f}k", color="#2e7d32")
barchart(summary["perf_mean"], "Mean performance score (0-100)",
         "score", "perf_mean.png", fmt=lambda v: f"{v:.1f}", color="#3b6ea5")
barchart(summary["tenure_median_yrs"], "Median tenure (years)",
         "years", "tenure_median.png", fmt=lambda v: f"{v:.1f}", color="#b05a2e")
# character charts
barchart(summary["potential_mean"], "Mean POTENTIAL index (0-100)",
         "score", "potential_mean.png", fmt=lambda v: f"{v:.1f}", color="#6a3d9a")
barchart(summary["adversity_origin_mean"], "Mean ADVERSITY-OF-ORIGIN score (0-100, higher = more self-made)",
         "score", "adversity_origin_mean.png", fmt=lambda v: f"{v:.1f}", color="#a6611a")
barchart(summary["mental_strength_mean"], "Mean MENTAL STRENGTH (0-100)",
         "score", "mental_strength_mean.png", fmt=lambda v: f"{v:.1f}", color="#c0392b")

# Origin-region stacked bar
fig, ax = plt.subplots(figsize=(12, 6))
bottom = np.zeros(len(order))
cmap = plt.get_cmap("tab10")
for i, reg in enumerate(region_pct.columns):
    vals = region_pct[reg].values
    ax.bar(labels, vals, bottom=bottom, label=reg, color=cmap(i % 10))
    bottom += vals
ax.set_title("Where employees come from — origin region mix by company (%)",
             fontsize=13, fontweight="bold")
ax.set_ylabel("% of workforce")
ax.set_xticklabels(labels, rotation=35, ha="right")
ax.legend(bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=8)
ax.set_ylim(0, 100)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "origin_region_mix.png"), dpi=110)
plt.close(fig)
print("wrote origin_region_mix.png")

# Character correlation heatmap (6x6)
fig, ax = plt.subplots(figsize=(7.5, 6.5))
im = ax.imshow(pooled_corr.values, cmap="RdBu_r", vmin=-1, vmax=1)
ax.set_xticks(range(len(ALL_METRICS)))
ax.set_yticks(range(len(ALL_METRICS)))
nice = [m.replace("_", "\n") for m in ALL_METRICS]
ax.set_xticklabels(nice, rotation=45, ha="right", fontsize=8)
ax.set_yticklabels(nice, fontsize=8)
for i in range(len(ALL_METRICS)):
    for j in range(len(ALL_METRICS)):
        ax.text(j, i, f"{pooled_corr.values[i, j]:.2f}", ha="center", va="center",
                fontsize=8, color="black")
ax.set_title("Correlation matrix — all six metrics (pooled)", fontsize=12, fontweight="bold")
fig.colorbar(im, fraction=0.046, pad=0.04)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "correlation_heatmap.png"), dpi=110)
plt.close(fig)
print("wrote correlation_heatmap.png")

# Adversity-of-origin vs mental strength scatter (company means)
fig, ax = plt.subplots(figsize=(9, 6))
sizes = (companies.set_index("company").reindex(order)["valuation_usd_trillions"] * 120).values
ax.scatter(summary["adversity_origin_mean"], summary["mental_strength_mean"],
           s=sizes, alpha=0.6, c=range(len(order)), cmap="plasma")
for i, c in enumerate(labels):
    ax.annotate(c, (summary["adversity_origin_mean"].iloc[i], summary["mental_strength_mean"].iloc[i]),
                fontsize=8, xytext=(4, 4), textcoords="offset points")
ax.set_xlabel("mean adversity-of-origin score")
ax.set_ylabel("mean mental strength")
ax.set_title("Origins vs mental strength (company means; bubble = market cap)",
             fontsize=13, fontweight="bold")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "adversity_vs_mental.png"), dpi=110)
plt.close(fig)
print("wrote adversity_vs_mental.png")


# --------------------------------------------------------------------------
# 5. Headline numbers
# --------------------------------------------------------------------------
# individual-level corr between adversity origin and mental strength
adv_mental_r = float(np.corrcoef(df["adversity_origin_score"], df["mental_strength"])[0, 1])
pot_mental_r = float(np.corrcoef(df["potential_index"], df["mental_strength"])[0, 1])
headline = {
    "total_employees": int(len(df)),
    "companies": len(order),
    "pooled_correlations": pooled_corr.to_dict(),
    "adversity_vs_mental_corr": round(adv_mental_r, 3),
    "potential_vs_mental_corr": round(pot_mental_r, 3),
    "highest_potential": [summary["potential_mean"].idxmax(), float(summary["potential_mean"].max())],
    "lowest_potential": [summary["potential_mean"].idxmin(), float(summary["potential_mean"].min())],
    "highest_mental": [summary["mental_strength_mean"].idxmax(), float(summary["mental_strength_mean"].max())],
    "lowest_mental": [summary["mental_strength_mean"].idxmin(), float(summary["mental_strength_mean"].min())],
    "highest_adversity_origin": [summary["adversity_origin_mean"].idxmax(), float(summary["adversity_origin_mean"].max())],
    "lowest_adversity_origin": [summary["adversity_origin_mean"].idxmin(), float(summary["adversity_origin_mean"].min())],
    "highest_first_gen_pct": [summary["pct_first_gen"].idxmax(), float(summary["pct_first_gen"].max())],
    "lowest_first_gen_pct": [summary["pct_first_gen"].idxmin(), float(summary["pct_first_gen"].min())],
}
print("\n=== HEADLINE ===")
print(json.dumps(headline, indent=2, default=str))
with open(os.path.join(DATA, "headline_stats.json"), "w") as f:
    json.dump(headline, f, indent=2, default=str)


# ==========================================================================
# 6. THE TYRELL INDEX  —  main objective
# --------------------------------------------------------------------------
# Which of the 10 is most likely to become the "Tyrell Corporation" of our
# universe? Per the brief, Tyrell matters as a GLOBALLY DOMINANT megacorp — an
# economic hegemon the world cannot route around — NOT because it builds robots.
# So we score the drivers of durable global dominance and combine them into a
# 0-100 Tyrell Index.
#
# Pillars:
#   1. DOMINANCE NOW   — market cap (current scale / resources).
#   2. STRATEGIC MOAT  — control of a critical global chokepoint the world
#                        depends on (AI compute, advanced-chip fabrication,
#                        cloud/OS lock-in, search/attention, energy). Curated,
#                        sourced 0-100 — this is what makes dominance DURABLE.
#   3. WORKFORCE POTENTIAL — mean potential_index (capacity to keep extending
#                            the lead).
#   4. MENTAL STRENGTH  — mean mental_strength (execution durability under
#                         pressure).
#   5. BUILDER ORIGINS  — mean adversity_origin_score (hungry, disruptive
#                         culture vs complacent incumbent).
#
# Dominance + moat carry most of the weight (they ARE global dominance);
# workforce character is the multiplier deciding who extends the lead. Weights
# are an explicit editorial choice — tweak and re-run to test sensitivity.
# --------------------------------------------------------------------------
# Curated "strategic moat / global chokehold" (0-100): how indispensable the
# company is to the world economy, mid-2026. Rationale per company in report.
STRATEGIC_MOAT = {
    "NVIDIA": 95,             # controls AI compute — the chokepoint of the AI era
    "TSMC": 90,              # fabricates ~all leading-edge chips; ultimate chokepoint
    "Alphabet (Google)": 86,  # search/ads/Android/cloud — the information layer
    "Microsoft": 85,         # Windows/Office/Azure enterprise lock-in
    "Apple": 84,             # iOS ecosystem + services lock-in across ~2.2bn devices
    "Amazon": 82,            # e-commerce + AWS, backbone of the internet
    "Meta Platforms": 74,    # ~4bn users; the global attention/social chokepoint
    "Saudi Aramco": 70,      # swing producer of world oil; declining-sector dependence
    "Broadcom": 66,          # critical networking + custom AI silicon infrastructure
    "Tesla": 55,             # strong EV/energy brand but the most contestable position
    "OpenAI": 90,           # frontier-model leader + ChatGPT, the consumer face of AI
    "SpaceX": 86,           # launch near-monopoly + Starlink global comms + xAI frontier AI
}

WEIGHTS = {"dominance": 0.34, "moat": 0.34, "potential": 0.14,
           "mental": 0.10, "builder": 0.08}


def scale_0_100(s: pd.Series) -> pd.Series:
    lo, hi = s.min(), s.max()
    if hi == lo:
        return pd.Series(50.0, index=s.index)
    return ((s - lo) / (hi - lo) * 100).round(1)


tyrell = pd.DataFrame(index=order)
tyrell["dominance"] = scale_0_100(companies.set_index("company").reindex(order)["valuation_usd_trillions"])
tyrell["moat"] = pd.Series(STRATEGIC_MOAT).reindex(order)
tyrell["potential"] = scale_0_100(summary["potential_mean"])
tyrell["mental"] = scale_0_100(summary["mental_strength_mean"])
tyrell["builder"] = scale_0_100(summary["adversity_origin_mean"])
tyrell["tyrell_index"] = sum(tyrell[k] * w for k, w in WEIGHTS.items()).round(1)
tyrell = tyrell.sort_values("tyrell_index", ascending=False)
tyrell["rank"] = range(1, len(tyrell) + 1)
tyrell.to_csv(os.path.join(DATA, "tyrell_index.csv"))
print("\n=== TYRELL INDEX (who becomes Tyrell Corp?) ===")
print(tyrell.to_string())

# Tyrell chart — stacked weighted contributions
fig, ax = plt.subplots(figsize=(12, 6))
t_lab = [short.get(c, c) for c in tyrell.index]
bottom = np.zeros(len(tyrell))
pillar_colors = {"dominance": "#2c3e50", "moat": "#8e44ad", "potential": "#2980b9",
                 "mental": "#c0392b", "builder": "#d68910"}
for k, w in WEIGHTS.items():
    vals = (tyrell[k] * w).values
    ax.bar(t_lab, vals, bottom=bottom, label=f"{k} (w={w})", color=pillar_colors[k])
    bottom += vals
for i, v in enumerate(tyrell["tyrell_index"].values):
    ax.text(i, bottom[i], f"{v:.1f}", ha="center", va="bottom", fontsize=9, fontweight="bold")
ax.set_title("THE TYRELL INDEX — which company becomes the Tyrell Corporation?",
             fontsize=13, fontweight="bold")
ax.set_ylabel("weighted score (0-100)")
ax.set_xticks(range(len(t_lab)))
ax.set_xticklabels(t_lab, rotation=35, ha="right")
ax.legend(loc="upper right", fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "tyrell_index.png"), dpi=110)
plt.close(fig)
print("wrote tyrell_index.png")

with open(os.path.join(DATA, "headline_stats.json"), "w") as f:
    headline["tyrell_index"] = tyrell["tyrell_index"].to_dict()
    headline["tyrell_winner"] = [tyrell.index[0], float(tyrell["tyrell_index"].iloc[0])]
    headline["tyrell_runner_up"] = [tyrell.index[1], float(tyrell["tyrell_index"].iloc[1])]
    json.dump(headline, f, indent=2, default=str)
