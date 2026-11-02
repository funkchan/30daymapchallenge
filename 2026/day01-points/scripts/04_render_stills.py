"""Render the Day 1 cartographic stills (landscape 2048x1280, portrait 1080x1350).

Needs data/hackerspaces.geojson (03_prepare_points.py), Natural Earth admin-0 countries
(02_fetch_naturalearth.py) and IBM Plex Sans (400/500/600/700 .ttf) in fonts/.
Labels, counts and the top-5 chart are written for the 2026-08-10 OSM snapshot.
Usage: python scripts/04_render_stills.py [land] [port]   (default: both) -> outputs/
"""
import sys, numpy as np, geopandas as gpd, matplotlib
from pathlib import Path
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Rectangle
import matplotlib.patheffects as pe
from scipy.ndimage import gaussian_filter
from shapely.geometry import LineString, Polygon
from pyproj import Transformer
ROOT=Path(__file__).resolve().parent.parent
DATA=ROOT/'data'; OUT=ROOT/'outputs'; FONTS=ROOT/'fonts'
if len(sys.argv)>1 and sys.argv[1] in ('-h','--help'): print(__doc__); sys.exit(0)
_fonts=[FONTS/f'IBMPlexSans-{w}.ttf' for w in (400,500,600,700)]
if all(f.exists() for f in _fonts):
    for f in _fonts: fm.fontManager.addfont(str(f))
    plt.rcParams['font.family']='IBM Plex Sans'
else: print('warning: IBM Plex Sans not found in fonts/, falling back to the default font')
PT=0.72  # px -> pt at dpi 100
BG='#07090d'; OCEAN='#0b1018'; LAND='#253044'; BORD='#3a4760'; COAST='#56688a'; GRAT='#1b2430'
CORE='#c8f4ff'; GLOW='#64ffff'; GOLD='#ffe154'; PK='#ff7d82'; BL='#408cc7'; VIO='#a58cff'
TXT='#eef3f8'; SUBT='#86aeb8'; FOOT='#b8c2c0'
T=Transformer.from_crs(4326,8857,always_xy=True)
hs=gpd.read_file(DATA/'hackerspaces.geojson').to_crs(8857)
ad=gpd.read_file(DATA/'naturalearth'/'ne_10m_admin_0_countries'/'ne_10m_admin_0_countries.shp').to_crs(8857)
LATMIN,LATMAX=-58,84
def P(lon,lat): return T.transform(lon,lat)
def gline(pts): x,y=T.transform(*zip(*pts)); return list(zip(x,y))
outline=Polygon(gline([(-180,la) for la in np.linspace(LATMIN,LATMAX,100)]+[(lo,LATMAX) for lo in np.linspace(-180,180,100)]+[(180,la) for la in np.linspace(LATMAX,LATMIN,100)]+[(lo,LATMIN) for lo in np.linspace(180,-180,100)]))
ad['geometry']=ad.geometry.intersection(outline)
coast=gpd.GeoSeries([ad.union_all().boundary])
grat=[LineString(gline([(lo,la) for la in np.linspace(LATMIN,LATMAX,80)])) for lo in range(-180,181,30)]+[LineString(gline([(lo,la) for lo in np.linspace(-180,180,160)])) for la in (-30,0,30,60)]
X=hs.geometry.x.values; Y=hs.geometry.y.values
from scipy.spatial import cKDTree
_la,_lo=np.radians(hs.lat.values),np.radians(hs.lon.values)
_P=np.c_[np.cos(_la)*np.cos(_lo),np.cos(_la)*np.sin(_lo),np.sin(_la)]
RADIUS_KM=100
NBR=np.array([len(q)-1 for q in cKDTree(_P).query_ball_point(_P,2*np.sin(RADIUS_KM/6371.0088/2))])
BREAKS=[(0,0,'none'),(1,5,'1–5'),(6,25,'6–25'),(26,10**6,'26+')]
CLS=np.select([NBR==0,NBR<=5,NBR<=25],[0,1,2],3)
# per class: core colour, core size factor, glow weight
STY=[('#4d95a2',0.85,0.15),('#7fd3dc',1.0,0.45),('#b4f4fb',1.25,0.8),('#f2ffff',1.5,1.2)]
COUNTS=[int((CLS==k).sum()) for k in range(4)]
print('neighbour classes',RADIUS_KM,'km',[(b[2],c) for b,c in zip(BREAKS,COUNTS)])
OB=outline.bounds; PAD=2e5; XL=(OB[0]-PAD,OB[2]+PAD); YL=(OB[1]-PAD,OB[3]+PAD); MASP=(XL[1]-XL[0])/(YL[1]-YL[0])
EU=(-11,35.5,31,60.5)
a=P(EU[0],EU[1]); b=P(EU[2],EU[1]); c=P(EU[0],EU[3]); d=P(EU[2],EU[3])
EUX=(min(a[0],c[0]),max(b[0],d[0])); EUY=(a[1],c[1]); EASP=(EUX[1]-EUX[0])/(EUY[1]-EUY[0])
def basemap(ax,lw=.4,gl=True):
    ax.set_facecolor(BG if gl else OCEAN)
    if gl:
        gpd.GeoSeries([outline]).plot(ax=ax,facecolor=OCEAN,edgecolor='#2a3442',lw=.9,zorder=0)
        gpd.GeoSeries(grat).plot(ax=ax,color=GRAT,lw=.8,zorder=1)
    ad.plot(ax=ax,facecolor=LAND,edgecolor=BORD,lw=lw,zorder=2)
