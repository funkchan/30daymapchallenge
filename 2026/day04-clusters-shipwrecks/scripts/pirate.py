import os,glob
import numpy as np,pandas as pd,geopandas as gpd,matplotlib
matplotlib.use('Agg');import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.offsetbox import OffsetImage,AnnotationBbox
from shapely.geometry import box
ROOT=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
os.chdir(ROOT)
_BUNDLED=os.path.join(ROOT,'glyphs','fonts')
FONT_DIR=os.environ.get('FONT_DIR') or _BUNDLED
_font_dirs=[FONT_DIR]
if os.path.abspath(FONT_DIR)!=os.path.abspath(_BUNDLED):
    _font_dirs.append(_BUNDLED)
_fonts=[]
for _d in _font_dirs:
    _fonts.extend(sorted(glob.glob(os.path.join(_d,'*.ttf'))))
for f in _fonts:fm.fontManager.addfont(f)
def _families(paths):
    names=[]
    for f in paths:
        n=fm.FontProperties(fname=f).get_name()
        if n not in names:names.append(n)
    return names
_names=_families(_fonts)
def _pick(name,fallback):
    return name if name in _names else fallback
TITLE=_pick('Pirata One','Pirata One')
LAB=_pick('IM FELL English','IM FELL English')
_extra=[n for n in _names if n not in (TITLE,LAB)]
NUM=_extra[0] if _extra else LAB
BLK='#17120E';OX='#7A1A1A';BR='#B8893A';BONE='#F1E4C3';PARCH='#E8D4A2';STAIN='#DCC38B';MID='#B8995F'
SEA='#EFE2BC';LAND=STAIN
E=5070;GL={t:plt.imread(os.path.join(ROOT,'glyphs',f'wreck_t{t}.png')) for t in (1,2,3,4)}
SZ={1:90,2:120,3:155,4:200}
D=os.path.join(ROOT,'data')+os.sep
pts=gpd.read_file(D+'merged_l48.gpkg').to_crs(E)
cl=pd.read_csv(D+'clusters.csv',index_col=0)
cg=gpd.GeoDataFrame(cl,geometry=gpd.points_from_xy(cl.lon,cl.lat),crs=4326).to_crs(E)
us=gpd.read_file(D+'cb_2023_us_state_500k.shp').to_crs(E)
ne=gpd.read_file(D+'ne_10m_land.shp')
ne=ne.clip(box(-130,20,-60,52)).to_crs(E)
lakes=gpd.read_file(os.path.join(D,'ne_10m_lakes.shp'));lakes=lakes[lakes.scalerank<=3].clip(box(-130,20,-60,52)).to_crs(E)
b200=gpd.read_file(os.path.join(D,'ne_10m_bathymetry_K_200.shp')).clip(box(-130,20,-60,52)).to_crs(E)
aw_all=gpd.read_file(os.path.join(D,'awois/2020445569/aw/AWOIS_Wrecks.shp')).to_crs(E)
def ext(lo0,la0,lo1,la1):
    g=gpd.GeoSeries([box(lo0,la0,lo1,la1)],crs=4326).to_crs(E).total_bounds;return g
def inbox(g,lo0,la0,lo1,la1):
    ll=g.to_crs(4326);x,y=ll.geometry.x,ll.geometry.y;return (x>lo0)&(x<lo1)&(y>la0)&(y<la1)
def glyph(ax,x,y,t,scale=1.0,z=8):
    S=SZ[t]*scale;ax.apply_aspect();bb=ax.get_window_extent();x0,x1=ax.get_xlim();y0,y1=ax.get_ylim()
    dx=S*(x1-x0)/bb.width;dy=S*(y1-y0)/bb.height
    l=x-0.5*dx;tp=y+0.78125*dy
    ax.imshow(GL[t],extent=(l,l+dx,tp-dy,tp),zorder=z,interpolation='lanczos');ax.set_xlim(x0,x1);ax.set_ylim(y0,y1)
