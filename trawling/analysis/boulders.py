import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the trawling/ folder
import numpy as np, geopandas as gpd, pandas as pd
from shapely.geometry import MultiPoint, Point
P=[(52,50.1889,2,55.6531),(52,52.01,2,53.27),(52,54.02,2,50.57),(52,55.084,2,49.04),(52,56.879,2,46.339),(52,57.3,2,52.4),(52,55.3,2,51.6),(52,51.3,2,49.2),(52,49.1,2,47.4),(52,56.3190,2,44.0123)]
pts=[(a+b/60,c+d/60) for a,b,c,d in P]
g=gpd.GeoSeries([Point(lon,lat) for lat,lon in pts],crs=4326)
hull=gpd.GeoSeries([MultiPoint(list(g.to_crs(3035))).convex_hull],crs=3035)
print('hull km2',hull.area.iloc[0]/1e6)
j=gpd.read_file(ROOT+'/bounds/jncc/c20251203_OffshoreMPAs_WGS84.shp'); sns=j[j.SITE_NAME=='Southern North Sea'].to_crs(3035).dissolve()
print('all inside SNS:',g.to_crs(3035).within(sns.geometry.iloc[0]).all())
lut=gpd.read_file(ROOT+'/ices/csquares.gpkg').to_crs(3035); lut['a']=lut.area
ov=gpd.overlay(lut[['cSquare','a','geometry']],gpd.GeoDataFrame(geometry=hull),how='intersection'); ov['w']=ov.area/ov.a
for y in range(2019,2026):
    for L in ['Total']:
        d=pd.read_parquet(ROOT+f'/ices/store/AnnexCategory_{L}_{y}.parquet').set_index('cSquare')
        m=ov.merge(d[['FISH_HRS','SAR']],left_on='cSquare',right_index=True,how='left').fillna(0)
        print(y,'hours %.0f'%(m.FISH_HRS*m.w).sum(),'hrs/km2 %.1f'%((m.FISH_HRS*m.w).sum()/(hull.area.iloc[0]/1e6)),'mean SAR %.2f'%((m.SAR*m.a*m.w).sum()/(m.a*m.w).sum()))
