import matplotlib.patheffects as pe
import matplotlib.transforms as mt
import os
ARROW=os.environ.get('ARROW','1')=='1'
import matplotlib.transforms as mt
import os
MODE=os.environ.get('MODE','x')
from pirate import *
W,H=2400,3000;fig=plt.figure(figsize=(24,30),dpi=100);fig.patch.set_facecolor(PARCH)
BX=(-76.75,34.35,-74.9,36.95)
MW,MH=2320,2540
EXT=35
ax=fig.add_axes([40/W,1-(2850+EXT)/H,MW/W,(MH+EXT)/H])
kp=gpd.GeoSeries(gpd.points_from_xy([-76.15,-76.75,-76.2],[37.02,34.5,35.5]),crs=4326).to_crs(E)
y0=kp.y.min()-12000;y1=kp.y.max()+42000;wx=kp.x.min()-26000;wid=(y1-y0)*MW/MH
y0=y0-(y1-y0)*EXT/MH
import pirate
from scipy.ndimage import maximum_filter
for t_,im_ in list(pirate.GL.items()):
    a_=im_[...,3];h_=maximum_filter(a_,size=17)>0.05;o_=np.zeros_like(im_);o_[...,:3]=np.array([241,228,195])/255;o_[...,3]=h_*1.0
    al=im_[...,3:4];o_[...,:3]=im_[...,:3]*al+o_[...,:3]*(1-al);o_[...,3]=np.maximum(h_,a_);pirate.GL[t_]=o_
from sklearn.cluster import DBSCAN
EPS,MIN,BW=5000,6,5000
x_,y_=pts.geometry.x,pts.geometry.y;inf=(x_>wx)&(x_<wx+wid)&(y_>y0)&(y_<y1)
P=pts.copy();P['cl']=-1
lab=DBSCAN(eps=EPS,min_samples=MIN).fit_predict(np.c_[x_[inf],y_[inf]]);P.loc[inf,'cl']=lab
F=P[inf&(P.cl>=0)];g=F.groupby('cl');C=gpd.GeoDataFrame({'n':g.size()},geometry=gpd.points_from_xy(g.apply(lambda d:d.geometry.x.mean()),g.apply(lambda d:d.geometry.y.mean())),crs=E)
C['tier']=pd.cut(C.n,[0,8,19,49,1e9],labels=[1,2,3,4]).astype(int)
pirate.pts=P;pirate.cg=C;pts=P
ll=C.to_crs(4326);print('REGIONAL',len(C),[(int(r.n),r.tier,round(q.x,2),round(q.y,2)) for r,q in zip(C.itertuples(),ll.geometry)])
INS=(-76.45,36.72,-75.55,37.42)
cll=C.to_crs(4326).geometry;inI=(cll.x>INS[0])&(cll.x<INS[2])&(cll.y>INS[1])&(cll.y<INS[3])
OUTC='#5E4E3C';kw=dict(mark=170,heavy=True,outc=OUTC,outa=.85,outlw=2.2)
PL=P.to_crs(4326).geometry;inINS=(PL.x>INS[0])&(PL.x<INS[2])&(PL.y>INS[1])&(PL.y<INS[3])
pirate.pts=P[(P.cl>=0)&~inINS]
basemap(ax,(wx,y0,wx+wid,y1),gly=1.3,cg_=C[~inI],**kw)
from shapely.geometry import MultiPoint
HG=[(k_,MultiPoint(list(zip(d.geometry.x,d.geometry.y))).convex_hull.buffer(1500)) for k_,d in P[P.cl>=0].groupby('cl')]
HUL=gpd.GeoSeries([h for _,h in HG],index=[k_ for k_,_ in HG],crs=E)
HUL[~HUL.index.isin(C.index[inI])].plot(ax=ax,fc='none',ec=OX,lw=1.8,ls='--',zorder=5.5)
ei=ext(*INS);ax.add_patch(plt.Rectangle((ei[0],ei[1]),ei[2]-ei[0],ei[3]-ei[1],fill=False,ec=BLK,lw=2,zorder=6))
# inset
ia=fig.add_axes([(40+.505*MW)/W,1-(2850-MH+22)/H-.275*MH/H,.475*MW/W,.275*MH/H])
big=C.n.idxmax()
pirate.pts=P[(P.cl>=0)&(P.cl!=big)]
basemap(ia,ei,gly=.95,cg_=C[inI],counts=False,**kw)
bp=P[P.cl==big];ia.scatter(bp.geometry.x,bp.geometry.y,s=170*1.3,marker='+',c=OX,lw=3,alpha=.28,zorder=5)
OFF={11:(70,55),23:(-95,-30),82:(0,-22),8:(45,50)}
for k_,r_ in C[inI].iterrows():
    dx_,dy_=OFF.get(int(r_.n),(0,-18))
    ia.annotate(f'{int(r_.n)}',(r_.geometry.x,r_.geometry.y),xytext=(dx_,dy_),textcoords='offset points',ha='center',va='top' if dy_<=0 else 'bottom',fontsize=30,family=NUM,fontweight='bold',color=BLK,zorder=9,
      bbox=dict(boxstyle='round,pad=0.15',fc=BONE,ec=BLK,lw=.8),arrowprops=None if abs(dx_)<1 else dict(arrowstyle='-',color=BLK,lw=1.2))
HUL.plot(ax=ia,fc='none',ec=OX,lw=2,ls='--',zorder=5.5)
pirate.pts=P
for s_ in ia.spines.values():s_.set_lw(3)
from matplotlib.patches import ConnectionPatch
for (xa,ya),(xb,yb) in [((ei[2],ei[1]),(0,0))]:
    fig.add_artist(ConnectionPatch((xa,ya),(xb,yb),coordsA=ax.transData,coordsB=ia.transAxes,color=BLK,lw=1.3,ls='-',alpha=.8,zorder=7))
