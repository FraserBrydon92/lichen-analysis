import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the trawling/ folder
import pandas as pd, numpy as np
P=pd.read_csv(ROOT+'/results/panel.csv',parse_dates=['start_date'])
P=P[P.layer=='Total']
W=P.pivot_table(index=['site','year'],columns='zone',values='hrs').reset_index()
A=P[P.year==2025].pivot_table(index='site',columns='zone',values='area_km2')
out=[]
for site,g in W.groupby('site'):
    sd=P[P.site==site].start_date.iloc[0]; by=sd.year
    g=g.set_index('year').drop(columns='site')
    pre=g.loc[by-3:by-1].mean()
    post_years=[y for y in range(by+1,2026)][:2] if by<2024 else [2025]
    post=g.loc[post_years].mean()
    r=post/pre
    out.append(dict(site=site,ban=sd.date(),area=round(A.loc[site,'inside']),
      pre_in=round(pre.inside),post_in=round(post.inside,1),
      chg_in=round((r.inside-1)*100),chg_r0_10=round((r.ring0_10-1)*100),chg_r10_25=round((r.ring10_25-1)*100),chg_ctrl=round((r.ring25_50-1)*100),
      # inside change relative to control (ratio of ratios)
      rel_in=round((r.inside/r.ring25_50-1)*100), rel_r0_10=round((r.ring0_10/r.ring25_50-1)*100),
      post_hrs_per_100km2=round(post.inside/A.loc[site,'inside']*100,1),
      ctrl_hrs_per_100km2_post=round(post.ring25_50/A.loc[site,'ring25_50']*100,1)))
T=pd.DataFrame(out).sort_values(['ban','site'])
T.to_csv(ROOT+'/results/site_summary.csv',index=False)
pd.set_option('display.width',250); print(T.to_string(index=False))
