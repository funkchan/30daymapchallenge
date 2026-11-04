import matplotlib.transforms as mt
from pirate import *
W,H=2400,3000;fig=plt.figure(figsize=(24,30),dpi=100);fig.patch.set_facecolor(PARCH)
BX=(-76.75,34.35,-74.9,36.95)
MW,MH=2320,2540
ax=fig.add_axes([40/W,1-2850/H,MW/W,MH/H])
kp=gpd.GeoSeries(gpd.points_from_xy([-76.15,-76.75,-76.2],[37.02,34.5,35.5]),crs=4326).to_crs(E)
y0=kp.y.min()-12000;y1=kp.y.max()+42000;wx=kp.x.min()-26000;wid=(y1-y0)*MW/MH
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
basemap(ax,(wx,y0,wx+wid,y1),gly=1.1,cg_=C[~inI],**kw)
from shapely.geometry import MultiPoint
HG=[(k_,MultiPoint(list(zip(d.geometry.x,d.geometry.y))).convex_hull.buffer(1500)) for k_,d in P[P.cl>=0].groupby('cl')]
HUL=gpd.GeoSeries([h for _,h in HG],index=[k_ for k_,_ in HG],crs=E)
HUL[~HUL.index.isin(C.index[inI])].plot(ax=ax,fc='none',ec=OX,lw=1.8,ls='--',zorder=5.5)
ei=ext(*INS);ax.add_patch(plt.Rectangle((ei[0],ei[1]),ei[2]-ei[0],ei[3]-ei[1],fill=False,ec=BLK,lw=2,zorder=6))
# inset
ia=fig.add_axes([(40+.505*MW)/W,1-(2850-.705*MH)/H-.275*MH/H,.475*MW/W,.275*MH/H])
big=C.n.idxmax()
pirate.pts=P[(P.cl>=0)&(P.cl!=big)]
basemap(ia,ei,gly=.8,cg_=C[inI],counts=False,**kw)
bp=P[P.cl==big];ia.scatter(bp.geometry.x,bp.geometry.y,s=170*1.3,marker='+',c=OX,lw=3,alpha=.28,zorder=5)
OFF={11:(70,55),23:(-95,-30),82:(0,-22),8:(45,50)}
for k_,r_ in C[inI].iterrows():
    dx_,dy_=OFF.get(int(r_.n),(0,-18))
    ia.annotate(f'{int(r_.n)}',(r_.geometry.x,r_.geometry.y),xytext=(dx_,dy_),textcoords='offset points',ha='center',va='top' if dy_<=0 else 'bottom',fontsize=24,family=NUM,fontweight='bold',color=BLK,zorder=9,
      bbox=dict(boxstyle='round,pad=0.15',fc=BONE,ec=BLK,lw=.8),arrowprops=None if abs(dx_)<1 else dict(arrowstyle='-',color=BLK,lw=1.2))
HUL.plot(ax=ia,fc='none',ec=OX,lw=2,ls='--',zorder=5.5)
pirate.pts=P
for s_ in ia.spines.values():s_.set_lw(3)
from matplotlib.patches import ConnectionPatch
for (xa,ya),(xb,yb) in [((ei[2],ei[1]),(0,0))]:
    fig.add_artist(ConnectionPatch((xa,ya),(xb,yb),coordsA=ax.transData,coordsB=ia.transAxes,color=BLK,lw=1.3,ls='-',alpha=.8,zorder=7))
ia.set_xlabel('');ia.set_ylabel('')
title_tag(ia,'Chesapeake Bay mouth (zoom)','tl',fs=26)
bd=P[P.cl==big];bc=C.loc[big].geometry
sh20=100*(np.hypot(bd.geometry.x-bc.x,bd.geometry.y-bc.y)<=20000).mean();r90=np.quantile(np.hypot(bd.geometry.x-bc.x,bd.geometry.y-bc.y),.9)/1000
hr=C[inI&(C.n<C.n.max())].n.max()
legend_box(ia,['THE TIGHT CLUSTER',f'{int(C.n.max())} wrecks off Cape Henry, {sh20:.0f}% within',f'20 km of the centre, where shipping','converges on the bay mouth;',f'{int(hr)} more at Hampton Roads.'],loc=(.98,.03),ha='right',fs=22)
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
    if X0<g.x<X1 and Y0<g.y<Y1: ax.text(g.x+(0 if R else -3000),g.y,'CAPE\nHATTERAS' if nm=='Cape Hatteras' else nm.upper(),linespacing=.95,ha='left' if R else 'right',va='center',fontsize=28,family=LAB,color=OX,zorder=10)
g=gpd.GeoSeries(gpd.points_from_xy([-75.33],[35.07]),crs=4326).to_crs(E)[0]
g=gpd.GeoSeries(gpd.points_from_xy([-75.28],[35.04]),crs=4326).to_crs(E)[0]
ax.text(g.x,g.y,'D I A M O N D   S H O A L S',fontsize=24,family=LAB,color=OX,ha='left',va='center',zorder=10,fontstyle='italic')
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
compass(ax,cb[1],cb[2],.042)

