import os
ROOT=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
os.chdir(ROOT)
D=os.path.join(ROOT,'data')
import numpy as np,pandas as pd,geopandas as gpd
from scipy.spatial import cKDTree
from sklearn.cluster import DBSCAN
a=gpd.read_file(os.path.join(D,'coastal_33.geojson'));a['src']='ENC coastal'
b=gpd.read_file(os.path.join(D,'general_29.geojson'));b['src']='ENC general'
E=5070
A=a.to_crs(E);B=b.to_crs(E);t=cKDTree(np.c_[A.geometry.x,A.geometry.y]);dd,_=t.query(np.c_[B.geometry.x,B.geometry.y])
enc=pd.concat([A,B[dd>1000]],ignore_index=True);enc['name']=enc.OBJNAM
aw=gpd.read_file(os.path.join(D,'awois','2020445569','aw','AWOIS_Wrecks.shp')).to_crs(E)
t=cKDTree(np.c_[enc.geometry.x,enc.geometry.y]);dd,_=t.query(np.c_[aw.geometry.x,aw.geometry.y])
aw=aw[dd>1000].copy();aw['src']='AWOIS';aw['name']=aw.VESSLTERMS.where(aw.VESSLTERMS.fillna('UNKNOWN').str.upper()!='UNKNOWN')
aw['year']=pd.to_numeric(aw.YEARSUNK,errors='coerce')
m=gpd.GeoDataFrame(pd.concat([enc[['src','name','geometry']],aw[['src','name','year','geometry']]],ignore_index=True),crs=E)
ll=m.to_crs(4326);x,y=ll.geometry.x,ll.geometry.y
m['region']=np.select([(x>-126)&(x<-66)&(y>24)&(y<50)],['L48'],'other')
print('ENC coastal',len(A),'ENC general kept',(dd>-1).sum() and len(enc)-len(A),'AWOIS kept',len(aw),'merged',len(m),m.region.value_counts().to_dict())
L=m[m.region=='L48'].copy();X=np.c_[L.geometry.x,L.geometry.y]/1000
L['cl']=DBSCAN(eps=20,min_samples=30).fit_predict(X)
s=L[L.cl>=0].groupby('cl')
o=pd.DataFrame({'n':s.size(),'hull':s.geometry.apply(lambda q:max(q.union_all().convex_hull.area/1e6,1))})
o['dens']=o.n/o.hull*1000
c=gpd.GeoSeries(s.geometry.apply(lambda q:q.union_all().centroid),crs=E).to_crs(4326);o['lon']=c.x.round(2);o['lat']=c.y.round(2)
# tier: score = rank-average of n and density
o['score']=(o.n.rank(pct=True)+o.dens.rank(pct=True))/2
o['tier']=pd.cut(o.score,[0,.4,.65,.85,1.01],labels=[1,2,3,4]).astype(int)
o=o.sort_values('n',ascending=False);print('clusters',len(o),'in',(L.cl>=0).sum());print(o.round(2).to_string())
L.to_crs(4326).to_file(os.path.join(D,'merged_l48.gpkg'));o.to_csv(os.path.join(D,'clusters.csv'))
