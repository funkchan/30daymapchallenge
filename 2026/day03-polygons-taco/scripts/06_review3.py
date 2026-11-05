import os, pandas as pd, numpy as np, shapely, geopandas as gpd
from common import DATA, local, parts
from geomcache import fetch
from review import upright, grid
p=pd.read_csv(os.path.join(DATA,"pool.csv"),low_memory=False)
ids=["GRC-2885","NE-isl-211","NE-isl-180","22746128B46636453933041","IDN-557","50627088B6162442693475"]
c2=pd.read_csv(os.path.join(DATA,"match_cilantro2.csv"))
sel=p[p.src_id.isin(ids)]
extra=c2[c2.name.isin(["'Maoa-Mafubelu","Viesītes pag.","Kaev Seima","Strumitsa","Krapes pag.","Cunduacán"])]
G=fetch(list(zip(sel.source,sel.src_id))+list(zip(extra.source,extra.src_id)))
items=[]
for _,r in sel.iterrows():
    g=G[(r.source,r.src_id)]; items.append((upright(g,0,True),f"{r['name']} ({r.country})\nsol {r.solidity:.2f} rot0"))
for _,r in extra.iterrows():
    items.append((upright(G[(r.source,r.src_id)],r.rot,True),f"{r['name']} ({r.country})\n{r.iou:.3f} rot{r.rot}"))
grid(items,os.path.join(DATA,"rev_cilantro3.png"),4,"cilantro named")
# squares adjacency clusters
q=p[(p.area_km2>=20)&(p.main_share>=0.99)&(p.rectangularity>=0.97)&(p.aspect<=1.12)]
G=fetch(list(zip(q.source,q.src_id)))
gs=gpd.GeoDataFrame(q[["src_id","name","country","area_km2","rectangularity"]].reset_index(drop=True),geometry=[G[(s,i)] for s,i in zip(q.source,q.src_id)],crs=4326)
gs.to_file(os.path.join(DATA,"squares.gpkg"))
t=shapely.STRtree(gs.geometry.values); adj={i:set() for i in range(len(gs))}
for i,g in enumerate(gs.geometry):
    for j in t.query(g.buffer(0.01)):
        if j!=i and g.buffer(0.01).intersects(gs.geometry[j]): adj[i].add(j)
seen=set(); comps=[]
for i in adj:
    if i in seen: continue
    st=[i]; cc=[]
    while st:
        k=st.pop()
        if k in seen: continue
        seen.add(k); cc.append(k); st+=list(adj[k])
    comps.append(cc)
comps.sort(key=len,reverse=True)
for cc in comps[:12]:
    sub=gs.iloc[cc]; c=sub.unary_union.centroid
    print(len(cc), sub.country.iloc[0], f"{c.x:.2f},{c.y:.2f}", list(sub.name)[:12], f"mean area {sub.area_km2.mean():.0f}")
