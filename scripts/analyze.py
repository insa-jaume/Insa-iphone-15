#!/usr/bin/env python3
"""
analyze.py
==========
Reads data/all_employees.csv, computes per-company and cross-company
statistics on the three employee metrics, writes a summary table
(data/company_metrics_summary.csv) and renders charts into reports/figures/.

Also prints a JSON-ish block of headline numbers used to write the report.
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

METRICS = ["performance_score", "total_compensation_usd", "tenure_years"]

# Stable company order = market-cap rank.
companies = pd.read_csv(os.path.join(DATA, "companies.csv"))
order = companies["company"].tolist()
short = {  # short labels for charts
    "Alphabet (Google)": "Alphabet", "Saudi Aramco": "Aramco",
    "Meta Platforms": "Meta",
}
labels = [short.get(c, c) for c in order]

df = pd.read_csv(os.path.join(DATA, "all_employees.csv"))
df["company"] = pd.Categorical(df["company"], categories=order, ordered=True)


# --------------------------------------------------------------------------
# 1. Per-company summary table
# --------------------------------------------------------------------------
g = df.groupby("company", observed=True)
summary = pd.DataFrame({
    "headcount": g.size(),
    "perf_mean": g["performance_score"].mean().round(1),
    "perf_median": g["performance_score"].median().round(1),
    "comp_median_usd": g["total_compensation_usd"].median().round(0).astype(int),
    "comp_mean_usd": g["total_compensation_usd"].mean().round(0).astype(int),
    "comp_p90_usd": g["total_compensation_usd"].quantile(0.90).round(0).astype(int),
    "tenure_mean_yrs": g["tenure_years"].mean().round(1),
    "tenure_median_yrs": g["tenure_years"].median().round(1),
    "pct_high_performers": (g["performance_score"].apply(lambda s: (s >= 85).mean() * 100)).round(1),
})
summary = summary.reindex(order)
summary = summary.merge(companies.set_index("company")[["market_cap_usd_trillions", "sector"]],
                        left_index=True, right_index=True)
summary.to_csv(os.path.join(DATA, "company_metrics_summary.csv"))
print(summary.to_string())


# --------------------------------------------------------------------------
# 2. Correlations (pooled, and per-company comp~performance)
# --------------------------------------------------------------------------
pooled_corr = df[METRICS].corr().round(3)
percompany_comp_perf = g.apply(
    lambda d: np.corrcoef(d["total_compensation_usd"], d["performance_score"])[0, 1],
    include_groups=False).round(3)

# Comp efficiency: market cap ($bn) per $ of median comp — a rough
# "value created per compensation dollar" proxy.
mc = companies.set_index("company")["market_cap_usd_trillions"] * 1_000_000  # to $M
cap_per_comp = (mc / summary["comp_median_usd"]).round(1)  # $M cap per $ median comp


# --------------------------------------------------------------------------
# 3. Charts
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


barchart(summary["comp_median_usd"], "Median total annual compensation (USD)",
         "USD", "comp_median.png", fmt=lambda v: f"${v/1000:.0f}k", color="#2e7d32")
barchart(summary["perf_mean"], "Mean performance score (0–100)",
         "score", "perf_mean.png", fmt=lambda v: f"{v:.1f}", color="#3b6ea5")
barchart(summary["tenure_median_yrs"], "Median tenure (years)",
         "years", "tenure_median.png", fmt=lambda v: f"{v:.1f}", color="#b05a2e")

# Compensation distribution (box plot) ordered by market cap.
fig, ax = plt.subplots(figsize=(11, 5.5))
data_by_co = [df.loc[df["company"] == c, "total_compensation_usd"] / 1000 for c in order]
ax.boxplot(data_by_co, tick_labels=labels, showfliers=False)
ax.set_title("Compensation distribution by company (k USD, outliers hidden)",
             fontsize=13, fontweight="bold")
ax.set_ylabel("total comp (k USD)")
ax.set_xticklabels(labels, rotation=35, ha="right")
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "comp_distribution_box.png"), dpi=110)
plt.close(fig)
print("wrote comp_distribution_box.png")

# Scatter: tenure (x) vs median comp (y), bubble size = market cap.
fig, ax = plt.subplots(figsize=(9, 6))
sizes = (companies.set_index("company").reindex(order)["market_cap_usd_trillions"] * 120).values
sc = ax.scatter(summary["tenure_median_yrs"], summary["comp_median_usd"] / 1000,
                s=sizes, alpha=0.6, c=range(len(order)), cmap="viridis")
for i, c in enumerate(labels):
    ax.annotate(c, (summary["tenure_median_yrs"].iloc[i], summary["comp_median_usd"].iloc[i] / 1000),
                fontsize=8, xytext=(4, 4), textcoords="offset points")
ax.set_xlabel("median tenure (years)")
ax.set_ylabel("median total comp (k USD)")
ax.set_title("Tenure vs compensation (bubble = market cap)", fontsize=13, fontweight="bold")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "tenure_vs_comp.png"), dpi=110)
plt.close(fig)
print("wrote tenure_vs_comp.png")


# --------------------------------------------------------------------------
# 4. Headline numbers for the report
# --------------------------------------------------------------------------
headline = {
    "total_employees": int(len(df)),
    "companies": len(order),
    "pooled_correlations": pooled_corr.to_dict(),
    "per_company_comp_perf_corr": percompany_comp_perf.to_dict(),
    "highest_median_comp": [summary["comp_median_usd"].idxmax(), int(summary["comp_median_usd"].max())],
    "lowest_median_comp": [summary["comp_median_usd"].idxmin(), int(summary["comp_median_usd"].min())],
    "longest_tenure": [summary["tenure_median_yrs"].idxmax(), float(summary["tenure_median_yrs"].max())],
    "shortest_tenure": [summary["tenure_median_yrs"].idxmin(), float(summary["tenure_median_yrs"].min())],
    "cap_per_median_comp_$M": cap_per_comp.to_dict(),
}
print("\n=== HEADLINE ===")
print(json.dumps(headline, indent=2, default=str))
with open(os.path.join(DATA, "headline_stats.json"), "w") as f:
    json.dump(headline, f, indent=2, default=str)
