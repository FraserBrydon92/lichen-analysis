"""
Lice burden against sea temperature.

Inputs : lice_with_temp
Outputs: outputs/figures/

Ported from the original working script `legacy/charts13.py` with the analysis and
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

import pandas as pd, numpy as np, statsmodels.formula.api as smf
GROUND="#081a24"; CREAM="#f2f7f8"; MIST="#9dbac6"; DIM="#5a7d8c"
AQUA="#3fd0c9"; CORAL="#ff6f5e"; GOLD="#f3c969"
SERIF=FONT_SERIF; SANS=FONT_SANS
plt.rcParams.update({"font.family":SANS,"figure.facecolor":GROUND,"savefig.facecolor":GROUND,
                     "axes.facecolor":GROUND,"text.color":CREAM})
w=load("lice_with_temp")
IQR=(w.rmean.quantile(.75)-w.rmean.quantile(.25))/1000.
def fit(dv,rhs,df):
    df=df.dropna(subset=['rmean1k']+(['t60'] if 't60' in rhs else [])).reset_index(drop=True)
    k=df.site.value_counts(); k=k[k>=30].index; df=df[df.site.isin(k)].reset_index(drop=True)
    m=smf.ols(f'{dv} ~ {rhs}',data=df).fit(cov_type='cluster',cov_kwds={'groups':df['yr'].values})
    tb=m.summary2().tables[1]; pc=[c for c in tb.columns if c.startswith('P>')][0]
    return (tb.loc['rmean1k','Coef.']*IQR*100, tb.loc['rmean1k','[0.025']*IQR*100,
            tb.loc['rmean1k','0.975]']*IQR*100, tb.loc['rmean1k',pc])
B='doyc + lenc + C(site)'; sub=w.dropna(subset=['t60'])
ROWS=[("ANY LICE",None,None,None),
      ("no controls","infested","rmean1k",w),
      ("+ sampling date and fish size","infested","rmean1k + doyc + lenc",w),
      ("+ region fixed effects","infested","rmean1k + doyc + lenc + C(region)",w),
      ("+ site fixed effects","infested",f"rmean1k + {B}",w),
      ("site FE, 2002-2019 only","infested",f"rmean1k + {B}",sub),
      ("site FE + sea temperature","infested",f"rmean1k + t60 + {B}",sub),
      ("SEVERE BURDEN, 10+ LICE",None,None,None),
      ("+ site fixed effects","hi",f"rmean1k + {B}",w),
      ("site FE, 2002-2019 only","hi",f"rmean1k + {B}",sub),
      ("site FE + sea temperature","hi",f"rmean1k + t60 + {B}",sub)]
res=[]
for lab,dv,rhs,df in ROWS:
    if dv is None: res.append((lab,None)); continue
    r=fit(dv,rhs,df); res.append((lab,r)); print(f'{lab:34s} {r[0]:+6.2f} [{r[1]:+.2f},{r[2]:+.2f}] p={r[3]:.4f}')
fig=plt.figure(figsize=(9.0,7.3))
ax=fig.add_axes([0.345,0.205,0.580,0.455])
for s in ax.spines.values(): s.set_visible(False)
ax.tick_params(length=0,colors=MIST,labelsize=10.5)
ax.axvline(0,color=MIST,linewidth=1.2,zorder=2)
n=len(res); labs=[]
for i,(lab,r) in enumerate(res):
    y=n-1-i
    if r is None:
        labs.append(""); ax.text(-5.9,y,lab,fontsize=9.3,color=AQUA,fontweight="700",va="center",ha="left")
        continue
    c,lo,hi,p=r; col=CORAL if p<0.05 else DIM
    ax.plot([lo,hi],[y,y],color=col,linewidth=2.5,solid_capstyle='round',zorder=3)
    ax.plot([c],[y],'o',color=col,ms=7.5,zorder=4)
    ax.text(hi+0.5,y,f'{c:+.1f}',va='center',fontsize=10,color=CREAM,fontweight='600')
    labs.append(lab)
ax.set_yticks(range(n)); ax.set_yticklabels(labs[::-1],fontsize=10.3)
ax.set_xlim(-6.0,23.5); ax.set_xticks([-4,0,4,8,12,16,20]); ax.set_ylim(-0.6,n-0.4)
ax.set_xlabel("change in the chance a wild sea trout is infested (percentage points)",fontsize=10,color=MIST,labelpad=9)
ax.text(-5.9,n-0.05,"grey = not significant",fontsize=9,color=DIM,va='center',ha='left')
fig.text(0.058,0.968,"TEMPERATURE IS NOT THE EXPLANATION",fontsize=9.3,color=AQUA,ha="left",va="top",fontweight="700")
fig.text(0.058,0.930,"The heavy infestations track farmed biomass; the light ones don't",
         fontsize=18.5,fontfamily=SERIF,fontweight="bold",color=CREAM,ha="left",va="top")
fig.text(0.058,0.872,
 "Effect of an interquartile rise in farmed biomass in the same local authority. Sea temperature is a strong\n"
 "predictor of lice in its own right but is almost uncorrelated with farmed biomass (r=0.07), so adding it barely\n"
 "moves the result. What does move it is the period: on pre-2020 data the presence of any lice is no longer\n"
 "significant, while severe burdens, the ones that kill fish, stay significant throughout.",
 fontsize=10.2,color=MIST,ha="left",va="top",linespacing=1.55)
fig.add_artist(plt.Line2D([0.058,0.960],[0.128,0.128],color="#1b3d4e",linewidth=1.2,transform=fig.transFigure))
fig.text(0.058,0.108,
 "Source: author's analysis of Marine Directorate wild sea trout lice sampling, SEPA site biomass returns and Scottish Coastal Observatory temperature\n"
 "loggers. Linear probability models on up to 24,039 individually examined fish across 75 sites, 2002-2024, standard errors clustered by year. Temperature\n"
 "is the mean of the 60 days before each fish was netted at the nearest observatory site; those series end in 2021, so temperature models cover 2002-2019.",
 fontsize=8.3,color=DIM,ha="left",va="top",linespacing=1.6)
fig.savefig(f"{OUT}/salmon_16_lice_temperature.png",dpi=200); print("rewrote salmon_16_lice_temperature.png")
