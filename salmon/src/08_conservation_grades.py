"""
River conservation gradings.

Inputs : data embedded in the script
Outputs: outputs/figures/

Ported from the original working script `legacy/charts8.py` with the analysis and
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

GROUND="#081a24"; CREAM="#f2f7f8"; MIST="#9dbac6"; DIM="#5a7d8c"
AQUA="#3fd0c9"; CORAL="#ff6f5e"; GOLD="#f3c969"
SERIF=FONT_SERIF; SANS=FONT_SANS
plt.rcParams.update({"font.family":SANS,"figure.facecolor":GROUND,
                     "savefig.facecolor":GROUND,"axes.facecolor":GROUND,"text.color":CREAM})

data={"2019":(28.9,17.5,53.6,166),"2026":(15.1,14.2,70.8,212)}
fig,ax=plt.subplots(figsize=(8.4,4.9))
fig.subplots_adjust(left=0.105,right=0.955,top=0.635,bottom=0.20)
for s in ax.spines.values(): s.set_visible(False)
ax.set_xticks([]); ax.tick_params(length=0,colors=MIST,labelsize=12)

ys=[0.62,0.0]
for (yr,(g,m,p,n)),y in zip(data.items(),ys):
    left=0
    for val,col,lab in [(g,AQUA,"Good"),(m,GOLD,"Moderate"),(p,CORAL,"Poor")]:
        ax.barh(y,val,left=left,height=0.40,color=col,edgecolor=GROUND,linewidth=1.6,zorder=3)
        if val>7:
            ax.text(left+val/2,y,f"{val:.1f}%",ha="center",va="center",
                    fontsize=12.5,fontweight="700",color=GROUND,zorder=6)
        left+=val
    ax.text(-1.6,y,yr,ha="right",va="center",fontsize=15,fontfamily=SERIF,
            fontweight="bold",color=CREAM)
    ax.text(-1.6,y-0.175,f"n={n}",ha="right",va="center",fontsize=9.5,color=DIM)

ax.set_xlim(0,100); ax.set_ylim(-0.42,1.08)
ax.set_yticks([])
for x,c,t in [(14,AQUA,"Good"),(36,GOLD,"Moderate"),(72,CORAL,"Poor")]:
    ax.text(x,1.00,t,ha="center",va="center",fontsize=11,color=c,fontweight="700")

fig.text(0.062,0.962,"THE GOVERNMENT'S OWN SCORECARD, UNREPORTED AS A TREND",
         fontsize=10,color=AQUA,ha="left",va="top",fontweight="700")
fig.text(0.062,0.905,"Seven years on, the share graded Good has halved",
         fontsize=19,fontfamily=SERIF,fontweight="bold",color=CREAM,ha="left",va="top")
fig.text(0.062,0.828,"Scottish rivers by annual conservation grade, first and latest years of the current method",
         fontsize=11,color=MIST,ha="left",va="top")
fig.add_artist(plt.Line2D([0.062,0.955],[0.112,0.112],color="#1b3d4e",linewidth=1.2,
                          transform=fig.transFigure))
fig.text(0.062,0.090,
  "Sources: 2019 grades from the Scottish Government's EIR release 202500465501; 2026 grades from Salmon fishing: final river gradings.\n"
  "Grades are assessed from rod catch converted to egg deposition, so this is the official scorecard, not evidence independent of catch.",
  fontsize=8.5,color=DIM,ha="left",va="top",linespacing=1.6)
fig.savefig(f"{OUT}/salmon_11_gradings.png",dpi=200)
print("wrote salmon_11_gradings.png")
