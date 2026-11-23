import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the trawling/ folder
import sys, zipfile, re, io, json, hashlib, numpy as np, rasterio
G=ROOT+'/grids/'
ref=rasterio.open(G+'gfw_2016.tif'); refgeo=json.load(open(G+'area.geojson'))
for z in sys.argv[1:]:
    zf=zipfile.ZipFile(z); names=zf.namelist()
    md=''.join(zf.read(n).decode('utf8','ignore') for n in names if n.endswith('.md'))
    yrs=re.findall(r"timestamp >= parseDateTimeBestEffort\('(\d{4}-\d\d-\d\d)",md); yrsE=re.findall(r"timestamp < parseDateTimeBestEffort\('(\d{4}-\d\d-\d\d)",md)
    tif=[n for n in names if n.endswith('.tif')]
    geo=json.loads(zf.read([n for n in names if n.endswith('geometry.geojson')][0]))
    if not tif: print(z.split('/')[-1],'NO TIF (not gridded)'); continue
    y=yrs[0][:4]; out=G+f'gfw_{y}.tif'; open(out,'wb').write(zf.read(tif[0]))
    r=rasterio.open(out); a=r.read(1).astype(float); a[a==r.nodata]=np.nan
    print(f"{y}: {yrs[0]} to {yrsE[0]} | gear filter ok: {'dredge_fishing' in md and 'trawlers' in md} | res {r.res[0]:.2f} | same area: {geo==refgeo} | bounds match: {tuple(round(v,2) for v in r.bounds)==tuple(round(v,2) for v in ref.bounds)} | cells {np.isfinite(a).sum():,} | hours {np.nansum(a):,.0f}")
