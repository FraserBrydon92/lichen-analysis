"""
Wild sea trout lice burden against farmed biomass.

Inputs : wildlice, farms
Outputs: outputs/figures/

Ported from the original working script `legacy/charts7.py` with the analysis and
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
from scipy import stats

GROUND="#081a24"; CREAM="#f2f7f8"; MIST="#9dbac6"; DIM="#5a7d8c"
AQUA="#3fd0c9"; CORAL="#ff6f5e"; GOLD="#f3c969"
SERIF=FONT_SERIF; SANS=FONT_SANS
plt.rcParams.update({"font.family":SANS,"figure.facecolor":GROUND,
                     "savefig.facecolor":GROUND,"axes.facecolor":GROUND,
                     "text.color":CREAM})

fish = load("wildlice"); fish = fish[(fish.yr>=1997)&(fish.yr<=2024)]
sea  = load("farms")
bio  = (sea.groupby("yr")["Actual Biomass on Site (tonnes)"].sum()/12).rename("biomass")
ann = pd.DataFrame({"pct_any": fish.assign(f=fish.total_lice>0).groupby("yr")["f"].mean()*100}
                   ).join(bio).dropna().sort_index()
dd = ann.diff().dropna()
x = dd.biomass.values/1000.0
y = dd.pct_any.values
r = stats.linregress(x, y)
pr, pp = stats.pearsonr(x, y)

fig, ax = plt.subplots(figsize=(8.4, 6.2))
fig.subplots_adjust(left=0.125, right=0.955, top=0.665, bottom=0.225)
for s in ax.spines.values():
    s.set_visible(False)
ax.tick_params(length=0, colors=MIST, labelsize=10.5)

ax.axhline(0, color="#2a5468", linewidth=1.2, zorder=2)
ax.axvline(0, color="#2a5468", linewidth=1.2, zorder=2)
for gy in [-20,-10,10,20]:
    ax.axhline(gy, color="#15394b", linewidth=0.9, zorder=1)

xs = np.linspace(x.min()-2, x.max()+2, 50)
ax.plot(xs, r.intercept + r.slope*xs, color=AQUA, linewidth=2.2,
        alpha=0.85, zorder=3)
ax.scatter(x, y, s=120, color=CORAL, alpha=0.9, edgecolor=GROUND,
           linewidth=1.5, zorder=5)
for xi, yi, yr_ in zip(x, y, dd.index.astype(int)):
    ax.annotate(str(yr_), (xi, yi), textcoords="offset points", xytext=(0, 11),
                ha="center", fontsize=8.5, color=DIM, zorder=6)

ax.set_xlabel("Change in farm standing biomass, thousand tonnes", fontsize=10.5,
              color=MIST, labelpad=12)
ax.set_ylabel("Change in share of wild sea trout carrying lice,\npercentage points",
              fontsize=10.5, color=MIST, labelpad=10, linespacing=1.5)
ax.set_xlim(x.min()-3, x.max()+3)
ax.set_ylim(-26, 26)

ax.text(0.975, 0.045, f"r = +{pr:.2f}   p = {pp:.3f}   n = {len(x)}",
        transform=ax.transAxes, fontsize=12.5, fontfamily=SERIF,
        fontweight="bold", color=AQUA, va="bottom", ha="right")

fig.text(0.062, 0.962, "YEARS WHEN FARM BIOMASS ROSE WERE YEARS WHEN LICE ROSE",
         fontsize=10, color=AQUA, ha="left", va="top", fontweight="700")
fig.text(0.062, 0.907, "The association survives removing the trend",
         fontsize=20, fontfamily=SERIF, fontweight="bold", color=CREAM,
         ha="left", va="top")
fig.text(0.062, 0.835,
         "Year-on-year change in each quantity, 2003–2024, with both series differenced",
         fontsize=11, color=MIST, ha="left", va="top")
fig.add_artist(plt.Line2D([0.062,0.955],[0.108,0.108], color="#1b3d4e",
                          linewidth=1.2, transform=fig.transFigure))
fig.text(0.062, 0.088,
         "Sources: lice measured on 26,068 individual wild sea trout, Marine Directorate Freshwater Laboratory sweep-net sampling, west coast and\n"
         "Western Isles; farm biomass from SEPA monthly site returns. Biomass is national and the lice sampling is not, so this is an association only.",
         fontsize=8.5, color=DIM, ha="left", va="top", linespacing=1.6)
fig.savefig(f"{OUT}/salmon_10_lice_biomass.png", dpi=200)
print("wrote salmon_10_lice_biomass.png")
print(f"slope {r.slope:+.3f} pp per kt, r={pr:+.3f}, p={pp:.4f}")