ia.set_xlabel('');ia.set_ylabel('')
title_tag(ia,'Chesapeake Bay mouth (zoom)','tl',fs=32)
bd=P[P.cl==big];bc=C.loc[big].geometry
sh20=100*(np.hypot(bd.geometry.x-bc.x,bd.geometry.y-bc.y)<=20000).mean();r90=np.quantile(np.hypot(bd.geometry.x-bc.x,bd.geometry.y-bc.y),.9)/1000
hr=C[inI&(C.n<C.n.max())].n.max()
fig.canvas.draw();_ipos=ia.get_position()
_tt=ax.text((_ipos.x0+_ipos.x1)/2,_ipos.y0-22/H,f'THE TIGHT CLUSTER: {int(C.n.max())} wrecks off Cape Henry, {sh20:.0f}% within 20 km;\nshipping converges on the bay mouth. {int(hr)} more at Hampton Roads.',transform=fig.transFigure,ha='center',va='top',fontsize=26,family=NUM,color=BLK,zorder=12,linespacing=1.3,bbox=dict(boxstyle='round,pad=0.45',fc=BONE,ec=OX,lw=2.2))
fig.canvas.draw();_tb_=_tt.get_bbox_patch().get_window_extent();_ax_=ax.get_window_extent();_sh=min(0,(_ax_.x1-12)-_tb_.x1);_tt.set_position(((_ipos.x0+_ipos.x1)/2+_sh/W,_ipos.y0-22/H));fig.canvas.draw();_tb_=_tt.get_bbox_patch().get_window_extent();print('TIGHTSTRIP px',_tb_.bounds,'right margin',_ax_.x1-_tb_.x1,'inset width',_ipos.width*W)
print('capehenry r90',r90,'sh20',sh20,'HR',hr)
obm=inbox(P,-76.9,34.4,-74.8,36.6);obn=int(obm.sum());obo=int((obm&(P.cl<0)).sum())
print('OB',obn,obo)
ob=counts_in(-76.9,34.4,-74.8,36.6)
_X0,_X1=ax.get_xlim();_Y0,_Y1=ax.get_ylim();tot=int(((pts.geometry.x>_X0)&(pts.geometry.x<_X1)&(pts.geometry.y>_Y0)&(pts.geometry.y<_Y1)).sum())
# AWOIS names (all AWOIS records in view, incl. those duplicated by chart points)
X0,X1=ax.get_xlim();Y0,Y1=ax.get_ylim()
a=aw_all[(aw_all.geometry.x>X0)&(aw_all.geometry.x<X1)&(aw_all.geometry.y>Y0)&(aw_all.geometry.y<Y1)]
a=a[~a.VESSLTERMS.fillna('UNKNOWN').str.upper().isin(['UNKNOWN','UNKNWON','WRECK','OBSTRUCTION','BARGE',''])]
# priority: inside clusters areas near Hatteras/Diamond Shoals, Lookout; then named years
import re as _re
def fixcase(n):
    out=[]
    for w in str(n).split():
        W=w.upper()
        if W in('USS','USCGC','SS','HMS','HMT','USNS','SS.') or _re.fullmatch(r'[IVXLC]+',W) and W not in('I',) or _re.fullmatch(r'U-\d+',W) or _re.fullmatch(r'YCF-?\d*',W):out.append(W)
        elif _re.fullmatch(r'([A-Z]\.)+[A-Z]?\.?',W):out.append(W)
        elif W in('OF','THE','AND') and out:out.append(W.lower())
        else:out.append(w.capitalize())
    return ' '.join(out)
from scipy.spatial import cKDTree
cp=pts[pts.cl>=0];t=cKDTree(np.c_[cp.geometry.x,cp.geometry.y])
ds=gpd.GeoSeries(gpd.points_from_xy([-75.4],[35.2]),crs=4326).to_crs(E)[0]
a=a.assign(d=np.hypot(a.geometry.x-ds.x,a.geometry.y-ds.y)).sort_values('d').drop_duplicates('VESSLTERMS')
a=a[~a.VESSLTERMS.str.upper().isin(['L. MATKOVIC','USS HURON'])]  # Huron: AWOIS position conflicts with public accounts; label omitted
FAM={'U-85','U-701','U-576','U-352','CITY OF ATLANTA','EMPIRE GEM','E.M. CLARK','BRITISH SPLENDOUR','DIXIE ARROW','CITY OF NEW YORK','MIRLO','MONITOR','HUNTSVILLE','KASSANDRA LOULOUDIS'}
HU=HUL.union_all() if hasattr(HUL,'union_all') else HUL.unary_union
al=a.to_crs(4326).geometry;inA=(al.x>INS[0])&(al.x<INS[2])&(al.y>INS[1])&(al.y<INS[3])
near=a.geometry.distance(HU)<=5000;fam=a.VESSLTERMS.str.upper().isin(FAM)
a=a[(near|fam)&~inA].assign(f=fam).sort_values(['f','d'],ascending=[False,True])
print('SHIPS',len(a),sorted(a.VESSLTERMS.map(fixcase)))
# place labels
for nm,lo,la in [('Cape Hatteras',-75.56,35.30),('Ocracoke',-75.98,35.11),('Cape Lookout',-76.53,34.6),('Currituck',-75.83,36.4),('Virginia Beach',-76.28,36.68),('Nags Head',-75.62,35.95)]:
    g=gpd.GeoSeries(gpd.points_from_xy([lo],[la]),crs=4326).to_crs(E)[0]
    R=nm in('Cape Lookout','Virginia Beach');
    if X0<g.x<X1 and Y0<g.y<Y1: ax.text(g.x+(0 if R else -3000),g.y,'CAPE\nHATTERAS' if nm=='Cape Hatteras' else nm.upper(),linespacing=.95,ha='left' if R else 'right',va='center',fontsize=34,family=LAB,color=OX,zorder=10.5,path_effects=[pe.withStroke(linewidth=5,foreground=BONE)])
g=gpd.GeoSeries(gpd.points_from_xy([-75.33],[35.07]),crs=4326).to_crs(E)[0]
g=gpd.GeoSeries(gpd.points_from_xy([-75.28],[35.04]),crs=4326).to_crs(E)[0]
_OP=P[(P.cl<0)&~inINS];_SKB=lambda: [mt.Bbox.from_extents(x_-14,y_-14,x_+14,y_+14) for x_,y_ in ax.transData.transform(np.c_[_OP.geometry.x,_OP.geometry.y])]
_dst=ax.text(g.x,g.y,'D I A M O N D   S H O A L S',fontsize=30,family=LAB,color=OX,ha='left',va='center',zorder=10.5,fontstyle='italic',path_effects=[pe.withStroke(linewidth=5,foreground=BONE)])
fig.canvas.draw();_sk=_SKB();_g0=ax.transData.transform((g.x,g.y));_best=None
for _r in range(0,90,3):
  for _a in np.linspace(0,2*np.pi,24,endpoint=False) if _r else [0]:
    _p=_g0+_r*np.array([np.cos(_a),np.sin(_a)]);_dst.set_position(ax.transData.inverted().transform(_p));_bb=_dst.get_window_extent()
    if not any(_bb.overlaps(k_) for k_ in _sk):_best=_p;break
  if _best is not None:break
