"""
Robustness checks. Prints statistics; writes no figure.

Inputs : zones, trout_zones, wildlice, farms
Outputs: outputs/figures/

Ported from the original working script `legacy/robust.py` with the analysis and
figure code unchanged. Only the plumbing differs: paths now resolve from the
repository root, the processed datasets are read from CSV rather than pickle,
and the display fonts fall back when they are not installed.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from repo import DATA, FIGS, load, load_series, use_font, save  # noqa: F401
import matplotlib
import matplotlib.pyplot as plt

OUT = str(FIGS)
FONT_SANS = use_font("Inter")
FONT_SERIF = use_font("Caladea", "DejaVu Serif")

import pandas as pd, numpy as np
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.stattools import durbin_watson
from statsmodels.stats.multitest import multipletests

rng = np.random.default_rng(7)
res = {}

def nw(y, X, maxlags=2):
    Xc = sm.add_constant(X)
    m = sm.OLS(y, Xc).fit()
    mn = sm.OLS(y, Xc).fit(cov_type='HAC', cov_kwds={'maxlags':maxlags})
    return m, mn

def boot_r(x, y, n=20000):
    rs=[]
    idx=np.arange(len(x))
    for _ in range(n):
        s=rng.choice(idx,len(idx),replace=True)
        if np.std(x[s])==0 or np.std(y[s])==0: continue
        rs.append(np.corrcoef(x[s],y[s])[0,1])
    return np.percentile(rs,[2.5,97.5])

print("="*70); print("TEST 1  salmon west vs east, log-ratio on year")
z = load("zones")
lr = np.log(z["aqua"]/z["east"]).dropna()
for lab,(a,b) in {"1952-2025":(1952,2025),"1980-2010":(1980,2010),
                  "pre-1980":(1952,1979),"post-2010":(2011,2025)}.items():
    s = lr.loc[a:b]
    m, mn = nw(s.values, s.index.values.astype(float))
    dw = durbin_watson(m.resid)
    print(f"  {lab:10s} n={len(s):3d} slope={m.params[1]:+.5f}/yr  "
          f"OLS p={m.pvalues[1]:.4f}  NW p={mn.pvalues[1]:.4f}  DW={dw:.2f}")
    if lab=="1980-2010": res["salmon_1980_2010"]=mn.pvalues[1]

print("="*70); print("TEST 2  sea trout west vs east, log-ratio on year")
t = load("trout_zones")
lrt = np.log(t["aqua"]/t["east"]).dropna()
for lab,(a,b) in {"1952-2025":(1952,2025),"pre-1980":(1952,1979),
                  "1980-2010":(1980,2010)}.items():
    s = lrt.loc[a:b]
    m, mn = nw(s.values, s.index.values.astype(float))
    print(f"  {lab:10s} n={len(s):3d} slope={m.params[1]:+.5f}/yr  "
          f"OLS p={m.pvalues[1]:.4f}  NW p={mn.pvalues[1]:.4f}  DW={durbin_watson(m.resid):.2f}")
    if lab=="pre-1980": res["trout_pre1980"]=mn.pvalues[1]

print("="*70); print("TEST 3  wild sea trout lice vs farm biomass, first-differenced")
fish = load("wildlice"); fish=fish[(fish.yr>=1997)&(fish.yr<=2024)]
sea  = load("farms")
bio  = (sea.groupby("yr")["Actual Biomass on Site (tonnes)"].sum()/12).rename("biomass")
ann = pd.DataFrame({"pct_any": fish.assign(f=fish.total_lice>0).groupby("yr")["f"].mean()*100}).join(bio).dropna().sort_index()
dd = ann.diff().dropna()
x = dd.biomass.values/1000.0; y = dd.pct_any.values
r,p = stats.pearsonr(x,y); rho,prho = stats.spearmanr(x,y)
m, mn = nw(y, x)
lo,hi = boot_r(x,y)
print(f"  n={len(x)}  Pearson r={r:+.3f} p={p:.4f}   bootstrap 95% CI [{lo:+.3f}, {hi:+.3f}]")
print(f"  Spearman rho={rho:+.3f} p={prho:.4f}")
print(f"  slope={m.params[1]:+.3f} pp/kt  OLS p={m.pvalues[1]:.4f}  Newey-West p={mn.pvalues[1]:.4f}")
print(f"  Durbin-Watson={durbin_watson(m.resid):.2f}   (2.0 = no autocorrelation)")
res["lice_biomass"]=mn.pvalues[1]

# residual autocorrelation of the UNdifferenced series, for comparison
mr,_ = nw(ann.pct_any.values, ann.biomass.values/1000.0)
print(f"  [undifferenced, for contrast: DW={durbin_watson(mr.resid):.2f}, p={mr.pvalues[1]:.4f}]")

print("="*70); print("MULTIPLE COMPARISONS across the three headline tests")
keys=list(res); pv=[res[k] for k in keys]
for meth,lab in [("holm","Holm-Bonferroni"),("fdr_bh","Benjamini-Hochberg")]:
    rej,adj,_,_ = multipletests(pv, alpha=0.05, method=meth)
    print(f"  {lab}:")
    for k,p0,pa,rj in zip(keys,pv,adj,rej):
        print(f"    {k:20s} p={p0:.4f} -> {pa:.4f}  {'survives' if rj else 'FAILS'}")
