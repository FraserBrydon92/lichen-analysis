import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the trawling/ folder
import sys; sys.path.insert(0,ROOT+'/analysis')
from lichen_style import *
import pandas as pd, numpy as np, matplotlib.ticker as mt
B=ROOT+'/'; O=B+'charts/'
kfmt=mt.FuncFormatter(lambda v,_: f'{v/1000:.0f}k' if v>=1000 else f'{v:.0f}')
# 01 Dogger
yrs=np.arange(2016,2026); ices=[9242,12154,13504,10343,11047,7508,460,487,215,71]; gfw=[551,698,2930,3133,6388,5465,7035,9511,12876,6924]
fig,ax=frame('Two datasets, opposite stories','Dogger Bank after the trawling ban',
 'Hours per year inside the ban area: bottom trawling recorded by vessel monitoring (ICES)\nagainst "trawler" hours inferred from ship transponders (Global Fishing Watch)',
 'Source: ICES OSPAR technical service ospar.2026.12 (mobile bottom-contacting gear, vessels 12 m and over); Global Fishing Watch\napparent fishing effort, trawlers and dredges. Ban in force from 13 June 2022. In 2024, wind-farm guard and survey vessels made up at least 74% of GFW hours.',
 plot=(0.085,0,0.86,0),plot_h=3.4)
hgrid(ax); ax.fill_between(yrs,ices,color=AREA,alpha=0.9); glow(ax,yrs,ices,TEAL); glow(ax,yrs,gfw,GOLD)
ax.axvline(2022.45,color=RULE,lw=1.5,ls=(0,(4,3)))
ax.scatter([2025],[71],s=110,color=CORAL,zorder=5); ax.scatter([2024],[12876],s=110,color=GOLD,zorder=5)
label(ax,2016.1,14100,'Bottom trawling (ICES)',TEAL); label(ax,2016.1,3900,'"Trawler" hours (GFW)',GOLD)
label(ax,2023.8,12300,'2024: 12,876 h,\nmostly guard boats',GOLD,ha='right',fontsize=11)
label(ax,2024.9,1400,'2025: 71 h',CORAL,ha='right'); label(ax,2022.55,4200,'Ban',INK,fontsize=11)
ax.set_xlim(2015.7,2025.4); ax.set_ylim(0,15500); ax.set_xticks([2016,2018,2020,2022,2024,2025]); ax.yaxis.set_major_formatter(kfmt)
fig.savefig(O+'01_dogger.png'); plt.close()

# 02 gap
fig,ax=frame('The trawling that is still allowed','Most trawling in English MPAs is in sites not yet protected',
 'Bottom-trawl hours per year inside each group of sites',
 'Source: ICES OSPAR technical service ospar.2026.12 (vessels 12 m and over); boundaries from MMO, JNCC and Natural England. Existing bans: three years\nbefore each ban against the years after. Stage 3: 2023-25 average, excluding areas already banned; part-site proposals counted whole (upper bound, about 1,700 h).',
 plot=(0.32,0,0.6,0),plot_h=2.6)
vgrid(ax); vals=[17229,2191,55498]; labs=['20 sites banned 2014-24,\nbefore their bans','The same 20 sites,\nafter their bans','35 Stage 3 sites still\nawaiting a decision']
cols=[TEAL,TEAL,CORAL]; y=[2,1,0]; ax.barh(y,vals,color=cols,height=0.5)
for yi,v,c in zip(y,vals,cols): label(ax,v+900,yi,f'{v:,} h',c,va='center',fontweight='semibold')
ax.set_yticks(y); ax.set_yticklabels(labs,color=WHITE,fontsize=12.5); ax.set_xlim(0,66000); ax.xaxis.set_major_formatter(kfmt)
fig.savefig(O+'02_gap.png'); plt.close()