def finish(ax):
    ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel(''); ax.set_ylabel('')
    for s in ax.spines.values(): s.set_visible(False)
def capped_glow(ax,xl,yl,wpx,hpx,sigma,cap,zorder=4):
    # rasterise the glow in screen pixels and clamp it, so dense clusters stop at `cap` opacity
    w,h=int(wpx),int(hpx); acc=np.zeros((h,w))
    ix=((X-xl[0])/(xl[1]-xl[0])*w).astype(int); iy=((yl[1]-Y)/(yl[1]-yl[0])*h).astype(int)
    wt=np.array([STY[k][2] for k in CLS]); ok=(ix>=0)&(ix<w)&(iy>=0)&(iy<h); np.add.at(acc,(iy[ok],ix[ok]),wt[ok])
    g=gaussian_filter(acc,sigma)*(2*np.pi*sigma**2)  # single isolated point peaks at 1
    al=np.clip(g*0.45,0,cap)
    rgba=np.zeros((h,w,4)); rgba[...,:3]=matplotlib.colors.to_rgb(GLOW); rgba[...,3]=al
    ax.imshow(rgba,extent=(xl[0],xl[1],yl[0],yl[1]),origin='upper',zorder=zorder,interpolation='bilinear')
def dots(ax,base,zorder=6):
    for k in range(4):
        m=CLS==k; ax.scatter(X[m],Y[m],s=base*STY[k][1]**2,c=STY[k][0],lw=0,zorder=zorder+k*0.01)
