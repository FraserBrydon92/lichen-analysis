import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the trawling/ folder
import sys; sys.path.insert(0,ROOT+'/analysis')
import matplotlib.ticker as mt
from lichen_style import *
O=ROOT+'/charts/'
rows=[('Queenie Corner MCZ (NI)','mud, sea pens',5.6,1580),('South Rigg MCZ (NI)','mud, sea pens',3.8,1090),('North Channel SAC (NI)','harbour porpoise',2.5,11660),
('Skomer, Skokholm & Pembrokeshire (Wales)','seabirds',1.9,6640),('North Anglesey Marine SAC (Wales/NI)','harbour porpoise',0.2,3040),
('West Wales Marine SAC (Wales)','harbour porpoise',0.1,8010),('Croker Carbonate Slabs SAC (Wales)','reef',0.03,14)][::-1]
fig,ax=frame('Wales and Northern Ireland','The Northern Irish mud is swept most often',
 'Average number of times each site\'s area is swept by bottom gear a year, 2023-25, with trawl hours a year',
 'Source: author\'s analysis of ICES OSPAR technical service ospar.2026.12 (vessels 12 m and over); JNCC and Natural Resources Wales boundaries. Swept-area ratio is total area swept divided by site area; it averages over the site, so heavily fished patches are swept far more often. No bottom-trawl bans in any of these sites. Pisces Reef Complex (9 km²) is too small for the grid.',
 eyebrow_color=CORAL,plot=(0.47,0,0.43,0),plot_h=3.3)
vgrid(ax)
for i,(n,f,v,h) in enumerate(rows):
    c=CORAL if 'mud' in f else TEAL
    ax.barh(i,v,color=c,height=0.55)
    label(ax,v+0.12,i,f'{v:g}×   {h:,} h',c,va='center',fontsize=11)
ax.set_yticks(range(len(rows))); ax.set_yticklabels([f'{n}\n{f}' for n,f,_,_ in rows],color=WHITE,fontsize=10.5); ax.set_xlim(0,8.2)
ax.xaxis.set_major_formatter(mt.FuncFormatter(lambda v,_: f'{v:.0f}×')) if False else None
fig.savefig(O+'09_wales_ni.png'); plt.close()
