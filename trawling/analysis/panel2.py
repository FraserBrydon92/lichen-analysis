import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the trawling/ folder
# Extended panel for inference: inside, core (wholly-inside cells), rings 0-10/10-25/25-50/50-100 km (rings exclude all bans and wind sites)
import geopandas as gpd, pandas as pd, numpy as np
B=ROOT+'/'
z=gpd.read_file(B+'results/zones.gpkg'); z=z[z.group=='Existing ban']
allban=z.geometry.union_all()
w1=gpd.read_file(B+'wind/raw/tce_wind.geojson').to_crs(3035).buffer(0).union_all()
w2=gpd.read_file(B+'wind/raw/ces_wind.geojson').to_crs(3035).buffer(0).union_all(); wind=w1.union(w2)
lut=gpd.read_file(B+'ices/csquares.gpkg').to_crs(3035); lut['a']=lut.area; sidx=lut.sindex
def W(g,core=False):
    if g.is_empty: return np.array([]),np.array([])
    sub=lut.iloc[sidx.query(g,predicate='intersects')]; f=(sub.intersection(g).area/sub['a']).values
    if core: m=f>0.99; return sub.cSquare.values[m],f[m]
    return sub.cSquare.values,f
Z={}
for _,r in z.iterrows():
    g=r.geometry; ex=allban.union(wind)
    Z[(r.site,'inside')]=W(g); Z[(r.site,'core')]=W(g,True)
    for a,b in [(0,10),(10,25),(25,50),(50,100)]:
        ring=(g.buffer(b*1000).difference(g.buffer(a*1000)) if a else g.buffer(b*1000).difference(g)).difference(ex)
        Z[(r.site,f'r{a}_{b}')]=W(ring)
rows=[]
for y in range(2009,2026):
    d=pd.read_parquet(f'{B}ices/store/AnnexCategory_Total_{y}.parquet').set_index('cSquare')
    for (s,zn),(ids,f) in Z.items():
        rows.append((s,zn,y,(d.FISH_HRS.reindex(ids).fillna(0).values*f).sum(),(d.swptarea.reindex(ids).fillna(0).values*f).sum()))
P=pd.DataFrame(rows,columns=['site','zone','year','hrs','swept'])
P['ban_year']=P.site.map(dict(zip(z.site,z.ban_year.astype(int))))
P.to_csv(B+'results/panel2.csv',index=False); print(P.groupby('zone').hrs.sum().round())