# 03 top stage 3 sites
M=pd.read_csv(B+'results/metrics.csv'); s=M[(M.group=='Stage 3')&M.year.between(2023,2025)].groupby('site').agg(hrs=('hrs','mean'),area=('area_km2','first'),value=('value','mean'))
s=s.nlargest(12,'hrs').iloc[::-1]
fig,ax=frame('Where the remaining trawling is','The twelve most-trawled Stage 3 sites',
 'Bottom-trawl hours per year, 2023-25 average, and hours per km²',
 'Source: ICES OSPAR technical service ospar.2026.12 (vessels 12 m and over); JNCC and Natural England boundaries, minus areas already\nbanned. Foreland: the part of the site outside the 2024 ban.',plot=(0.40,0,0.52,0),plot_h=4.6)
vgrid(ax); dens=s.hrs/s.area; cols=[CORAL if d>15 else TEAL for d in dens]
ax.barh(range(len(s)),s.hrs,color=cols,height=0.62)
for i,(h,d,c) in enumerate(zip(s.hrs,dens,cols)): label(ax,h+150,i,f'{h:,.0f}  ·  {d:.0f}/km²',c,va='center',fontsize=11)
ax.set_yticks(range(len(s))); ax.set_yticklabels(s.index.str.replace('South West Approaches to the Bristol Channel','SW Approaches to Bristol Channel'),color=WHITE,fontsize=11.5)
ax.set_xlim(0,11500); ax.xaxis.set_major_formatter(kfmt)
ax.text(0,1.02,'Coral: more than 15 trawl hours per km² a year',transform=ax.transAxes,fontsize=10.5,color=CORAL)
fig.savefig(O+'03_stage3_sites.png'); plt.close()

# 04 event study (PPML)
E=pd.read_csv(B+'results/inf_event.csv')
fig,ax=frame('Fifteen bans, lined up by year','Trawling falls by four-fifths once a ban takes effect',
 'Change in trawl hours inside each site relative to seabed 25-50 km away, against the year before the ban.\nPoisson regression with site-by-year fixed effects; bars are 95% confidence intervals clustered by site.',
 'Source: author\'s analysis of ICES OSPAR technical service ospar.2026.12 and MMO byelaw boundaries; 15 sites with 50+ pre-ban hours. Years +2 and +3 rest on 5 sites.\nPre-ban coefficients are jointly non-zero (Wald p<0.001): part of the fall began before the bans. Allowing for site-specific trends the estimate is -83% (p=0.035).',
 plot=(0.11,0,0.84,0),plot_h=3.6)
hgrid(ax); ax.axhline(0,color=INK,lw=1); ax.axvline(-0.5,color=RULE,lw=1.5,ls=(0,(4,3)))
L=lambda p: np.log1p(np.asarray(p)/100)
pre=E[E.k<0]; post=E[E.k>=0]
ax.vlines(pre.k,L(pre.lo),L(pre.hi),color=MUTED,lw=2.4); ax.scatter(pre.k,L(pre.pct),s=80,color=INK,zorder=5)
ax.vlines(post.k,L(post.lo),L(post.hi),color=TEAL,lw=2.4); ax.scatter(post.k,L(post.pct),s=90,color=TEAL,zorder=5)
for _,r in post.iterrows(): label(ax,r.k+0.14,L(r.pct),f'{r.pct:.0f}%',TEAL,va='center',fontsize=11)
label(ax,-0.4,L(220),'Ban year',INK,fontsize=11)
tk=[-99,-95,-90,-75,-50,0,100]; ax.set_yticks(L(tk)); ax.set_yticklabels([f'{t:+d}%' if t else '0' for t in tk]); ax.set_ylim(L(-99.3),L(280))
ax.set_xticks(range(-6,4)); ax.set_xticklabels(['≤-6' if k==-6 else ('+3' if k==3 else (f'{k:+d}' if k else '0')) for k in range(-6,4)])
fig.savefig(O+'04_event_study.png'); plt.close()

