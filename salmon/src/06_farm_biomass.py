"""
Farm locations and biomass on site over time.

Inputs : farms
Outputs: outputs/figures/

Ported from the original working script `legacy/charts6.py` with the analysis and
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

sea = load("farms")
act = sea[sea["Actual Biomass on Site (tonnes)"] > 0]
site = (act[act.yr >= 2021]
        .groupby(["SEPA Site", "Easting", "Northing", "Local Authority"])
        ["Actual Biomass on Site (tonnes)"].mean().reset_index())

# ============================================================== MAP
fig, ax = plt.subplots(figsize=(7.6, 9.2))
fig.subplots_adjust(left=0.04, right=0.97, top=0.775, bottom=0.095)
ax.set_facecolor(GROUND)
for s in ax.spines.values():
    s.set_visible(False)
ax.set_xticks([]); ax.set_yticks([])

ax.scatter(site.Easting, site.Northing,
           s=np.clip(site["Actual Biomass on Site (tonnes)"] / 2.1, 10, 220),
           color=CORAL, alpha=0.55, edgecolor="none", zorder=4)
ax.scatter(site.Easting, site.Northing, s=5, color=CREAM, alpha=0.75,
           edgecolor="none", zorder=5)

ax.axvline(0, color=GROUND)
ax.set_aspect("equal")
ax.set_xlim(45000, 500000)
ax.set_ylim(555000, 1245000)

labels = [(392000, 1168000, "Shetland", "right"),
          (288000, 1008000, "Orkney", "right"),
          (62000, 1000000, "Outer\nHebrides", "left"),
          (252000, 872000, "Skye and\nWester Ross", "left"),
          (272000, 712000, "Argyll", "left"),
          (268000, 628000, "Clyde", "left")]
for x, y, t, ha in labels:
    ax.text(x, y, t, fontsize=10.5, color=MIST, ha=ha, va="center",
            linespacing=1.4, zorder=6)

ax.annotate("Scotland's entire east coast\nhas no marine salmon farm",
            xy=(392000, 800000), fontsize=12, color=GOLD, ha="center",
            va="center", linespacing=1.5, fontweight="600", zorder=6)

ax.scatter([310000], [640000], s=30, color=CORAL, alpha=0.55, zorder=6)
ax.scatter([310000], [602000], s=180, color=CORAL, alpha=0.55, zorder=6)
ax.text(330000, 640000, "smaller site", fontsize=9.5, color=DIM, va="center")
ax.text(330000, 602000, "larger site", fontsize=9.5, color=DIM, va="center")

fig.text(0.055, 0.965, "324 FARMS, SIX LOCAL AUTHORITIES, ONE COAST",
         fontsize=10, color=AQUA, ha="left", va="top", fontweight="700")
fig.text(0.055, 0.925, "Where the salmon farms are",
         fontsize=21, fontfamily=SERIF, fontweight="bold", color=CREAM,
         ha="left", va="top")
fig.text(0.055, 0.874, "Every marine salmon farm site that has held fish, sized by average standing biomass, 2021–2025",
         fontsize=11, color=MIST, ha="left", va="top")
fig.add_artist(plt.Line2D([0.055, 0.96], [0.068, 0.068], color="#1b3d4e",
                          linewidth=1.2, transform=fig.transFigure))
fig.text(0.055, 0.052,
         "Source: SEPA monthly site returns, 2002-2025, plotted on the Ordnance Survey national grid. Sites: Shetland 103, Highland 72,\n"
         "Eilean Siar 61, Argyll and Bute 55, Orkney 32, North Ayrshire 1. No coastline is drawn; the shape is made by the farms themselves.",
         fontsize=8.4, color=DIM, ha="left", va="top", linespacing=1.6)
fig.savefig(f"{OUT}/salmon_08_map.png", dpi=200)
plt.close(fig); print("wrote salmon_08_map.png")

# ========================================================= BIOMASS TREND
b = sea.groupby("yr")["Actual Biomass on Site (tonnes)"].sum() / 12
b = b.loc[2002:2025]

fig, ax = plt.subplots(figsize=(8.4, 5.4))
fig.subplots_adjust(left=0.095, right=0.955, top=0.70, bottom=0.165)
for s in ax.spines.values():
    s.set_visible(False)
ax.tick_params(length=0, colors=MIST, labelsize=10.5)
for gy in range(25000, 150000, 25000):
    ax.axhline(gy, color="#15394b", linewidth=1, zorder=1)
    ax.text(2001.2, gy, f"{gy//1000}k", ha="right", va="center",
            fontsize=10, color=DIM)
ax.fill_between(b.index, 0, b.values, color=CORAL, alpha=0.20, zorder=2)
ax.plot(b.index, b.values, color=CORAL, linewidth=2.6, zorder=4)
ax.scatter([2002, 2025], [b.loc[2002], b.loc[2025]], s=110, color=CORAL, zorder=5)
ax.annotate(f"{b.loc[2002]:,.0f} t", (2002, b.loc[2002]), textcoords="offset points",
            xytext=(6, 14), fontsize=12, fontfamily=SERIF, fontweight="bold", color=CREAM)
ax.annotate(f"{b.loc[2025]:,.0f} t", (2025, b.loc[2025]), textcoords="offset points",
            xytext=(-6, 16), ha="right", fontsize=12, fontfamily=SERIF,
            fontweight="bold", color=CREAM)
ax.set_xlim(2001, 2026.5); ax.set_ylim(0, 150000)
ax.set_yticks([]); ax.set_xticks([2002, 2008, 2014, 2020, 2025])
ax.set_xticklabels(["2002", "2008", "2014", "2020", "2025"])

fig.text(0.062, 0.962, "STANDING BIOMASS HAS NEARLY TRIPLED SINCE 2002",
         fontsize=10, color=AQUA, ha="left", va="top", fontweight="700")
fig.text(0.062, 0.907, "More fish in the water, all of it on one coast",
         fontsize=20, fontfamily=SERIF, fontweight="bold", color=CREAM,
         ha="left", va="top")
fig.text(0.062, 0.835, "Average salmon held in Scottish marine pens, tonnes, mean of monthly site returns",
         fontsize=11.5, color=MIST, ha="left", va="top")
fig.add_artist(plt.Line2D([0.062, 0.955], [0.108, 0.108], color="#1b3d4e",
                          linewidth=1.2, transform=fig.transFigure))
fig.text(0.062, 0.088,
         "Source: SEPA monthly site returns, seawater sites, 2002-2025. Standing biomass is the stock held at a point in time,\n"
         "not annual production; the two differ because fish are harvested and restocked through the year.",
         fontsize=8.6, color=DIM, ha="left", va="top", linespacing=1.6)
fig.savefig(f"{OUT}/salmon_09_biomass.png", dpi=200)
plt.close(fig); print("wrote salmon_09_biomass.png")
