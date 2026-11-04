#!/usr/bin/env python3
"""Round 2: deeper-lobed cilantro template; dollop re-ranked for smooth (curved, not faceted) outlines; named extras."""
import os, numpy as np, pandas as pd, shapely
from multiprocessing import Pool
from common import DATA, local, norm, parts
import importlib, sys
M = importlib.import_module("02_match")
from geomcache import fetch

def curvy(wkb):
    g = local(shapely.from_wkb(wkb)).buffer(0); m = norm(max(parts(g), key=lambda p: p.area))
    return len(m.simplify(0.004).exterior.coords)

def main():
    pool = pd.read_csv(os.path.join(DATA, "pool.csv"), low_memory=False); pool = pool[pool.area_km2 >= 20]
    sel = pool.query("main_share>=0.85 and 0.4<=solidity<=0.8 and aspect<=2.0")
    M.ING_T["cilantro_deep"] = "cilantro_deep"
    want = {(s, i): ["cilantro_deep"] for s, i in zip(sel.source, sel.src_id)}
    allm = pd.read_csv(os.path.join(DATA, "match_all.csv"), low_memory=False)
    dol = allm[allm.ingredient == "dollop"].nlargest(600, "iou")
    extra = [("Natural Earth 10m land, named by geography_regions_polys", "NE-isl-223")]  # Sri Lanka
    for k in list(zip(dol.source, dol.src_id)) + extra: want.setdefault(k, []).append("dollop")
    geoms = M.load_geoms(set(want)); print("geoms", len(geoms), flush=True)
    with Pool(7) as p:
        rows = [r for part in p.imap_unordered(M.job, [(k, geoms[k], v) for k, v in want.items() if k in geoms], chunksize=20) for r in part]
    res = pd.DataFrame([dict(source=k[0], src_id=k[1], ingredient=ing, iou=iou, rot=rot, refl=refl) for k, ing, iou, rot, refl in rows]).merge(pool, on=["source", "src_id"], how="left")
    d = res[res.ingredient == "dollop"].copy()
    with Pool(7) as p:
        d["n_vert"] = p.map(curvy, [geoms[(s, i)] for s, i in zip(d.source, d.src_id)])
    c = res[res.ingredient == "cilantro_deep"].nlargest(80, "iou").copy()
    with Pool(7) as p:
        c["iou_decoy"] = p.map(M.decoy, [geoms[(s, i)] for s, i in zip(c.source, c.src_id)])
    c["margin"] = c.iou - c.iou_decoy
    d.to_csv(os.path.join(DATA, "match_dollop2.csv"), index=False); c.to_csv(os.path.join(DATA, "match_cilantro2.csv"), index=False)
    pd.set_option("display.width", 250)
    print(c.head(20)[["name", "country", "admin_level", "iou", "margin", "solidity"]].to_string())
    print(d[d.n_vert >= 60].nlargest(20, "iou")[["name", "country", "admin_level", "iou", "n_vert", "rough"]].to_string())
if __name__ == "__main__":
    main()
