import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the trawling/ folder
# How much of the residual inside effort sits in cells that straddle the boundary (spillover risk) vs cells wholly inside?
import geopandas as gpd, pandas as pd, numpy as np
B=ROOT+'/'
m=gpd.read_file(B+'bounds/mmo/Marine_Conservation_Byelaws.geojson').to_crs(3035)
m['site']=m.sub_name.str.replace(' reef','').str.replace(' sandbank','')
sites=m.dissolve('site',aggfunc={'start_date':'min'}).reset_index()
lut=gpd.read_file(B+'ices/csquares.gpkg').to_crs(3035); lut['a']=lut.area; sidx=lut.sindex
D={y:pd.read_parquet(f'{B}ices/store/AnnexCategory_Total_{y}.parquet').set_index('cSquare').FISH_HRS for y in range(2009,2026)}
rows=[]
for _,r in sites.iterrows():
    g=r.geometry; by=pd.Timestamp(r.start_date).year
    sub=lut.iloc[sidx.query(g,predicate='intersects')].copy()
    sub['frac']=sub.intersection(g).area/sub['a']
    full=sub.frac>0.99
    pre=[y for y in range(by-3,by)]; post=[y for y in range(by+1,2026)][:2] if by<2024 else [2025]
    def h(yrs,mask): return np.mean([(D[y].reindex(sub.cSquare[mask]).fillna(0).values*sub.frac[mask].values).sum() for y in yrs])
    rows.append(dict(site=r.site,cells=len(sub),full_cells=int(full.sum()),
        pre_full=round(h(pre,full)),post_full=round(h(post,full),1),pre_edge=round(h(pre,~full)),post_edge=round(h(post,~full),1)))
T=pd.DataFrame(rows); T['post_full_chg%']=((T.post_full/T.pre_full-1)*100).round()
T.to_csv(B+'results/edge_check.csv',index=False); print(T.to_string(index=False))
