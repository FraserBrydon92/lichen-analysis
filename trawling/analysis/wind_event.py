import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the trawling/ folder
# Wind farm before/after: trawl hours inside each operational farm vs a 5-20 km ring, around its commissioning year
# Commissioning years: Wikipedia, List of offshore wind farms in the United Kingdom (operational table), accessed 14 Nov 2026.
import sys; sys.path.insert(0,ROOT+'/analysis')
import geopandas as gpd, pandas as pd, numpy as np, statsmodels.api as sm, itertools, warnings; warnings.filterwarnings('ignore')
B=ROOT+'/'
YEAR={'Barrow':2006,'Burbo Bank':2007,'Burbo Bank Extension':2017,'Dudgeon':2017,'East Anglia ONE':2020,'Galloper':2018,'Greater Gabbard':2012,
 'Gunfleet Sands I':2010,'Gunfleet Sands II':2010,'Gunfleet Sands Demo':2013,'Gwynt y Mor':2015,'Hornsea 1':2020,'Hornsea Project 2':2022,'Humber Gateway':2015,
 'Kentish Flats':2005,'Lincs':2013,'London Array':2013,'Lynn':2009,'Inner Dowsing':2009,'North Hoyle':2003,'Ormonde':2012,'Race Bank':2018,'Rampion':2018,
 'Rhyl Flats':2009,'Scroby Sands':2004,'Sheringham Shoal':2012,'Teesside':2013,'Thanet':2010,'Triton Knoll':2022,'Walney 1':2010,'Walney 2':2010,
 'Walney Extension':2018,'Westermost Rough':2015,'West of Duddon Sands':2014,'Beatrice Offshore Wind Farm':2019,'Moray Offshore Windfarm (East)':2022,
 'Robin Rigg':2010,'Seagreen Phase 1 Windfarm':2023,'Aberdeen Offshore Wind Farm':2018,'Kincardine':2021}
def key(n):
    for k in sorted(YEAR,key=len,reverse=True):
        if n.startswith(k): return k
t=gpd.read_file(B+'wind/raw/tce_wind.geojson').to_crs(3035); t=t[t.Inf_Status.str.contains('Operation')]; t['name']=t.Name_Prop
c=gpd.read_file(B+'wind/raw/ces_wind.geojson').to_crs(3035); c=c[(c.Property_Classification=='Wind Farm')&(c.Project_Phase=='Operational')]; c['name']=c.Property_Description
W=pd.concat([t[['name','geometry']],c[['name','geometry']]]); W['farm']=W.name.map(key); W=W.dropna(subset=['farm'])
W=gpd.GeoDataFrame(W,crs=3035); W['geometry']=W.buffer(0); F=W.dissolve('farm').reset_index(); F['cy']=F.farm.map(YEAR)
allw=pd.concat([gpd.read_file(B+'wind/raw/tce_wind.geojson').to_crs(3035).geometry,gpd.read_file(B+'wind/raw/ces_wind.geojson').to_crs(3035).geometry]).buffer(0).union_all()
ban=gpd.read_file(B+'results/zones.gpkg'); ban=ban[ban.group=='Existing ban'].geometry.union_all()
lut=gpd.read_file(B+'ices/csquares.gpkg').to_crs(3035); lut['a']=lut.area; sidx=lut.sindex
Hy={y:pd.read_parquet(f'{B}ices/store/AnnexCategory_Total_{y}.parquet').set_index('cSquare').FISH_HRS for y in range(2009,2026)}
rows=[]
for _,r in F.iterrows():
    g=r.geometry; ring=g.buffer(20000).difference(g.buffer(5000)).difference(allw).difference(ban)
    for zn,geo in [('inside',g),('ring',ring)]:
        sub=lut.iloc[sidx.query(geo,predicate='intersects')]; f=(sub.intersection(geo).area/sub['a']).values
        for y in range(2009,2026): rows.append((r.farm,zn,y,(Hy[y].reindex(sub.cSquare).fillna(0).values*f).sum(),r.cy))
P=pd.DataFrame(rows,columns=['site','zone','year','hrs','ban_year'])
P.to_csv(B+'results/wind_panel.csv',index=False)
# farms commissioned 2012-2023 with >=3 pre years and >=50 pre hours inside
pre=P[(P.zone=='inside')&(P.year>=P.ban_year-3)&(P.year<P.ban_year)].groupby('site').hrs.mean()
S=sorted([s for s in pre.index if pre[s]>=50 and 2012<=P[P.site==s].ban_year.iloc[0]<=2023])
print('farms in test:',len(S),S)
import inference as I
I.P=P.rename(columns={}).copy(); I.P['zone']=I.P.zone.replace({'ring':'r5_20'})
r=I.did(T='inside',C='r5_20',sites=S,label='wind'); print('Wind DiD: %.1f%% (95%% CI %.1f to %.1f), p=%.4f, farms=%d'%(r['pct'],r['lo'],r['hi'],r['p'],r['sites']))
rt=I.did(T='inside',C='r5_20',sites=S,trend=True,label='wind trend'); print('With farm trends: %.1f%% (%.1f to %.1f), p=%.4f'%(rt['pct'],rt['lo'],rt['hi'],rt['p']))
d=I.stack('inside','r5_20',S); m=I.fit(d,event=True)
ks=[k for k in range(-6,4) if k!=-1]; E=pd.DataFrame({'k':ks,'pct':[I.pct(m.params[f'b{k}']) for k in ks],'lo':[I.pct(m.params[f'b{k}']-1.96*m.bse[f'b{k}']) for k in ks],'hi':[I.pct(m.params[f'b{k}']+1.96*m.bse[f'b{k}']) for k in ks]})
print(E.round(1).to_string(index=False)); E.to_csv(B+'results/wind_event.csv',index=False)
# wild cluster score bootstrap
import wildboot as WB
WB.P=I.P; WB.stack=I.stack; WB.design=I.design
G,p=WB.score_boot(T='inside',C='r5_20',sites=S) if len(S)<=18 else (len(S),np.nan)
print('wild cluster score bootstrap p=',p,'G=',G)
