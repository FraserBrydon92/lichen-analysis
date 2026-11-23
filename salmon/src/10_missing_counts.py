"""
Missing farm lice counts, and what the stated reasons imply.

Inputs : lice
Outputs: outputs/figures/

Ported from the original working script `legacy/charts10.py` with the analysis and
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
                     "savefig.facecolor":GROUND,"axes.facecolor":GROUND,"text.color":CREAM})

d=load("lice").copy(); d['v']=d['Weekly Average AF']
d=d.sort_values(['Site No','Year','Week No']).reset_index(drop=True)
d=d.join(d.groupby(['Site No','Year'])['v'].median().rename('med'),on=['Site No','Year'])
lut={k:dict(zip(g['Week No'],g['v'])) for k,g in d[d.v.notna()].groupby(['Site No','Year'])}
def neigh(s,y,w):
    m=lut.get((s,y))
    if not m: return np.nan
    vals=[m[w+k] for k in (-1,1,-2,2,-3,3) if (w+k) in m]
    return np.mean(vals) if vals else np.nan
d['nv']=[neigh(r._1,r.Year,r._6) for r in d.itertuples()]
ann=d.groupby('Year').apply(lambda g: pd.Series({
    'rep':g.v.mean(),'imp':g.v.fillna(g.nv).mean(),'nc':(1-g.v.notna().mean())*100}),
    include_groups=False)
rec=[(r._9,neigh(r._1,r.Year,r._6)-r.med) for r in d[d.v.isna()].itertuples() if np.isfinite(r.med)]
nb=pd.DataFrame(rec,columns=['reason','d']).dropna()
ctrl=(d[d.v.notna()].assign(x=lambda t:t.nv-t.med)).x.dropna().mean()
grp=nb.groupby('reason').agg(n=('d','size'),m=('d','mean')).query('n>=50').sort_values('m')
LAB={'Withdrawal period prior to harvesting':'Harvest withdrawal',
     'Veterinary advice':'Veterinary advice','Site recently stocked':'Recently stocked',
     'Weather':'Weather','Site fallow':'Site fallow',
     'Broodstock population visually inspected':'Broodstock'}

fig=plt.figure(figsize=(9.0,7.5))
ax =fig.add_axes([0.115,0.530,0.845,0.200])
ax2=fig.add_axes([0.300,0.190,0.620,0.245])

for s_ in ax.spines.values(): s_.set_visible(False)
ax.tick_params(length=0,colors=MIST,labelsize=10.5)
for gy in np.arange(0.2,0.81,0.2):
    ax.axhline(gy,color="#15394b",linewidth=1,zorder=1)
    ax.text(2020.70,gy,f"{gy:.1f}",ha="right",va="center",fontsize=10,color=DIM)
yrs=ann.index.values
ax.fill_between(yrs,ann.rep,ann.imp,color=CORAL,alpha=0.22,zorder=2)
ax.plot(yrs,ann.imp,color=CORAL,linewidth=2.5,marker='o',ms=5,zorder=5)
ax.plot(yrs,ann.rep,color=AQUA,linewidth=2.5,marker='o',ms=5,zorder=6)
ax.text(2021.12,0.80,"corrected for missing counts",fontsize=10.5,color=CORAL,fontweight="700",va="top")
ax.text(2025.22,0.345,"as published",fontsize=10.5,color=AQUA,fontweight="700",ha="right",va="top")
ax.set_xlim(2020.72,2025.3); ax.set_ylim(0.1,0.88); ax.set_yticks([])
ax.set_xticks(yrs)
ax.set_title("The gap is the bias. The shape is unchanged.",fontsize=12.5,color=CREAM,
             fontfamily=SERIF,fontweight="bold",loc="left",pad=7)

for s_ in ax2.spines.values(): s_.set_visible(False)
ax2.tick_params(length=0,colors=MIST,labelsize=10.5)
cols=[AQUA if v<0 else (GOLD if v<0.45 else CORAL) for v in grp.m]
ax2.barh(range(len(grp)),grp.m,color=cols,height=0.6,zorder=3)
ax2.axvline(0,color=MIST,linewidth=1.1,zorder=4)
ax2.axvline(ctrl,color=CREAM,linewidth=1.2,linestyle=(0,(4,3)),zorder=4)
ax2.annotate("skew alone\nexplains this much",xy=(ctrl,-0.78),xytext=(ctrl+0.02,-1.02),
             fontsize=9,color=CREAM,va="center",linespacing=1.4,zorder=5,annotation_clip=False)
ax2.set_yticks(range(len(grp)))
ax2.set_yticklabels([f"{LAB.get(i,i)}  ({int(grp.n[i]):,})" for i in grp.index],fontsize=10.5)
for i,v in enumerate(grp.m):
    ax2.text(v+(0.02 if v>0 else -0.02),i,f"{v:+.2f}",va="center",
             ha="left" if v>0 else "right",fontsize=10,color=CREAM,fontweight="600")
ax2.set_xlim(-0.30,0.72); ax2.set_xticks([]); ax2.set_ylim(-0.6,len(grp)-0.4)
ax2.set_title("Lice around a missed count, vs that site's own normal level",
              fontsize=12.5,color=CREAM,fontfamily=SERIF,fontweight="bold",loc="left",pad=7)

fig.text(0.058,0.972,"THE WEEKS NOBODY COUNTS ARE THE WEEKS WITH THE MOST LICE",
         fontsize=9.3,color=AQUA,ha="left",va="top",fontweight="700")
fig.text(0.058,0.936,"Scotland's lice data is biased low, and knowably so",
         fontsize=20,fontfamily=SERIF,fontweight="bold",color=CREAM,ha="left",va="top")
fig.text(0.058,0.888,
 "About 17% of site-weeks carry no lice count. Counts at the same site within three\n"
 "weeks of a gap sit above that site's median, furthest above when the stated reason\n"
 "is harvest withdrawal. Newly stocked sites run the other way, as they must.",
 fontsize=10.3,color=MIST,ha="left",va="top",linespacing=1.55)
fig.add_artist(plt.Line2D([0.058,0.960],[0.122,0.122],color="#1b3d4e",linewidth=1.2,
                          transform=fig.transFigure))
fig.text(0.058,0.106,
 "Source: author's analysis of Fish Health Inspectorate weekly sea lice returns, 34,507 site-weeks, 2021-2025. Bars: mean of observed counts\n"
 "within +/-3 weeks of a no-count at the same site, minus that site's annual median; brackets give the number of no-counts. Dashed line is the\n"
 "same statistic for counted weeks (+0.17), the baseline from right-skew alone. Top panel imputes missing weeks from neighbours. p=7.5e-14.",
 fontsize=8.3,color=DIM,ha="left",va="top",linespacing=1.6)
fig.savefig(f"{OUT}/salmon_13_nocount.png",dpi=200)
print("wrote salmon_13_nocount.png")
print(ann.round(3).to_string()); print(grp.round(3).to_string()); print('control',round(ctrl,3))