print('DSHOALS shift px',None if _best is None else np.round(_best-_g0,1))
fig.canvas.draw();rend=fig.canvas.get_renderer()
PX=ax.transData.transform(np.c_[pts.geometry.x,pts.geometry.y])
def cov(bb):return ((PX[:,0]>bb.x0-15)&(PX[:,0]<bb.x1+15)&(PX[:,1]>bb.y0-15)&(PX[:,1]<bb.y1+15)).sum()
cb=None
for yy in np.arange(.3,.66,.02):
  for xx in np.arange(.6,.93,.03):
    c=ax.transAxes.transform((xx,yy));r=.052*ax.get_window_extent().width
    k=(np.hypot(PX[:,0]-c[0],PX[:,1]-c[1])<r).sum()+5*sum(mt.Bbox.from_extents(c[0]-r,c[1]-r,c[0]+r,c[1]+r*1.4).overlaps(o.get_window_extent(rend)) for o in ax.texts)
    if cb is None or k<cb[0]:cb=(k,xx,yy)
print('compass',cb)
fig.canvas.draw();_sub=[t for t in fig.texts if t.get_text().startswith('Chesapeake to')]
_t1=fig.text(40/W,1-16/H,'Graveyards of the Atlantic',fontsize=110,family=TITLE,va='top');_t2=fig.text(44/W,1-232/H,'Chesapeake to Cape Lookout: one tight cluster, one scattered graveyard',fontsize=50,family=LAB,va='top');fig.canvas.draw();_subx=max(_t1.get_window_extent().x1,_t2.get_window_extent().x1);_t1.remove();_t2.remove();print('HEADER text right edge px',_subx)
if _subx<W-330:
    cax=fig.add_axes([(W-300)/W,1-300/H,260/W,260/H]);cax.axis('off');cax.set_xlim(0,1);cax.set_ylim(0,1);compass(cax,.5,.42,.33);cb=(0,5,5);print('COMPASS header')
else:
    cb=(0,.91,.55);compass(ax,cb[1],cb[2],.05);print('COMPASS deep water')

# caveats box removed (v4b): caveats live in caption.md methods reply 3
gO=gpd.GeoSeries(gpd.points_from_xy([-75.5],[35.45]),crs=4326).to_crs(E)[0]
bestO=None
for yy in np.arange(.22,.62,.02):
  for xx in (np.arange(.5,.7,.03) if ARROW else np.arange(.56,.78,.03)):
    ax.annotate(f'THE SCATTERED GRAVEYARD\n{obn} wrecks off the Outer Banks;\n{obo} ({100*obo/obn:.0f}%) lie outside any cluster.\nNo single funnel: losses spread\nalong the whole barrier coast.',(gO.x,gO.y),xytext=(xx,yy),textcoords='axes fraction',ha='left',va='center',fontsize=30,family=NUM,color=BLK,zorder=12,linespacing=1.3,bbox=dict(boxstyle='round,pad=0.45',fc=BONE,ec=OX,lw=2.2),arrowprops=dict(arrowstyle='-|>',color=OX,lw=2.2,connectionstyle='arc3,rad=0.2'))
    an=ax.texts[-1];fig.canvas.draw();B=an.get_bbox_patch().get_window_extent(rend).expanded(1,1);B=mt.Bbox.from_extents(B.x0-6,B.y0-6,B.x1+6,B.y1+6);_axb=ax.get_window_extent();_cc=ax.transAxes.transform((cb[1],cb[2]));_cr=.05*_axb.width*1.3;k=cov(B)+(1000 if B.y0<_axb.y0+178+400+40 else 0)+(1000 if B.overlaps(mt.Bbox.from_extents(_cc[0]-_cr,_cc[1]-_cr,_cc[0]+_cr,_cc[1]+_cr*1.2)) else 0)+(1000 if B.x1>_axb.x1-12 else 0)+100*sum(B.overlaps(o.get_window_extent(rend)) for o in ax.texts[:-1]);an.remove()
    if bestO is None or k<bestO[0]:bestO=(k,xx,yy)
print('OBbox',bestO,'covers marks',bestO[0])
ax.annotate(f'THE SCATTERED GRAVEYARD\n{obn} wrecks off the Outer Banks;\n{obo} ({100*obo/obn:.0f}%) lie outside any cluster.\nNo single funnel: losses spread\nalong the whole barrier coast.',(gO.x,gO.y),xytext=(bestO[1],bestO[2]),textcoords='axes fraction',ha='left',va='center',fontsize=30,family=NUM,color=BLK,zorder=12,
  bbox=dict(boxstyle='round,pad=0.45',fc=BONE,ec=OX,lw=2.2),arrowprops=dict(arrowstyle='-|>',color=OX,lw=2.2,connectionstyle='arc3,rad=0.2'))
