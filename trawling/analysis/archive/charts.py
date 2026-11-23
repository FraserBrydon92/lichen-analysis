import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the trawling/ folder
import pandas as pd, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.ticker
B=ROOT+'/'; INK='#0b0b0b'; INK2='#52514e'; GRID='#e4e3df'; BLUE='#2a78d6'; ORANGE='#eb6834'; SURF='#fcfcfb'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.edgecolor':GRID,'axes.labelcolor':INK2,'xtick.color':INK2,'ytick.color':INK2,'figure.facecolor':SURF,'axes.facecolor':SURF})
def frame(ax):
    for s in ['top','right','left']: ax.spines[s].set_visible(False)
    ax.grid(axis='y',color=GRID,lw=0.8); ax.set_axisbelow(True); ax.tick_params(length=0)
# Chart 1: Dogger
yrs=list(range(2016,2026))
ices=[9242,12154,13504,10343,11047,7508,460,487,215,71]
gfw=[551,698,2930,3133,6388,5465,7035,9511,12876,6924]
fig,ax=plt.subplots(figsize=(10,6),dpi=200); frame(ax)
ax.plot(yrs,ices,color=BLUE,lw=2.5,marker='o',ms=6); ax.plot(yrs,gfw,color=ORANGE,lw=2.5,marker='o',ms=6)
ax.axvline(2022.45,color=INK2,lw=1,ls=(0,(3,3)))
ax.text(2022.55,5600,'Trawling ban\n13 June 2022',color=INK2,fontsize=10,va='top')
ax.axvspan(2022.2,2025.5,color='#f1f0ec',zorder=0); ax.text(2025.4,15200,'Wind farm construction\n(offshore from March 2022)',color=INK2,fontsize=9.5,ha='right',va='top')
ax.plot([2015.75,2016.05],[14900,14900],color=BLUE,lw=3); ax.text(2016.12,14900,'Bottom trawling (ICES, vessel monitoring)',color=INK,fontsize=11,fontweight='bold',va='center')
ax.plot([2015.75,2016.05],[4300,4300],color=ORANGE,lw=3); ax.text(2016.12,4300,'"Trawler" hours (GFW, AIS)',color=INK,fontsize=11,fontweight='bold',va='center')
ax.set_xlim(2015.6,2025.5); ax.set_ylim(0,15500); ax.set_xticks(yrs)
ax.set_yticks(range(0,15001,2500)); ax.set_yticklabels([f'{v:,}' for v in range(0,15001,2500)])
ax.set_ylabel('Hours per year inside the ban area')
fig.suptitle('Dogger Bank: bottom trawling collapsed after the ban.\nThe "trawlers" GFW still sees are mostly wind-farm guard boats',x=0.06,ha='left',fontsize=15,fontweight='bold',color=INK,y=0.99)
fig.text(0.06,0.01,'Sources: ICES OSPAR technical service ospar.2026.12 (mobile bottom-contacting gear, vessels ≥12 m); Global Fishing Watch apparent fishing effort,\ntrawlers and dredges. In 2024, guard and survey vessels made up at least 74% of GFW hours in the area. Analysis: Fraser.',fontsize=8.5,color=INK2)
fig.tight_layout(rect=(0,0.06,1,0.92)); fig.savefig(B+'charts/01_dogger_ices_vs_gfw.png'); plt.close()

# Chart 2: gap
s=pd.read_csv(B+'results/site_summary.csv'); g=pd.read_csv(B+'results/gap.csv'); gi=pd.read_csv(B+'results/gap_inshore.csv')
off=g[(g.group=='England Stage 3')&g.status.isin(['whole','partial'])]; ins=gi[(gi.status=='whole')|gi.status.str.startswith('partial',na=False)]
st3=off.hrs.sum()+ins.hrs.sum(); n3=len(off)+len(ins)
vals=[s.pre_in.sum(),s.post_in.sum(),st3]
labs=[f'{len(s)} sites banned 2014–2024\nbefore their bans',f'The same {len(s)} sites\nafter their bans',f'{n3} Stage 3 sites still\nawaiting a decision (2023–25)']
fig,ax=plt.subplots(figsize=(10,5.6),dpi=200)
for sp in ['top','right','bottom']: ax.spines[sp].set_visible(False)
ax.grid(axis='x',color=GRID,lw=0.8); ax.set_axisbelow(True); ax.tick_params(length=0)
cols=[BLUE,BLUE,ORANGE]; y=[2,1,0]
ax.barh(y,vals,color=cols,height=0.55)
for yi,v in zip(y,vals): ax.text(v+600,yi,f'{v:,.0f} h',va='center',color=INK,fontsize=12,fontweight='bold')
ax.set_yticks(y); ax.set_yticklabels(labs,fontsize=11,color=INK); ax.set_xlim(0,max(vals)*1.15)
ax.set_xticks(range(0,60001,10000)); ax.set_xticklabels([f'{v:,}' for v in range(0,60001,10000)]); ax.set_xlabel('Bottom-trawl hours per year inside the site')
fig.suptitle('Most of the trawling inside English MPAs is in sites not yet protected',x=0.03,ha='left',fontsize=15,fontweight='bold',color=INK,y=0.98)
fig.text(0.03,0.885,'Existing bans: three years before each ban vs the years after. Stage 3: 2023–25 average, excluding areas already banned.',fontsize=10,color=INK2)
fig.text(0.03,0.01,'Source: ICES OSPAR technical service ospar.2026.12 (vessels ≥12 m only). Boundaries: MMO byelaws, JNCC, Natural England. Sites where the proposal covers only\nthe part beyond 6 nm are counted whole, so the Stage 3 figure is a slight upper bound (≈1,700 h). Two traps-only proposals and boundary amendments excluded.',fontsize=8,color=INK2)
fig.tight_layout(rect=(0,0.07,1,0.87)); fig.savefig(B+'charts/02_stage3_gap.png'); plt.close()

# Chart 3: top Stage 3 sites
a=pd.concat([off[['site','hrs','unbanned_km2']],ins[['site','hrs','unbanned_km2']]]).nlargest(12,'hrs').iloc[::-1]
fig,ax=plt.subplots(figsize=(10,6.4),dpi=200)
for sp in ['top','right','bottom']: ax.spines[sp].set_visible(False)
ax.grid(axis='x',color=GRID,lw=0.8); ax.set_axisbelow(True); ax.tick_params(length=0)
ax.barh(range(len(a)),a.hrs,color=ORANGE,height=0.6)
for i,(h,k) in enumerate(zip(a.hrs,a.unbanned_km2)): ax.text(h+120,i,f'{h:,.0f} h  ·  {h/k:.0f} h per km²',va='center',fontsize=9.5,color=INK2)
ax.set_yticks(range(len(a))); ax.set_yticklabels(a.site,fontsize=10.5,color=INK); ax.set_xlim(0,a.hrs.max()*1.35)
ax.set_xlabel('Bottom-trawl hours per year, 2023–25 average'); ax.xaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
fig.suptitle('The most-trawled Stage 3 sites',x=0.03,ha='left',fontsize=15,fontweight='bold',color=INK,y=0.98)
fig.text(0.03,0.01,'Source: ICES OSPAR technical service ospar.2026.12; JNCC and Natural England boundaries, minus areas already banned. Foreland: the part outside the 2024 ban.',fontsize=8,color=INK2)
fig.tight_layout(rect=(0,0.04,1,0.94)); fig.savefig(B+'charts/03_stage3_top_sites.png'); plt.close()
print(vals,n3)
