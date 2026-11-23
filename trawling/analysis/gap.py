import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the trawling/ folder
import geopandas as gpd, pandas as pd, numpy as np, re
B=ROOT+'/'
norm=lambda s: re.sub(r'[^a-z]','',s.lower().replace('’',"'").split('/')[0])
j=gpd.read_file(B+'bounds/jncc/c20251203_OffshoreMPAs_WGS84.shp').to_crs(3035)
j=j.dissolve('SITE_NAME',aggfunc={'Country':'first'}).reset_index(); j['k']=j.SITE_NAME.map(norm)
s3=pd.read_csv(B+'bounds/stage3_sites.csv'); s3['k']=s3.site.map(norm)
ban=gpd.read_file(B+'bounds/mmo/Marine_Conservation_Byelaws.geojson').to_crs(3035).geometry.union_all()
lut=gpd.read_file(B+'ices/csquares.gpkg').to_crs(3035); lut['a']=lut.area; sidx=lut.sindex
D={y:pd.read_parquet(f'{B}ices/store/AnnexCategory_Total_{y}.parquet').set_index('cSquare') for y in (2023,2024,2025)}
def stats(g):
    sub=lut.iloc[sidx.query(g,predicate='intersects')]; w=(sub.intersection(g).area/sub['a']).values
    hrs=np.mean([(D[y].FISH_HRS.reindex(sub.cSquare).fillna(0).values*w).sum() for y in D])
    sa=np.mean([(D[y].swptarea.reindex(sub.cSquare).fillna(0).values*w).sum() for y in D])  # km2 swept per year
    return hrs,sa
rows=[]
s3m=s3.merge(j,on='k',how='left')
for _,r in s3m.iterrows():
    if r.geometry is None or pd.isna(r.SITE_NAME): rows.append(dict(group='England Stage 3',site=r.site,status='no offshore boundary in JNCC file')); continue
    g=r.geometry.difference(ban); h,sa=stats(g)
    rows.append(dict(group='England Stage 3',site=r.site,status='whole' if 'throughout the MPA' in r.proposal or 'whole' in r.proposal else ('amend existing' if 'minor amendments' in r.proposal or 'incorporated' in r.proposal else 'partial'),
       unbanned_km2=round(g.area/1e6),hrs=round(h),swept_km2=round(sa),sar=round(sa/(g.area/1e6),2)))
for _,r in j[j.Country.str.contains('Scot',na=False)].iterrows():
    h,sa=stats(r.geometry); rows.append(dict(group='Scotland offshore',site=r.SITE_NAME,status='measures from Oct 2025 (not site-checked)',unbanned_km2=round(r.geometry.area/1e6),hrs=round(h),swept_km2=round(sa),sar=round(sa/(r.geometry.area/1e6),2)))
T=pd.DataFrame(rows); T.to_csv(B+'results/gap.csv',index=False)
pd.set_option('display.width',220); print(T.sort_values(['group','hrs'],ascending=[True,False]).to_string(index=False))
print(T.groupby(['group','status'])[['unbanned_km2','hrs','swept_km2']].sum())