fig.canvas.draw();rend=fig.canvas.get_renderer();placed=[];nl=0
_c=ax.transAxes.transform((cb[1],cb[2]));_r=.052*ax.get_window_extent().width
gb=[ia.get_window_extent(),mt.Bbox.from_extents(_c[0]-_r,_c[1]-_r,_c[0]+_r,_c[1]+_r*1.4)]+[g.get_window_extent() for g in ax.images]+[(tx.get_bbox_patch().get_window_extent() if tx.get_bbox_patch() else tx.get_window_extent()) for tx in ax.texts]
_skl=_SKB();KEEP={'U-85','U-701','U-576','City of Atlanta','City of New York','Dixie Arrow','E.M. Clark','Empire Gem','Empire Thrush','Monitor','Tenas'};_fb=[]
for r in a.itertuples():
    if nl>=40:break
    if fixcase(r.VESSLTERMS) not in KEEP:continue
    nm='† '+fixcase(r.VESSLTERMS);y=f' ({int(float(r.YEARSUNK))})' if str(r.YEARSUNK) not in('None','nan','') else ''
    _cands=[(d_*s_,e_,'left' if s_>0 else 'right') for d_ in (10,14,18,24) for e_ in (0,8,-8,14,-14) for s_ in (1,-1)]
    _opt=None
    for dx,dy,ha in _cands:
        tx=ax.annotate(nm+y,(r.geometry.x,r.geometry.y),xytext=(dx*1.6,dy*1.6),textcoords='offset points',ha=ha,va='center',fontsize=26,family=LAB,fontstyle='italic',color='#4A3A2C',zorder=10,path_effects=[__import__('matplotlib.patheffects',fromlist=['x']).withStroke(linewidth=8,foreground=BONE)])
        bb=tx.get_window_extent(rend).expanded(1.05,1.25);axb=ax.get_window_extent();tx.remove()
        if axb.contains(bb.x0,bb.y0) and axb.contains(bb.x1,bb.y1) and not any(bb.overlaps(o) for o in placed+gb):
            k_=sum(bb.overlaps(o) for o in _skl)
            if _opt is None or k_<_opt[0]:_opt=(k_,dx,dy,ha,bb)
            if k_==0:break
    if _opt:
        k_,dx,dy,ha,bb=_opt;ax.annotate(nm+y,(r.geometry.x,r.geometry.y),xytext=(dx*1.6,dy*1.6),textcoords='offset points',ha=ha,va='center',fontsize=26,family=LAB,fontstyle='italic',color='#4A3A2C',zorder=10,path_effects=[__import__('matplotlib.patheffects',fromlist=['x']).withStroke(linewidth=8,foreground=BONE)])
        placed.append(bb);nl+=1;_fb.append((nm,k_,dx,dy))
print('DAGGER skull-overlaps (name, n, dx, dy)',_fb)
fig.text(40/W,1-16/H,'Graveyards of the Atlantic',fontsize=110,family=TITLE,color=OX,va='top')
fig.text(44/W,1-232/H,'Chesapeake to Cape Lookout: one tight cluster, one scattered graveyard',fontsize=50,family=LAB,color=BLK,va='top')
fig.text(40/W,1-2905/H,'Data: NOAA Office of Coast Survey (ENC, AWOIS) · NOAA ONMS · NOAA NCEI (CRM, ETOPO 2022) · Natural Earth · US Census Bureau',fontsize=25,family=NUM,color=BLK,va='top')
fig.text(40/W,1-2948/H,'Map: @funkchan · #30DayMapChallenge Day 4: Clusters',fontsize=25,family=NUM,color=OX,va='top',fontweight='bold')
from scipy.ndimage import gaussian_filter
from matplotlib.colors import LinearSegmentedColormap
X0,X1=ax.get_xlim();Y0,Y1=ax.get_ylim();cs=500
H2,xe,ye=np.histogram2d(pts.geometry.x[inf],pts.geometry.y[inf],bins=[int((X1-X0)/cs),int((Y1-Y0)/cs)],range=[[X0,X1],[Y0,Y1]])
K=gaussian_filter(H2.T,BW/cs)/((cs/1000)**2)  # wrecks per km2
v=np.clip(K/np.quantile(K[K>0],.995),0,1)
cm=LinearSegmentedColormap.from_list('ember',[(0,(0.910,0.831,0.635,0)),(.08,(0.88,0.70,0.35,0)),(.2,(0.85,0.62,0.25,.35)),(.45,(0.72,0.42,0.15,.62)),(1,(0.478,0.102,0.102,.9))])
import xarray as xr
from pyproj import Transformer
from matplotlib.colors import LightSource,ListedColormap,BoundaryNorm
gs=200;gx=np.arange(X0,X1,gs);gy=np.arange(Y0,Y1,gs);GX,GY=np.meshgrid(gx,gy)
LO,LA=Transformer.from_crs(E,4326,always_xy=True).transform(GX,GY)
def samp(fn):
    dz=xr.open_dataset(fn);zv=[v for v in dz.data_vars if dz[v].ndim==2][0];Z=dz[zv];la=Z[Z.dims[0]].values;lo=Z[Z.dims[1]].values;lo=np.where(lo>180,lo-360,lo);Zv=Z.values.astype(float)
    ii=np.round((LA-la[0])/(la[1]-la[0])).astype(int);jj=np.round((LO-lo[0])/(lo[1]-lo[0])).astype(int)
    ok=(ii>=0)&(ii<len(la))&(jj>=0)&(jj<len(lo));out=np.full(LA.shape,np.nan);out[ok]=Zv[ii[ok],jj[ok]];return out
