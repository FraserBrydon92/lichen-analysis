import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the trawling/ folder
import geopandas as gpd, pandas as pd, numpy as np
from rasterio.features import rasterize
from rasterio.transform import from_origin
B=ROOT+'/'
r=np.load('hab_raster.npz'); sub=r['sub']; X0=float(r['x0']); Y1=float(r['y1']); R=float(r['r']); H,W=sub.shape
T=from_origin(X0,Y1,R,R)
lat=Y1-(np.arange(H)+0.5)*R; wrow=np.cos(np.radians(lat))[:,None]*np.ones((1,W))
# pixel -> c-square hours (2023-25 mean), spread evenly over the 100 pixels of each 0.05 cell
lut=gpd.read_file(B+'ices/csquares.gpkg'); c=lut.geometry.centroid
hrs=np.mean([pd.read_parquet(f'{B}ices/store/AnnexCategory_Total_{y}.parquet').set_index('cSquare').FISH_HRS.reindex(lut.cSquare).fillna(0).values for y in (2023,2024,2025)],axis=0)
ci=((Y1-c.y)/0.05).astype(int).values; cj=((c.x-X0)/0.05).astype(int).values
G=np.zeros((int(round((Y1-49)/0.05)),int(round((4.5-X0)/0.05))))
ok=(ci>=0)&(ci<G.shape[0])&(cj>=0)&(cj<G.shape[1]); np.add.at(G,(ci[ok],cj[ok]),hrs[ok])
HP=np.kron(G,np.ones((10,10)))/100.0
NAMES={1:'sand',2:'mud',3:'coarse',4:'mixed',5:'rock_reef',0:'unmapped'}
z=gpd.read_file(B+'results/zones.gpkg').to_crs(4326)
j=gpd.read_file(B+'bounds/jncc/c20251203_OffshoreMPAs_WGS84.shp'); sns=j[j.SITE_NAME=='Southern North Sea'].dissolve()
extra=gpd.GeoDataFrame({'group':['No ban'],'site':['Southern North Sea'],'geometry':[sns.geometry.iloc[0]]},crs=4326)
z=pd.concat([z[['group','site','geometry']],extra],ignore_index=True)
rows=[]
for _,s in z.iterrows():
    m=rasterize([(s.geometry,1)],out_shape=(H,W),transform=T,fill=0,dtype='uint8')==1
    a=wrow[m]; hs=HP[m]; sb=sub[m]; d=dict(group=s.group,site=s.site,hours=hs.sum())
    for k,n in NAMES.items():
        d['area_'+n]=a[sb==k].sum()/a.sum(); d['hrs_'+n]=hs[sb==k].sum()
    rows.append(d)
D=pd.DataFrame(rows); D.to_csv(B+'results/hab_sites.csv',index=False)
pd.set_option('display.width',250)
print(D.round(2).to_string(index=False))
for g in ['Existing ban','Stage 3','No ban']:
    x=D[D.group==g]; t=x.hours.sum()
    print(g,'hours %.0f'%t, {n:round(x['hrs_'+n].sum()/t*100,1) for n in NAMES.values()})
