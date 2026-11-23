import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the trawling/ folder
import sys; sys.path.insert(0,ROOT+'/analysis'); sys.path.insert(0,ROOT+'/bounds/scot')
from lichen_style import *
import geopandas as gpd, pandas as pd
from shapely.geometry import box
from shapely.ops import unary_union
from scotland import poly
from zones_src import Z, WHOLE
B=ROOT+'/'; O=B+'charts/'
P=3035
ext=gpd.GeoSeries([box(-11.5,49.0,4.2,61.6)],crs=4326).to_crs(P).total_bounds
land=gpd.read_file(ROOT+'/bounds/ne/land50.geojson').clip(box(-20,45,15,65)).to_crs(P)
z=gpd.read_file(B+'results/zones.gpkg').to_crs(P)
ban=z[z.group=='Existing ban']; s3=z[z.group=='Stage 3']
j=gpd.read_file(B+'bounds/jncc/c20251203_OffshoreMPAs_WGS84.shp')
snsea=j[j.SITE_NAME=='Southern North Sea'].to_crs(P)
ni=j[j.SITE_NAME.isin(['Queenie Corner','South Rigg'])].to_crs(P)
scz=[unary_union([poly(p) for p in Z[n]]) for n in Z]
scot=gpd.GeoSeries(scz,crs=4326).to_crs(P)
scw=j[j.SITE_NAME.isin(WHOLE)].to_crs(P)
t=gpd.read_file(B+'wind/raw/tce_wind.geojson').to_crs(P)
c=gpd.read_file(B+'wind/raw/ces_wind.geojson'); c=c[c.Property_Classification=='Wind Farm'].to_crs(P)
wind=pd.concat([t.geometry,c.geometry])
W_IN=(ext[2]-ext[0]); H_IN=(ext[3]-ext[1]); aw=0.88*W; ph=aw*H_IN/W_IN
fig,ax=frame('Where the lines are drawn','Bans, proposals and wind farms in UK seas',
 'Existing English bottom-trawl bans, England\'s Stage 3 proposals, Scotland\'s closed zones and whole-site closures, the two Northern Irish mud sites, the Southern North Sea MPA and offshore wind sites',
 'Source: MMO byelaw boundaries and Stage 3 consultation (2025); JNCC offshore MPA boundaries (Dec 2025); Scottish closed-zone coordinates from the Scottish Government (2025); The Crown Estate and Crown Estate Scotland offshore wind leases, all statuses. Coastline: Natural Earth. Wind sites include planned and consented farms.',
 plot=(0.06,0,0.88,0),plot_h=ph,eyebrow_color=TEAL)
ax.set_facecolor(PLATE)
land.plot(ax=ax,color='#1d3a47',edgecolor='#2a4d5c',lw=0.4)
gpd.GeoSeries(wind,crs=P).plot(ax=ax,facecolor='none',edgecolor=MUTED,lw=0.6,hatch='////',alpha=0.9)
snsea.plot(ax=ax,facecolor=GOLD,alpha=0.10,edgecolor=GOLD,lw=1.0)
s3.plot(ax=ax,color=CORAL,alpha=0.85,lw=0)
scw.plot(ax=ax,facecolor='#7fe3de',alpha=0.22,edgecolor='#7fe3de',lw=0.8); scot.plot(ax=ax,facecolor='#7fe3de',alpha=0.22,edgecolor='#7fe3de',lw=0.8)
ni.plot(ax=ax,facecolor='none',edgecolor=CORAL,lw=1.4,linestyle=(0,(2,1.5)))
ban.plot(ax=ax,color=TEAL,alpha=0.95,lw=0)
ax.set_xlim(ext[0],ext[2]); ax.set_ylim(ext[1],ext[3]); ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel(''); ax.set_ylabel(''); ax.set_aspect('equal')
def at(lon,lat): return gpd.GeoSeries([gpd.points_from_xy([lon],[lat])[0]],crs=4326).to_crs(P).iloc[0].coords[0]
for name,lon,lat,col,ha in [('Dogger Bank',2.4,56.05,TEAL,'center'),('Southern\nNorth Sea\nMPA',3.05,53.55,GOLD,'left'),
    ('Western Channel',-5.0,49.25,CORAL,'left'),('Queenie Corner /\nSouth Rigg',-5.05,54.15,CORAL,'right'),('West Shetland Shelf',-3.3,60.55,TEAL,'right')]:
    x,y=at(lon,lat); label(ax,x,y,name,col,fontsize=10.5,ha=ha,va='center')
# legend
import matplotlib.patches as mp
h=[mp.Patch(color=TEAL,alpha=0.95,label='English bans in force'),mp.Patch(color=CORAL,alpha=0.85,label='English Stage 3 proposals'),
   mp.Patch(facecolor='#7fe3de',alpha=0.35,edgecolor='#7fe3de',label='Scottish closures (Oct 2025)'),mp.Patch(facecolor=GOLD,alpha=0.25,edgecolor=GOLD,label='Southern North Sea MPA (no ban)'),
   mp.Patch(facecolor='none',edgecolor=CORAL,linestyle='--',label='NI mud sites (consulted)'),mp.Patch(facecolor='none',edgecolor=MUTED,hatch='////',label='Offshore wind sites')]
lg=ax.legend(handles=h,loc='lower right',frameon=True,fontsize=9.5,labelcolor=INK,facecolor=PLATE,edgecolor=RULE,borderpad=0.8)
fig.savefig(O+'00_map.png',facecolor=PLATE); plt.close()
print('ok',ph)
