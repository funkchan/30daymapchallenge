"""Fetch geometries for (source, src_id) pairs and cache them in data/cand_geoms.gpkg."""
import os, pandas as pd, geopandas as gpd, pyogrio, shapely
from common import DATA, D3
F = os.path.join(DATA, "cand_geoms.gpkg")
def fetch(pairs):
    pairs = set(pairs); have = gpd.read_file(F) if os.path.exists(F) else gpd.GeoDataFrame(columns=["source", "src_id", "geometry"], geometry="geometry", crs=4326)
    need = pairs - set(zip(have.source, have.src_id)); out = []
    by = {}
    for s, i in need: by.setdefault(s, []).append(i)
    if "Natural Earth 10m admin-1" in by:
        a1 = gpd.read_file(os.path.join(D3, "ne_10m_admin_1_states_provinces.shp"), columns=["adm1_code"]); a1 = a1[a1.adm1_code.isin(by["Natural Earth 10m admin-1"])]
        out += [("Natural Earth 10m admin-1", r.adm1_code, r.geometry) for _, r in a1.iterrows()]
    k = "Natural Earth 10m land, named by geography_regions_polys"
    if k in by:
        isl = gpd.read_file(os.path.join(DATA, "islands.gpkg")); isl = isl[isl.sid.isin(by[k])]
        out += [(k, r.sid, r.geometry) for _, r in isl.iterrows()]
    k = "geoBoundaries CGAZ ADM2"
    if k in by:
        ids = by[k]
        for j in range(0, len(ids), 300):
            q = "shapeID IN (" + ",".join("'" + x.replace("'", "''") + "'" for x in ids[j:j + 300]) + ")"
            g = pyogrio.read_dataframe(os.path.join(DATA, "geoBoundariesCGAZ_ADM2.gpkg"), where=q, columns=["shapeID"])
            out += [(k, r.shapeID, r.geometry) for _, r in g.iterrows()]
    if out:
        new = gpd.GeoDataFrame([dict(source=a, src_id=b) for a, b, _ in out], geometry=[c for _, _, c in out], crs=4326)
        have = pd.concat([have, new], ignore_index=True); gpd.GeoDataFrame(have, geometry="geometry", crs=4326).to_file(F)
    return {(r.source, r.src_id): r.geometry for _, r in have.iterrows()}
