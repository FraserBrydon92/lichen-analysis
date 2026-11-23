import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the trawling/ folder
import geopandas as gpd, pandas as pd, numpy as np
B=ROOT+'/'
m=gpd.read_file(B+'bounds/mmo/Marine_Conservation_Byelaws.geojson').to_crs(3035)
lut=gpd.read_file(B+'ices/csquares.gpkg').to_crs(3035); lut['a']=lut.area; sidx=lut.sindex
for s in ['Wight-Barfleur Reef','Haig Fras','Farnes East','Dogger Bank','Offshore Brighton']:
    g=m[m.sub_name==s].geometry.union_all(); sub=lut.iloc[sidx.query(g,predicate='intersects')].copy()
    sub=sub[sub.intersection(g).area/sub['a']>0.99]
    for y in [2023,2024,2025]:
        v={L:pd.read_parquet(f'{B}ices/store/AnnexCategory_{L}_{y}.parquet').set_index('cSquare').reindex(sub.cSquare) for L in ['Total','Otter_trawl','Beam_trawl']}
        t=v['Total'].FISH_HRS.fillna(0).sum(); o=v['Otter_trawl'].FISH_HRS.fillna(0).sum(); b=v['Beam_trawl'].FISH_HRS.fillna(0).sum()
        n=(v['Total'].FISH_HRS.fillna(0)>0).sum(); mk=v['Total'].MASKED.fillna(0).sum()
        print(f'{s[:20]:20} {y} total {t:6.0f} otter {o:6.0f} beam {b:6.0f} other(dredge/seine) {t-o-b:6.0f} | cells fished {n}/{len(sub)} masked(<=3 vessels) {mk:.0f}')
