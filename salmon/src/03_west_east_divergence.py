"""
West coast against east coast: the divergence in rod catch.

Inputs : data embedded in the script
Outputs: outputs/figures/

Ported from the original working script `legacy/charts3.py` with the analysis and
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

from matplotlib.path import Path
from matplotlib.patches import PathPatch, Circle
import numpy as np
import os


# ---- deep-water palette ---------------------------------------------------
GROUND = "#081a24"
PANEL  = "#0d2634"
CREAM  = "#f2f7f8"
MIST   = "#9dbac6"
DIM    = "#5a7d8c"
AQUA   = "#3fd0c9"
AQUA_D = "#1b8ca8"
DEEPB  = "#14465c"
CORAL  = "#ff6f5e"
GOLD   = "#f3c969"

SERIF = FONT_SERIF
SANS  = FONT_SANS

plt.rcParams.update({
    "font.family": SANS,
    "figure.facecolor": GROUND,
    "savefig.facecolor": GROUND,
    "axes.facecolor": GROUND,
    "text.color": CREAM,
})


def furniture(fig, title, subtitle, source, kicker=None):
    y = 0.962
    if kicker:
        fig.text(0.058, y, kicker.upper(), fontsize=10, color=AQUA,
                 ha="left", va="top", fontweight="700")
        y -= 0.052
    fig.text(0.058, y, title, fontsize=20, fontfamily=SERIF, fontweight="bold",
             color=CREAM, ha="left", va="top")
    fig.text(0.058, y - 0.072, subtitle, fontsize=11.5, color=MIST,
             ha="left", va="top")
    fig.add_artist(plt.Line2D([0.058, 0.95], [0.105, 0.105], color="#1b3d4e",
                              linewidth=1.2, transform=fig.transFigure))
    fig.text(0.058, 0.085, source, fontsize=8.6, color=DIM, ha="left",
             va="top", linespacing=1.6)


def save(fig, name):
    fig.savefig(f"{OUT}/{name}", dpi=200)
    plt.close(fig)
    print("wrote", name)


def blank(ax):
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)


# =========================================================== 1. RIVER DOTS
# Every assessed river in the North-East Atlantic, one dot each.
rows = [("Norway", 106, 190), ("Scotland", 47, 173), ("Ireland", 48, 144),
        ("England & Wales", 7, 58), ("Sweden", 3, 24),
        ("Northern Ireland", 10, 17), ("Tana / Teno", 0, 14)]

COLS = 38
fig, ax = plt.subplots(figsize=(8.2, 7.4))
fig.subplots_adjust(left=0.235, right=0.915, top=0.745, bottom=0.145)
blank(ax)

y = 0.0
ytick_pos, ytick_lab = [], []
for name, pass_n, total in rows:
    nrows = int(np.ceil(total / COLS))
    block_top = y
    for i in range(total):
        r, c = divmod(i, COLS)
        cx, cy = c, -(y + r)
        attained = i < pass_n
        if attained:
            ax.add_patch(Circle((cx, cy), 0.36, facecolor=AQUA,
                                edgecolor="none", zorder=3))
        else:
            ax.add_patch(Circle((cx, cy), 0.36, facecolor=PANEL,
                                edgecolor="#23566b", linewidth=0.8, zorder=2))
    ytick_pos.append(-(block_top + (nrows - 1) / 2))
    ytick_lab.append(name)
    y += nrows + 1.25

ax.set_xlim(-1.2, COLS + 5.2)
ax.set_ylim(-(y - 0.6), 1.2)
ax.set_aspect("equal")

for pos, lab in zip(ytick_pos, ytick_lab):
    strong = lab == "Scotland"
    ax.text(-2.2, pos, lab, ha="right", va="center",
            fontsize=12 if strong else 11,
            color=CORAL if strong else MIST,
            fontweight="700" if strong else "500")
    n_pass = dict((r[0], r[1]) for r in rows)[lab]
    n_tot = dict((r[0], r[2]) for r in rows)[lab]
    ax.text(COLS + 1.0, pos, f"{n_pass}/{n_tot}", ha="left", va="center",
            fontsize=10.5, color=DIM, fontfamily=SERIF)

# legend
ax.add_patch(Circle((0.0, 3.4), 0.36, facecolor=AQUA, edgecolor="none"))
ax.text(1.0, 3.4, "met its conservation limit", va="center", fontsize=10, color=MIST)
ax.add_patch(Circle((15.5, 3.4), 0.36, facecolor=PANEL,
                    edgecolor="#23566b", linewidth=0.8))
ax.text(16.5, 3.4, "did not", va="center", fontsize=10, color=MIST)

furniture(fig,
          "Every salmon river, counted",
          "Each dot is one river assessed against its own conservation limit, 2024",
          "Source: ICES advice to NASCO, 2025, Table 4. Scotland assessed on 2023 data.\n"
          "A conservation limit is the spawning stock a river needs to sustain itself.",
          kicker="620 rivers · 399 below the line")
save(fig, "salmon_01_rivers.png")


# ============================================================ 2. FISH UNITS
UNIT = 1000
series = [("2010", 111405, "#2e8fa8"), ("2024", 47618, "#2bb3b8"), ("2025", 28020, CORAL)]

fverts = [(1.00, 0.00),
          (0.55, 0.34), (0.18, 0.21),
          (0.09, 0.07), (-0.24, 0.31), (-0.06, 0.00), (-0.24, -0.31),
          (0.09, -0.07), (0.18, -0.21),
          (0.55, -0.34), (1.00, 0.00), (0.0, 0.0)]
fcodes = [Path.MOVETO,
          Path.CURVE3, Path.CURVE3,
          Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO,
          Path.LINETO, Path.LINETO,
          Path.CURVE3, Path.CURVE3, Path.CLOSEPOLY]
FISH = Path(fverts, fcodes)


def draw_fish(ax, x, y, s, color, alpha=1.0):
    tr = matplotlib.transforms.Affine2D().scale(s).translate(x, y) + ax.transData
    ax.add_patch(PathPatch(FISH, transform=tr, facecolor=color,
                           edgecolor="none", alpha=alpha, zorder=3))
    ax.add_patch(Circle((x + 0.66 * s, y + 0.085 * s), 0.052 * s,
                        facecolor=GROUND, edgecolor="none", zorder=4))


FCOLS = 24
fig, ax = plt.subplots(figsize=(8.2, 7.0))
fig.subplots_adjust(left=0.075, right=0.965, top=0.745, bottom=0.145)
blank(ax)

y = 0.0
for label, value, col in series:
    n = int(round(value / UNIT))
    nrows = int(np.ceil(n / FCOLS))
    ax.text(-0.9, -(y - 0.75), label, ha="left", va="bottom",
            fontsize=15, fontfamily=SERIF, fontweight="bold", color=CREAM)
    ax.text(2.3, -(y - 0.78), f"{value:,}", ha="left", va="bottom",
            fontsize=11.5, color=DIM)
    for i in range(n):
        r, c = divmod(i, FCOLS)
        draw_fish(ax, c * 1.0, -(y + r * 0.88), 0.74, col)
    y += nrows * 0.88 + 1.95

ax.set_xlim(-1.3, FCOLS + 0.2)
ax.set_ylim(-(y - 1.1), 1.6)
ax.set_aspect("equal")

furniture(fig,
          "A quarter of the salmon, fifteen years on",
          "Reported rod catch of wild Atlantic salmon, Scotland. Each fish = 1,000 caught",
          "Source: Salmon & sea trout fishery statistics 2025, Scottish Government.\n"
          "98% of the 2025 catch was released alive; rod effort fell only 5% between 2024 and 2025.",
          kicker="2025 was the lowest in 73 years")
save(fig, "salmon_02_catch_units.png")


# =============================================================== 3. FLOWS
def ribbon(ax, x0, x1, y0a, y0b, y1a, y1b, color, alpha=0.9):
    cx = (x0 + x1) / 2
    verts = [(x0, y0a), (cx, y0a), (cx, y1a), (x1, y1a),
             (x1, y1b), (cx, y1b), (cx, y0b), (x0, y0b), (x0, y0a)]
    codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4,
             Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4,
             Path.CLOSEPOLY]
    ax.add_patch(PathPatch(Path(verts, codes), facecolor=color,
                           edgecolor="none", alpha=alpha, zorder=2))


classes = [("2015 year class", 45465, 35963, 9502),
           ("2022 year class", 55261, 34151, 21110)]

fig, axes = plt.subplots(2, 1, figsize=(8.2, 7.2))
fig.subplots_adjust(left=0.075, right=0.80, top=0.70, bottom=0.145, hspace=0.42)
SCALE = 55261.0

for ax, (title, total, harv, lost) in zip(axes, classes):
    blank(ax)
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.60, 0.60)
    h = total / SCALE * 0.92
    top, bot = h / 2, -h / 2
    ax.add_patch(plt.Rectangle((0.25, bot), 0.42, h, facecolor=DEEPB,
                               edgecolor="none", zorder=3))
    hh = harv / SCALE * 0.92
    lh = lost / SCALE * 0.92
    ribbon(ax, 0.67, 8.2, top, top - lh, 0.52, 0.52 - lh, CORAL, 0.92)
    ribbon(ax, 0.67, 8.2, top - lh, bot, -0.06, -0.06 - hh, AQUA_D, 0.92)
    ax.add_patch(plt.Rectangle((8.2, 0.52 - lh), 0.42, lh, facecolor=CORAL,
                               edgecolor="none", zorder=3))
    ax.add_patch(plt.Rectangle((8.2, -0.06 - hh), 0.42, hh, facecolor=AQUA,
                               edgecolor="none", zorder=3))

    ax.text(0.46, top + 0.075, title, ha="center", va="bottom", fontsize=12.5,
            fontfamily=SERIF, fontweight="bold", color=CREAM)
    ax.text(0.46, bot - 0.075, f"{total/1000:.1f}m smolts", ha="center",
            va="top", fontsize=10.5, color=MIST)
    ax.text(8.85, 0.52 - lh / 2 + 0.075, "not harvested", ha="left", va="bottom",
            fontsize=10.5, color=CORAL, fontweight="600")
    ax.text(8.85, 0.52 - lh / 2 + 0.045, f"{lost/1000:.1f}m", ha="left",
            va="top", fontsize=15, fontfamily=SERIF, fontweight="bold",
            color=CORAL)
    ax.text(8.85, -0.06 - hh / 2 + 0.075, "harvested", ha="left", va="bottom",
            fontsize=10.5, color=AQUA, fontweight="600")
    ax.text(8.85, -0.06 - hh / 2 + 0.045, f"{harv/1000:.1f}m", ha="left",
            va="top", fontsize=15, fontfamily=SERIF, fontweight="bold",
            color=AQUA)

furniture(fig,
          "The same farms. Twice the losses.",
          "Scottish farmed Atlantic salmon: smolts put to sea, and where they ended up",
          "Source: Scottish Fish Farm Production Survey 2024, Scottish Government, Table 11. Harvested derived from smolts put to sea x survival.\n"
          "'Not harvested' covers mortality, escapes, culls, sampling and broodstock; the survey does not publish the split.",
          kicker="9.5m lost in 2015 · 21.1m in 2022")
save(fig, "salmon_03_flows.png")


# ============================================================ 4. SURVIVAL
yc = np.array([2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023])
surv = np.array([79.1, 76.6, 73.8, 77.5, 74.4, 75.9, 68.7, 61.8, 68.8])

fig, ax = plt.subplots(figsize=(8.2, 5.6))
fig.subplots_adjust(left=0.085, right=0.955, top=0.70, bottom=0.165)
ax.set_facecolor(GROUND)
for s in ax.spines.values():
    s.set_visible(False)

for gy in [60, 65, 70, 75, 80]:
    ax.axhline(gy, color="#16384a", linewidth=1, zorder=1)
    ax.text(2014.55, gy, f"{gy}%", ha="right", va="center", fontsize=10, color=DIM)

ax.fill_between(yc, 53, surv, color=AQUA_D, alpha=0.20, zorder=2)
for w, a in [(9, 0.06), (6, 0.10), (3.4, 0.22)]:
    ax.plot(yc, surv, color=AQUA, linewidth=w, alpha=a, zorder=3,
            solid_capstyle="round")
ax.plot(yc, surv, color=AQUA, linewidth=2.6, zorder=4, solid_capstyle="round")
ax.scatter(yc, surv, s=58, facecolor=GROUND, edgecolor=AQUA, linewidth=2.2, zorder=5)
ax.scatter([2022], [61.8], s=150, color=CORAL, zorder=6)

ax.set_xlim(2014.5, 2023.75)
ax.set_ylim(53, 86)
ax.set_yticks([])
ax.set_xticks(yc)
ax.set_xticklabels(yc, fontsize=10.5, color=MIST)
ax.tick_params(length=0)

ax.annotate("79.1%", (2015, 79.1), textcoords="offset points", xytext=(4, 16),
            fontsize=13, fontfamily=SERIF, fontweight="bold", color=CREAM)
ax.annotate("61.8%", (2022, 61.8), textcoords="offset points", xytext=(0, -30),
            ha="center", fontsize=14, fontfamily=SERIF, fontweight="bold", color=CORAL)
ax.annotate("worst in the series", (2022, 61.8), textcoords="offset points",
            xytext=(0, -48), ha="center", fontsize=9.5, color=CORAL)
ax.annotate("68.8%", (2023, 68.8), textcoords="offset points", xytext=(10, -4),
            fontsize=13, fontfamily=SERIF, fontweight="bold", color=CREAM)

furniture(fig,
          "Fewer farmed salmon survive to harvest",
          "Share of smolts put to sea that were harvested, Scotland, by input year class",
          "Source: Scottish Fish Farm Production Survey 2024 and 2025, Scottish Government, Table 11.\n"
          "'Not harvested' also covers escapes, culls, sampling and broodstock, so this is not a pure mortality rate.")
save(fig, "salmon_04_survival.png")
