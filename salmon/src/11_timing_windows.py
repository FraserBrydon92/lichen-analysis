"""
Catch timing windows by zone.

Inputs : zones
Outputs: outputs/figures/

Ported from the original working script `legacy/charts11.py` with the analysis and
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

from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
import pandas as pd, numpy as np, statsmodels.api as sm
GROUND="#081a24"; CREAM="#f2f7f8"; MIST="#9dbac6"; DIM="#5a7d8c"
AQUA="#3fd0c9"; CORAL="#ff6f5e"; GOLD="#f3c969"
SERIF=FONT_SERIF; SANS=FONT_SANS
plt.rcParams.update({"font.family":SANS,"figure.facecolor":GROUND,
                     "savefig.facecolor":GROUND,"axes.facecolor":GROUND,"text.color":CREAM})
z=load("zones"); r=np.log(z['aqua']/z['east']).dropna()
def sl(s,e):
    y=r.loc[s:e]; x=sm.add_constant(y.index.values.astype(float))
    m=sm.OLS(y.values,x).fit(cov_type='HAC',cov_kwds={'maxlags':3}); return m.params[1]*100,m.pvalues[1]
starts=list(range(1970,1996)); ends=list(range(2005,2026))
S=np.full((len(starts),len(ends)),np.nan); P=np.full_like(S,np.nan)
for i,s in enumerate(starts):
    for j,e in enumerate(ends):
        if e-s>=20: S[i,j],P[i,j]=sl(s,e)
cmap=LinearSegmentedColormap.from_list("d",[CORAL,"#7a3b45",GROUND,"#1d6b78",AQUA])
fig=plt.figure(figsize=(9.0,6.9))
ax=fig.add_axes([0.093,0.205,0.74,0.455])
im=ax.imshow(S,cmap=cmap,norm=TwoSlopeNorm(vcenter=0,vmin=-2.5,vmax=2.0),
             aspect='auto',origin='lower',interpolation='nearest')
ys,xs=np.where(P<0.05)
ax.scatter(xs,ys,s=5.5,c=CREAM,alpha=.75,linewidths=0,zorder=3)
i0,j0=starts.index(1980),ends.index(2010)
ax.add_patch(plt.Rectangle((j0-.5,i0-.5),1,1,fill=False,edgecolor=GOLD,linewidth=2.2,zorder=5))
ax.annotate("the window\nthis series used",xy=(j0,i0+.6),xytext=(j0-3.4,i0+7.6),
            fontsize=9.5,color=GOLD,linespacing=1.4,ha="center",zorder=6,
            arrowprops=dict(arrowstyle="-",color=GOLD,linewidth=1.1))
ax.set_xticks([ends.index(e) for e in (2005,2010,2015,2020,2025)]); ax.set_xticklabels([2005,2010,2015,2020,2025])
ax.set_yticks([starts.index(s) for s in (1970,1975,1980,1985,1990,1995)]); ax.set_yticklabels([1970,1975,1980,1985,1990,1995])
ax.tick_params(length=0,colors=MIST,labelsize=10)
for sp in ax.spines.values(): sp.set_visible(False)
ax.set_xlabel("last year of the window",fontsize=10.5,color=MIST,labelpad=8)
ax.set_ylabel("first year of the window",fontsize=10.5,color=MIST,labelpad=8)
cax=fig.add_axes([0.858,0.205,0.022,0.455])
cb=fig.colorbar(im,cax=cax); cb.outline.set_visible(False)
cb.ax.tick_params(length=0,colors=MIST,labelsize=9.5)
cb.set_label("%/yr change in the west-to-east ratio",fontsize=9.5,color=MIST,labelpad=10)
fig.text(0.885,0.675,"west falls\nbehind",fontsize=9,color=CORAL,ha="center",va="bottom",linespacing=1.35)
fig.text(0.885,0.188,"west gains",fontsize=9,color=AQUA,ha="center",va="top")
fig.text(0.058,0.968,"ONE WINDOW IN FOUR SHOWS THE WEST FALLING BEHIND",
         fontsize=9.3,color=GOLD,ha="left",va="top",fontweight="700")
fig.text(0.058,0.930,"The farm-coast divergence depends on where you start and stop",
         fontsize=19,fontfamily=SERIF,fontweight="bold",color=CREAM,ha="left",va="top")
fig.text(0.058,0.868,
 "Every window of at least 20 years, fitted separately; a dot marks the fits that reach p<0.05. Of 491 windows,\n"
 "only 25% are both negative and significant, and the median is -0.24%/yr against the -1.07%/yr used here.",
 fontsize=10.2,color=MIST,ha="left",va="top",linespacing=1.55)
fig.add_artist(plt.Line2D([0.058,0.960],[0.088,0.088],color="#1b3d4e",linewidth=1.2,transform=fig.transFigure))
fig.text(0.058,0.068,
 "Source: author's analysis of Marine Directorate rod catch by district, 1952-2025. Each cell is an OLS fit of log(west catch / east catch) on year with\n"
 "Newey-West standard errors (3 lags). Blank cells are windows shorter than 20 years. The pre-1980 control period is flat under every window tested.",
 fontsize=8.3,color=DIM,ha="left",va="top",linespacing=1.6)
fig.savefig(f"{OUT}/salmon_14_windows.png",dpi=200)
print("wrote salmon_14_windows.png")
