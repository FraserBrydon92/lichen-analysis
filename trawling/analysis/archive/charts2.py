import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the trawling/ folder
import pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.ticker as mt
B=ROOT+'/'; INK='#0b0b0b'; INK2='#52514e'; GRID='#e4e3df'; BLUE='#2a78d6'; ORANGE='#eb6834'; SURF='#fcfcfb'; GREY='#b9b8b2'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.edgecolor':GRID,'axes.labelcolor':INK2,'xtick.color':INK2,'ytick.color':INK2,'figure.facecolor':SURF,'axes.facecolor':SURF})
def clean(ax,grid='y'):
    for s in ['top','right','left'] if grid=='y' else ['top','right','bottom']: ax.spines[s].set_visible(False)
    ax.grid(axis=grid,color=GRID,lw=0.8); ax.set_axisbelow(True); ax.tick_params(length=0)
# 04 event study
R=pd.read_csv(B+'results/event.csv'); R=R[R.k.between(-6,3)]
fig,ax=plt.subplots(figsize=(10,6),dpi=200); clean(ax)
ax.axhline(0,color=INK2,lw=1); ax.axvline(-0.5,color=INK2,lw=1,ls=(0,(3,3)))
ax.vlines(R.k,R.lo_pct,R.hi_pct,color=BLUE,lw=2); ax.plot(R.k,R.mean_pct,'o',color=BLUE,ms=8,mec=SURF,mew=2)
for _,r in R.iterrows(): ax.text(r.k,max(r.hi_pct,r.mean_pct)+5,f'n={int(r.n_sites)}',ha='center',fontsize=8.5,color=INK2)
ax.text(-0.4,60,'Ban takes effect',color=INK2,fontsize=10)
ax.set_xticks(range(-6,4)); ax.set_xticklabels([f'{k:+d}' if k else '0' for k in range(-6,4)]); ax.set_xlabel('Years since ban (0 = ban year)')
ax.set_ylim(-100,80); ax.yaxis.set_major_formatter(mt.FuncFormatter(lambda v,_: f'{v:+.0f}%')); ax.set_ylabel('Trawl hours vs pre-ban level,\nrelative to nearby seabed')
fig.suptitle('Across England\'s banned sites, trawling falls by three-quarters in the first year',x=0.04,ha='left',fontsize=14.5,fontweight='bold',color=INK,y=0.98)
fig.text(0.04,0.875,'15 sites with ≥50 pre-ban hours. Inside-site change net of change 25–50 km away, vs 3 pre-ban years.\nBars: 95% interval (site bootstrap).',fontsize=9.5,color=INK2)
fig.text(0.04,0.01,'Source: ICES OSPAR technical service ospar.2026.12 (mobile bottom-contacting gear, vessels ≥12 m); MMO byelaw boundaries. Later years rest on few sites (n shown).\nEdge cells straddling boundaries are counted pro rata, so true falls inside the boundaries are likely larger.',fontsize=8,color=INK2)
fig.tight_layout(rect=(0,0.06,1,0.86)); fig.savefig(B+'charts/04_event_study.png'); plt.close()
# 05 modelled seabed status, Stage 3
M=pd.read_csv(B+'results/metrics.csv'); s=M[(M.group=='Stage 3')&M.year.between(2023,2025)].groupby('site')[['rbs_central','rbs_pessimistic','rbs_optimistic','hrs']].mean()
s=s[s.hrs>=100].sort_values('rbs_central').head(16).iloc[::-1]
fig,ax=plt.subplots(figsize=(10,7),dpi=200); clean(ax,'x')
y=np.arange(len(s)); ax.hlines(y,s.rbs_pessimistic,s.rbs_optimistic,color=GREY,lw=6,alpha=0.7)
ax.plot(s.rbs_central,y,'o',color=ORANGE,ms=9,mec=SURF,mew=2)
ax.set_yticks(y); ax.set_yticklabels(s.index,fontsize=10,color=INK); ax.set_xlim(0,1.02)
ax.xaxis.set_major_formatter(mt.FuncFormatter(lambda v,_: f'{v:.0%}')); ax.set_xlabel('Modelled seabed biomass as % of untrawled state, 2023–25 trawling')
fig.suptitle('Modelled: some Stage 3 sites are trawled so hard the seabed has almost nothing left',x=0.03,ha='left',fontsize=14,fontweight='bold',color=INK,y=0.98)
fig.text(0.03,0.925,'Dot: central estimate. Grey bar: range across recovery and depletion assumptions. The 16 lowest-scoring sites with ≥100 trawl hours a year.',fontsize=9.5,color=INK2)
fig.text(0.03,0.01,'MODELLED, not measured. Equilibrium biomass B/K = 1 − F·d/r per c-square (Hiddink et al. 2017, PNAS): F = ICES swept-area ratio by gear; d = 0.06 otter, 0.14 beam,\n0.06–0.20 other gear; r = 0.82/yr (0.42–1.53). Assumes trawling spread evenly within each ~15 km² cell, which overstates impact where trawling is patchy.',fontsize=8,color=INK2)
fig.tight_layout(rect=(0,0.06,1,0.91)); fig.savefig(B+'charts/05_stage3_modelled_status.png'); plt.close()
# 06 Scotland
T=pd.read_csv(B+'results/scotland_zones.csv'); Zd=T[T.type=='zoned'].copy()
tot=pd.DataFrame([dict(site='All 11 zoned sites',pct_area_closed=Zd.closed_km2.sum()/(Zd.closed_km2.sum()+Zd.open_km2.sum())*100,pct_hrs_closed=Zd.closed_hrs.sum()/(Zd.closed_hrs.sum()+Zd.open_hrs.sum())*100)])
Zd=Zd.sort_values('pct_hrs_closed'); D=pd.concat([Zd[['site','pct_area_closed','pct_hrs_closed']],tot]).iloc[::-1].reset_index(drop=True)
fig,ax=plt.subplots(figsize=(10,7),dpi=200); clean(ax,'x'); y=np.arange(len(D))
ax.barh(y+0.19,D.pct_area_closed,height=0.36,color=GREY); ax.barh(y-0.19,D.pct_hrs_closed,height=0.36,color=ORANGE)
ax.set_yticks(y); ax.set_yticklabels([('$\\bf{'+n.replace(' ','\\ ')+'}$') if n.startswith('All') else n.replace(' and Hebrides Terrace Seamount',' and HTS') for n in D.site],fontsize=10,color=INK)
ax.set_xlim(0,105); ax.xaxis.set_major_formatter(mt.FuncFormatter(lambda v,_: f'{v:.0f}%'))
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=GREY,label='Share of site area closed'),Patch(color=ORANGE,label='Share of trawling in the closed zones')],loc='upper center',bbox_to_anchor=(0.45,1.07),ncol=2,frameon=False,fontsize=10)
fig.suptitle('Scotland closed 86% of its zoned MPAs — but only 34% of the trawling',x=0.03,ha='left',fontsize=14.5,fontweight='bold',color=INK,y=0.98)
fig.text(0.03,0.925,'Bottom-trawl hours 2022–24 (before the October 2025 measures), split by the new closed zones and the parts left open.',fontsize=9.5,color=INK2)
fig.text(0.03,0.01,'Source: ICES OSPAR technical service ospar.2026.12; zone coordinates from Scottish Government supporting guidance (2025 Order); JNCC site boundaries.\nEast Rockall Bank and Wyville Thomson Ridge (low effort) not included. Some zones still allow demersal seines.',fontsize=8,color=INK2)
fig.tight_layout(rect=(0,0.06,1,0.91)); fig.savefig(B+'charts/06_scotland_zones.png'); plt.close()
