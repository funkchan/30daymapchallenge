#!/usr/bin/env python3
"""Cheap refinement: 0.01 deg rasterisation of the vector RESOLVE polygons (no closing) in a regional bbox,
hill-climb great-circle pole + centre; 1 km samples; only water (no-polygon) gaps <=5 km bridged.
Winner is re-checked with validate.py (vector point-in-polygon). Usage: python refine_raster.py <code>"""
import json, os, sys
import numpy as np, shapely
from rasterio import features
from rasterio.transform import from_origin
import validate as V, longest_lines as ll
from validate import pole_of
RES = 0.01
BBOX = {5: (-20, 0, 45, 22), 2: (25, 45, 145, 70)}
k = int(sys.argv[1]); x0, y0, x1, y1 = BBOX[k]
W, H = int((x1 - x0) / RES), int((y1 - y0) / RES); tr = from_origin(x0, y1, RES, RES)
sel = shapely.intersects(V.geoms, shapely.box(x0, y0, x1, y1))
gs, cs = V.geoms[sel], V.code[sel]
biome = features.rasterize(((g, 1) for g, c in zip(gs, cs) if c == k), out_shape=(H, W), transform=tr, fill=0, dtype="uint8").astype(bool)
land = features.rasterize(((g, 1) for g in gs), out_shape=(H, W), transform=tr, fill=0, dtype="uint8").astype(bool)
print("rasterised", flush=True)
def look(m, lat, lon):
    i = ((y1 - lat) / RES).astype(int); j = ((lon - x0) / RES).astype(int)
    ok = (i >= 0) & (i < H) & (j >= 0) & (j < W)
    out = np.zeros(lat.shape, bool); out[ok] = m[i[ok], j[ok]]; return out
def score(pole, mid, half_km=4000, step=1.0):
    u = mid - np.dot(mid, pole) * pole; u /= np.linalg.norm(u); v = np.cross(pole, u)
    t = np.arange(-half_km, half_km, step) / ll.R
    x = np.cos(t)[:, None] * u + np.sin(t)[:, None] * v
    lat = np.degrees(np.arcsin(x[:, 2])); lon = np.degrees(np.arctan2(x[:, 1], x[:, 0]))
    ins = look(biome, lat, lon); wat = ~look(land, lat, lon)
    ok = ins.copy(); out = np.where(~ins)[0]
    if len(out):
        brk = np.where(np.diff(out) > 1)[0]
        for s, e in zip(np.r_[out[0], out[brk + 1]], np.r_[out[brk], out[-1]]):
            if e - s + 1 <= 5 and s > 0 and e < len(ins) - 1 and wat[s:e+1].all(): ok[s:e+1] = True
    a = np.r_[False, ok, False].astype(int); d = np.diff(a); st = np.where(d == 1)[0]; en = np.where(d == -1)[0]
    if not len(st): return 0, mid, None, None
    j = np.argmax(en - st); s, e = st[j], en[j] - 1
    tm = t[(s + e) // 2]; m2 = np.cos(tm) * u + np.sin(tm) * v
    return (e - s) * step, m2, (lon[s], lat[s]), (lon[e], lat[e])
res = {r["code"]: r for r in json.load(open(os.path.join(ll.WORK, "_raw_results.json")))}
r = res[k]; rng = np.random.default_rng(11)
starts = [pole_of(r["lon1"], r["lat1"], r["lon2"], r["lat2"])]
best = None
for p0, m0 in starts + [(None, None)] * 0:
    p, m = p0, m0; bl, bm, e1, e2 = score(p, m); print("start", round(bl), flush=True)
    for sig in (1.0, 0.4, 0.15, 0.05, 0.015):
        for it in range(10):
            C = p + np.radians(sig) * rng.standard_normal((48, 3)); C /= np.linalg.norm(C, axis=1)[:, None]
            M = bm + np.radians(sig) * rng.standard_normal((48, 3)); M /= np.linalg.norm(M, axis=1)[:, None]
            for c, mm in zip(C, M):
                L, m2, a, b = score(c, mm)
                if L > bl: p, bl, bm, e1, e2 = c, L, m2, a, b
        print(" sigma", sig, round(bl), flush=True)
    if best is None or bl > best[0]: best = (bl, e1, e2)
bl, e1, e2 = best
v = V.validate(k, e1[0], e1[1], e2[0], e2[1]); t = v["trimmed"]
print("raster", round(bl), "vector-validated", round(t["km"], 1), "pct", round(t["pct_inside"], 2), t["lat1"], t["lon1"], t["lat2"], t["lon2"], [ (g["km"], g["what"]) for g in v["all_gaps"]], flush=True)
json.dump(v, open(os.path.join(ll.WORK, f"refine_raster_{k}.json"), "w"), indent=1, default=float)
