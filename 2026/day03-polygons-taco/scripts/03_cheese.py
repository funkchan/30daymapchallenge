#!/usr/bin/env python3
"""Shredded cheese: bundles of long, thin, parallel islands. Built from Natural Earth 10m land parts, grouped by proximity,
named after the NE admin-1 unit they fall in. Also scores whole multipart admin units on the same criteria."""
import os, numpy as np, pandas as pd, geopandas as gpd, shapely
from common import DATA, D3, local, mrr_aspect, parts
EQ = "EPSG:8857"
land = gpd.read_file(os.path.join(D3, "ne_10m_land.shp")).explode(index_parts=False).reset_index(drop=True)
land["km2"] = land.to_crs(EQ).area / 1e6
isl = land[(land.km2 >= 3) & (land.km2 <= 20000)].copy()
asp, ori = [], []
for g in isl.geometry:
    a, r, o = mrr_aspect(local(g)); asp.append(a); ori.append(o)
isl["aspect"], isl["orient"] = asp, ori
lng = isl[isl.aspect >= 3.0].copy().reset_index(drop=True)
# group long islands lying within 12 km of each other
b = gpd.GeoSeries(lng.to_crs(EQ).geometry.buffer(6000), crs=EQ)
groups = gpd.GeoDataFrame(geometry=list(shapely.union_all(b.values).geoms) if shapely.union_all(b.values).geom_type == "MultiPolygon" else [shapely.union_all(b.values)], crs=EQ)
lng_eq = lng.to_crs(EQ); lng["grp"] = gpd.sjoin(lng_eq[["geometry"]], groups, predicate="within").index_right.reindex(lng.index).values
a1 = gpd.read_file(os.path.join(D3, "ne_10m_admin_1_states_provinces.shp"), columns=["adm1_code", "name", "admin"])
rows = []
for gid, g in lng.groupby("grp"):
    if len(g) < 3: continue
    th = np.radians(g.orient.values) * 2; w = g.km2.values
    R = np.hypot((w * np.cos(th)).sum(), (w * np.sin(th)).sum()) / w.sum()
    std = np.degrees(np.sqrt(-2 * np.log(max(R, 1e-9))) / 2)
    geom = shapely.union_all(g.geometry.values)
    rp = geom.representative_point(); hit = a1[a1.contains(rp)]
    if hit.empty: hit = a1.iloc[[a1.distance(rp).idxmin()]]
    rows.append(dict(source="Natural Earth 10m land (island bundle)", admin_level="island group (constructed)",
                     src_id=f"NE-land-bundle-{int(gid)}", name=f"{hit.iloc[0]['name']} islands", country=hit.iloc[0].admin,
                     n_strips=len(g), mean_aspect=float(np.average(g.aspect, weights=w)), orient_std=std, area_km2=float(w.sum()),
                     licence="public domain", wkt=geom.wkt))
df = pd.DataFrame(rows)
df["score"] = (np.clip(df.n_strips, 3, 8) / 8) * np.clip(df.mean_aspect / 6, 0, 1) * np.clip(1 - df.orient_std / 30, 0, 1)
df = df.sort_values("score", ascending=False); df.to_csv(os.path.join(DATA, "cheese_bundles.csv"), index=False)
pd.set_option("display.width", 250)
print(df.head(20).drop(columns="wkt").to_string())
