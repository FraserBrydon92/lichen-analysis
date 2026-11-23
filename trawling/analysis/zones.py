import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the trawling/ folder
# Build a registry of analysis zones: existing bans, Stage 3 (offshore JNCC + NE inshore), minus existing bans
import geopandas as gpd, pandas as pd, re
B=ROOT+'/'
norm=lambda s: re.sub(r'[^a-z]','',s.lower().replace('’',"'").replace('&','and').split('/')[0])
def build():
    m=gpd.read_file(B+'bounds/mmo/Marine_Conservation_Byelaws.geojson').to_crs(3035)
    m['site']=m.sub_name.str.replace(' reef','').str.replace(' sandbank','')
    ban=m.dissolve('site',aggfunc={'start_date':'min'}).reset_index()
    allban=m.geometry.union_all()
    rows=[dict(group='Existing ban',site=r.site,ban_year=pd.Timestamp(r.start_date).year,geometry=r.geometry) for _,r in ban.iterrows()]
    s3=pd.read_csv(B+'bounds/stage3_sites.csv'); s3['k']=s3.site.map(norm)
    j=gpd.read_file(B+'bounds/jncc/c20251203_OffshoreMPAs_WGS84.shp').to_crs(3035).dissolve('SITE_NAME').reset_index(); j['k']=j.SITE_NAME.map(norm)
    mcz=gpd.read_file(B+'bounds/ne/mcz.geojson').to_crs(3035).rename(columns={'mcz_name':'n'})[['n','geometry']]
    sac=gpd.read_file(B+'bounds/ne/sac.geojson').to_crs(3035).rename(columns={'sac_name':'n'})[['n','geometry']]
    ne=pd.concat([mcz,sac]); ne['k']=ne.n.str.replace('Isles of Scilly Sites - ','').map(norm); ne=ne.dissolve('k').reset_index()
    for _,r in s3.iterrows():
        p=r.proposal
        if p.startswith('a prohibition of the use of traps') or 'minor amendments' in p or 'incorporated into' in p: continue
        hit=j[j.k==r.k]
        if hit.empty: hit=ne[ne.k==r.k]
        if hit.empty: print('missing',r.site); continue
        g=hit.geometry.iloc[0].difference(allban)
        part=('6 nm' in p) or ('part of the MPA' in p) or ('most of' in p) or ('except' in p)
        rows.append(dict(group='Stage 3',site=r.site,ban_year=None,partial=part,geometry=g))
    return gpd.GeoDataFrame(rows,crs=3035)
if __name__=='__main__':
    z=build(); z.to_file(B+'results/zones.gpkg'); print(z.groupby('group').size()); print(z[z.group=='Stage 3'][['site','partial']].to_string())
