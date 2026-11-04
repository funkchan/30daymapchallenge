#!/usr/bin/env python3
"""Pre-filter the pool on cheap descriptors, then rotation(5°)+reflection IoU template search per ingredient."""
import os, sys, numpy as np, pandas as pd, geopandas as gpd, pyogrio, shapely
from shapely import affinity
from multiprocessing import Pool
from common import DATA, D3, local, parts, norm
from templates import TEMPLATES, DECOYS
ANG = np.arange(0, 360, 5)
ROT = {k: [np.array([affinity.rotate(t, a, origin=(0, 0)) for a in ANG]),
           np.array([affinity.rotate(affinity.scale(t, -1, 1, origin=(0, 0)), a, origin=(0, 0)) for a in ANG])] for k, t in TEMPLATES.items()}
DEC = np.array([affinity.rotate(d, a, origin=(0, 0)) for d in DECOYS for a in range(0, 180, 10)])

# cheap pre-filters (on main part unless noted); thresholds chosen loosely so the IoU search decides
FILTERS = {
    "shell":     "main_share>=0.9 and 0.3<=solidity<=0.75 and 1.4<=aspect<=3.5",
    "drumstick": "main_share>=0.9 and 0.55<=solidity<=0.9 and 1.8<=aspect<=4.5 and rough<=1.3",
    "chorizo":   "main_share>=0.9 and 0.35<=solidity<=0.9 and 2.5<=aspect<=9 and rough<=1.25",
    "leaf":      "main_share>=0.85 and 0.45<=solidity<=0.85 and 1.2<=aspect<=2.6 and rough>=1.25",
    "cilantro":  "main_share>=0.9 and 0.5<=solidity<=0.85 and aspect<=1.8",
    "dollop":    "main_share>=0.95 and solidity>=0.85 and 1.1<=aspect<=2.0 and rough<=1.12",
}
ING_T = {"shell": "shell", "drumstick": "drumstick", "chorizo": "chorizo", "leaf": "leaf", "cilantro": "cilantro", "dollop": "dollop"}

def best_iou(m, k):
    out = (0.0, 0, False)
    for refl, arr in enumerate(ROT[k]):
        inter = shapely.area(shapely.intersection(arr, m)); iou = inter / (2 - inter); i = int(np.argmax(iou))
        if iou[i] > out[0]: out = (float(iou[i]), int(ANG[i]), bool(refl))
    return out

def job(args):
    key, wkb, ings = args
    g = local(shapely.from_wkb(wkb)).buffer(0); m = norm(max(parts(g), key=lambda p: p.area)).simplify(0.004)
    res = []
    for ing in ings:
        iou, rot, refl = best_iou(m, ING_T[ing]); res.append((key, ing, iou, rot, refl))
    return res

def decoy(wkb):
    g = local(shapely.from_wkb(wkb)).buffer(0); m = norm(max(parts(g), key=lambda p: p.area)).simplify(0.004)
    inter = shapely.area(shapely.intersection(DEC, m)); return float((inter / (2 - inter)).max())

def load_geoms(keys):
    """keys: set of (source, src_id) -> wkb"""
    out = {}
    a1 = gpd.read_file(os.path.join(D3, "ne_10m_admin_1_states_provinces.shp"), columns=["adm1_code"])
    for _, r in a1.iterrows():
        k = ("Natural Earth 10m admin-1", r.adm1_code)
        if k in keys: out[k] = shapely.to_wkb(r.geometry)
    isl = gpd.read_file(os.path.join(DATA, "islands.gpkg"))
    for _, r in isl.iterrows():
        k = ("Natural Earth 10m land, named by geography_regions_polys", r.sid)
        if k in keys: out[k] = shapely.to_wkb(r.geometry)
    f = os.path.join(DATA, "geoBoundariesCGAZ_ADM2.gpkg"); n = pyogrio.read_info(f)["features"]
    for s in range(0, n, 5000):
        g = pyogrio.read_dataframe(f, skip_features=s, max_features=5000, columns=["shapeID"])
        for sid, geom in zip(g.shapeID, g.geometry):
            k = ("geoBoundaries CGAZ ADM2", sid)
            if k in keys: out[k] = shapely.to_wkb(geom)
    return out

def main():
    pool = pd.read_csv(os.path.join(DATA, "pool.csv"), low_memory=False)
    pool = pool[pool.area_km2 >= 20]
    want = {}
    for ing, q in FILTERS.items():
        sel = pool.query(q); print(ing, len(sel), flush=True)
        for s, i in zip(sel.source, sel.src_id): want.setdefault((s, i), []).append(ing)
    geoms = load_geoms(set(want)); print("geoms", len(geoms), flush=True)
    with Pool(7) as p:
        rows = [r for part in p.imap_unordered(job, [(k, geoms[k], v) for k, v in want.items() if k in geoms], chunksize=20) for r in part]
    res = pd.DataFrame([dict(source=k[0], src_id=k[1], ingredient=ing, iou=iou, rot=rot, refl=refl) for k, ing, iou, rot, refl in rows])
    res = res.merge(pool, on=["source", "src_id"])
    top = res.sort_values("iou", ascending=False).groupby("ingredient").head(60).copy()
    with Pool(7) as p:
        top["iou_decoy"] = p.map(decoy, [geoms[(s, i)] for s, i in zip(top.source, top.src_id)])
    top["margin"] = top.iou - top.iou_decoy
    res.to_csv(os.path.join(DATA, "match_all.csv"), index=False); top.to_csv(os.path.join(DATA, "match_top.csv"), index=False)
    pd.set_option("display.width", 250)
    for ing, g in top.groupby("ingredient"):
        print("\n==", ing); print(g.head(15)[["name", "country", "admin_level", "area_km2", "iou", "iou_decoy", "margin"]].to_string())

if __name__ == "__main__":
    main()
