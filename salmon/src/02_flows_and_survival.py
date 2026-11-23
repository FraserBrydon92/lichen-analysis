"""
Marine survival and the flow of fish through the system.

Inputs : data embedded in the script
Outputs: outputs/figures/

Ported from the original working script `legacy/charts2.py` with the analysis and
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
from matplotlib.patches import FancyArrowPatch
import os


# --- subject palette: North Atlantic water, with coral for loss -------------
PAPER   = "#ffffff"
PLOT    = "#f4f7f8"
INK     = "#0d2b38"
INK2    = "#4a6570"
INK3    = "#8ba0a9"
GRID    = "#dde7ea"
DEEP    = "#0f3a4d"
RIVER   = "#1d6f8e"
MID     = "#3b9ab5"
PALE    = "#aad2de"
PALER   = "#d3e7ed"
CORAL   = "#d9614a"
CORAL_P = "#eda georgia"  # placeholder, unused

SERIF = FONT_SERIF
SANS  = FONT_SANS

plt.rcParams.update({
    "font.family": SANS,
    "font.size": 11,
    "figure.facecolor": PAPER,
    "savefig.facecolor": PAPER,
    "axes.facecolor": PAPER,
    "text.color": INK,
    "axes.edgecolor": GRID,
    "xtick.color": INK2,
    "ytick.color": INK3,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.spines.left": False,
    "xtick.bottom": False,
    "ytick.left": False,
})


def furniture(fig, ax, title, subtitle, source):
    fig.text(0.062, 0.955, title, fontsize=19, fontfamily=SERIF,
             fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.062, 0.878, subtitle, fontsize=11.5, color=INK2,
             ha="left", va="top")
    fig.add_artist(plt.Line2D([0.062, 0.945], [0.108, 0.108],
                              color=GRID, linewidth=1.1,
                              transform=fig.transFigure))
    fig.text(0.062, 0.088, source, fontsize=8.8, color=INK3,
             ha="left", va="top", linespacing=1.55)
    for s in ax.spines.values():
        s.set_linewidth(1.0)


def save(fig, name):
    fig.savefig(f"{OUT}/{name}", dpi=200)
    plt.close(fig)
    print("wrote", name)


# ============================================================ 1. ROD CATCH
yrs = ["2010", "2024", "2025"]
catch = [111405, 47618, 28020]

fig, ax = plt.subplots(figsize=(7.6, 5.4))
fig.subplots_adjust(left=0.062, right=0.945, top=0.70, bottom=0.185)
bars = ax.bar(yrs, catch, width=0.46, color=[PALE, MID, DEEP], zorder=3)
ax.set_ylim(0, 138000)
ax.set_yticks([])
ax.set_xticks(range(3))
ax.set_xticklabels(yrs, fontsize=13, color=INK2)

for b, v in zip(bars, catch):
    ax.annotate(f"{v:,}", (b.get_x() + b.get_width() / 2, v),
                textcoords="offset points", xytext=(0, 10), ha="center",
                fontsize=15, fontfamily=SERIF, fontweight="bold", color=INK)

ax.annotate("peak year", (0, 111405), textcoords="offset points",
            xytext=(0, 34), ha="center", fontsize=10, color=INK3)
ax.annotate("lowest in the\n73-year record", (2, 28020),
            textcoords="offset points", xytext=(0, 34), ha="center",
            fontsize=10, color=CORAL, fontweight="600", linespacing=1.4)

arr = FancyArrowPatch((0.34, 126000), (1.94, 126000),
                      arrowstyle="-|>,head_width=3.4,head_length=7",
                      color=CORAL, linewidth=1.6,
                      connectionstyle="arc3,rad=-0.13", zorder=4)
ax.add_patch(arr)
ax.text(1.14, 134500, "down 75%", ha="center", va="bottom",
        fontsize=13, fontfamily=SERIF, fontstyle="italic", color=CORAL)

furniture(fig, ax,
          "Scotland's wild salmon catch has collapsed",
          "Reported rod catch of wild Atlantic salmon, Scotland, number of fish",
          "Source: Salmon & sea trout fishery statistics 2025, Scottish Government. Peak season and the two most recent shown.\n"
          "98% of the 2025 catch was released alive; rod effort fell only 5% between 2024 and 2025.")
save(fig, "salmon_01_rod_catch.png")


# ================================================== 2. SURVIVAL TO HARVEST
yc = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]
surv = [79.1, 76.6, 73.8, 77.5, 74.4, 75.9, 68.7, 61.8, 68.8]

fig, ax = plt.subplots(figsize=(7.6, 5.4))
fig.subplots_adjust(left=0.095, right=0.945, top=0.70, bottom=0.185)
ax.set_facecolor(PLOT)
ax.yaxis.grid(True, color="#ffffff", linewidth=1.4)
ax.set_axisbelow(True)

ax.fill_between(yc, 55, surv, color=RIVER, alpha=0.13, zorder=2)
ax.plot(yc, surv, color=RIVER, linewidth=2.8, zorder=3, solid_capstyle="round")
ax.plot(yc, surv, "o", markersize=8, markerfacecolor=PAPER,
        markeredgecolor=RIVER, markeredgewidth=2.4, zorder=4)
ax.plot([2022], [61.8], "o", markersize=10, color=CORAL, zorder=5)

ax.set_ylim(55, 88)
ax.set_xlim(2014.5, 2023.6)
ax.set_xticks(yc)
ax.set_xticklabels(yc, fontsize=10.5)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{int(v)}%"))
ax.tick_params(axis="y", labelsize=10.5)

ax.annotate("79.1%", (2015, 79.1), textcoords="offset points", xytext=(2, 14),
            ha="left", fontsize=12, fontfamily=SERIF, fontweight="bold", color=INK)
ax.annotate("61.8%", (2022, 61.8), textcoords="offset points", xytext=(0, -26),
            ha="center", fontsize=12, fontfamily=SERIF, fontweight="bold", color=CORAL)
ax.annotate("68.8%", (2023, 68.8), textcoords="offset points", xytext=(6, 4),
            ha="left", fontsize=12, fontfamily=SERIF, fontweight="bold", color=INK)
ax.annotate("worst in the series", (2022, 61.8), textcoords="offset points",
            xytext=(0, -42), ha="center", fontsize=9.5, color=CORAL)

furniture(fig, ax,
          "Fewer farmed salmon survive to harvest",
          "Share of smolts put to sea that were harvested, Scotland, by input year class",
          "Source: Scottish Fish Farm Production Survey 2024 and 2025, Scottish Government, Table 11.\n"
          "'Not harvested' also covers escapes, culls, sampling and broodstock, so this is not a pure mortality rate.")
save(fig, "salmon_02_survival.png")


# ============================================ 3. PUT TO SEA VS HARVESTED
yc2 = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022]
to_sea = [45465, 42957, 46116, 45513, 52990, 52492, 51131, 55261]
pct = [79.1, 76.6, 73.8, 77.5, 74.4, 75.9, 68.7, 61.8]
harv = [round(t * p / 100) for t, p in zip(to_sea, pct)]
lost = [t - h for t, h in zip(to_sea, harv)]

fig, ax = plt.subplots(figsize=(7.6, 5.6))
fig.subplots_adjust(left=0.095, right=0.945, top=0.695, bottom=0.185)
x = list(range(len(yc2)))
ax.bar(x, harv, width=0.58, color=RIVER, edgecolor=PAPER, linewidth=2.2, zorder=3)
ax.bar(x, lost, width=0.58, bottom=harv, color=CORAL, edgecolor=PAPER,
       linewidth=2.2, zorder=3)
ax.set_xticks(x)
ax.set_xticklabels(yc2, fontsize=10.5)
ax.set_yticks([])
ax.set_ylim(0, 68000)
ax.set_xlim(-0.72, 9.6)

ax.text(0, to_sea[0] + 1800, "9.5m", ha="center", va="bottom",
        fontsize=11.5, fontfamily=SERIF, fontweight="bold", color=CORAL, zorder=8)

ax.text(7.48, harv[-1] + lost[-1] / 2, "not harvested", ha="left", va="center",
        fontsize=11, fontweight="600", color=CORAL, zorder=8)
ax.text(7.48, harv[-1] + lost[-1] / 2 - 3400, "21.1m", ha="left", va="center",
        fontsize=14, fontfamily=SERIF, fontweight="bold", color=CORAL, zorder=8)
ax.text(7.48, harv[-1] / 2, "harvested", ha="left", va="center",
        fontsize=11, fontweight="600", color=RIVER, zorder=8)
ax.text(7.48, harv[-1] / 2 - 3400, "34.2m", ha="left", va="center",
        fontsize=14, fontfamily=SERIF, fontweight="bold", color=RIVER, zorder=8)

ax.annotate("", xy=(7.28, 62000), xytext=(0, 62000),
            arrowprops=dict(arrowstyle="-|>,head_width=0.22,head_length=0.5",
                            color=INK3, linewidth=1.3))
ax.text(3.6, 63500, "the gap more than doubles", ha="center", va="bottom",
        fontsize=11.5, fontfamily=SERIF, fontstyle="italic", color=INK2)

furniture(fig, ax,
          "More smolts go in. A smaller share comes out.",
          "Scottish farmed Atlantic salmon, millions of fish, by input year class",
          "Source: Scottish Fish Farm Production Survey 2024, Table 11. Harvested = smolts put to sea x survival to harvest.\n"
          "'Not harvested' includes mortality, escapes, culls, sampling and broodstock; the split is not published.")
save(fig, "salmon_03_put_to_sea.png")


# ============================================== 4. CONSERVATION LIMITS
rows = [("Northern Ireland", 10, 17), ("Norway", 106, 190), ("Ireland", 48, 144),
        ("Scotland", 47, 173), ("Sweden", 3, 24), ("England & Wales", 7, 58),
        ("Tana / Teno", 0, 14)]
rows.sort(key=lambda r: r[1] / r[2])
labels = [r[0] for r in rows]
vals = [100 * r[1] / r[2] for r in rows]
counts = [f"{r[1]} of {r[2]}" for r in rows]
cols = [CORAL if r[0] == "Scotland" else PALE for r in rows]

fig, ax = plt.subplots(figsize=(7.6, 5.4))
fig.subplots_adjust(left=0.235, right=0.945, top=0.695, bottom=0.185)
bars = ax.barh(labels, vals, height=0.56, color=cols, zorder=3)
ax.set_xlim(0, 78)
ax.set_xticks([])
ax.invert_yaxis()

for b, v, c, lab in zip(bars, vals, counts, labels):
    y = b.get_y() + b.get_height() / 2
    strong = lab == "Scotland"
    ax.annotate(f"{v:.0f}%", (v, y), textcoords="offset points", xytext=(9, 0),
                va="center", fontsize=13, fontfamily=SERIF, fontweight="bold",
                color=CORAL if strong else INK)
    ax.annotate(c, (v, y), textcoords="offset points", xytext=(46, 0),
                va="center", fontsize=10, color=INK3)

for t in ax.get_yticklabels():
    strong = t.get_text() == "Scotland"
    t.set_color(CORAL if strong else INK2)
    t.set_fontweight("700" if strong else "400")
    t.set_fontsize(11.5)

furniture(fig, ax,
          "Most salmon rivers are below their conservation limit",
          "Share of assessed rivers attaining their river-specific conservation limit, 2024",
          "Source: ICES advice to NASCO, 2025, Table 4. Scotland assessed on 2023 data.\n"
          "Of the 620 rivers assessed across the North-East Atlantic, 399 failed to attain their conservation limit.")
save(fig, "salmon_04_conservation_limits.png")
