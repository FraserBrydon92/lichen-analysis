import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the trawling/ folder
# Event study: inside-site trawl hours relative to comparison ring (25-50 km), indexed to each site's 3 pre-ban years; site-bootstrap 95% CI
import pandas as pd, numpy as np
P=pd.read_csv(ROOT+'/results/panel.csv',parse_dates=['start_date']); P=P[P.layer=='Total']
W=P.pivot_table(index=['site','year'],columns='zone',values='hrs').reset_index()
W['by']=W.site.map(P.groupby('site').start_date.first().dt.year); W['k']=W.year-W.by
W['rel']=np.log(W.inside+1)-np.log(W.ring25_50+1)
base=W[W.k.between(-3,-1)].groupby('site').agg(b=('rel','mean'),pre=('inside','mean'))
keep=base[base.pre>=50].index
E=W[W.site.isin(keep)].merge(base,on='site'); E['d']=E.rel-E.b
E=E[E.k.between(-6,6)]
rng=np.random.default_rng(1); sites=np.array(sorted(keep)); out=[]
for k,g in E.groupby('k'):
    vals=g.set_index('site').d
    s=vals.index.values; bs=[vals.loc[rng.choice(s,len(s))].mean() for _ in range(4000)]
    out.append((k,len(vals),vals.mean(),np.percentile(bs,2.5),np.percentile(bs,97.5)))
R=pd.DataFrame(out,columns=['k','n_sites','mean_log','lo','hi'])
for c in ['mean_log','lo','hi']: R[c.replace('log','pct') if c=='mean_log' else c+'_pct']=(np.exp(R[c])-1)*100
print('sites:',list(keep)); print(R.round(2).to_string(index=False)); R.to_csv(ROOT+'/results/event.csv',index=False)
# leave-Dogger-out check for k>=1
g=E[(E.k>=1)&(E.site!='Dogger Bank')].groupby('site').d.mean(); print('post mean excl Dogger, % :',round((np.exp(g.mean())-1)*100), ' n=',len(g), ' sites with post<pre:',(g<0).sum())
