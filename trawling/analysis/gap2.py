import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the trawling/ folder
import geopandas as gpd, pandas as pd, numpy as np, re
B=ROOT+'/'
norm=lambda s: re.sub(r'[^a-z]','',s.lower().replace('’',"'").replace('&','and').split('/')[0].replace('mcz','').replace('sac',''))
mcz=gpd.read_file(B+'bounds/ne/mcz.geojson').to_crs(3035).rename(columns={'mcz_name':'n'})[['n','geometry']]
sac=gpd.read_file(B+'bounds/ne/sac.geojson').to_crs(3035).rename(columns={'sac_name':'n'})[['n','geometry']]
ne=pd.concat([mcz,sac]); ne['k']=ne.n.map(norm); ne=ne.dissolve('k').reset_index()
g=pd.read_csv(B+'results/gap.csv'); s3=pd.read_csv(B+'bounds/stage3_sites.csv')
miss=g[g.status.str.startswith('no offshore',na=False)].site.tolist()
ban=gpd.read_file(B+'bounds/mmo/Marine_Conservation_Byelaws.geojson').to_crs(3035).geometry.union_all()
lut=gpd.read_file(B+'ices/csquares.gpkg').to_crs(3035); lut['a']=lut.area; sidx=lut.sindex
D={y:pd.read_parquet(f'{B}ices/store/AnnexCategory_Total_{y}.parquet').set_index('cSquare') for y in (2023,2024,2025)}
rows=[]
for s in miss:
    k=norm(s); hit=ne[ne.k==k]
    prop=s3[s3.site==s].proposal.iloc[0]
    if hit.empty: rows.append(dict(site=s,match=None)); continue
    geom=hit.geometry.iloc[0].difference(ban)
    sub=lut.iloc[sidx.query(geom,predicate='intersects')]; w=(sub.intersection(geom).area/sub['a']).values
    hrs=np.mean([(D[y].FISH_HRS.reindex(sub.cSquare).fillna(0).values*w).sum() for y in D])
    sa=np.mean([(D[y].swptarea.reindex(sub.cSquare).fillna(0).values*w).sum() for y in D])
    kind='traps only - not a trawl ban' if prop.startswith('a prohibition of the use of traps') else ('amend existing' if 'minor amendments' in prop else ('partial (offshore of 6 nm or part of site) - upper bound' if ('6 nm' in prop or 'part of the MPA' in prop or 'most of' in prop) else 'whole'))
    rows.append(dict(site=s,match=hit.n.iloc[0],status=kind,unbanned_km2=round(geom.area/1e6),hrs=round(hrs),swept_km2=round(sa),sar=round(sa/(geom.area/1e6),2)))
T=pd.DataFrame(rows); print(T.to_string(index=False)); T.to_csv(B+'results/gap_inshore.csv',index=False)