CR=samp('data/crm2.nc');ET=samp('data/et_N45W090.nc');E2=samp('data/et_N45W075.nc');ET=np.where(np.isnan(ET),E2,ET)
DZ=np.where(np.isnan(CR)|(CR<-200),ET,CR);D=np.where(DZ<0,-DZ,np.nan)
print('cells from CRM %.0f%%'%(100*np.mean(~np.isnan(CR)&(CR>=-200)&(DZ<0))/max(np.mean(DZ<0),1e-9)))
LV=[0,5,10,20,50,100,200,1000,2000,3000,5000]
DC=['#F4E9CC','#ECDDB4','#DCD3A8','#C8C8A2','#B1B9A0','#98A99C','#7E9593','#678184','#566F74','#4A6066']
dcm=ListedColormap(DC);dn=BoundaryNorm(LV,dcm.N)
rgb=dcm(dn(np.nan_to_num(D,nan=0)))[...,:3]
hs=LightSource(315,45).hillshade(np.nan_to_num(-D,nan=0),vert_exag=12,dx=gs,dy=gs)
rgb=rgb*(0.82+0.18*hs[...,None]);A_=np.where(np.isnan(D),0,1.0)
ax.imshow(np.dstack([rgb,A_]),extent=(X0,X1,Y0,Y1),origin='lower',zorder=2.4,interpolation='bilinear')
Ds=gaussian_filter(np.nan_to_num(D,nan=0),2)
CS=ax.contour(GX,GY,Ds,levels=[10,20,50,100,200,1000,2000],colors='#3E4F52',linewidths=[.6,.6,.7,.8,1.2,.9,.9],alpha=.7,zorder=2.6)
cl_=ax.clabel(CS,fmt=lambda v:f'{int(v)} m',fontsize=26,inline=True,inline_spacing=6)
import matplotlib.patheffects as pe
for t in cl_:t.set_family(NUM);t.set_color('#1F2A2C');t.set_fontweight('bold');t.set_path_effects([pe.withStroke(linewidth=4,foreground='#E9E3CC')])
print('depth max m',np.nanmax(D))
yc=(np.arange(v.shape[0])+.5)*cs;xc=(np.arange(v.shape[1])+.5)*cs
Dk=D[np.clip((yc/gs).astype(int),0,D.shape[0]-1)][:,np.clip((xc/gs).astype(int),0,D.shape[1]-1)]
v=np.where(np.nan_to_num(Dk,nan=0)>200,0,v)
_gv=cm(v);_yy=np.linspace(Y0,Y1,v.shape[0]);_xx=np.linspace(X0,X1,v.shape[1]);_m_=((_yy>ei[1])&(_yy<ei[3]))[:,None]&((_xx>ei[0])&(_xx<ei[2]))[None,:];_gv[...,3]=np.where(_m_,_gv[...,3]*0.7,_gv[...,3])
ax.imshow(_gv,extent=(X0,X1,Y0,Y1),origin='lower',zorder=3,interpolation='bilinear')
pirate.ne.plot(ax=ax,color=LAND,lw=0,zorder=3.4);pirate.us.plot(ax=ax,color=LAND,ec=BLK,lw=.9,zorder=3.5);pirate.lakes.plot(ax=ax,color=SEA,ec=BLK,lw=.6,zorder=3.5)
ax.set_xlim(X0,X1);ax.set_ylim(Y0,Y1);print('KDE peak/km2',round(K.max(),3));ax.set_xlabel('');ax.set_ylabel('')

from matplotlib.path import Path as MP
def _c(cx,cy,r,rev=False):
    p=MP.unit_circle();v=p.vertices*r+[cx,cy];return MP(v[::-1] if rev else v,p.codes)
def _rect(x0,y0,x1,y1,ang):
    import math;c,s_=math.cos(ang),math.sin(ang);pts_=[(x0,y0),(x1,y0),(x1,y1),(x0,y1),(x0,y0)]
    return MP([(x*c-y*s_,x*s_+y*c) for x,y in pts_],[1,2,2,2,79])
SK=MP.make_compound_path(_rect(-.95,-.11,.95,.11,.62),_rect(-.95,-.11,.95,.11,-.62),_c(0,.18,.52),_rect(-.27,-.42,.27,-.1,0),_c(-.2,.2,.15,True),_c(.2,.2,.15,True))
OM=SK if MODE=='skulls' else 'x'
from matplotlib.offsetbox import OffsetImage,AnnotationBbox
SKPX=int(os.environ.get('SKPX','22'));_SKI={k:plt.imread(f'glyphs/skulls_gd/skull_{k}_40.png') for k in ('ink','bone')}
def omark(axx,x,y,deep,s_=170):
    im=_SKI['bone' if deep else 'ink']
    for xx,yy in zip(np.atleast_1d(np.asarray(x)),np.atleast_1d(np.asarray(y))):
        axx.add_artist(AnnotationBbox(OffsetImage(im,zoom=SKPX/40,interpolation='antialiased'),(xx,yy),box_alignment=(.5,.5),frameon=False,pad=0,zorder=4.6,annotation_clip=True));_ab=axx.artists[-1];_ab.set_clip_path(axx.patch);_ab.offsetbox.set_clip_path(axx.patch)
# outliers: depth-aware colour (bone beyond 200 m)
O=P[P.cl<0];oi=np.clip(((O.geometry.y-Y0)/gs).astype(int),0,D.shape[0]-1);oj=np.clip(((O.geometry.x-X0)/gs).astype(int),0,D.shape[1]-1)
od=np.nan_to_num(D[oi,oj],nan=0);deep=od>200;print('deep outliers',int(deep.sum()))
for axx,m_ in ((ax,~inINS[O.index]),(ia,np.ones(len(O),bool))):
    sh=O[m_&~deep];dp=O[m_&deep]
    omark(axx,sh.geometry.x,sh.geometry.y,False)
    omark(axx,dp.geometry.x,dp.geometry.y,True)
_OD=(O,deep);ia.apply_aspect();IX=ia.get_xlim();IY=ia.get_ylim();print('INSET lims',IX,IY,ei)
gx2=np.arange(IX[0],IX[1],60);gy2=np.arange(IY[0],IY[1],60);GX2,GY2=np.meshgrid(gx2,gy2)
LO2,LA2=Transformer.from_crs(E,4326,always_xy=True).transform(GX2,GY2)
dz=xr.open_dataset('data/crm2.nc');zv=[v_ for v_ in dz.data_vars if dz[v_].ndim==2][0];Z=dz[zv];la_=Z[Z.dims[0]].values;lo_=Z[Z.dims[1]].values;Zv=Z.values.astype(float)
ii=np.clip(np.round((LA2-la_[0])/(la_[1]-la_[0])).astype(int),0,len(la_)-1);jj=np.clip(np.round((LO2-lo_[0])/(lo_[1]-lo_[0])).astype(int),0,len(lo_)-1)
Z2=Zv[ii,jj];_LA,_LO=LA,LO;LA,LO=LA2,LO2;_e=samp('data/et_N45W075.nc');_e2=samp('data/et_N45W090.nc');_e=np.where(np.isnan(_e),_e2,_e);LA,LO=_LA,_LO;print('INSET crm nan',np.isnan(Z2).mean());Z2=np.where(np.isnan(Z2),_e,Z2);D2=np.where(Z2<0,-Z2,np.nan);print('INSET depth pct<20m',np.nanmean(D2<20),'bands main-tint share',[round(np.nanmean((D2>=a_)&(D2<b_)),2) for a_,b_ in zip(LV[:-1],LV[1:])][:5])
LVi=[0,2,5,10,15,20,30,50,100];dcmi=ListedColormap(DC[:8]);dni=BoundaryNorm(LVi,dcmi.N)
rgb2=dcmi(dni(np.clip(np.nan_to_num(D2,nan=0),0,99)))[...,:3];hs2=LightSource(315,45).hillshade(np.nan_to_num(-D2,nan=0),vert_exag=6,dx=60,dy=60)
rgb2=rgb2*(0.85+0.15*hs2[...,None])
ia.imshow(np.dstack([rgb2,np.where(np.isnan(D2),0,1.0)]),extent=(gx2[0],gx2[-1],gy2[0],gy2[-1]),origin='lower',zorder=2.4,interpolation='bilinear')
CS2=ia.contour(GX2,GY2,gaussian_filter(np.nan_to_num(D2,nan=0),3),levels=[5,10,20],colors='#3E4F52',linewidths=.6,alpha=.6,zorder=2.6)
fig.canvas.draw();_tb=[t_.get_bbox_patch().get_window_extent() for t_ in ia.texts if t_.get_bbox_patch()]
for t in ia.clabel(CS2,fmt=lambda v_:f'{int(v_)} m',fontsize=22,inline=True):
  if any(t.get_window_extent().overlaps(b_) for b_ in _tb):t.remove();continue
  _px,_py=t.get_position();_i=int(np.clip((_py-gy2[0])/60,0,len(gy2)-1));_j=int(np.clip((_px-gx2[0])/60,0,len(gx2)-1))
  if np.isnan(D2[_i,_j]):t.remove();continue
  t.set_family(NUM);t.set_color('#1F2A2C');t.set_path_effects([pe.withStroke(linewidth=3,foreground='#E9E3CC')])