legend_box(ax,['CAVEATS','Charted/recorded wrecks only: most losses were never','located or were buried by shifting shoals. Clusters','also reflect survey effort. Some points may be','artificial reefs. AWOIS: 2016 snapshot.'],loc=(.985,.012),ha='right',va='bottom',fs=22)
gO=gpd.GeoSeries(gpd.points_from_xy([-75.5],[35.45]),crs=4326).to_crs(E)[0]
bestO=None
for yy in np.arange(.2,.66,.02):
  for xx in (.02,.05,.08):
    ax.annotate(f'THE SCATTERED GRAVEYARD\n{obn} wrecks off the Outer Banks;\n{obo} ({100*obo/obn:.0f}%) lie outside any cluster.\nNo single funnel: losses spread\nalong the whole barrier coast.\nLegend vs. chart: "more than 2,000"\nhistorical wrecks (NOAA ONMS) vs\n{ob} charted & recorded (ENC + AWOIS).',(gO.x,gO.y),xytext=(xx,yy),textcoords='axes fraction',ha='left',va='center',fontsize=22,family=NUM,color=BLK,zorder=12,linespacing=1.3,bbox=dict(boxstyle='round,pad=0.45',fc=BONE,ec=OX,lw=2.2),arrowprops=dict(arrowstyle='-|>',color=OX,lw=2.2,connectionstyle='arc3,rad=-0.2'))
    an=ax.texts[-1];fig.canvas.draw();B=an.get_bbox_patch().get_window_extent(rend);k=cov(B)+100*sum(B.overlaps(o.get_window_extent(rend)) for o in ax.texts[:-1]);an.remove()
    if bestO is None or k<bestO[0]:bestO=(k,xx,yy)
print('OBbox',bestO)
ax.annotate(f'THE SCATTERED GRAVEYARD\n{obn} wrecks off the Outer Banks;\n{obo} ({100*obo/obn:.0f}%) lie outside any cluster.\nNo single funnel: losses spread\nalong the whole barrier coast.\nLegend vs. chart: "more than 2,000"\nhistorical wrecks (NOAA ONMS) vs\n{ob} charted & recorded (ENC + AWOIS).',(gO.x,gO.y),xytext=(bestO[1],bestO[2]),textcoords='axes fraction',ha='left',va='center',fontsize=24,family=NUM,color=BLK,zorder=12,
  bbox=dict(boxstyle='round,pad=0.45',fc=BONE,ec=OX,lw=2.2),arrowprops=dict(arrowstyle='-|>',color=OX,lw=2.2,connectionstyle='arc3,rad=-0.2'))
fig.canvas.draw();rend=fig.canvas.get_renderer();placed=[];nl=0
_c=ax.transAxes.transform((cb[1],cb[2]));_r=.052*ax.get_window_extent().width
gb=[ia.get_window_extent(),mt.Bbox.from_extents(_c[0]-_r,_c[1]-_r,_c[0]+_r,_c[1]+_r*1.4)]+[g.get_window_extent() for g in ax.images]+[tx.get_window_extent() for tx in ax.texts]
for r in a.itertuples():
    if nl>=40:break
    nm='† '+fixcase(r.VESSLTERMS);y=f' ({int(float(r.YEARSUNK))})' if str(r.YEARSUNK) not in('None','nan','') else ''
    for dx,ha in [(10,'left'),(-10,'right')]:
        tx=ax.annotate(nm+y,(r.geometry.x,r.geometry.y),xytext=(dx*1.6,0),textcoords='offset points',ha=ha,va='center',fontsize=22,family=LAB,fontstyle='italic',color='#4A3A2C',zorder=10,path_effects=[__import__('matplotlib.patheffects',fromlist=['x']).withStroke(linewidth=8,foreground=BONE)])
        bb=tx.get_window_extent(rend).expanded(1.05,1.25);axb=ax.get_window_extent()
        if axb.contains(bb.x0,bb.y0) and axb.contains(bb.x1,bb.y1) and not any(bb.overlaps(o) for o in placed+gb):
            placed.append(bb);nl+=1;break
        tx.remove()
