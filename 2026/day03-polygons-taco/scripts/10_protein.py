#!/usr/bin/env python3
"""Multi-piece protein: (a) ground beef = tight clump of many small irregular islands; (b) chicken = several elongated
slices/shreds (orientation free, unlike the cheese's parallel strips). Natural Earth 10m land + minor islands (public domain),
grouped by proximity, named after the NE admin-1 unit. Reuses common.py helpers and the 03_cheese.py grouping approach."""
import os, numpy as np, pandas as pd, geopandas as gpd, shapely
from common import DATA, D3, local, mrr_aspect, parts
EQ = "EPSG:8857"
land = pd.concat([gpd.read_file(os.path.join(D3, "ne_10m_land.shp"))[["geometry"]],
                  gpd.read_file(os.path.join(DATA, "ne_10m_minor_islands.shp"))[["geometry"]]]).explode(index_parts=False).reset_index(drop=True)
land = gpd.GeoDataFrame(land, geometry="geometry", crs=4326)
land["km2"] = land.to_crs(EQ).area / 1e6
isl = land[(land.km2 >= 0.05) & (land.km2 <= 3000)].copy().reset_index(drop=True)
A, SOL, ORI = [], [], []
for g in isl.geometry:
    l = local(g).buffer(0); a, r, o = mrr_aspect(l); A.append(a); ORI.append(o); SOL.append(l.area / l.convex_hull.area)
isl["aspect"], isl["solidity"], isl["orient"] = A, SOL, ORI
a1 = gpd.read_file(os.path.join(D3, "ne_10m_admin_1_states_provinces.shp"), columns=["adm1_code", "name", "admin"])
isl_eq = isl.to_crs(EQ)
def groups(sub, buf):
    u = shapely.union_all(gpd.GeoSeries(isl_eq.loc[sub.index].geometry.buffer(buf)).values)
    G = gpd.GeoDataFrame(geometry=list(u.geoms) if u.geom_type == "MultiPolygon" else [u], crs=EQ)
    j = gpd.sjoin(isl_eq.loc[sub.index, ["geometry"]], G, predicate="within")
    return j.index_right
def name_of(geom):
    rp = geom.representative_point(); hit = a1[a1.contains(rp)]
    if hit.empty: hit = a1.iloc[[a1.distance(rp).idxmin()]]
    return hit.iloc[0]["name"], hit.iloc[0].admin
rows = []
# ---- ground beef: pieces up to 400 km2, clustered within 2*buf
beef = isl[isl.km2 <= 400]
for buf in (2500, 5000):
    gi = groups(beef, buf)
    for gid, idx in gi.groupby(gi).groups.items():
        g = beef.loc[idx]; w = g.km2.values
        if len(g) < 8: continue
        geom = shapely.union_all(g.geometry.values); L = local(geom).buffer(0); hull = L.convex_hull
        n_eff = w.sum() ** 2 / (w ** 2).sum()                     # effective number of similar-size pieces
        hull_pp = 4 * np.pi * hull.area / hull.length ** 2         # cluster footprint roundness
        density = L.area / hull.area                               # how tightly packed
        irreg = 1 - np.average(g.solidity, weights=w)
        nm, ad = name_of(geom)
        score = np.clip(n_eff / 12, 0, 1) * hull_pp * np.clip(density / 0.35, 0, 1) * (0.5 + np.clip(irreg / 0.3, 0, 1) / 2)
        rows.append(dict(kind="ground_beef", buf_km=buf / 1000, name=f"{nm} islands", country=ad, n_pieces=len(g), n_eff=n_eff,
                         hull_pp=hull_pp, density=density, irregularity=irreg, max_share=w.max() / w.sum(), area_km2=w.sum(),
                         hull_km2=hull.area / 1e6, score=score, wkt=geom.wkt))
# ---- chicken: elongated pieces (aspect>=2.3), any orientation, 3..3000 km2
ch = isl[(isl.aspect >= 2.3) & (isl.km2 >= 0.3)]
for buf in (4000, 10000):
    gi = groups(ch, buf)
    for gid, idx in gi.groupby(gi).groups.items():
        g = ch.loc[idx]; w = g.km2.values
        if len(g) < 4: continue
        geom = shapely.union_all(g.geometry.values); L = local(geom).buffer(0); hull = L.convex_hull
        n_eff = w.sum() ** 2 / (w ** 2).sum(); asp = np.average(g.aspect, weights=w)
        th = np.radians(g.orient.values) * 2; R = np.hypot((w * np.cos(th)).sum(), (w * np.sin(th)).sum()) / w.sum()
        ostd = np.degrees(np.sqrt(-2 * np.log(max(R, 1e-9))) / 2)
        hull_pp = 4 * np.pi * hull.area / hull.length ** 2; density = L.area / hull.area
        nm, ad = name_of(geom)
        score = np.clip(n_eff / 6, 0, 1) * np.clip((asp - 1.5) / 4, 0, 1) * np.clip(hull_pp / 0.5, 0, 1) * np.clip(density / 0.2, 0, 1)
        rows.append(dict(kind="chicken", buf_km=buf / 1000, name=f"{nm} islands", country=ad, n_pieces=len(g), n_eff=n_eff,
                         mean_aspect=asp, orient_std=ostd, hull_pp=hull_pp, density=density, max_share=w.max() / w.sum(),
                         area_km2=w.sum(), hull_km2=hull.area / 1e6, score=score, wkt=geom.wkt))
df = pd.DataFrame(rows).sort_values(["kind", "score"], ascending=[True, False])
df.to_csv(os.path.join(DATA, "protein_clusters.csv"), index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
for k in ("ground_beef", "chicken"): print(df[df.kind == k].head(25).drop(columns="wkt").round(3).to_string())