pirate.ne.plot(ax=ia,color=LAND,lw=0,zorder=3.4);pirate.us.plot(ax=ia,color=LAND,ec=BLK,lw=.9,zorder=3.5);pirate.lakes.plot(ax=ia,color=SEA,ec=BLK,lw=.6,zorder=3.5);ia.set_xlabel('');ia.set_ylabel('')
ia.set_xlim(*IX);ia.set_ylim(*IY)
# hidden-under-inset counts (new vs previous position)
fig.canvas.draw();T=ax.transData.transform(np.c_[P.geometry.x,P.geometry.y]);AB=ax.get_window_extent()
vis=(T[:,0]>AB.x0)&(T[:,0]<AB.x1)&(T[:,1]>AB.y0)&(T[:,1]<AB.y1)&~inINS.values
Pd=np.zeros(len(P),bool);ti=np.clip(((P.geometry.y-Y0)/gs).astype(int),0,D.shape[0]-1);tj=np.clip(((P.geometry.x-X0)/gs).astype(int),0,D.shape[1]-1);Pd=np.nan_to_num(D[ti,tj],nan=0)>200
x0_=40+.505*MW;x1_=x0_+.475*MW
for nm_,top_ in (('NEW',2850-MH+22),('PREV',2850-.705*MH)):
    hb=(T[:,0]>x0_)&(T[:,0]<x1_)&(T[:,1]<H-top_)&(T[:,1]>H-top_-.275*MH)&vis
    print('HIDDEN',nm_,'total',hb.sum(),'outlier shallow',(hb&(P.cl.values<0)&~Pd).sum(),'outlier deep',(hb&(P.cl.values<0)&Pd).sum(),'clustered',(hb&(P.cl.values>=0)).sum())
    if nm_=='NEW':
        aa=aw_all.geometry;ta=ax.transData.transform(np.c_[aa.x,aa.y]);print('named AWOIS under new inset',int(((ta[:,0]>x0_)&(ta[:,0]<x1_)&(ta[:,1]<H-top_)&(ta[:,1]>H-top_-.275*MH)).sum()))
        inv=ax.transData.inverted();(dx0,dy0)=inv.transform((x0_,H-top_-.275*MH));(dx1,dy1)=inv.transform((x1_,H-top_))
        vy=((np.arange(v.shape[0])+.5)*cs+Y0);vx=((np.arange(v.shape[1])+.5)*cs+X0)
        sub=v[np.ix_((vy>dy0)&(vy<dy1),(vx>dx0)&(vx<dx1))];print('GLOW under inset max',float(sub.max()),'global max',float(v.max()))

# symbol key above caveat box
fig.canvas.draw();axb_=ax.get_window_extent()
K=1.4;kw_,kh_=int(840*K),int(282*K)
_ap0=ax.transData.transform(np.c_[pts.geometry.x,pts.geometry.y]);_kbest=None
for _ky in range(18,400,10):
  for _kx in range(18,200,10):
    x0_=axb_.x1-kw_-_kx;y0_=axb_.y0+_ky;n_=int(((_ap0[:,0]>x0_-10)&(_ap0[:,0]<x0_+kw_+10)&(_ap0[:,1]>y0_-10)&(_ap0[:,1]<y0_+kh_+10)).sum())
    if _kbest is None or n_<_kbest[0]:_kbest=(n_,x0_,y0_)
  if _kbest[0]==0:break
kx,ky=_kbest[1],_kbest[2];print('KEY search',_kbest)
ka=fig.add_axes([kx/W,ky/H,kw_/W,kh_/H]);ka.axis('off')
ka.add_patch(plt.matplotlib.patches.FancyBboxPatch((4,4),kw_-8,kh_-8,boxstyle='round,pad=0,rounding_size=16',fc=BONE,ec=OX,lw=2.6))
yy0,yy1,yy2=184*K,110*K,42*K;fk=dict(fontsize=22*K,family=NUM,color=BLK,va='center');fr=dict(fontsize=20*K,family=NUM,color=BLK,va='center')
for k_,(t_,lab_) in enumerate([(1,'≤8'),(2,'9–19'),(3,'20–49'),(4,'50+')]):
    x_=[10,130,268,430][k_]*K;ka.imshow(pirate.GL[t_],extent=(x_,x_+69*K,yy0-32*K,yy0+37*K),zorder=3);ka.text(x_+73*K,yy0,lab_,**fr)
