#!/usr/bin/env python3
"""Export results/final_lines.json as results/final_lines.geojson: each line is the WGS84 geodesic
between the final endpoints, densified every ~10 km (pyproj Geod). Usage: python scripts/export_geojson.py"""
import json, os
from pyproj import Geod
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
G = Geod(ellps="WGS84")
feats = []
for o in json.load(open(os.path.join(RES, "final_lines.json"))):
    d = G.inv(o["lon1"], o["lat1"], o["lon2"], o["lat2"])[2]
    pts = [(o["lon1"], o["lat1"])] + G.npts(o["lon1"], o["lat1"], o["lon2"], o["lat2"], max(1, int(d / 10000))) + [(o["lon2"], o["lat2"])]
    props = {k: o[k] for k in ("code", "biome", "km", "lon1", "lat1", "lon2", "lat2", "pct_inside", "bridged_km", "country_sequence", "source")}
    props["km"] = round(props["km"], 1)
    feats.append({"type": "Feature", "properties": props,
                  "geometry": {"type": "LineString", "coordinates": [[round(x, 5), round(y, 5)] for x, y in pts]}})
json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(RES, "final_lines.geojson"), "w"))
print(len(feats), "lines ->", os.path.join(RES, "final_lines.geojson"))
