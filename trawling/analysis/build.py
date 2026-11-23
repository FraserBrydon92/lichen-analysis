import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the trawling/ folder
# Build site x year panel: inside, 0-10km, 10-25km, 25-50km rings (rings exclude all ban areas)
import geopandas as gpd, pandas as pd, numpy as np
B=ROOT+'/'
m=gpd.read_file(B+'bounds/mmo/Marine_Conservation_Byelaws.geojson').to_crs(3035)
m['site']=m.sub_name.str.replace(' reef','').str.replace(' sandbank','')  # merge Inner Dowsing parts
sites=m.dissolve('site',aggfunc={'start_date':'min','area_km':'sum','mpa_type':'first'}).reset_index()
allban=m.geometry.union_all()
lut=gpd.read_file(B+'ices/csquares.gpkg').to_crs(3035)
xmin,ymin,xmax,ymax=sites.total_bounds; pad=60000
lut=lut.cx[xmin-pad:xmax+pad, ymin-pad:ymax+pad].copy(); lut['a']=lut.area
sidx=lut.sindex
def weights(geom):
    if geom.is_empty: return np.array([]),np.array([]),0
    ii=sidx.query(geom,predicate='intersects'); sub=lut.iloc[ii]
    ov=sub.intersection(geom).area.values
    return sub.cSquare.values, ov/sub['a'].values, geom.area
zones={}
for _,r in sites.iterrows():
    g=r.geometry
    zones[(r.site,'inside')]=g
    zones[(r.site,'ring0_10')]=g.buffer(10000).difference(g).difference(allban)
    zones[(r.site,'ring10_25')]=g.buffer(25000).difference(g.buffer(10000)).difference(allban)
    zones[(r.site,'ring25_50')]=g.buffer(50000).difference(g.buffer(25000)).difference(allban)
W={k:weights(v) for k,v in zones.items()}
rows=[]
for layer in ['Total','Otter_trawl','Beam_trawl']:
    for y in range(2009,2026):
        d=pd.read_parquet(f'{B}ices/store/AnnexCategory_{layer}_{y}.parquet').set_index('cSquare')
        h=d.FISH_HRS; s=d.SAR
        for (site,zone),(ids,w,area) in W.items():
            if len(ids)==0: continue
            hrs=(h.reindex(ids).fillna(0).values*w).sum()
            # area-weighted mean swept-area ratio (times swept per year)
            sar=(s.reindex(ids).fillna(0).values*w*lut.set_index('cSquare').loc[ids,'a'].values).sum()/area
            rows.append((site,zone,layer,y,hrs,sar,area/1e6))
P=pd.DataFrame(rows,columns=['site','zone','layer','year','hrs','sar','area_km2'])
P=P.merge(sites[['site','start_date','mpa_type']],on='site')
P.to_csv(B+'results/panel.csv',index=False)
print(P[(P.layer=='Total')&(P.zone=='inside')].pivot_table(index='site',columns='year',values='hrs').round(0).to_string())
