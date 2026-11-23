import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the trawling/ folder
# Per zone x year: hours, landed value, swept-area ratio by gear, modelled relative benthic status (Hiddink et al. 2017 logistic model)
import geopandas as gpd, pandas as pd, numpy as np
B=ROOT+'/'
z=gpd.read_file(B+'results/zones.gpkg')
lut=gpd.read_file(B+'ices/csquares.gpkg').to_crs(3035); lut['a']=lut.area; sidx=lut.sindex
W={}
for i,r in z.iterrows():
    sub=lut.iloc[sidx.query(r.geometry,predicate='intersects')]
    ov=sub.intersection(r.geometry).area.values
    W[i]=(sub.cSquare.values, ov/sub['a'].values, ov)   # ids, fraction of cell inside, overlap area
SC={'central':(0.82,0.13),'pessimistic':(0.42,0.20),'optimistic':(1.53,0.06)}  # (r per year, depletion assumed for dredge/seine remainder)
rows=[]
for y in range(2009,2026):
    L={k:pd.read_parquet(f'{B}ices/store/AnnexCategory_{k}_{y}.parquet').set_index('cSquare') for k in ['Total','Otter_trawl','Beam_trawl']}
    for i,(ids,f,ov) in W.items():
        t=L['Total'].reindex(ids); o=L['Otter_trawl'].reindex(ids).SAR.fillna(0).values; b=L['Beam_trawl'].reindex(ids).SAR.fillna(0).values
        sar=t.SAR.fillna(0).values; rem=np.clip(sar-o-b,0,None)
        rec=dict(zid=i,year=y,hrs=(t.FISH_HRS.fillna(0).values*f).sum(),value=(t.TOT_VAL.fillna(0).values*f).sum(),
                 sar=(sar*ov).sum()/ov.sum(), sar_ot=(o*ov).sum()/ov.sum(), sar_bt=(b*ov).sum()/ov.sum(), sar_rem=(rem*ov).sum()/ov.sum(),
                 frac_untrawled=(ov*(sar==0)).sum()/ov.sum())
        for k,(rr,dr) in SC.items():
            st=np.clip(1-(0.06*o+0.14*b+dr*rem)/rr,0,1); rec['rbs_'+k]=(st*ov).sum()/ov.sum()
        rows.append(rec)
M=pd.DataFrame(rows).merge(z.drop(columns='geometry').reset_index().rename(columns={'index':'zid'}),on='zid')
M['area_km2']=M.zid.map({i:v[2].sum()/1e6 for i,v in W.items()})
M.to_csv(B+'results/metrics.csv',index=False); print(len(M))