def build(mode):
    if mode=='port':
        W,H=1080,1350; M=40
        L=dict(title=(M,38,40),sub=(M,108,20),map=(11,150,1058),
               eh=(M,668),inset=(M,682,588),ch=(None,668),chart=(800,None,240,300),
               leg=(M,1128),foot=[(M,1258,24,FOOT),(M,1290,20,'#9aa6a4')],handle=(M,M))
        footer=['Data © OpenStreetMap contributors (ODbL)','Equal Earth projection']
        CO=dict(lone=(70,-70),north=(70,10),south=(-30,-14))
    else:
        W,H=2048,1280; M=40
        L=dict(title=(M,50,56),sub=(M,140,26),map=(16,260,1544),
               eh=(1600,305),inset=(1600,320,408),ch=(1600,690),chart=(1760,710,230,250),
               leg=(M,1010),foot=[(M,1196,24,FOOT),(M,1232,20,'#9aa6a4')],handle=(M,M))
        footer=['Data © OpenStreetMap contributors (ODbL)','Equal Earth projection']
        CO=dict(lone=(90,-90),north=(90,10),south=(-30,-14))
    fig=plt.figure(figsize=(W/100,H/100),dpi=100,facecolor=BG)
    def ax_px(x,y,w,h): return fig.add_axes([x/W,1-(y+h)/H,w/W,h/H])
    def txt(x,y,s,px,col,w=400,ha='left',va='baseline'): return fig.text(x/W,1-y/H,s,fontsize=px*PT,color=col,fontweight=w,ha=ha,va=va)
    # main map
    mx,my,mw=L['map']; mh=mw/MASP; axm=ax_px(mx,my,mw,mh)
    basemap(axm); coast.plot(ax=axm,color=COAST,lw=.7,zorder=5)
    axm.set_xlim(*XL); axm.set_ylim(*YL); axm.set_aspect('equal')
    capped_glow(axm,XL,YL,mw,mh,sigma=2.2,cap=0.35)
    dots(axm,4 if mode=='port' else 6)
    axm.add_patch(Rectangle((EUX[0],EUY[0]),EUX[1]-EUX[0],EUY[1]-EUY[0],fill=False,ec=GOLD,lw=1.6,zorder=7,ls=(0,(4,3))))
    def callout(lon,lat,l1,l2,off,col,ha='left'):
        px,py=P(lon,lat); dx,dy=off
        axm.scatter([px],[py],s=130,facecolors='none',edgecolors=col,lw=1.8,zorder=8)
        halo=[pe.withStroke(linewidth=5,foreground=BG)]
        t1=axm.annotate(l1,(px,py),xytext=(dx,dy),textcoords='offset pixels',fontsize=26*PT,fontweight=600,color=TXT,ha=ha,va='baseline',zorder=9,path_effects=halo,
            arrowprops=dict(arrowstyle='-',color=col,lw=1.3,shrinkA=4,shrinkB=8,relpos=(0 if ha=='left' else 1,0.3)))
        axm.annotate(l2,(px,py),xytext=(dx,dy-1.2*24),textcoords='offset pixels',fontsize=22*PT,color='#cfd8e2',ha=ha,va='baseline',zorder=9,path_effects=halo)
    callout(33.2499,0.4784,'Loneliest: AfrexLab, Uganda','2,063 km to the nearest',CO['lone'],PK)
    callout(22.136,65.617,'Northernmost: Luleå, Sweden','65.6°N',CO['north'],BL)
    callout(172.642,-43.546,'Southernmost: Christchurch, NZ','43.5°S',CO['south'],VIO,ha='right')
    finish(axm)
    # Europe inset
    ix,iy,iw=L['inset']; ih=iw/EASP; axe=ax_px(ix,iy,iw,ih)
    basemap(axe,lw=.6,gl=False); coast.plot(ax=axe,color=COAST,lw=.8,zorder=5)
    axe.set_xlim(*EUX); axe.set_ylim(*EUY); axe.set_aspect('equal')
    capped_glow(axe,EUX,EUY,iw,ih,sigma=3.0,cap=0.5)
    dots(axe,10 if mode=='port' else 8)
    finish(axe)
    for s in axe.spines.values(): s.set_visible(True); s.set_color(GOLD); s.set_linewidth(1.6)
    k=iw/588
    for lon,lat,t,dx,dy in [(2.35,48.86,'Paris · 52',-150,-60),(2.17,41.39,'Barcelona · 33',40,-62),(13.4,52.52,'Berlin · 24',40,60)]:
        px,py=P(lon,lat); dx,dy=dx*k,dy*k
        axe.annotate(t,(px,py),xytext=(dx,dy),textcoords='offset pixels',color=TXT,fontsize=(26 if mode=='port' else 22)*PT,fontweight=600,ha='left',va='center',zorder=9,
          arrowprops=dict(arrowstyle='-',color=GOLD,lw=1.2,shrinkA=2,shrinkB=5),path_effects=[pe.withStroke(linewidth=5,foreground=BG)])
    ex,ey=L['eh']; txt(ex,ey,'Europe close-up · 1,230 (65%)',26,TXT,600)
    # chart
    cx,cy,cw,chh=L['chart']
    if cy is None: cy=iy+ih/2-chh/2   # centre against inset
    axb=ax_px(cx,cy,cw,chh); axb.set_facecolor(BG)
    names=['France','USA','Germany','China','Spain']; vals=[438,287,276,118,81]; yy=np.arange(5)[::-1]
    axb.barh(yy,vals,color=BL,height=.62)
    for yi,v,n in zip(yy,vals,names):
        axb.annotate(n,(0,yi),xytext=(-12,0),textcoords='offset pixels',ha='right',va='center',color=TXT,fontsize=24*PT)
        axb.annotate(f'{v}',(v,yi),xytext=(10,0),textcoords='offset pixels',ha='left',va='center',color='#ffffff',fontsize=24*PT,fontweight=700)
    axb.set_xlim(0,600); axb.set_ylim(-.6,4.6); axb.axis('off')
    hx,hy=L['ch']
    if hx is None: hx=cx-150
    txt(hx,hy,'Top 5 countries',26,TXT,600)
    # titles
    tx,ty,tp=L['title']; fig.text(tx/W,1-ty/H,'Hackerspaces Across the World',fontsize=tp,color=TXT,fontweight=700,va='top')
    sx,sy,sp=L['sub']; fig.text(sx/W,1-sy/H,'1,898 hackerspaces in 92 countries',fontsize=sp,color=SUBT,va='top')
    # density legend: same symbols, dim to bright
    lx,ly=L['leg']; txt(lx,ly,f'Other hackerspaces within {RADIUS_KM} km',24,TXT,600)
    step=150
    lax=ax_px(lx,ly+14,step*4,44); lax.axis('off'); lax.set_xlim(0,step*4); lax.set_ylim(-1,1); lax.set_facecolor(BG)
    for k in range(4):
        cx0=step*k+22; g=STY[k][2]
        for sz,al in ((900,.10),(300,.22)): lax.scatter([cx0],[0],s=sz*min(g,1.0),c=GLOW,alpha=al*min(1,g+.2),lw=0)
        lax.scatter([cx0],[0],s=60*STY[k][1]**2,c=STY[k][0],lw=0)
        txt(lx+cx0+30,ly+14+22,BREAKS[k][2],24,FOOT,va='center')
    for (fx,fy,fp,fc),s_ in zip(L['foot'],footer): txt(fx,fy,s_,fp,fc)
    hx,hb=L['handle']; txt(W-hb,H-hb,'@funkchan · #30DayMapChallenge Day 1: Points',26,CORE,600,ha='right',va='bottom')
    OUT.mkdir(exist_ok=True); out=OUT/('day01_map_still.png' if mode=='land' else 'day01_map_still_portrait.png')
    fig.savefig(out,dpi=100,facecolor=BG); plt.close(fig); print(out)
for m in sys.argv[1:] or ['land','port']: build(m)
