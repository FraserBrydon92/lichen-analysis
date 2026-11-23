import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the trawling/ folder
# Uncertainty for the Scotland zoning and wind-farm comparisons: c-square-level bootstrap
import sys; sys.path.insert(0,ROOT+'/bounds/scot')
import geopandas as gpd, pandas as pd, numpy as np
from shapely.ops import unary_union
from zones_src import Z
sys.path.insert(0,ROOT+'/analysis'); from scotland import poly
B=ROOT+'/'
j=gpd.read_file(B+'bounds/jncc/c20251203_OffshoreMPAs_WGS84.shp').dissolve('SITE_NAME').reset_index()
lut=gpd.read_file(B+'ices/csquares.gpkg').to_crs(3035); lut['a']=lut.area; sidx=lut.sindex
D=sum(pd.read_parquet(f'{B}ices/store/AnnexCategory_Total_{y}.parquet').set_index('cSquare').FISH_HRS for y in (2022,2023,2024))/3
D=pd.read_parquet(f'{B}ices/store/AnnexCategory_Total_2022.parquet').set_index('cSquare').FISH_HRS.add(pd.read_parquet(f'{B}ices/store/AnnexCategory_Total_2023.parquet').set_index('cSquare').FISH_HRS,fill_value=0).add(pd.read_parquet(f'{B}ices/store/AnnexCategory_Total_2024.parquet').set_index('cSquare').FISH_HRS,fill_value=0)/3
cells=[]  # per (site, 0.05-degree cell incl. untrawled cells): area closed/open and hours
from shapely.geometry import box
from pyproj import Transformer
lut4=lut.to_crs(4326); lut4['h']=lut4.cSquare.map(D).fillna(0.0)
for name in Z:
    s4=j[j.SITE_NAME.str.startswith(name)].geometry.iloc[0]
    z4=unary_union([poly(p) for p in Z[name]]).intersection(s4)
    x0,y0,x1,y1=s4.bounds; xs=np.arange(np.floor(x0/0.05)*0.05,x1,0.05); ys=np.arange(np.floor(y0/0.05)*0.05,y1,0.05)
    G=gpd.GeoDataFrame(geometry=[box(x,y,x+0.05,y+0.05) for x in xs for y in ys],crs=4326)
    G=G[G.intersects(s4)].copy(); G['cent']=G.geometry.centroid
    hit=gpd.sjoin(gpd.GeoDataFrame(geometry=G.cent,crs=4326),lut4[['h','geometry']],predicate='within',how='left')
    G['h']=hit.groupby(level=0).h.first().reindex(G.index).fillna(0).values
    Gm=G.to_crs(3035); S=gpd.GeoSeries([s4],crs=4326).to_crs(3035).iloc[0]; Zm=gpd.GeoSeries([z4],crs=4326).to_crs(3035).iloc[0]
    for (_,c),h in zip(Gm.iterrows(),G.h.values):
        full=c.geometry.area; ac=c.geometry.intersection(Zm).area; ao=c.geometry.intersection(S).area-ac
        cells.append((name,ac/1e6,ao/1e6,h*ac/full,h*ao/full))
C=pd.DataFrame(cells,columns=['site','ac','ao','hc','ho'])
def stat(df): return (df.hc.sum()/df.ac.sum())/(df.ho.sum()/df.ao.sum()), df.hc.sum()/(df.hc.sum()+df.ho.sum())
rng=np.random.default_rng(3); obs=stat(C)
# bootstrap: resample cells within each site
bs=[]
for _ in range(2000):
    s=pd.concat([g.sample(len(g),replace=True,random_state=int(rng.integers(1e9))) for _,g in C.groupby('site')]); bs.append(stat(s))
bs=np.array(bs)
print('Scotland zoned sites: intensity closed/open = %.3f (95%% CI %.3f-%.3f); share of effort closed = %.1f%% (95%% CI %.1f-%.1f); area closed %.1f%%'%(obs[0],*np.percentile(bs[:,0],[2.5,97.5]),obs[1]*100,*np.percentile(bs[:,1]*100,[2.5,97.5]),C.ac.sum()/(C.ac.sum()+C.ao.sum())*100))
# per-site sign test: in how many sites is closed intensity lower than open
ps=C.groupby('site').apply(lambda g:(g.hc.sum()/max(g.ac.sum(),1e-9))<(g.ho.sum()/max(g.ao.sum(),1e-9)))
from scipy.stats import binomtest
print('sites with closed intensity < open: %d/%d, sign test p=%.4f'%(ps.sum(),len(ps),binomtest(int(ps.sum()),len(ps),0.5).pvalue))
# Wind: farm-level inside vs ring intensity, operational farms 2023-25
t=gpd.read_file(B+'wind/raw/tce_wind.geojson').to_crs(3035); c=gpd.read_file(B+'wind/raw/ces_wind.geojson').to_crs(3035)
op=pd.concat([t[t.Inf_Status.str.contains('Operation')].geometry, c[(c.Property_Classification=='Wind Farm')&(c.Project_Phase=='Operational')].geometry]).buffer(0)
allw=pd.concat([t.geometry,c.geometry]).buffer(0).union_all()
z=gpd.read_file(B+'results/zones.gpkg'); ban=z[z.group=='Existing ban'].geometry.union_all()
D2=sum(pd.read_parquet(f'{B}ices/store/AnnexCategory_Total_{y}.parquet').set_index('cSquare').FISH_HRS.reindex(lut.cSquare).fillna(0).values for y in (2023,2024,2025))/3
lut['h']=D2
def hrs(g):
    sub=lut.iloc[sidx.query(g,predicate='intersects')]; return (sub.h*(sub.intersection(g).area/sub['a'])).sum()
F=[]
for g in op:
    ring=g.buffer(20000).difference(g.buffer(5000)).difference(allw).difference(ban)
    if ring.area==0: continue
    F.append((hrs(g),g.area/1e6,hrs(ring),ring.area/1e6))
F=pd.DataFrame(F,columns=['hi','ai','hr','ar']); F=F[F.hr>0]
ratio=lambda f:(f.hi.sum()/f.ai.sum())/(f.hr.sum()/f.ar.sum())
bsw=[ratio(F.sample(len(F),replace=True,random_state=i)) for i in range(2000)]
lowr=((F.hi/F.ai)<(F.hr/F.ar)).sum()
print('Wind (operational, %d farms): intensity inside/ring = %.2f (95%% CI %.2f-%.2f); farms lower inside: %d/%d, sign test p=%.4f'%(len(F),ratio(F),*np.percentile(bsw,[2.5,97.5]),lowr,len(F),binomtest(int(lowr),len(F),0.5).pvalue))