# 05 robustness forest
R=pd.read_csv(B+'results/inf_robust.csv').iloc[::-1].reset_index(drop=True)
names={'Main: all hours inside vs 25-50 km ring (PPML)':'Main estimate','Wholly-inside cells only':'Only grid cells wholly inside the ban',
 'Control ring 10-25 km':'Comparison seabed 10-25 km away','Control ring 50-100 km':'Comparison seabed 50-100 km away','Excluding Dogger Bank':'Excluding Dogger Bank',
 'Dropping the part-year ban year':'Dropping the part-year ban year','Outcome: swept area, not hours':'Swept area instead of hours',
 'OLS on log(hours+1), HC1 SE (not clustered)':'Linear model on log hours','All 20 banned sites':'All 20 banned sites','With site-specific linear trends':'Allowing site-specific trends'}
fig,ax=frame('Ten ways of asking the same question','The fall survives every check I ran',
 'Estimated change in trawl hours inside banned sites after the ban, relative to nearby seabed, with 95% intervals',
 'Source: author\'s analysis of ICES OSPAR technical service ospar.2026.12. Poisson regression with site-by-year fixed effects and site-clustered errors\nunless stated. Leave-one-site-out estimates range from -74% to -90%. A placebo ban three years early gives -29% (p=0.003): some decline came first.',
 h=6.4,plot=(0.40,0,0.52,0),plot_h=4.2)
vgrid(ax); ax.axvline(0,color=INK,lw=1)
for i,r in R.iterrows():
    c=GOLD if r.spec.startswith('Main') else TEAL
    ax.hlines(i,r.lo,r.hi,color=c,lw=2.4); ax.scatter(r.pct,i,s=80,color=c,zorder=5)
    label(ax,4,i,f'{r.pct:.0f}%',c,va='center',fontsize=11)
ax.set_yticks(range(len(R))); ax.set_yticklabels([names[s] for s in R.spec],color=WHITE,fontsize=11.5)
ax.set_xlim(-100,15); ax.xaxis.set_major_formatter(mt.FuncFormatter(lambda v,_: f'{v:.0f}%'))
fig.savefig(O+'05_robustness.png'); plt.close()

# 06 modelled seabed status
s=M[(M.group=='Stage 3')&M.year.between(2023,2025)].groupby('site')[['rbs_central','rbs_pessimistic','rbs_optimistic','hrs']].mean()
s=s[s.hrs>=100].sort_values('rbs_central').head(14).iloc[::-1]
fig,ax=frame('Modelled, not measured','At current trawling, some Stage 3 seabed has almost nothing left',
 'Modelled seabed biomass as a share of its untrawled state, at 2023-25 trawling. Dot: central estimate;\nbar: range across recovery and depletion assumptions. The 14 lowest-scoring sites with 100+ trawl hours.',
 'Model: equilibrium biomass B/K = 1 - F·d/r per grid cell (Hiddink et al. 2017, PNAS). F = ICES swept-area ratio by gear; d = 0.06 otter trawl,\n0.14 beam trawl, 0.06-0.20 other gear; r = 0.82/yr (0.42-1.53). Assumes trawling is spread evenly within each ~15 km² cell, which overstates impact.',
 h=6.6,plot=(0.34,0,0.58,0),plot_h=5.0)
vgrid(ax); y=np.arange(len(s))
ax.hlines(y,s.rbs_pessimistic*100,s.rbs_optimistic*100,color=RULE,lw=7)
cols=[CORAL if v<0.5 else GOLD if v<0.8 else TEAL for v in s.rbs_central]
ax.scatter(s.rbs_central*100,y,s=95,color=cols,zorder=5)
for yi,v,c in zip(y,s.rbs_central*100,cols): label(ax,v+2.5,yi+0.28,f'{v:.0f}%',c,fontsize=10.5,va='center')
ax.set_yticks(y); ax.set_yticklabels(s.index.str.replace('South West Approaches to the Bristol Channel','SW Approaches to Bristol Channel'),color=WHITE,fontsize=11.5)
ax.set_xlim(0,102); ax.xaxis.set_major_formatter(mt.FuncFormatter(lambda v,_: f'{v:.0f}%'))
fig.savefig(O+'06_modelled_status.png'); plt.close()

