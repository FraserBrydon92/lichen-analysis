import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the trawling/ folder
# Counterfactual accounting: expected = pre x (control post/pre). removed = expected_in - actual_in; extra in ring = actual_ring - expected_ring
import pandas as pd
P=pd.read_csv(ROOT+'/results/panel.csv',parse_dates=['start_date']); P=P[P.layer=='Total']
W=P.pivot_table(index=['site','year'],columns='zone',values='hrs')
rows=[]
for site in P.site.unique():
    by=P[P.site==site].start_date.iloc[0].year; g=W.loc[site]
    pre=g.loc[by-3:by-1].mean(); post=g.loc[[y for y in range(by+1,2026)][:2] if by<2024 else [2025]].mean()
    k=post.ring25_50/pre.ring25_50
    rem=pre.inside*k-post.inside; e10=post.ring0_10-pre.ring0_10*k; e25=post.ring10_25-pre.ring10_25*k
    rows.append(dict(site=site,ban=by,pre_inside=round(pre.inside),removed=round(rem),extra_0_10=round(e10),extra_10_25=round(e25),
        reappear_0_25_pct=round((e10+e25)/rem*100) if rem>50 else None))
T=pd.DataFrame(rows).sort_values(['ban','site']); print(T.to_string(index=False))
big=T[T.removed>50]; print('\nSites with >50 h removed:',len(big),' removed',big.removed.sum(),' extra 0-10',big.extra_0_10.sum(),' extra 10-25',big.extra_10_25.sum())
nd=big[big.site!='Dogger Bank']; print('excl Dogger: removed',nd.removed.sum(),' extra 0-10',nd.extra_0_10.sum(),' extra 10-25',nd.extra_10_25.sum())
T.to_csv(ROOT+'/results/displacement.csv',index=False)
