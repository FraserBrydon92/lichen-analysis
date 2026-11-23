import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the trawling/ folder
import sys; sys.path.insert(0,ROOT+'/bounds/scot')
import geopandas as gpd, pandas as pd, numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
from zones_src import Z, WHOLE
B=ROOT+'/'
def poly(s):
    pts=[]
    for p in s.split(';'):
        a=p.split(); lat=float(a[0])+float(a[1])/60; lon=float(a[3])+float(a[4])/60
        if a[2]=='S': lat=-lat
        if a[5]=='W': lon=-lon
        pts.append((lon,lat))
    return Polygon(pts).buffer(0)
if __name__=='__main__':
    j=gpd.read_file(B+'bounds/jncc/c20251203_OffshoreMPAs_WGS84.shp').dissolve('SITE_NAME').reset_index()
    lut=gpd.read_file(B+'ices/csquares.gpkg').to_crs(3035); lut['a']=lut.area; sidx=lut.sindex
    D={y:pd.read_parquet(f'{B}ices/store/AnnexCategory_Total_{y}.parquet').set_index('cSquare') for y in (2022,2023,2024)}
    def stats(g):
        if g.is_empty: return 0,0,0
        sub=lut.iloc[sidx.query(g,predicate='intersects')]; ov=sub.intersection(g).area.values; f=ov/sub['a'].values
        h=np.mean([(D[y].FISH_HRS.reindex(sub.cSquare).fillna(0).values*f).sum() for y in D])
        v=np.mean([(D[y].TOT_VAL.reindex(sub.cSquare).fillna(0).values*f).sum() for y in D])
        return g.area/1e6,h,v
    rows=[]
    for name in list(Z)+WHOLE:
        site=j[j.SITE_NAME.str.startswith(name)]
        if site.empty: print('no site',name); continue
        sg=gpd.GeoSeries([site.geometry.iloc[0]],crs=4326).to_crs(3035).iloc[0]
        if name in Z:
            zg=gpd.GeoSeries([unary_union([poly(p) for p in Z[name]])],crs=4326).to_crs(3035).iloc[0]
            closed=zg.intersection(sg); outside_site=zg.difference(sg).area/zg.area
        else: closed=sg; outside_site=0
        opn=sg.difference(closed)
        ac,hc,vc=stats(closed); ao,ho,vo=stats(opn)
        rows.append(dict(site=name,type='zoned' if name in Z else 'whole-site',zone_outside_site_pct=round(outside_site*100,1),
           closed_km2=ac,open_km2=ao,closed_hrs=hc,open_hrs=ho,closed_val=vc,open_val=vo))
    T=pd.DataFrame(rows); T['pct_area_closed']=T.closed_km2/(T.closed_km2+T.open_km2)*100
    T['pct_hrs_closed']=T.closed_hrs/(T.closed_hrs+T.open_hrs).replace(0,np.nan)*100
    T['int_closed']=T.closed_hrs/T.closed_km2*100; T['int_open']=T.open_hrs/T.open_km2.replace(0,np.nan)*100
    pd.set_option('display.width',250); print(T.round(1).to_string(index=False))
    Zd=T[T.type=='zoned']
    print('\nZONED sites: area closed %',round(Zd.closed_km2.sum()/(Zd.closed_km2.sum()+Zd.open_km2.sum())*100,1),
          ' effort inside closed zones %',round(Zd.closed_hrs.sum()/(Zd.closed_hrs.sum()+Zd.open_hrs.sum())*100,1),
          ' intensity closed vs open (h/100km2)',round(Zd.closed_hrs.sum()/Zd.closed_km2.sum()*100,1),round(Zd.open_hrs.sum()/Zd.open_km2.sum()*100,1))
    print('ALL 17: total hrs',round(T.closed_hrs.sum()+T.open_hrs.sum()),' left open',round(T.open_hrs.sum()))
    T.to_csv(B+'results/scotland_zones.csv',index=False)