ka.text(18*K,248*K,'Ship size and number = wrecks in each cluster',**fk)
gg=np.linspace(-1,1,60);G2=np.exp(-3*(gg[None]**2+gg[:,None]**2));ka.imshow(cm(G2*v.max()),extent=(18*K,68*K,yy1-22*K,yy1+22*K),zorder=2);ka.text(76*K,yy1,'density',**fk)
ka.add_patch(plt.matplotlib.patches.Ellipse((250*K,yy1),60*K,34*K,fill=False,ec=OX,lw=2.4,ls='--'));ka.text(288*K,yy1,'cluster hull',**fk)
ka.text(560*K,yy1,'† ship (AWOIS)',fontsize=22*K,family=LAB,color='#4A3A2C',fontstyle='italic',va='center')
ka.scatter([40*K],[yy2],s=170*1.3*K*K,marker='+',c=OX,lw=3.4*K);ka.text(62*K,yy2,'clustered',**fk)
ka.add_patch(plt.matplotlib.patches.FancyBboxPatch((222*K,yy2-15*K),30*K,30*K,boxstyle='round,pad=0,rounding_size=7',fc='#475C62',ec='none',zorder=4))
for xk_,kk_ in ((205,'ink'),(237,'bone')):ka.add_artist(AnnotationBbox(OffsetImage(_SKI[kk_],zoom=28/40,interpolation='antialiased'),(xk_*K,yy2),box_alignment=(.5,.5),frameon=False,pad=0,zorder=5))
ka.text(260*K,yy2,'outlier, shallow / deep (>200 m)',**fk)
ka.set_xlim(0,kw_);ka.set_ylim(0,kh_);ka.set_aspect('auto')
fig.canvas.draw();_kb=ka.get_window_extent()
for t in ax.texts:
  if t.get_visible() and t.get_window_extent().overlaps(_kb) and t.get_text().endswith(' m'):t.set_visible(False)
_ap=ax.transData.transform(np.c_[pts.geometry.x,pts.geometry.y]);print('KEY covers marks',int(((_ap[:,0]>_kb.x0-10)&(_ap[:,0]<_kb.x1+10)&(_ap[:,1]>_kb.y0-10)&(_ap[:,1]<_kb.y1+10)).sum()),'key px',_kb.bounds,'texts hit',[t.get_text()[:15] for t in ax.texts+fig.texts if t.get_visible() and t.get_text().strip() and t.get_window_extent().overlaps(_kb)])
import matplotlib.transforms as mt
px=ax.transData.transform(np.c_[pts.geometry.x,pts.geometry.y]);axb=ax.get_window_extent()
for t in ax.texts:
    bb=t.get_window_extent(rend)
    if t.get_bbox_patch() is not None:
        k=((px[:,0]>bb.x0)&(px[:,0]<bb.x1)&(px[:,1]>bb.y0)&(px[:,1]<bb.y1)).sum()
        if k: print('BOX COVERS',k,repr(t.get_text()[:20]))
cx,cy=ax.transAxes.transform((cb[1],cb[2]));r=.07*axb.width
print('compass covers',(np.hypot(px[:,0]-cx,px[:,1]-cy)<r).sum())
fig.canvas.draw();_r=fig.canvas.get_renderer()
_cl=set(cl_);_oth=[t for t in ax.texts if t not in _cl]
for t in list(cl_):
    b_=t.get_window_extent(_r)
    if any(b_.overlaps(o.get_bbox_patch().get_window_extent(_r) if o.get_bbox_patch() else o.get_window_extent(_r)) for o in _oth):t.remove();print('drop isobath label',t.get_text())
_t=fig.texts[0].get_window_extent(_r);_s=fig.texts[1].get_window_extent(_r);print('HEADER title bottom px',H-_t.y0,'subtitle top px',H-_s.y1,'gap',_s.y1 and _t.y0-_s.y1,'subtitle bottom',H-_s.y0,'map top',H-ax.get_window_extent().y1)
_all=[t for t in fig.texts]+[t for a_ in fig.axes for t in a_.texts if t.get_visible() and t.get_text().strip() and t.axes is not None]
_bb=[(t,(t.get_bbox_patch().get_window_extent(_r) if t.get_bbox_patch() else t.get_window_extent(_r))) for t in _all]
for i in range(len(_bb)):
  for j in range(i+1,len(_bb)):
    if _bb[i][1].overlaps(_bb[j][1]):print('OVERLAP',repr(_bb[i][0].get_text()[:25]),repr(_bb[j][0].get_text()[:25]))
fig.canvas.draw()
_ds=O[~inINS[O.index]].to_crs(4326);_m=(_ds.geometry.y.between(34.9,35.45)&_ds.geometry.x.between(-75.9,-75.0)).values
_p=ax.transData.transform(np.c_[O[~inINS[O.index]].geometry.x,O[~inINS[O.index]].geometry.y])[_m]
from scipy.spatial.distance import pdist
_d=pdist(_p,'chebyshev')
for _s in (20,18,16):print('DS OVERLAP',_s,'px: n pts',len(_p),'pairs overlapping',int((_d<_s).sum()),'pairs >50% overlap',int((_d<_s/2).sum()),'exact dupes',int((_d<1).sum()))
_a=ax.transData.transform(np.c_[O[~inINS[O.index]].geometry.x,O[~inINS[O.index]].geometry.y]);_D=pdist(_a,'chebyshev');print('ALL main overlap 20/18',int((_D<20).sum()),int((_D<18).sum()))
fig.canvas.draw();rend=fig.canvas.get_renderer()
import matplotlib.path as mpath
_co=[t for t in ax.texts if t.get_text().startswith('THE SCATTERED')][0]
_lab=[t for t in ax.texts if t.get_visible() and t.get_text().strip() and t is not _co]
_obs=[(t.get_bbox_patch().get_window_extent() if t.get_bbox_patch() else t.get_window_extent()) for t in _lab]+[g.get_window_extent() for g in ax.images if g.get_window_extent().width<300]
_obs=[mt.Bbox.from_extents(b.x0-4,b.y0-4,b.x1+4,b.y1+4) for b in _obs]
def _hits():
    fig.canvas.draw();pth=_co.arrow_patch.get_path();v_=np.vstack([np.asarray(p) for p in pth.to_polygons(closed_only=False)]);v_=np.vstack([v_[k]+(v_[k+1]-v_[k])*f for k in range(len(v_)-1) for f in np.linspace(0,1,12)])
    return sum(any(b.contains(*q) for q in v_) for b in _obs)
