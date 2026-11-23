import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the trawling/ folder
# Rasterise EUSeaMap 2025 (UK cut) to 0.005-degree grid aligned with ICES 0.05-degree c-squares
import geopandas as gpd, numpy as np, rasterio, pyogrio
from rasterio.features import rasterize
from rasterio.transform import from_origin
X0,X1,Y0,Y1=-11.0,4.5,49.0,61.5; R=0.005
W=int(round((X1-X0)/R)); H=int(round((Y1-Y0)/R)); T=from_origin(X0,Y1,R,R)
SUB={'Sand':1,'Muddy sand':1,'Mud':2,'Sandy mud':2,'Mud to muddy sand':2,'Fine mud':2,'Coarse substrate':3,'Mixed sediment':4,'Rock or other hard substrata':5,'Fine mud or Sandy mud or Muddy sand':2,'Sandy mud or Muddy sand':2,'Biogenic substrate':5}
import re
def zone(m):
    if not isinstance(m,str): return 0
    if m.startswith('Infralittoral'): return 1
    if m.startswith('Offshore'): return 3
    if m.startswith('Circalittoral'): return 2
    if 'bathyal' in m.lower() or 'Abyssal' in m: return 4
    return 0
sub=np.zeros((H,W),np.uint8); dep=np.zeros((H,W),np.uint8); seen=set()
for i in range(1,5):
    d=pyogrio.read_dataframe(fROOT+f'/data/EUSeaMap_2025_UK/uk_part{i}.gpkg',columns=['Substrate','MSFD_BBHT'])
    print(i,len(d),flush=True); seen|=set(d.Substrate.unique())
    s=d.Substrate.map(lambda v: SUB.get(v, 5 if isinstance(v,str) and re.search('reef|beds',v,re.I) else 0)).astype(int); z=d.MSFD_BBHT.map(zone)
    m=s>0; sub=np.maximum(sub,rasterize(zip(d.geometry[m],s[m]),out_shape=(H,W),transform=T,fill=0,dtype='uint8'))
    m=z>0; dep=np.maximum(dep,rasterize(zip(d.geometry[m],z[m]),out_shape=(H,W),transform=T,fill=0,dtype='uint8'))
print('substrate values seen',seen)
np.savez_compressed(ROOT+'/results/hab_raster.npz',sub=sub,dep=dep,x0=X0,y1=Y1,r=R)
print({k:(sub==v).sum() for k,v in [('sand',1),('mud',2),('coarse',3),('mixed',4),('rock',5),('none',0)]})
