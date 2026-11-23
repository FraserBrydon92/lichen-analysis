import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the trawling/ folder
import geopandas as gpd, pandas as pd, numpy as np
B=ROOT+'/'
t=gpd.read_file(B+'wind/raw/tce_wind.geojson').to_crs(3035)
c=gpd.read_file(B+'wind/raw/ces_wind.geojson').to_crs(3035); c=c[c.Property_Classification=='Wind Farm']
def ph(s):
    s=s.lower()
    return 'Operational' if ('operation' in s) else 'Under construction' if 'construction' in s else 'Consented / planning'
t['phase']=t.Inf_Status.map(ph); c['phase']=c.Project_Phase.map(ph)
W=pd.concat([t[['Name_Prop','phase','geometry']].rename(columns={'Name_Prop':'name'}).assign(country='EWNI'),
             c[['Property_Description','phase','geometry']].rename(columns={'Property_Description':'name'}).assign(country='Scotland')])
W=gpd.GeoDataFrame(W,crs=3035); W['geometry']=W.buffer(0)
agg=gpd.read_file(B+'wind/raw/tce_aggregates.geojson').to_crs(3035); agg['geometry']=agg.buffer(0)
z=gpd.read_file(B+'results/zones.gpkg')
j=gpd.read_file(B+'bounds/jncc/c20251203_OffshoreMPAs_WGS84.shp').to_crs(3035); j['geometry']=j.buffer(0)
mpa_all=j.geometry.union_all().union(gpd.read_file(B+'bounds/ne/mcz.geojson').to_crs(3035).buffer(0).union_all())
ban=z[z.group=='Existing ban'].geometry.union_all(); s3=z[z.group=='Stage 3'].geometry.union_all()
lut=gpd.read_file(B+'ices/csquares.gpkg').to_crs(3035); lut['a']=lut.area; sidx=lut.sindex
D={y:pd.read_parquet(f'{B}ices/store/AnnexCategory_Total_{y}.parquet').set_index('cSquare') for y in range(2009,2026)}
def hrs(g,yrs):
    if g.is_empty: return 0.0
    sub=lut.iloc[sidx.query(g,predicate='intersects')]; f=(sub.intersection(g).area/sub['a']).values
    return np.mean([(D[y].FISH_HRS.reindex(sub.cSquare).fillna(0).values*f).sum() for y in yrs])
rows=[]
allwind=W.geometry.union_all()
for p,g in W.groupby('phase'):
    geom=g.geometry.union_all(); ring=geom.buffer(20000).difference(geom.buffer(5000)).difference(allwind).difference(ban)
    a=geom.area/1e6; ar=ring.area/1e6; h=hrs(geom,range(2023,2026)); hr=hrs(ring,range(2023,2026))
    rows.append(dict(phase=p,sites=len(g),area_km2=a,hrs_2325=h,int_per100=h/a*100,ring_int_per100=hr/ar*100,
       ov_mpa_km2=geom.intersection(mpa_all).area/1e6, ov_ban_km2=geom.intersection(ban).area/1e6, ov_stage3_km2=geom.intersection(s3).area/1e6))
R=pd.DataFrame(rows); R['ratio_vs_ring']=R.int_per100/R.ring_int_per100
pd.set_option('display.width',250); print(R.round(2).to_string(index=False))
print('aggregates: area',round(agg.geometry.union_all().area/1e6),' overlap MPAs',round(agg.geometry.union_all().intersection(mpa_all).area/1e6),' overlap Stage3',round(agg.geometry.union_all().intersection(s3).area/1e6),' overlap bans',round(agg.geometry.union_all().intersection(ban).area/1e6))
# operational farms: annual trawl hours inside, and ring
op=W[W.phase=='Operational'].geometry.union_all(); opr=op.buffer(20000).difference(op.buffer(5000)).difference(allwind).difference(ban)
ts=pd.DataFrame([(y,hrs(op,[y]),hrs(opr,[y])) for y in range(2009,2026)],columns=['year','inside','ring'])
ts['inside_idx']=ts.inside/ts.inside.iloc[:3].mean()*100; ts['ring_idx']=ts.ring/ts.ring.iloc[:3].mean()*100
print(ts.round(0).to_string(index=False)); ts.to_csv(B+'results/wind_ts.csv',index=False); R.to_csv(B+'results/wind_summary.csv',index=False)
# which MPAs overlap wind most
ov=[]
for _,r in j.iterrows():
    a=r.geometry.intersection(allwind).area/1e6
    if a>1: ov.append((r.SITE_NAME,round(a),round(a/(r.geometry.area/1e6)*100,1)))
print(sorted(ov,key=lambda x:-x[1])[:15])
