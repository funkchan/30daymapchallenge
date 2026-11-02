#!/usr/bin/env python3
"""Merge vector validation + refinements into final_lines.json/csv (all lengths = pyproj Geod WGS84 between final endpoints)."""
import json, os, csv
import numpy as np, geopandas as gpd
from shapely.geometry import Point
import validate as V, longest_lines as ll
HERE = ll.HERE
val = json.load(open(os.path.join(ll.RESULTS, "validation.json")))
ref = {5: "refine_raster_5.json", 2: "refine_raster_2.json"}
adm = gpd.read_file(os.path.join(ll.DATA, "ne_10m_admin_0_countries.shp"))[["NAME_EN", "geometry"]]
out = []
for k, (name, *_ ) in ll.GROUPS.items():
    v = val[name]; src = "vector-trimmed"
    if k in ref:
        r = json.load(open(os.path.join(ll.WORK, ref[k])))
        if r["trimmed"]["km"] > v["trimmed"]["km"]: v = r; src = "refined (0.01 deg vector raster hill-climb)"
    # re-validate the final endpoints themselves
    t = v["trimmed"]; f = V.validate(k, t["lon1"], t["lat1"], t["lon2"], t["lat2"]); ft = f["trimmed"]
    gl, _ = V.densify(ft["lon1"], ft["lat1"], ft["lon2"], ft["lat2"], 5000)
    j = gpd.sjoin(gpd.GeoDataFrame(geometry=[Point(x, y) for x, y in gl], crs=4326), adm, how="left", predicate="within")
    seq = []
    for nm in j.sort_index()["NAME_EN"].fillna("(sea/none)"):
        if not seq or seq[-1] != nm: seq.append(nm)
    out.append(dict(code=k, biome=name, source=src, km=ft["km"], lon1=ft["lon1"], lat1=ft["lat1"], lon2=ft["lon2"], lat2=ft["lat2"],
                    pct_inside=ft["pct_inside"], bridged_km=ft["bridged_km"], bridged=[(g["km"], g["lat"], g["lon"], list(g["what"])) for g in ft["bridged"]],
                    feasibility_km=val[name]["orig_km"], feasibility_pct_inside=val[name]["pct_inside_orig"], country_sequence=" > ".join(seq)))
    o = out[-1]; print(f'{name:26s} {o["km"]:8.1f} km  {o["pct_inside"]:.2f}% in, bridged {o["bridged_km"]} km  ({o["lat1"]:.3f},{o["lon1"]:.3f})->({o["lat2"]:.3f},{o["lon2"]:.3f})  [{src}]  {o["country_sequence"]}')
json.dump(out, open(os.path.join(ll.RESULTS, "final_lines.json"), "w"), indent=1, default=float)
with open(os.path.join(ll.RESULTS, "final_lines.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["biome", "km", "lat1", "lon1", "lat2", "lon2", "pct_inside", "bridged_km", "country_sequence", "source"], extrasaction="ignore")
    w.writeheader(); [w.writerow({**o, "km": round(o["km"], 1)}) for o in out]
