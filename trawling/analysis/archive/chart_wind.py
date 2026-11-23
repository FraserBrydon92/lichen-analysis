import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the trawling/ folder
import pandas as pd, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
B=ROOT+'/'; INK='#0b0b0b'; INK2='#52514e'; GRID='#e4e3df'; BLUE='#2a78d6'; ORANGE='#eb6834'; SURF='#fcfcfb'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.edgecolor':GRID,'axes.labelcolor':INK2,'xtick.color':INK2,'ytick.color':INK2,'figure.facecolor':SURF,'axes.facecolor':SURF})
t=pd.read_csv(B+'results/wind_ts.csv')
fig,ax=plt.subplots(figsize=(10,6),dpi=200)
for s in ['top','right','left']: ax.spines[s].set_visible(False)
ax.grid(axis='y',color=GRID,lw=0.8); ax.set_axisbelow(True); ax.tick_params(length=0)
ax.plot(t.year,t.inside_idx,color=ORANGE,lw=2.5,marker='o',ms=6); ax.plot(t.year,t.ring_idx,color=BLUE,lw=2.5,marker='o',ms=6)
ax.axhline(100,color=INK2,lw=1)
ax.plot([2018.2,2018.5],[118,118],color=BLUE,lw=3); ax.text(2018.6,118,'Seabed 5–20 km around them',color=INK,fontsize=11,fontweight='bold',va='center')
ax.plot([2009.2,2009.5],[20,20],color=ORANGE,lw=3); ax.text(2009.6,20,"Inside today's 52 operational wind farms",color=INK,fontsize=11,fontweight='bold',va='center')
ax.set_ylim(0,130); ax.set_xticks(range(2009,2026,2)); ax.set_ylabel('Bottom-trawl hours, index (2009–11 = 100)')
fig.suptitle('Trawlers are already being squeezed out of wind farms',x=0.05,ha='left',fontsize=15,fontweight='bold',color=INK,y=0.98)
fig.text(0.05,0.905,'In 2023–25, operational farms were trawled at 43% of the intensity of the seabed around them.',fontsize=10,color=INK2)
fig.text(0.05,0.01,'Source: ICES OSPAR technical service ospar.2026.12 (vessels ≥12 m); The Crown Estate and Crown Estate Scotland wind site agreements. Farms were commissioned in\ndifferent years, so the fall inside reflects the build-out over time. Ring excludes other wind sites and banned MPAs. Fishing is not prohibited in operational UK wind farms.',fontsize=8,color=INK2)
fig.tight_layout(rect=(0,0.06,1,0.89)); fig.savefig(B+'charts/07_wind_farms.png'); plt.close()
