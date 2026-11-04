import os, pandas as pd, shapely, geopandas as gpd
from shapely import wkt as W
from common import DATA, local, parts
from geomcache import fetch
from review import upright, grid
c = pd.read_csv(os.path.join(DATA,"match_cilantro2.csv")).sort_values("iou",ascending=False).head(36)
d = pd.read_csv(os.path.join(DATA,"match_dollop2.csv"))
d = d[(d.n_vert>=60)&(d.rough<=1.12)|(d.src_id=="NE-isl-223")].nlargest(36,"iou")
G = fetch(list(zip(c.source,c.src_id))+list(zip(d.source,d.src_id)))
for df,nm in [(c,"cilantro2"),(d,"dollop2")]:
    items=[(upright(G[(r.source,r.src_id)],r.rot,True,False),f"{i}. {r['name'][:22]} ({r.country})\n{r.iou:.3f}") for i,(_,r) in enumerate(df.iterrows())]
    grid(items,os.path.join(DATA,f"rev_{nm}.png"),6,nm)
b = pd.read_csv(os.path.join(DATA,"cheese_bundles.csv")); print(b.drop(columns="wkt").head(20).to_string())
items=[]
for i,(_,r) in enumerate(b.head(18).iterrows()):
    g=local(W.loads(r.wkt)); items.append((g,f"{i}. {str(r.get('name',''))[:24]}\n{r.get('score',0):.2f}"))
grid(items,os.path.join(DATA,"rev_cheese.png"),6,"cheese")
a=pd.read_csv(os.path.join(DATA,"match_top.csv")); s=a[a.ingredient=="square"] if "square" in set(a.ingredient) else None
print(sorted(set(a.ingredient)))
if s is not None:
    s=s.nlargest(36,"iou"); G=fetch(list(zip(s.source,s.src_id)))
    grid([(upright(G[(r.source,r.src_id)],r.rot),f"{i}. {r['name'][:22]} ({r.country})\n{r.iou:.3f} {r.area_km2:.0f}km²") for i,(_,r) in enumerate(s.iterrows())],os.path.join(DATA,"rev_square.png"),6,"square")
