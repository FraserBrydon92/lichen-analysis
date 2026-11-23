"""
Species specificity of the lice association.

Inputs : wildlice, farms
Outputs: outputs/figures/

Ported from the original working script `legacy/charts12.py` with the analysis and
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
w=load("wildlice").copy(); w['doy']=pd.to_datetime(w['date']).dt.dayofyear
w=w[(w.yr>=2002)&(w.yr<=2024)].dropna(subset=['total_lice','length','doy']).reset_index(drop=True)
f=load("farms")
M={'Argyll':'Argyll and Bute','Eilean siar':'Eilean Siar','West Sutherland':'Highland',
   'Lochaber':'Highland','Lochalsh':'Highland','Skye':'Highland','Wester Ross':'Highland'}
w['LA']=w.region.map(M); w['infested']=(w.total_lice>0).astype(int); w['hi']=(w.total_lice>=10).astype(int)
w['lenc']=(w.length-w.length.mean())/100.; w['doyc']=(w.doy-w.doy.mean())/10.
g=f.groupby(['yr','Local Authority'])['Actual Biomass on Site (tonnes)'].mean().rename('rmean').reset_index()
g.columns=['yr','LA','rmean']; w=w.merge(g,on=['yr','LA'],how='left').dropna(subset=['rmean']).reset_index(drop=True)
w['rmean1k']=w.rmean/1000.
keep=w.site.value_counts(); keep=keep[keep>=30].index; wc=w[w.site.isin(keep)].reset_index(drop=True)
IQR=(w.rmean.quantile(.75)-w.rmean.quantile(.25))/1000.
SPECS=[("no controls at all","infested ~ rmean1k",w),
       ("+ sampling date and fish size","infested ~ rmean1k + doyc + lenc",w),
       ("+ region fixed effects","infested ~ rmean1k + doyc + lenc + C(region)",w),
       ("+ site fixed effects","infested ~ rmean1k + doyc + lenc + C(site)",wc),
       ("site FE, severe burden (10+ lice)","hi ~ rmean1k + doyc + lenc + C(site)",wc)]
res=[]
for lab,fo,df in SPECS:
    m=smf.ols(fo,data=df).fit(cov_type='cluster',cov_kwds={'groups':df['yr'].values})
    tb=m.summary2().tables[1]; pc=[c for c in tb.columns if c.startswith('P>')][0]
    res.append((lab,tb.loc['rmean1k','Coef.']*IQR*100,tb.loc['rmean1k','[0.025']*IQR*100,
                tb.loc['rmean1k','0.975]']*IQR*100,tb.loc['rmean1k',pc]))
    print(f'{lab:36s} {res[-1][1]:+.2f}pp [{res[-1][2]:+.2f},{res[-1][3]:+.2f}] p={res[-1][4]:.4f}')
fig=plt.figure(figsize=(9.0,6.6))
ax=fig.add_axes([0.345,0.245,0.580,0.395])
for s in ax.spines.values(): s.set_visible(False)
ax.tick_params(length=0,colors=MIST,labelsize=10.5)
ax.axvline(0,color=MIST,linewidth=1.2,zorder=2)
for i,(lab,c,lo,hi,p) in enumerate(res):
    y=len(res)-1-i
    col=CORAL if p<0.05 else DIM
    ax.plot([lo,hi],[y,y],color=col,linewidth=2.6,solid_capstyle='round',zorder=3)
    ax.plot([c],[y],'o',color=col,ms=8,zorder=4)
    ax.text(hi+0.45,y,f'{c:+.1f} pp',va='center',fontsize=10.5,color=CREAM,fontweight='600')
ax.set_yticks(range(len(res)))
ax.set_yticklabels([l for l,_,_,_,_ in res][::-1],fontsize=10.5)
ax.set_xlim(-4.6,17.6); ax.set_xticks([-4,0,4,8,12])
ax.set_xlabel("change in the chance a wild sea trout carries lice (percentage points)",
              fontsize=10,color=MIST,labelpad=9)
ax.text(-4.3,4.52,"grey = not significant",fontsize=9,color=DIM,va='bottom')
fig.text(0.058,0.965,"IT SHOWS UP ONLY WHEN EACH SITE IS COMPARED WITH ITSELF",
         fontsize=9.3,color=AQUA,ha="left",va="top",fontweight="700")
fig.text(0.058,0.922,"More farmed salmon nearby, more lice on wild fish",
         fontsize=19.5,fontfamily=SERIF,fontweight="bold",color=CREAM,ha="left",va="top")
fig.text(0.058,0.852,
 "Each row refits the same model with more controls. The bar is the effect of an interquartile rise in farmed\n"
 "biomass in the same local authority. With no controls the relationship is absent, because the regions with the\n"
 "most farmed salmon happen to be the ones with the fewest lice; it appears only when each site is compared\n"
 "against itself over time.",
 fontsize=10.2,color=MIST,ha="left",va="top",linespacing=1.55)
fig.add_artist(plt.Line2D([0.058,0.960],[0.142,0.142],color="#1b3d4e",linewidth=1.2,transform=fig.transFigure))
fig.text(0.058,0.122,
 "Source: author's analysis of Marine Directorate wild sea trout lice sampling and SEPA site biomass returns, 2002-2024. Linear probability models on\n"
 "24,039 individually examined fish across 75 sites, standard errors clustered by year (22 clusters). Bars are 95% confidence intervals. Local sea\n"
 "temperature is not controlled for and remains the main untested confounder.",
 fontsize=8.3,color=DIM,ha="left",va="top",linespacing=1.6)
fig.savefig(f"{OUT}/salmon_15_species_specificity.png",dpi=200); print("wrote salmon_15_species_specificity.png")
