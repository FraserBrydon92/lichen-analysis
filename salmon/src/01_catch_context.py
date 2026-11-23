"""
Rod catch context: rivers, catch units and the long series.

Inputs : data embedded in the script
Outputs: outputs/figures/

Ported from the original working script `legacy/charts.py` with the analysis and
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

from matplotlib.ticker import FuncFormatter
import os


SURFACE   = "#fcfcfb"
INK       = "#0b0b0b"
SECOND    = "#52514e"
MUTED     = "#898781"
GRID      = "#e1e0d9"
BASELINE  = "#c3c2b7"
BLUE      = "#2a78d6"
ORANGE    = "#eb6834"
BLUE_PALE = "#9ec5f4"

plt.rcParams.update({
    "font.family": FONT_SANS,
    "font.size": 10,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "axes.edgecolor": BASELINE,
    "axes.labelcolor": SECOND,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "text.color": INK,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.spines.left": False,
    "xtick.bottom": False,
    "ytick.left": False,
})

thousands = FuncFormatter(lambda v, p: f"{int(v):,}")


def frame(ax, title, subtitle, source, ygrid=True):
    ax.set_title("")
    ax.figure.text(0.055, 0.955, title, fontsize=15, fontweight="600",
                   color=INK, ha="left", va="top")
    ax.figure.text(0.055, 0.893, subtitle, fontsize=10.5, color=SECOND,
                   ha="left", va="top")
    ax.figure.text(0.055, 0.035, source, fontsize=8.5, color=MUTED,
                   ha="left", va="bottom")
    if ygrid:
        ax.yaxis.grid(True, color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
    for s in ax.spines.values():
        s.set_linewidth(0.8)


def save(fig, name):
    fig.savefig(f"{OUT}/{name}", dpi=200, bbox_inches=None)
    plt.close(fig)
    print("wrote", name)


# ---------------------------------------------------------------- Chart 1
# Survival to harvest, Scottish farmed salmon, by input year class
yc = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]
surv = [79.1, 76.6, 73.8, 77.5, 74.4, 75.9, 68.7, 61.8, 68.8]

fig, ax = plt.subplots(figsize=(7.2, 4.9))
fig.subplots_adjust(left=0.1, right=0.955, top=0.76, bottom=0.17)
ax.plot(yc, surv, color=BLUE, linewidth=2.2, marker="o", markersize=7,
        markerfacecolor=BLUE, markeredgecolor=SURFACE, markeredgewidth=2,
        zorder=3, solid_capstyle="round")
ax.set_ylim(55, 85)
ax.set_xticks(yc)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{int(v)}%"))
for x, y, lab in [(2015, 79.1, "79.1%"), (2022, 61.8, "61.8%"), (2023, 68.8, "68.8%")]:
    off = -16 if x == 2022 else 12
    ax.annotate(lab, (x, y), textcoords="offset points", xytext=(0, off),
                ha="center", fontsize=10, fontweight="600", color=INK)
frame(ax,
      "Fewer farmed salmon are surviving to harvest",
      "Share of smolts put to sea that were harvested, Scotland, by input year class",
      "Source: Scottish Fish Farm Production Survey 2024 and 2025, Scottish Government.\n"
      "'Not harvested' also covers escapes, culls, sampling and broodstock, so this is not a pure mortality rate.")
save(fig, "salmon_01_survival_to_harvest.png")


# ---------------------------------------------------------------- Chart 2
# Put to sea vs harvested, by complete input year class
yc2 = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022]
to_sea = [45465, 42957, 46116, 45513, 52990, 52492, 51131, 55261]
pct = [79.1, 76.6, 73.8, 77.5, 74.4, 75.9, 68.7, 61.8]
harvested = [round(t * p / 100) for t, p in zip(to_sea, pct)]
lost = [t - h for t, h in zip(to_sea, harvested)]

fig, ax = plt.subplots(figsize=(7.2, 5.1))
fig.subplots_adjust(left=0.115, right=0.955, top=0.74, bottom=0.2)
x = range(len(yc2))
ax.bar(x, harvested, width=0.62, color=BLUE, label="Harvested",
       edgecolor=SURFACE, linewidth=2, zorder=3)
ax.bar(x, lost, width=0.62, bottom=harvested, color=ORANGE,
       label="Not harvested", edgecolor=SURFACE, linewidth=2, zorder=3)
ax.set_xticks(list(x))
ax.set_xticklabels(yc2)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{int(v/1000)}m"))
ax.set_ylim(0, 62000)
ax.annotate(f"{lost[-1]/1000:.1f}m", (7, harvested[-1] + lost[-1] / 2),
            ha="center", va="center", fontsize=10, fontweight="600", color="#ffffff")
ax.annotate(f"{lost[0]/1000:.1f}m", (0, harvested[0] + lost[0] / 2),
            ha="center", va="center", fontsize=10, fontweight="600", color="#ffffff")
leg = ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(0, 1.085),
                ncol=2, fontsize=10, handlelength=1.1, handleheight=1.1,
                borderpad=0, columnspacing=1.4)
for t in leg.get_texts():
    t.set_color(SECOND)
frame(ax,
      "More smolts go in; a smaller share comes out",
      "Scottish farmed Atlantic salmon, millions of fish, by input year class",
      "Source: Scottish Fish Farm Production Survey 2024, Scottish Government, Table 11.\n"
      "Harvested derived from smolts put to sea x survival to harvest. 'Not harvested' includes\n"
      "mortality, escapes, culls, sampling and broodstock.")
save(fig, "salmon_02_put_to_sea_vs_harvested.png")


# ---------------------------------------------------------------- Chart 3
# Share of assessed rivers meeting conservation limits
rows = [
    ("Northern Ireland", 10, 17),
    ("Norway", 106, 190),
    ("Ireland", 48, 144),
    ("Scotland", 47, 173),
    ("Sweden", 3, 24),
    ("England & Wales", 7, 58),
    ("Tana / Teno", 0, 14),
]
rows.sort(key=lambda r: r[1] / r[2])
labels = [f"{r[0]}" for r in rows]
vals = [100 * r[1] / r[2] for r in rows]
counts = [f"{r[1]} of {r[2]}" for r in rows]
colors = [BLUE if r[0] == "Scotland" else BLUE_PALE for r in rows]

fig, ax = plt.subplots(figsize=(7.2, 4.9))
fig.subplots_adjust(left=0.235, right=0.93, top=0.76, bottom=0.17)
bars = ax.barh(labels, vals, height=0.62, color=colors, zorder=3)
ax.xaxis.grid(True, color=GRID, linewidth=0.8)
ax.yaxis.grid(False)
ax.set_axisbelow(True)
ax.set_xlim(0, 70)
ax.xaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{int(v)}%"))
for b, v, c, lab in zip(bars, vals, counts, labels):
    ax.annotate(f"{v:.0f}%   {c}", (v, b.get_y() + b.get_height() / 2),
                textcoords="offset points", xytext=(7, 0), va="center",
                fontsize=9.5, color=INK if lab == "Scotland" else SECOND,
                fontweight="600" if lab == "Scotland" else "normal")
for t in ax.get_yticklabels():
    if t.get_text() == "Scotland":
        t.set_color(INK)
        t.set_fontweight("600")
    else:
        t.set_color(SECOND)
ax.tick_params(axis="y", labelsize=10)
frame(ax,
      "Most salmon rivers are below their conservation limit",
      "Share of assessed rivers attaining their river-specific conservation limit, 2024",
      "Source: ICES advice to NASCO, 2025, Table 4. Scotland assessed on 2023 data.\n"
      "Across the 620 rivers assessed in the North-East Atlantic, 399 did not attain their limit.",
      ygrid=False)
save(fig, "salmon_03_conservation_limits.png")


# ---------------------------------------------------------------- Chart 4
# Scottish wild salmon rod catch, selected years
yrs = ["2010", "2024", "2025"]
catch = [111405, 47618, 28020]
fig, ax = plt.subplots(figsize=(7.2, 4.9))
fig.subplots_adjust(left=0.125, right=0.955, top=0.76, bottom=0.17)
cols = [BLUE_PALE, BLUE_PALE, BLUE]
bars = ax.bar(yrs, catch, width=0.5, color=cols, zorder=3)
ax.yaxis.set_major_formatter(thousands)
ax.set_ylim(0, 125000)
for b, v in zip(bars, catch):
    ax.annotate(f"{v:,}", (b.get_x() + b.get_width() / 2, v),
                textcoords="offset points", xytext=(0, 7), ha="center",
                fontsize=11, fontweight="600", color=INK)
ax.annotate("peak year", (0, 111405), textcoords="offset points",
            xytext=(0, 26), ha="center", fontsize=9.5, color=MUTED)
frame(ax,
      "The 2025 rod catch was the lowest since records began in 1952",
      "Reported rod catch of wild Atlantic salmon, Scotland, number of fish",
      "Source: Salmon & sea trout fishery statistics 2025, Scottish Government.\n"
      "98% of the 2025 rod catch was released. Rod effort fell only 5% between 2024 and 2025.")
save(fig, "salmon_04_rod_catch.png")

print("\nderived check:")
for y, t, h, l in zip(yc2, to_sea, harvested, lost):
    print(f"  {y}: to sea {t:,}k  harvested {h:,}k  not harvested {l:,}k ({100*l/t:.1f}%)")
