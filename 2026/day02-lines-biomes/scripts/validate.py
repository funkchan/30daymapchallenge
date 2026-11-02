#!/usr/bin/env python3
"""Validate each line against the vector RESOLVE polygons (geodesic densify ~1 km).
Inside = point intersects a polygon of the line's biome group. Only water gaps (no polygon: rivers/lakes/bays) <=5.5 km are bridged; other-biome gaps end the line.
Endpoints are trimmed to the longest bridged run; lengths re-measured with pyproj Geod (WGS84)."""
import json, os, sys
import numpy as np, pyogrio, shapely
from pyproj import Geod
import longest_lines as ll
GEOD = Geod(ellps="WGS84"); MAXGAP = 5.5
df = pyogrio.read_dataframe(os.path.join(ll.DATA, "Ecoregions2017.shp"), columns=["BIOME_NUM", "BIOME_NAME", "ECO_NAME"])
code = np.zeros(len(df), np.uint8)
for k, g in ll.GROUPS.items():
    m = df.BIOME_NUM.isin(g[1])
    if len(g) > 2: m &= df.BIOME_NAME == g[2]
    code[m.values] = k
geoms = df.geometry.values
tree = shapely.STRtree(geoms)

def pole_of(lon1, lat1, lon2, lat2):
    def xyz(lo, la):
        lo, la = np.radians(lo), np.radians(la); return np.array([np.cos(la)*np.cos(lo), np.cos(la)*np.sin(lo), np.sin(la)])
    a, b = xyz(lon1, lat1), xyz(lon2, lat2); p = np.cross(a, b); return p / np.linalg.norm(p), (a + b) / np.linalg.norm(a + b)

def classify(lon, lat):
    pts = shapely.points(lon, lat)
    pi, gi = tree.query(pts, predicate="intersects")
    out = np.zeros(len(pts), np.int16) - 1  # -1 = no polygon (sea/lake)
    names = np.array([""] * len(pts), dtype=object)
    for p, g in zip(pi, gi):
        out[p] = code[g] if out[p] <= 0 else out[p]; names[p] = df.ECO_NAME.iat[g]
    return out, names

def densify(lon1, lat1, lon2, lat2, step=1000.0):
    d = GEOD.inv(lon1, lat1, lon2, lat2)[2]; n = max(2, int(d / step))
    p = np.array(GEOD.npts(lon1, lat1, lon2, lat2, n))
    gl = np.vstack([[lon1, lat1], p, [lon2, lat2]]); return gl, d / (n + 1) / 1000.0  # km per step

def validate(k, lon1, lat1, lon2, lat2):
    gl, ds = densify(lon1, lat1, lon2, lat2)
    c, names = classify(gl[:, 0], gl[:, 1]); ins = c == k
    # runs of outside
    gaps, i = [], 0
    while i < len(ins):
        if not ins[i]:
            j = i
            while j + 1 < len(ins) and not ins[j + 1]: j += 1
            vals, cnt = np.unique(c[i:j+1], return_counts=True)
            gaps.append(dict(i=i, j=j, km=round((j - i + 1) * ds, 1), lat=round(gl[i, 1], 3), lon=round(gl[i, 0], 3),
                             what={("water/none" if v == -1 else "other biome" if v == 0 else ll.GROUPS[int(v)][0]): int(n) for v, n in zip(vals, cnt)},
                             eco=sorted(set(names[i:j+1]) - {""})[:3]))
            i = j + 1
        else: i += 1
    # longest run with gaps <= MAXGAP bridged
    ok = ins.copy()
    for g in gaps:
        if g["km"] <= MAXGAP and set(g["what"]) == {"water/none"} and g["i"] > 0 and g["j"] < len(ins) - 1: ok[g["i"]:g["j"]+1] = True
    best, s = (0, 0, -1), None
    for idx, v in enumerate(list(ok) + [False]):
        if v and s is None: s = idx
        if not v and s is not None:
            if idx - s > best[0]: best = (idx - s, s, idx - 1)
            s = None
    _, a, b = best
    L = GEOD.inv(gl[a, 0], gl[a, 1], gl[b, 0], gl[b, 1])[2] / 1000
    seg = ins[a:b+1]
    return dict(orig_km=GEOD.inv(lon1, lat1, lon2, lat2)[2] / 1000, pct_inside_orig=100 * ins.mean(),
                trimmed=dict(lon1=gl[a, 0], lat1=gl[a, 1], lon2=gl[b, 0], lat2=gl[b, 1], km=L,
                             pct_inside=100 * seg.mean(), bridged_km=round(float((~seg).sum() * ds), 1),
                             bridged=[g for g in gaps if g["i"] >= a and g["j"] <= b]),
                all_gaps=gaps)

if __name__ == "__main__":
    res = json.load(open(os.path.join(ll.WORK, "_raw_results.json")))
    out = {}
    for r in res:
        v = validate(r["code"], r["lon1"], r["lat1"], r["lon2"], r["lat2"])
        out[r["biome"]] = v; t = v["trimmed"]
        print(f'{r["biome"]:26s} orig {v["orig_km"]:7.1f} in {v["pct_inside_orig"]:.2f}% | trimmed {t["km"]:7.1f} in {t["pct_inside"]:.2f}% bridged {t["bridged_km"]} km  ({t["lat1"]:.3f},{t["lon1"]:.3f})->({t["lat2"]:.3f},{t["lon2"]:.3f})', flush=True)
        for g in v["all_gaps"]: print("    gap", g["km"], "km at", g["lat"], g["lon"], g["what"], g["eco"])
    json.dump(out, open(os.path.join(ll.RESULTS, "validation.json"), "w"), indent=1, default=float)
