import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the trawling/ folder
# Build one geometry layer of every ICES 0.05-degree c-square that appears in any OSPAR layer or year.
# The analysis joins the attribute tables (ices/store/*.parquet) to these shapes by cSquare id.
import glob, geopandas as gpd, pandas as pd
parts=[]
for f in sorted(glob.glob(ROOT+'/ices/raw/OSPAR_*.shp')):
    parts.append(gpd.read_file(f,columns=['cSquare'])[['cSquare','geometry']])
g=pd.concat(parts).drop_duplicates('cSquare')
gpd.GeoDataFrame(g,geometry='geometry',crs=parts[0].crs).to_file(ROOT+'/ices/csquares.gpkg',driver='GPKG')
print(len(g),'c-squares written')
