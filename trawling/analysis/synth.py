import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the trawling/ folder
# Synthetic control for each banned site: donor pool of unprotected 0.25-degree blocks within 300 km,
# matched on pre-ban trawl intensity trajectory; inference by in-space placebos (post/pre RMSPE ranks).
import geopandas as gpd, pandas as pd, numpy as np
from scipy.optimize import minimize
B=ROOT+'/'
lut=gpd.read_file(B+'ices/csquares.gpkg'); c=lut.geometry.centroid; lut['lon']=c.x; lut['lat']=c.y
lut3=lut.to_crs(3035); lut['km2']=lut3.area/1e6; lut['x']=lut3.centroid.x; lut['y']=lut3.centroid.y
# exclusions: any MPA (JNCC offshore, NE MCZ+SAC), wind sites, and 25 km around each banned site
j=gpd.read_file(B+'bounds/jncc/c20251203_OffshoreMPAs_WGS84.shp').to_crs(3035)[['geometry']]
ne=pd.concat([gpd.read_file(B+'bounds/ne/mcz.geojson').to_crs(3035)[['geometry']],gpd.read_file(B+'bounds/ne/sac.geojson').to_crs(3035)[['geometry']]])
wind=pd.concat([gpd.read_file(B+'wind/raw/tce_wind.geojson').to_crs(3035)[['geometry']],gpd.read_file(B+'wind/raw/ces_wind.geojson').to_crs(3035)[['geometry']]])
z=gpd.read_file(B+'results/zones.gpkg'); bans=z[z.group=='Existing ban']
bb=bans[['geometry']].copy(); bb['geometry']=bb.buffer(25000)
EX=gpd.GeoDataFrame(pd.concat([j,ne,wind,bb]),crs=3035); EX['geometry']=EX.buffer(0)
pts=gpd.GeoDataFrame(geometry=gpd.points_from_xy(lut.x,lut.y),crs=3035)
hit=gpd.sjoin(pts,EX,predicate='within',how='inner').index.unique()
lut['ok']=True; lut.loc[hit,'ok']=False
YRS=range(2009,2026)
H=pd.DataFrame({y:pd.read_parquet(f'{B}ices/store/AnnexCategory_Total_{y}.parquet').set_index('cSquare').FISH_HRS.reindex(lut.cSquare).fillna(0).values for y in YRS},index=lut.cSquare)
lut['blk']=(np.floor(lut.lon/0.25)).astype(int).astype(str)+'_'+(np.floor(lut.lat/0.25)).astype(int).astype(str)
okc=lut[lut.ok]
g=okc.groupby('blk'); blkarea=g.km2.sum(); blkn=g.size()
D=(H.loc[okc.cSquare].groupby(okc.blk.values).sum()).div(blkarea,axis=0)*100   # hours per 100 km2
D=D[blkn.reindex(D.index)>=10]
bxy=okc.groupby('blk')[['x','y']].mean().reindex(D.index)
print('donor blocks',len(D))
# treated series: hours per 100 km2 inside each site (panel2 inside)
P=pd.read_csv(B+'results/panel2.csv'); A=pd.read_csv(B+'results/metrics.csv').groupby('site').area_km2.first()
ins=P[P.zone=='inside'].pivot_table(index='site',columns='year',values='hrs')
by=P.groupby('site').ban_year.first()
pre_mean=P[(P.zone=='inside')&(P.year>=P.ban_year-3)&(P.year<P.ban_year)].groupby('site').hrs.mean()
MAIN=sorted(pre_mean[pre_mean>=50].index)
def scm(y,Y0,pre):
    # y: treated series (T,), Y0: donors (T,J). weights >=0 sum 1 minimising pre-period MSE
    J=Y0.shape[1]; w0=np.ones(J)/J
    f=lambda w: ((y[pre]-Y0[pre]@w)**2).mean()
    r=minimize(f,w0,method='SLSQP',bounds=[(0,1)]*J,constraints=[{'type':'eq','fun':lambda w:w.sum()-1}],options={'maxiter':500})
    return r.x
rows=[];paths={}
for s in MAIN:
    yr=by[s]; geo=bans[bans.site==s].geometry.iloc[0]; cx,cy=geo.centroid.x,geo.centroid.y
    near=D[np.hypot(bxy.x-cx,bxy.y-cy)<300000]
    yrs=np.array(list(YRS)); pre=yrs<yr; post=yrs>yr   # drop part-year ban year
    yv=(ins.loc[s,list(YRS)]/A[s]*100).values
    Y0=near[list(YRS)].values.T
    # keep donors with pre-period mean within 0.2x-5x of treated (comparable intensity), up to 60 nearest by pre-period distance
    pm=Y0[pre].mean(0); keep=(pm>0)&(pm>yv[pre].mean()*0.2)&(pm<yv[pre].mean()*5)
    Y0=Y0[:,keep]
    if Y0.shape[1]>40:   # cap at the 40 donors closest in pre-ban trajectory, for tractable placebo inference
        dist=((Y0[pre]-yv[pre][:,None])**2).mean(0); Y0=Y0[:,np.argsort(dist)[:40]]
    if Y0.shape[1]<8: print(s,'too few donors',Y0.shape[1]); continue
    w=scm(yv,Y0,pre); synth=Y0@w
    rm=lambda a,b,m: np.sqrt(((a[m]-b[m])**2).mean())
    pre_r=rm(yv,synth,pre); post_r=rm(yv,synth,post); ratio=post_r/max(pre_r,1e-9)
    # placebos: each donor treated in turn, using remaining donors
    pr=[]
    for k in range(Y0.shape[1]):
        yk=Y0[:,k]; Yk=np.delete(Y0,k,axis=1); wk=scm(yk,Yk,pre); sk=Yk@wk
        pr.append(rm(yk,sk,post)/max(rm(yk,sk,pre),1e-9))
    p=(np.sum(np.array(pr)>=ratio)+1)/(len(pr)+1)
    eff=(yv[post].sum()-synth[post].sum())/synth[post].sum()*100
    print(s,flush=True); rows.append(dict(site=s,ban=yr,donors=Y0.shape[1],pre_rmspe=pre_r,pre_mean=yv[pre].mean(),post_actual=yv[post].mean(),post_synth=synth[post].mean(),effect_pct=eff,p_placebo=p,actual_hrs_post=yv[post].mean()*A[s]/100,synth_hrs_post=synth[post].mean()*A[s]/100))
    paths[s]=(yrs,yv,synth)
R=pd.DataFrame(rows); pd.set_option('display.width',220); print(R.round(3).to_string(index=False))
R=R[R.post_synth>0]
tot=(R.actual_hrs_post.sum()-R.synth_hrs_post.sum())/R.synth_hrs_post.sum()*100
nd=R[R.site!='Dogger Bank']; tot_nd=(nd.actual_hrs_post.sum()-nd.synth_hrs_post.sum())/nd.synth_hrs_post.sum()*100
print('pooled effect (hours-weighted) %.1f%%, excluding Dogger %.1f%%, median site %.1f%%, sites with p<0.10: %d/%d'%(tot,tot_nd,R.effect_pct.median(),(R.p_placebo<0.1).sum(),len(R)))
# Fisher combination of site placebo p-values
from scipy.stats import combine_pvalues
print('combined (Fisher) p =',combine_pvalues(R.p_placebo,method='fisher')[1])
R.to_csv(B+'results/synth.csv',index=False)
import pickle; pickle.dump(paths,open(B+'results/synth_paths.pkl','wb'))
