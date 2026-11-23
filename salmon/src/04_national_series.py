"""
The 73-year national series, and catch by aquaculture zone.

Inputs : national, zones
Outputs: outputs/figures/

Ported from the original working script `legacy/charts4.py` with the analysis and
figure code unchanged. Only the plumbing differs: paths now resolve from the
repository root, the processed datasets are read from CSV rather than pickle,
and the display fonts fall back when they are not installed.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from repo import DATA, FIGS, load, load_series, use_font, save  # noqa: F401
import matplotlib
import matplotlib.pyplot as plt

OUT = str(FIGS)
FONT_SANS = use_font("Inter")
FONT_SERIF = use_font("Caladea", "DejaVu Serif")

import pandas as pd, numpy as np, os

GROUND = "#081a24"; CREAM = "#f2f7f8"; MIST = "#9dbac6"; DIM = "#5a7d8c"
AQUA = "#3fd0c9"; AQUA_D = "#1b8ca8"; CORAL = "#ff6f5e"; GOLD = "#f3c969"
SERIF = FONT_SERIF; SANS = FONT_SANS

plt.rcParams.update({"font.family": SANS, "figure.facecolor": GROUND,
                     "savefig.facecolor": GROUND, "axes.facecolor": GROUND,
                     "text.color": CREAM})


def furniture(fig, title, subtitle, source, kicker=None):
    y = 0.962
    if kicker:
        fig.text(0.062, y, kicker.upper(), fontsize=10, color=AQUA,
                 ha="left", va="top", fontweight="700")
        y -= 0.055
    fig.text(0.062, y, title, fontsize=20, fontfamily=SERIF,
             fontweight="bold", color=CREAM, ha="left", va="top")
    fig.text(0.062, y - 0.072, subtitle, fontsize=11.5, color=MIST,
             ha="left", va="top")
    fig.add_artist(plt.Line2D([0.062, 0.95], [0.108, 0.108], color="#1b3d4e",
                              linewidth=1.2, transform=fig.transFigure))
    fig.text(0.062, 0.088, source, fontsize=8.6, color=DIM, ha="left",
             va="top", linespacing=1.6)


def save(fig, name):
    fig.savefig(f"{OUT}/{name}", dpi=200); plt.close(fig); print("wrote", name)


def style(ax):
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0, colors=MIST, labelsize=10.5)


nat = load_series("national")
z = load("zones")

# ===================================================== 1. 73-YEAR SERIES
fig, ax = plt.subplots(figsize=(8.4, 5.6))
fig.subplots_adjust(left=0.095, right=0.955, top=0.695, bottom=0.165)
style(ax)
for gy in range(20000, 130000, 20000):
    ax.axhline(gy, color="#15394b", linewidth=1, zorder=1)
    ax.text(1950.0, gy, f"{gy//1000}k", ha="right", va="center",
            fontsize=10, color=DIM)

x = nat.index.values.astype(float); y = nat.values.astype(float)
ax.fill_between(x, 0, y, color=AQUA_D, alpha=0.22, zorder=2)
for w, a in [(8, 0.07), (5, 0.11)]:
    ax.plot(x, y, color=AQUA, linewidth=w, alpha=a, zorder=3)
ax.plot(x, y, color=AQUA, linewidth=2.1, zorder=4)

ax.scatter([2010], [111405], s=120, color=GOLD, zorder=6)
ax.annotate("2010 peak\n111,405", (2010, 111405), textcoords="offset points",
            xytext=(-14, 10), ha="right", fontsize=10.5, color=GOLD,
            linespacing=1.4, fontweight="600")
ax.scatter([2025], [28020], s=150, color=CORAL, zorder=6)
ax.annotate("2025\n28,020", (2025, 28020), textcoords="offset points",
            xytext=(-6, -42), ha="right", fontsize=11.5, color=CORAL,
            linespacing=1.4, fontweight="700")

ax.set_xlim(1950, 2028); ax.set_ylim(0, 125000)
ax.set_yticks([]); ax.set_xticks([1952, 1970, 1990, 2010, 2025])
ax.set_xticklabels(["1952", "1970", "1990", "2010", "2025"])

furniture(fig, "Seventy-three years of Scottish salmon",
          "Reported rod catch of wild Atlantic salmon, Scotland, all districts, retained and released",
          "Source: Marine Directorate, Scottish Government, rod catch by district and month, 1952-2025.\n"
          "Wild fish only; farmed-origin fish are reported separately and excluded here.",
          kicker="2025 was the lowest season on record")
save(fig, "salmon_05_series.png")


# ================================================= 2. WEST vs EAST INDEX
base = z.loc[1952:1970].mean()
idx = z / base * 100
roll = idx.rolling(5, center=True, min_periods=3).mean()

fig, ax = plt.subplots(figsize=(8.4, 5.9))
fig.subplots_adjust(left=0.095, right=0.955, top=0.665, bottom=0.185)
style(ax)

ax.axvspan(1980, 2010, color="#102f3e", zorder=1)
ax.text(1995, 193, "aquaculture expansion", ha="center", fontsize=10,
        color=DIM, style="italic")

for gy in [50, 100, 150]:
    ax.axhline(gy, color="#15394b", linewidth=1, zorder=2)
    ax.text(1950.5, gy, f"{gy}", ha="right", va="center", fontsize=10, color=DIM)
ax.axhline(100, color="#2a5468", linewidth=1.3, zorder=2)

ax.plot(idx.index, idx["east"], color=GOLD, linewidth=0.9, alpha=0.28, zorder=3)
ax.plot(idx.index, idx["aqua"], color=CORAL, linewidth=0.9, alpha=0.28, zorder=3)
ax.plot(roll.index, roll["east"], color=GOLD, linewidth=2.8, zorder=5)
ax.plot(roll.index, roll["aqua"], color=CORAL, linewidth=2.8, zorder=5)

ax.set_xlim(1950, 2026); ax.set_ylim(20, 205)
ax.set_yticks([]); ax.set_xticks([1952, 1970, 1990, 2010, 2025])
ax.set_xticklabels(["1952", "1970", "1990", "2010", "2025"])

ax.text(1999, 168, "east and south \u2014 no salmon farms", ha="center",
        va="bottom", fontsize=11, color=GOLD, fontweight="700")
ax.text(1999, 62, "west coast and islands", ha="center", va="top",
        fontsize=11, color=CORAL, fontweight="700")

furniture(fig, "The west pulled away from the east. Then both fell.",
          "Rod catch indexed to each zone's own 1952–1970 average = 100, five-year rolling mean",
          "Source: Marine Directorate rod catch by district, 1952-2025. West = West Coast, North West, Outer Hebrides, Shetland, Clyde Coast.\n"
          "East and south = East, North East, Moray Firth, Solway; North excluded as mixed. Catch is not abundance, so this is an association.",
          kicker="1980–2010: west fell 1.1% a year against the east, p=0.009")
save(fig, "salmon_06_west_east.png")