def basemap(ax,b,fine=True,mark=4,gly=1.0,counts=True,minn=0,heavy=False,outc=BLK,outa=1.0,outlw=2.6,cg_=None):
    ax.set_xlabel('');ax.set_ylabel('')
    ax.set_facecolor(SEA)
    b200.plot(ax=ax,color=PARCH,lw=0)   # deeper than 200 m = plain parchment; shelf = lighter
    ne.plot(ax=ax,color=LAND,lw=0)
    (us if fine else ne).plot(ax=ax,color=LAND,ec=BLK,lw=0.9 if fine else .6)
    lakes.plot(ax=ax,color=SEA,ec=BLK,lw=.6)
    n=pts[pts.cl<0];c=pts[pts.cl>=0]
    if heavy:
        import matplotlib.patheffects as pe
        h=[pe.withStroke(linewidth=7,foreground=BONE)]
        ax.scatter(n.geometry.x,n.geometry.y,s=mark,marker='x',c=outc,alpha=outa,lw=outlw,zorder=5,path_effects=h if outc==BLK else [pe.withStroke(linewidth=3.5,foreground=BONE)])
        ax.scatter(c.geometry.x,c.geometry.y,s=mark*1.3,marker='+',c=OX,lw=3.4,zorder=6,path_effects=h)
    else:
        ax.scatter(n.geometry.x,n.geometry.y,s=mark,marker='+',c=BLK,lw=.8,alpha=.75,zorder=5)
        ax.scatter(c.geometry.x,c.geometry.y,s=mark,marker='+',c=OX,lw=.9,zorder=5)
    x0,y0,x1,y1=b;ax.set_xlim(x0,x1);ax.set_ylim(y0,y1);ax.set_aspect('equal',adjustable='datalim')
    X0,X1=ax.get_xlim();Y0,Y1=ax.get_ylim()
    for r in (cg if cg_ is None else cg_).itertuples():
        if X0<r.geometry.x<X1 and Y0<r.geometry.y<Y1 and r.n>=minn:
            glyph(ax,r.geometry.x,r.geometry.y,r.tier,gly)
            if counts: ax.annotate(f'{r.n:,}',(r.geometry.x,r.geometry.y),xytext=(0,-14),textcoords='offset points',ha='center',va='top',fontsize=22*gly,family=NUM,fontweight='bold',color=BLK,zorder=9,
                bbox=dict(boxstyle='round,pad=0.15',fc=BONE,ec=BLK,lw=.8))
    ax.set_xticks([]);ax.set_yticks([]);ax.set_xlabel('');ax.set_ylabel('')
    for s in ax.spines.values():s.set_lw(2.5);s.set_color(BLK)
def title_tag(ax,txt,loc='tl',fs=30):
    x,ha=(0.02,'left') if 'l' in loc else (0.98,'right');y,va=(0.98,'top') if 't' in loc else (0.02,'bottom')
    ax.text(x,y,txt,transform=ax.transAxes,ha=ha,va=va,fontsize=fs,family=LAB,color=BLK,zorder=12,bbox=dict(boxstyle='square,pad=0.3',fc=BONE,ec=BLK,lw=1.5))
def legend_box(ax,lines,loc=(0.02,0.02),fs=21,ha='left',va='bottom'):
    ax.text(*loc,'\n'.join(lines),transform=ax.transAxes,ha=ha,va=va,fontsize=fs,family=NUM,color=BLK,zorder=12,linespacing=1.3,
      bbox=dict(boxstyle='round,pad=0.45',fc=BONE,ec=OX,lw=2.2))
def compass(ax,cx,cy,R):
    for r,l in [(R,2),(R*.84,.8)]:ax.add_patch(plt.Circle((cx,cy),r,transform=ax.transAxes,fill=False,ec=BLK,lw=l,zorder=11))
    for a,L in [(0,1),(90,.7),(180,.7),(270,.7),(45,.45),(135,.45),(225,.45),(315,.45)]:
        t=np.radians(a);p=np.radians(a+90);w=R*.12
        ax.fill([cx+R*.85*L*np.sin(t),cx+w*np.sin(p),cx-w*np.sin(p)],[cy+R*.85*L*np.cos(t),cy+w*np.cos(p),cy-w*np.cos(p)],c=OX if a==0 else (BLK if a%90==0 else BR),transform=ax.transAxes,zorder=11,lw=0)
    ax.text(cx,cy+R*1.08,'N',transform=ax.transAxes,ha='center',va='bottom',fontsize=26,family=TITLE,color=OX,zorder=11)
def counts_in(lo0,la0,lo1,la1):
    m=inbox(pts,lo0,la0,lo1,la1);return int(m.sum())
