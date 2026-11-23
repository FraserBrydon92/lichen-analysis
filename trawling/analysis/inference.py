import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the trawling/ folder
# Inference for the ban effect: PPML difference-in-differences / event study with site-by-year fixed effects,
# site-clustered SEs, leave-one-site-out, and randomization inference on ban timing.
import pandas as pd, numpy as np, statsmodels.api as sm, warnings; warnings.filterwarnings('ignore')
P=pd.read_csv(ROOT+'/results/panel2.csv')
pre=P[(P.zone=='inside')&(P.year>=P.ban_year-3)&(P.year<P.ban_year)].groupby('site').hrs.mean()
MAIN=sorted(pre[pre>=50].index); ALL=sorted(pre.index)
def stack(T,C,sites,var='hrs',by=None):
    d=P[P.site.isin(sites)&P.zone.isin([T,C])].copy()
    if by is not None: d['ban_year']=d.site.map(by)
    d['treat']=(d.zone==T).astype(int); d['k']=(d.year-d.ban_year).clip(-6,3); d['y']=d[var]
    ok=d[(d.treat==1)&(d.year<d.ban_year)].groupby('site').y.sum(); ok=ok[ok>0].index   # drop sites with no pre-ban effort in the treated zone
    return d[d.site.isin(ok)]
def design(d,event,trend=False):
    X=pd.get_dummies(d.site+'|'+d.zone,drop_first=True,dtype=float)
    X=X.join(pd.get_dummies(d.site+'|'+d.year.astype(str),prefix='sy',drop_first=True,dtype=float))
    if event:
        for k in range(-6,4):
            if k!=-1: X[f'b{k}']=((d.k==k)&(d.treat==1)).astype(float)
    else: X['post']=((d.k>=0)&(d.treat==1)).astype(float)
    if trend:   # site-specific linear trend in the inside-vs-ring gap
        for st in d.site.unique(): X['tr_'+st]=((d.site==st)&(d.treat==1)).astype(float)*(d.year-2017)/10
    X.insert(0,'const',1.0); return X
def fit(d,event=False,ols=False,trend=False):
    X=design(d,event,trend); g=d.site.astype('category').cat.codes.values
    if ols: m=sm.OLS(np.log1p(d.y.values),X).fit(cov_type='HC1')
    else:
        y=d.y.values/d.y.mean()   # PPML is scale-invariant; rescale for numerical stability
        m=sm.GLM(y,X,family=sm.families.Poisson()).fit(method='newton',maxiter=500,start_params=np.zeros(X.shape[1]),cov_type='cluster',cov_kwds={'groups':g})
    return m
pct=lambda b:(np.exp(b)-1)*100
def did(T='inside',C='r25_50',sites=MAIN,var='hrs',ols=False,dropk0=False,label='',trend=False):
    d=stack(T,C,sites,var)
    if dropk0: d=d[d.k!=0]
    m=fit(d,ols=ols,trend=trend); b=m.params['post']; se=m.bse['post']
    return dict(spec=label,sites=d.site.nunique(),beta=b,se=se,pct=pct(b),lo=pct(b-1.96*se),hi=pct(b+1.96*se),p=m.pvalues['post'])
if __name__=='__main__':
    rows=[did(label='Main: all hours inside vs 25-50 km ring (PPML)'),
     did(T='core',label='Wholly-inside cells only'),
     did(C='r10_25',label='Control ring 10-25 km'),
     did(C='r50_100',label='Control ring 50-100 km'),
     did(sites=[s for s in MAIN if s!='Dogger Bank'],label='Excluding Dogger Bank'),
     did(dropk0=True,label='Dropping the part-year ban year'),
     did(var='swept',label='Outcome: swept area, not hours'),
     did(ols=True,label='OLS on log(hours+1), HC1 SE (not clustered)'),
     did(sites=ALL,label='All 20 banned sites'),
     did(trend=True,label='With site-specific linear trends')]
    R=pd.DataFrame(rows); pd.set_option('display.width',220); print(R.round(3).to_string(index=False)); R.to_csv(ROOT+'/results/inf_robust.csv',index=False)
    # leave-one-site-out
    loo=[did(sites=[x for x in MAIN if x!=s],label=s)['pct'] for s in MAIN]; print('leave-one-out % range',round(min(loo),1),round(max(loo),1))
    # event study + pre-trend test
    d=stack('inside','r25_50',MAIN); m=fit(d,event=True)
    ks=[k for k in range(-6,4) if k!=-1]; E=pd.DataFrame({'k':ks,'b':[m.params[f'b{k}'] for k in ks],'se':[m.bse[f'b{k}'] for k in ks]})
    E=pd.concat([E,pd.DataFrame({'k':[-1],'b':[0.0],'se':[0.0]})]).sort_values('k')
    E['n_sites']=E.k.map(lambda k: d[(d.treat==1)&(d.k==k)].site.nunique())
    E['pct']=pct(E.b); E['lo']=pct(E.b-1.96*E.se); E['hi']=pct(E.b+1.96*E.se); print(E.round(2).to_string(index=False)); E.to_csv(ROOT+'/results/inf_event.csv',index=False)
    leads=[f'b{k}' for k in range(-6,-1)]; w=m.wald_test(' , '.join(f'{l}=0' for l in leads),scalar=True); print('pre-trend joint Wald: chi2=%.2f p=%.3f'%(w.statistic,w.pvalue))
    # placebo: pre-period only, fake ban 3 years early
    dp=P[P.year<P.ban_year].copy(); fake=P.groupby('site').ban_year.first()-3
    r2=None
    d=stack('inside','r25_50',MAIN); d=d[d.year<d.ban_year]; d['ban_year']=d.ban_year-3; d['k']=(d.year-d.ban_year).clip(-6,3)
    mp=fit(d); print('Placebo (fake ban 3y early, pre-period only): %.1f%%  p=%.3f'%(pct(mp.params['post']),mp.pvalues['post']))
    # randomization inference: reshuffle ban years across sites
    rng=np.random.default_rng(7); obs=rows[0]['beta']; years=P[P.site.isin(MAIN)].groupby('site').ban_year.first()
    perm=[]
    for i in range(0):
        by=dict(zip(years.index,rng.permutation(years.values)))
        d=stack('inside','r25_50',MAIN,by=by); 
        try: perm.append(fit(d).params['post'])
        except Exception: pass
    perm=np.array(perm); print('randomization inference: n=%d, p=%.4f, perm 95%% range %.1f%% to %.1f%%'%(len(perm),(np.abs(perm)>=abs(obs)).mean(),pct(np.percentile(perm,2.5)),pct(np.percentile(perm,97.5))))
    # displacement: near rings vs far ring
    for T in ['r0_10','r10_25']:
        r=did(T=T,C='r50_100',label=f'Displacement {T} vs 50-100'); print('%s: %+.1f%% (95%% CI %+.1f to %+.1f), p=%.3f'%(r['spec'],r['pct'],r['lo'],r['hi'],r['p']))
        r=did(T=T,C='r50_100',sites=['Dogger Bank'] if False else MAIN,label='');