_best=None if ARROW else (0,-75.47,35.6,.2)
for la_ in ((35.45,35.5,35.55,35.6,35.66,35.72) if ARROW else ()):
  for lo_ in (-75.47,-75.49,-75.52):
    q=gpd.GeoSeries(gpd.points_from_xy([lo_],[la_]),crs=4326).to_crs(E)[0]
    for rad in (.35,.25,.15,.05,-.05,-.15,-.25):
      _co.xy=(q.x,q.y);_co.arrow_patch.set_connectionstyle(f'arc3,rad={rad}');h_=_hits()
      if _best is None or h_<_best[0]:_best=(h_,lo_,la_,rad)
  if _best[0]==0:break
if not ARROW:_co.arrow_patch.set_visible(False)
q=gpd.GeoSeries(gpd.points_from_xy([_best[1]],[_best[2]]),crs=4326).to_crs(E)[0];_co.xy=(q.x,q.y);_co.arrow_patch.set_connectionstyle(f'arc3,rad={_best[3]}');print('ARROW',_best);_ttb=_tt.get_bbox_patch().get_window_extent();_q=ax.transData.transform(np.c_[pts.geometry.x,pts.geometry.y]);print('TIGHTBOX main covers marks',int(((_q[:,0]>_ttb.x0)&(_q[:,0]<_ttb.x1)&(_q[:,1]>_ttb.y0)&(_q[:,1]<_ttb.y1)).sum()),'px',_ttb.bounds)
# DIAMOND SHOALS clearance from callout
fig.canvas.draw();_cb=_co.get_bbox_patch().get_window_extent();_ds=[t for t in ax.texts if t.get_text().startswith('D I A')][0];_db=_ds.get_window_extent()
print('DS-callout gap px x',_cb.x0-_db.x1,'y',max(_db.y0-_cb.y1,_cb.y0-_db.y1))
# Virginia Beach vs inset frame rectangle
_vb=[t for t in ax.texts if t.get_text()=='VIRGINIA BEACH'][0];_r0=ax.transData.transform((ei[0],ei[1]));_r1=ax.transData.transform((ei[2],ei[3]))
for _k in range(60):
  fig.canvas.draw();b_=_vb.get_window_extent()
  if b_.y1<_r0[1]-10 or b_.y0>_r0[1]+10:break
  p_=ax.transData.transform(_vb.get_position());_vb.set_position(ax.transData.inverted().transform((p_[0],p_[1]-2)))
fig.canvas.draw();b_=_vb.get_window_extent();print('VB gap to frame px',round(_r0[1]-b_.y1,1),'top',b_.y1,'frame',_r0[1])
# inset tight-cluster box vs galleon/badge
_cbb=_co.get_bbox_patch().get_window_extent();_ap_=ax.transData.transform(np.c_[pts.geometry.x,pts.geometry.y]);print('SCATTERED box covers marks',int(((_ap_[:,0]>_cbb.x0)&(_ap_[:,0]<_cbb.x1)&(_ap_[:,1]>_cbb.y0)&(_ap_[:,1]<_cbb.y1)).sum()))
fig.savefig(f"outputs/day04_v6_{'arrow' if ARROW else 'noarrow'}.png" ,dpi=100,facecolor=PARCH)
from PIL import Image;_f=f"outputs/day04_v6_{'arrow' if ARROW else 'noarrow'}.png";Image.open(_f).resize((1200,1500),Image.LANCZOS).save(_f.replace('.png','_1200.png'))
print(tot,ob,nl,len(a))

_sk=_SKB();_cl=[]
for t in ax.texts:
  if not t.get_visible() or not t.get_text().strip():continue
  _b=t.get_window_extent();_b2=t.get_bbox_patch().get_window_extent() if t.get_bbox_patch() else _b
  _n=sum(_b2.overlaps(k_) for k_ in _sk)
  if _n:_cl.append((t.get_text()[:30],_n))
_sk=_SKB();_fixed=[]
for t in list(ax.texts):
  if not t.get_visible() or not t.get_text().strip() or t.get_text().startswith(('†','THE ')):continue
  _box=lambda: (t.get_bbox_patch().get_window_extent() if t.get_bbox_patch() else t.get_window_extent())
  if not any(_box().overlaps(k_) for k_ in _sk):continue
  _ot=[o.get_window_extent() for o in ax.texts if o is not t and o.get_visible()]
  isann=hasattr(t,'xyann');p0=np.array(t.xyann if isann else t.get_position(),float);ok=False;_mn=None
  def _setp(q):
    if isann:t.xyann=tuple(q)
    else:t.set_position(q)
  for _r in range(2,(40 if isann else 80),2):
    for _a in np.linspace(0,2*np.pi,24,endpoint=False):
      if isann:  # offset points (1pt=100/72 px)
        t.xyann=tuple(p0+_r*72/100*np.array([np.cos(_a),np.sin(_a)]))
      else:
        t.set_position(ax.transData.inverted().transform(ax.transData.transform(p0)+_r*np.array([np.cos(_a),np.sin(_a)])))
      b_=_box()
      if any(b_.overlaps(o) for o in _ot) or not (ax.get_window_extent().contains(b_.x0,b_.y0) and ax.get_window_extent().contains(b_.x1,b_.y1)):continue
      _k=sum(b_.overlaps(k_) for k_ in _sk)
      if _mn is None or _k<_mn[0]:_mn=(_k,np.array(t.xyann if isann else t.get_position(),float),_r)
      if _k==0:ok=True;break
    if ok:break
  if not ok:
    _k0=sum(_box().overlaps(k_) for k_ in _sk) if False else None
    if _mn is not None:_setp(_mn[1])
    else:_setp(p0)
  _fixed.append((t.get_text()[:14].replace(chr(10),' '),_r if ok else ('PARTIAL',None if _mn is None else (_mn[0],_mn[2]))))
print('NUDGED',_fixed)
_cl=[]
for t in ax.texts:
  if not t.get_visible() or not t.get_text().strip():continue
  _b=t.get_window_extent();_b2=t.get_bbox_patch().get_window_extent() if t.get_bbox_patch() else _b
  _n=sum(_b2.overlaps(k_) for k_ in _sk)
  if _n:_cl.append((t.get_text()[:30],_n))
print('SKULL COLLISIONS (4px margin)',_cl)
print('PLACED',sorted(t.get_text() for t in ax.texts if t.get_text().startswith('†')))