fig.text(40/W,1-16/H,'Graveyards of the Atlantic',fontsize=110,family=TITLE,color=OX,va='top')
fig.text(44/W,1-232/H,'Chesapeake to Cape Lookout: one tight cluster, one scattered graveyard',fontsize=44,family=LAB,color=BLK,va='top')
fig.text(40/W,1-2862/H,f'Methods: {tot:,} wrecks in frame · glow = wreck density, Gaussian KDE 5 km (hidden beyond 200 m depth) · clusters = regional DBSCAN, eps 5 km, min 6 (EPSG:5070) · hull = convex hull + 1.5 km',fontsize=19,family=NUM,color=BLK,va='top')
fig.text(40/W,1-2905/H,'Data: NOAA Office of Coast Survey (ENC, AWOIS) · NOAA ONMS · NOAA NCEI (CRM, ETOPO 2022) · Natural Earth · US Census Bureau',fontsize=22,family=NUM,color=BLK,va='top')
fig.text(40/W,1-2945/H,'Map: @funkchan · #30DayMapChallenge Day 4: Clusters',fontsize=22,family=NUM,color=OX,va='top',fontweight='bold')
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
cl_=ax.clabel(CS,fmt=lambda v:f'{int(v)} m',fontsize=22,inline=True,inline_spacing=6)
import matplotlib.patheffects as pe
for t in cl_:t.set_family(NUM);t.set_color('#1F2A2C');t.set_fontweight('bold');t.set_path_effects([pe.withStroke(linewidth=4,foreground='#E9E3CC')])
print('depth max m',np.nanmax(D))
yc=(np.arange(v.shape[0])+.5)*cs;xc=(np.arange(v.shape[1])+.5)*cs
Dk=D[np.clip((yc/gs).astype(int),0,D.shape[0]-1)][:,np.clip((xc/gs).astype(int),0,D.shape[1]-1)]
v=np.where(np.nan_to_num(Dk,nan=0)>200,0,v)
ax.imshow(cm(v),extent=(X0,X1,Y0,Y1),origin='lower',zorder=3,interpolation='bilinear')
pirate.ne.plot(ax=ax,color=LAND,lw=0,zorder=3.4);pirate.us.plot(ax=ax,color=LAND,ec=BLK,lw=.9,zorder=3.5);pirate.lakes.plot(ax=ax,color=SEA,ec=BLK,lw=.6,zorder=3.5)
ax.set_xlim(X0,X1);ax.set_ylim(Y0,Y1);print('KDE peak/km2',round(K.max(),3));ax.set_xlabel('');ax.set_ylabel('')

# outliers: depth-aware colour (bone beyond 200 m)
O=P[P.cl<0];oi=np.clip(((O.geometry.y-Y0)/gs).astype(int),0,D.shape[0]-1);oj=np.clip(((O.geometry.x-X0)/gs).astype(int),0,D.shape[1]-1)
od=np.nan_to_num(D[oi,oj],nan=0);deep=od>200;print('deep outliers',int(deep.sum()))
for axx,m_ in ((ax,~inINS[O.index]),(ia,np.ones(len(O),bool))):
    sh=O[m_&~deep];dp=O[m_&deep]
    axx.scatter(sh.geometry.x,sh.geometry.y,s=170,marker='x',c=OUTC,alpha=.85,lw=2.2,zorder=4.6,path_effects=[pe.withStroke(linewidth=3.5,foreground=BONE)])
    axx.scatter(dp.geometry.x,dp.geometry.y,s=170,marker='x',c='#F1E4C3',lw=2.2,zorder=4.6,path_effects=[pe.withStroke(linewidth=3.6,foreground='#1F2A2C')])
ia.set_xlim(ei[0],ei[2]);ia.set_ylim(ei[1],ei[3])
# symbol key above caveat box
fig.canvas.draw();cvb=[t for t in ax.texts if t.get_text().startswith('CAVEATS')][0].get_window_extent(rend)
kw_,kh_=820,150;kx=cvb.x1-kw_;ky=cvb.y1+18
ka=fig.add_axes([kx/W,ky/H,kw_/W,kh_/H]);ka.set_xlim(0,kw_);ka.set_ylim(0,kh_);ka.axis('off')
ka.add_patch(plt.matplotlib.patches.FancyBboxPatch((4,4),kw_-8,kh_-8,boxstyle='round,pad=0,rounding_size=12',fc=BONE,ec=OX,lw=2.2))
yy1,yy2=105,42;fk=dict(fontsize=22,family=NUM,color=BLK,va='center')
gg=np.linspace(-1,1,60);G2=np.exp(-3*(gg[None]**2+gg[:,None]**2));ka.imshow(cm(G2*v.max()),extent=(18,68,yy1-22,yy1+22),zorder=2);ka.text(76,yy1,'density',**fk)
ka.imshow(pirate.GL[2],extent=(205,255,yy1-20,yy1+30),zorder=3);ka.text(262,yy1,'cluster (n)',**fk)
ka.add_patch(plt.matplotlib.patches.Ellipse((470,yy1),60,34,fill=False,ec=OX,lw=1.8,ls='--'));ka.text(508,yy1,'cluster hull',**fk)
ka.scatter([40],[yy2],s=170*1.3,marker='+',c=OX,lw=3.4);ka.text(62,yy2,'clustered',**fk)
ka.scatter([205],[yy2],s=170,marker='x',c=OUTC,lw=2.2);ka.scatter([235],[yy2],s=170,marker='x',c='#F1E4C3',lw=2.2,path_effects=[pe.withStroke(linewidth=3.6,foreground='#1F2A2C')]);ka.text(256,yy2,'outlier, shallow / deep',**fk)
ka.text(590,yy2,'† ship (AWOIS)',fontsize=22,family=LAB,color='#4A3A2C',fontstyle='italic',va='center')
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
fig.savefig('outputs/day04_final_v4.png',dpi=100,facecolor=PARCH)
from PIL import Image;Image.open('outputs/day04_final_v4.png').resize((1200,1500),Image.LANCZOS).save('outputs/day04_final_v4_1200.png')
print(tot,ob,nl,len(a))

print('PLACED',sorted(t.get_text() for t in ax.texts if t.get_text().startswith('†')))
