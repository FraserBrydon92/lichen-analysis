import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the trawling/ folder
import sys; sys.path.insert(0,ROOT+'/analysis')
from lichen_style import *
import pandas as pd, numpy as np, matplotlib.ticker as mt
B=ROOT+'/'; O=B+'charts/'
kfmt=mt.FuncFormatter(lambda v,_: f'{v/1000:.0f}k' if v>=1000 else f'{v:.0f}')
# 05 robustness forest
R=pd.read_csv(B+'results/inf_robust.csv')
extra=pd.DataFrame([{'spec':'Pairs cluster bootstrap interval','pct':R.pct.iloc[0],'lo':-94,'hi':-67},{'spec':'Synthetic controls, pooled (no interval)','pct':-81,'lo':np.nan,'hi':np.nan}])
R=pd.concat([R,extra]).iloc[::-1].reset_index(drop=True)
names={'Main: all hours inside vs 25-50 km ring (PPML)':'Main estimate','Wholly-inside cells only':'Only grid cells wholly inside the ban',
 'Control ring 10-25 km':'Comparison seabed 10-25 km away','Control ring 50-100 km':'Comparison seabed 50-100 km away','Excluding Dogger Bank':'Excluding Dogger Bank',
 'Dropping the part-year ban year':'Dropping the part-year ban year','Outcome: swept area, not hours':'Swept area instead of hours',
 'OLS on log(hours+1), HC1 SE (not clustered)':'Linear model on log hours','All 20 banned sites':'All 20 banned sites','Pairs cluster bootstrap interval':'Bootstrap interval (resampling sites)','Synthetic controls, pooled (no interval)':'Synthetic controls, pooled','With site-specific linear trends':'Allowing site-specific trends'}
fig,ax=frame('Twelve ways of asking the same question','The fall survives every check I ran',
 'Estimated change in trawl hours inside banned sites after the ban, relative to nearby seabed, with 95% intervals',
 'Source: author\'s analysis of ICES OSPAR technical service ospar.2026.12. Poisson regression with site-by-year fixed effects and site-clustered errors\nunless stated. Wild cluster bootstrap p=0.0001 for the main estimate. Synthetic controls: 14 of 15 sites below their control, Fisher combined p=0.021; no interval shown. Leave-one-site-out estimates range from -74% to -90%. A placebo ban three years early gives -29% (p=0.003): some decline came first.',
 h=6.4,plot=(0.40,0,0.52,0),plot_h=4.9)
vgrid(ax); ax.axvline(0,color=INK,lw=1)
for i,r in R.iterrows():
    c=GOLD if r.spec.startswith('Main') else TEAL
    if r.spec.startswith('Synth'): ax.scatter(r.pct,i,s=95,color=WHITE,marker='D',zorder=5); c=WHITE
    else: ax.hlines(i,r.lo,r.hi,color=c,lw=2.4); ax.scatter(r.pct,i,s=80,color=c,zorder=5)
    label(ax,4,i,f'{r.pct:.0f}%',c,va='center',fontsize=11)
ax.set_yticks(range(len(R))); ax.set_yticklabels([names[s] for s in R.spec],color=WHITE,fontsize=11.5)
ax.set_xlim(-100,15); ax.xaxis.set_major_formatter(mt.FuncFormatter(lambda v,_: f'{v:.0f}%'))
fig.savefig(O+'05_robustness.png'); plt.close()