# 07 Scotland
T=pd.read_csv(B+'results/scotland_zones.csv'); Zd=T[T.type=='zoned'].copy().sort_values('pct_hrs_closed')
tot=dict(site='All 11 zoned sites',pct_area_closed=Zd.closed_km2.sum()/(Zd.closed_km2.sum()+Zd.open_km2.sum())*100,pct_hrs_closed=Zd.closed_hrs.sum()/(Zd.closed_hrs.sum()+Zd.open_hrs.sum())*100)
D=pd.concat([pd.DataFrame([tot]),Zd[['site','pct_area_closed','pct_hrs_closed']].iloc[::-1]]).iloc[::-1].reset_index(drop=True)
fig,ax=frame('Scotland, October 2025','The zones closed most of the area but missed most of the trawling',
 'Share of each site closed to bottom-towed gear, against the share of its 2022-24 trawling that falls inside the closed zones',
 'Source: author\'s analysis of ICES OSPAR technical service ospar.2026.12; zone coordinates from Scottish Government guidance on the 2025 Order; JNCC\nboundaries. Overall share of trawling closed: 34% (bootstrap 95% CI 29-39%). Closed zones less trawled than open parts in 11 of 11 sites (sign test p=0.001).',
 h=6.8,plot=(0.36,0,0.56,0),plot_h=5.0)
vgrid(ax); y=np.arange(len(D))
ax.barh(y+0.19,D.pct_area_closed,height=0.36,color=MUTED); ax.barh(y-0.19,D.pct_hrs_closed,height=0.36,color=CORAL)
ax.set_yticks(y); ax.set_yticklabels(D.site.str.replace(' and Hebrides Terrace Seamount',' & Hebrides Terrace'),color=WHITE,fontsize=11.5)
for lab in ax.get_yticklabels():
    if lab.get_text().startswith('All'): lab.set_fontweight('bold')
ax.set_xlim(0,100); ax.xaxis.set_major_formatter(mt.FuncFormatter(lambda v,_: f'{v:.0f}%'))
ax.text(0,1.02,'■ area closed',transform=ax.transAxes,color=MUTED,fontsize=11.5); ax.text(0.25,1.02,'■ trawling inside the closed zones',transform=ax.transAxes,color=CORAL,fontsize=11.5)
fig.savefig(O+'07_scotland.png'); plt.close()

# 08 wind
t=pd.read_csv(B+'results/wind_ts.csv')
fig,ax=frame('The other thing taking seabed','Trawlers are already being squeezed out of wind farms',
 'Bottom-trawl hours inside today\'s 52 operational wind farms and on seabed 5-20 km around them, index 2009-11 = 100',
 'Source: author\'s analysis of ICES OSPAR technical service ospar.2026.12; The Crown Estate and Crown Estate Scotland wind site agreements. Farms were\ncommissioned in different years. In 2023-25, 47 of 52 farms were trawled less than their surroundings; intensity ratio 0.54 (bootstrap 95% CI 0.20-0.97).',
 plot=(0.085,0,0.86,0),plot_h=3.4)
hgrid(ax); ax.axhline(100,color=RULE,lw=1.2); glow(ax,t.year,t.ring_idx,TEAL); glow(ax,t.year,t.inside_idx,CORAL)
label(ax,2016.5,104,'Seabed around them',TEAL); label(ax,2016.5,30,'Inside the farms',CORAL)
ax.set_ylim(0,130); ax.set_xticks([2009,2013,2017,2021,2025])
fig.savefig(O+'08_wind.png'); plt.close()
print('done')
