"""
Sea trout catch timing, west against east.

Inputs : zones, trout_zones
Outputs: outputs/figures/

Ported from the original working script `legacy/charts5.py` with the analysis and
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

import pandas as pd, numpy as np

GROUND="#081a24"; CREAM="#f2f7f8"; MIST="#9dbac6"; DIM="#5a7d8c"
AQUA="#3fd0c9"; CORAL="#ff6f5e"; GOLD="#f3c969"
SERIF=FONT_SERIF; SANS=FONT_SANS
plt.rcParams.update({"font.family":SANS,"figure.facecolor":GROUND,
                     "savefig.facecolor":GROUND,"axes.facecolor":GROUND,
                     "text.color":CREAM})

sal = load("zones")
tro = load("trout_zones")

fig, axes = plt.subplots(2, 1, figsize=(8.4, 8.0), sharex=True)
fig.subplots_adjust(left=0.10, right=0.955, top=0.745, bottom=0.135, hspace=0.20)

panels = [(axes[0], sal, "Salmon", "no divergence before 1980; then the west falls away"),
          (axes[1], tro, "Sea trout", "the west had already gone by 1980")]

for ax, data, name, note in panels:
    base = data.loc[1952:1970].mean()
    idx = data / base * 100
    roll = idx.rolling(5, center=True, min_periods=3).mean()

    ax.axvspan(1980, 2010, color="#102f3e", zorder=1)
    for gy in [50, 100, 150]:
        ax.axhline(gy, color="#15394b", linewidth=1, zorder=2)
        ax.text(1950.5, gy, f"{gy}", ha="right", va="center", fontsize=9.5, color=DIM)
    ax.axhline(100, color="#2a5468", linewidth=1.3, zorder=2)

    ax.plot(idx.index, idx["east"], color=GOLD, linewidth=0.8, alpha=0.25, zorder=3)
    ax.plot(idx.index, idx["aqua"], color=CORAL, linewidth=0.8, alpha=0.25, zorder=3)
    ax.plot(roll.index, roll["east"], color=GOLD, linewidth=2.7, zorder=5)
    ax.plot(roll.index, roll["aqua"], color=CORAL, linewidth=2.7, zorder=5)

    ax.set_xlim(1950, 2026); ax.set_ylim(15, 200)
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0, colors=MIST, labelsize=10.5)

    ax.text(1951.5, 186, name, fontsize=15, fontfamily=SERIF,
            fontweight="bold", color=CREAM, va="top")
    ax.text(1951.5, 170, note, fontsize=10.5, color=MIST, va="top")

axes[0].text(1995, 192, "aquaculture expansion", ha="center", fontsize=9.5,
             color=DIM, style="italic", va="top")
axes[0].text(2024, 150, "east and south\nno salmon farms", ha="right", va="top",
             fontsize=10.5, color=GOLD, fontweight="700", linespacing=1.4)
axes[1].text(2024, 150, "west coast\nand islands", ha="right", va="top",
             fontsize=10.5, color=CORAL, fontweight="700", linespacing=1.4)

axes[1].set_xticks([1952, 1970, 1990, 2010, 2025])
axes[1].set_xticklabels(["1952", "1970", "1990", "2010", "2025"])

fig.text(0.062, 0.962, "SEA TROUT FELL FIRST, AND FELL BEFORE THE FARMS",
         fontsize=10, color=AQUA, ha="left", va="top", fontweight="700")
fig.text(0.062, 0.907, "Two species, one coastline, different timing",
         fontsize=20, fontfamily=SERIF, fontweight="bold", color=CREAM,
         ha="left", va="top")
fig.text(0.062, 0.835, "Rod catch indexed to each zone's own 1952–1970 average = 100, five-year rolling mean",
         fontsize=11.5, color=MIST, ha="left", va="top")
fig.add_artist(plt.Line2D([0.062, 0.955], [0.085, 0.085], color="#1b3d4e",
                          linewidth=1.2, transform=fig.transFigure))
fig.text(0.062, 0.068,
         "Source: Marine Directorate rod catch by district, 1952-2025. Sea trout includes finnock. Zones as defined in the previous chart.\n"
         "Sea trout catch is especially sensitive to angling effort, which is unrecorded before 2023.",
         fontsize=8.6, color=DIM, ha="left", va="top", linespacing=1.6)

fig.savefig(f"{OUT}/salmon_07_seatrout.png", dpi=200)
print("wrote salmon_07_seatrout.png")
