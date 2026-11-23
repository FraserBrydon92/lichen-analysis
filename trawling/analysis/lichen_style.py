# Chart house style matched to the 'Counting Salmon' series: dark plate, Caladea Bold titles, Inter text, teal/gold/coral accents
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.font_manager as fm, matplotlib.patheffects as pe
for f in ['/usr/share/fonts/truetype/crosextra/Caladea-Bold.ttf']+[f'/usr/share/fonts/opentype/inter/Inter-{w}.otf' for w in ['Regular','Medium','SemiBold','Bold']]:
    fm.fontManager.addfont(f)
PLATE='#081a24'; AREA='#0c3340'; GRID='#133546'; RULE='#1b3d4e'; INK='#9dbac6'; SRC='#5a7d8c'; WHITE='#f2f7f8'
TEAL='#3fd0c9'; GOLD='#f3c969'; CORAL='#ff6f5e'; MUTED='#5a7d8c'
SERIF=fm.FontProperties(fname='/usr/share/fonts/truetype/crosextra/Caladea-Bold.ttf')
plt.rcParams.update({'font.family':'Inter','font.size':13,'text.color':INK,'axes.labelcolor':INK,'xtick.color':INK,'ytick.color':INK,
  'axes.facecolor':PLATE,'figure.facecolor':PLATE,'savefig.facecolor':PLATE,'axes.edgecolor':PLATE,'xtick.labelsize':13,'ytick.labelsize':13})
W,H=8.4,5.6
def _wrap(fig,text,maxw,**kw):
    r=fig.canvas.get_renderer(); out=[]
    for para in text.split('\n'):
        line=''
        for w in para.split(' '):
            t=(line+' '+w).strip(); tt=fig.text(0,0,t,**kw); wid=tt.get_window_extent(r).width; tt.remove()
            if wid>maxw and line: out.append(line); line=w
            else: line=t
        out.append(line)
    return out
def frame(eyebrow,title,subtitle,source,eyebrow_color=TEAL,plot_h=3.2,plot=(0.075,0,0.88,0),gap=0.35,h=None):
    """Header and footer in fixed inches; figure height grows so the plot area is plot_h inches tall."""
    subtitle=subtitle.replace('\n',' '); source=source.replace('\n',' ')
    tmp=plt.figure(figsize=(W,5),dpi=200); maxw=(0.95-0.0625)*W*200
    tl=_wrap(tmp,title,maxw,fontproperties=SERIF,fontsize=22); sl=_wrap(tmp,subtitle,maxw,fontsize=12); src=_wrap(tmp,source,maxw,fontsize=8.8); plt.close(tmp)
    head=0.32+0.30+0.40*len(tl)+0.12+0.27*len(sl)+gap
    yb=0.16+0.21*len(src); foot=yb+0.55
    h=head+plot_h+foot
    fig=plt.figure(figsize=(W,h),dpi=200); L=0.0625; y=h-0.32
    fig.text(L,y/h,eyebrow.upper(),fontsize=11,fontweight='semibold',color=eyebrow_color,va='top'); y-=0.30
    for t in tl: fig.text(L,y/h,t,fontproperties=SERIF,fontsize=22,color=WHITE,va='top'); y-=0.40
    y-=0.12
    for t in sl: fig.text(L,y/h,t,fontsize=12,color=INK,va='top'); y-=0.27
    fig.add_artist(plt.Line2D([L,0.95],[yb/h,yb/h],color=RULE,lw=1.2,transform=fig.transFigure))
    yy=yb-0.13
    for t in src: fig.text(L,yy/h,t,fontsize=8.8,color=SRC,va='top'); yy-=0.21
    l,_,w,_=plot; ax=fig.add_axes([l,foot/h,w,plot_h/h])
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.tick_params(length=0,pad=8); ax.set_axisbelow(True)
    return fig,ax
def glow(ax,x,y,color=TEAL,lw=2.4,**k):
    ax.plot(x,y,color=color,lw=lw*3.2,alpha=0.12,solid_capstyle='round',**k)
    return ax.plot(x,y,color=color,lw=lw,solid_capstyle='round',**k)
def hgrid(ax): ax.grid(axis='y',color=GRID,lw=1)
def vgrid(ax): ax.grid(axis='x',color=GRID,lw=1)
def label(ax,x,y,t,color,**k):
    k.setdefault('fontsize',13); k.setdefault('fontweight','medium')
    return ax.text(x,y,t,color=color,**k)
