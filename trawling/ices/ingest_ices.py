import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the trawling/ folder
import glob, re, os, geopandas as gpd, pandas as pd
S=ROOT+'/ices/store/'
rows=[]
for f in sorted(glob.glob(ROOT+'/ices/**/OSPAR_*.dbf',recursive=True)):
    m=re.search(r'OSPAR_(.+)_(\d{4})\.dbf',os.path.basename(f)); layer,yr=m.group(1),int(m.group(2)); out=f'{S}{layer}_{yr}.parquet'
    if os.path.exists(out): d=pd.read_parquet(out)
    else:
        d=pd.DataFrame(gpd.read_file(f,ignore_geometry=True)); d['layer']=layer; d.to_parquet(out)
    rows.append((layer.replace('AnnexCategory_',''),yr,len(d),d.cSquare.nunique()==len(d),int(d.YEAR.iloc[0])==yr,round(d.FISH_HRS.sum()),round(d.MASKED.mean()*100,1)))
t=pd.DataFrame(rows,columns=['layer','year','cells','one_row_per_cell','year_ok','fish_hrs','pct_masked'])
t.to_csv(ROOT+'/ices/inventory.csv',index=False); print(t.to_string(index=False))
