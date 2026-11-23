import os as _os
ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the trawling/ folder
# Wild cluster score bootstrap (Kline & Santos 2012) for the PPML ban effect, full enumeration of Rademacher weights over 15 site clusters,
# plus a pairs cluster bootstrap for percentile intervals.
import sys; sys.path.insert(0,ROOT+'/analysis')
import numpy as np, pandas as pd, statsmodels.api as sm, itertools, warnings; warnings.filterwarnings('ignore')
from inference import *
def score_boot(T='inside',C='r25_50',sites=MAIN,trend=False,var='hrs'):
    d=stack(T,C,sites,var); X=design(d,False,trend); y=d.y.values/d.y.mean(); g=d.site.values
    Xr=X.drop(columns='post')
    mr=sm.GLM(y,Xr,family=sm.families.Poisson()).fit(method='newton',maxiter=500,start_params=np.zeros(Xr.shape[1]))
    mu=np.asarray(mr.fittedvalues); u=y-mu
    # partial the post regressor out of the restricted regressors with Poisson weights
    W=np.sqrt(mu); xp=X['post'].values
    b=np.linalg.lstsq(Xr.values*W[:,None],xp*W,rcond=None)[0]; xt=xp-Xr.values@b
    cl=pd.Series(xt*u).groupby(g).sum().values; S=cl.sum(); G=len(cl)
    W_all=np.array(list(itertools.product([-1,1],repeat=G)))
    Sb=W_all@cl; p=(np.abs(Sb)>=abs(S)-1e-12).mean()
    return G,p
def pairs_ci(T='inside',C='r25_50',sites=MAIN,B=499,trend=False):
    rng=np.random.default_rng(11); out=[]
    for _ in range(B):
        s=rng.choice(sites,len(sites))
        d=pd.concat([stack(T,C,[x]).assign(site=f'{x}#{i}') for i,x in enumerate(s)]).reset_index(drop=True)
        try: out.append(fit(d,trend=trend).params['post'])
        except Exception: pass
    out=np.array(out); return len(out),pct(np.percentile(out,2.5)),pct(np.percentile(out,97.5))
if __name__=='__main__':
    for lab,kw in [] and [('Main',{}),('Excluding Dogger',{'sites':[s for s in MAIN if s!='Dogger Bank']}),('Site-specific trends',{'trend':True}),('Displacement 0-10 vs 50-100',{'T':'r0_10','C':'r50_100'})]:
        G,p=score_boot(**kw); print(f'{lab}: wild cluster score bootstrap p = {p:.4f} (G={G}, all {2**G} Rademacher draws)')
    for lab,kw in [('Main',{}),('Site-specific trends',{'trend':True})]:
        n,lo,hi=pairs_ci(**kw); print(f'{lab}: pairs cluster bootstrap 95% CI {lo:.0f}% to {hi:.0f}% (n={n})')
