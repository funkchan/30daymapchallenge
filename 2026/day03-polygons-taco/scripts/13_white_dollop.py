"""Sour cream, colour-first: white surfaces (NE 10m playas = salt flats/dry lakes, NE 10m glaciated areas) scored against the dollop template
with the same rotation+reflection IoU search as 02_match.py, plus the best decoy (ellipse/rectangle) IoU as a shape-specificity check."""
import os, numpy as np, pandas as pd, geopandas as gpd, shapely
from common import DATA, local, parts, norm
import importlib; M = importlib.import_module("02_match")
rows = []
for src, f in (("NE 10m playas", "ne_10m_playas.shp"), ("NE 10m glaciated areas", "ne_10m_glaciated_areas.shp")):
    g = gpd.read_file(os.path.join(DATA, f)).explode(index_parts=False).reset_index(drop=True)
    g["km2"] = g.to_crs("EPSG:8857").area / 1e6; g = g[g.km2 >= 20]
    for i, r in g.iterrows():
        L = local(r.geometry).buffer(0); m = norm(max(parts(L), key=lambda p: p.area)).simplify(0.004)
        if m.area / m.convex_hull.area < 0.8: continue
        iou, rot, refl = M.best_iou(m, "dollop"); d = M.decoy(shapely.to_wkb(r.geometry))
        rp = r.geometry.representative_point()
        rows.append(dict(source=src, idx=i, name=r.get("name") or "", lon=rp.x, lat=rp.y, km2=r.km2, dollop_iou=iou, decoy_iou=d, margin=iou - d, rot=rot, refl=refl, wkt=r.geometry.wkt))
df = pd.DataFrame(rows).sort_values("dollop_iou", ascending=False); df.to_csv(os.path.join(DATA, "match_white_dollop.csv"), index=False)
pd.set_option("display.width", 200); print(df.drop(columns="wkt").head(20).round(3).to_string())
from review import grid, upright
grid([(upright(shapely.wkt.loads(r.wkt), r.rot, flip=False), f"{r['name'] or r.source[7:]} {r.lat:.1f},{r.lon:.1f}\nIoU {r.dollop_iou:.3f} decoy {r.decoy_iou:.3f}") for _, r in df.head(12).iterrows()], os.path.join(DATA, "rev_white_dollop.png"), cols=6, title="white dollops")
