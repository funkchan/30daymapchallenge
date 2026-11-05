#!/usr/bin/env python3
"""Build the candidate pool with cheap shape descriptors: NE admin-1, geoBoundaries CGAZ ADM2, NE named islands/island groups."""
import os, sys, numpy as np, pandas as pd, geopandas as gpd, pyogrio, shapely
from multiprocessing import Pool
from common import DATA, D3, descriptors

def run(rows):
    out = []
    for meta, wkb in rows:
        try:
            d = descriptors(shapely.from_wkb(wkb))
        except Exception as e:
            d = None
        if d: out.append({**meta, **d})
    return out

def chunks(gdf, src, lvl, idcol, namecol, ctrycol, lic, n=400):
    rows = [(dict(source=src, admin_level=lvl, src_id=r[idcol], name=r[namecol], country=r[ctrycol], licence=lic), shapely.to_wkb(r.geometry))
            for _, r in gdf.iterrows() if r.geometry is not None]
    return [rows[i:i + n] for i in range(0, len(rows), n)]

def main():
    jobs = []
    a1 = gpd.read_file(os.path.join(D3, "ne_10m_admin_1_states_provinces.shp"), columns=["adm1_code", "name", "admin", "adm0_a3"])
    a1 = a1[a1.adm0_a3 != "ATA"]
    jobs += chunks(a1, "Natural Earth 10m admin-1", "admin-1", "adm1_code", "name", "admin", "public domain")
    # named islands and island groups: detailed NE land parts under each NE region polygon
    rg = gpd.read_file(os.path.join(DATA, "ne_10m_geography_regions_polys.shp"), columns=["FEATURECLA", "NAME", "NAME_EN", "REGION", "SUBREGION"])
    rg = rg[rg.FEATURECLA.isin(["Island", "Island group"])].reset_index(drop=True)
    land = gpd.read_file(os.path.join(D3, "ne_10m_land.shp")).explode(index_parts=False).reset_index(drop=True)
    land = land[land.geometry.area < 5000]  # drop continental masses (deg²), keep islands
    sidx = land.sindex; geoms = []
    for _, r in rg.iterrows():
        hit = land.iloc[sidx.query(r.geometry, predicate="intersects")]
        hit = hit[hit.geometry.intersection(r.geometry).area > 0.5 * hit.geometry.area] if len(hit) else hit
        geoms.append(shapely.union_all(hit.geometry.values) if len(hit) else None)
    rg["geometry"] = geoms; rg = rg[rg.geometry.notna()]
    rg["sid"] = ["NE-isl-" + str(i) for i in rg.index]; rg["ctry"] = rg.SUBREGION.fillna(rg.REGION)
    rg["NAME"] = rg.NAME_EN.fillna(rg.NAME)
    jobs += chunks(rg, "Natural Earth 10m land, named by geography_regions_polys", "island / island group", "sid", "NAME", "ctry", "public domain")
    n = pyogrio.read_info(os.path.join(DATA, "geoBoundariesCGAZ_ADM2.gpkg"))["features"]
    for s in range(0, n, 4000):
        g = pyogrio.read_dataframe(os.path.join(DATA, "geoBoundariesCGAZ_ADM2.gpkg"), skip_features=s, max_features=4000)
        g = g.set_crs(4326, allow_override=True)
        jobs += chunks(g, "geoBoundaries CGAZ ADM2", "ADM2", "shapeID", "shapeName", "shapeGroup", "CC BY 4.0 (geoBoundaries)")
        del g
    print(len(jobs), "chunks", flush=True)
    with Pool(6) as p:
        res = [x for part in p.imap_unordered(run, jobs, chunksize=1) for x in part]
    df = pd.DataFrame(res); df.to_csv(os.path.join(DATA, "pool.csv"), index=False); print(df.shape); print(df.groupby("source").size())

if __name__ == "__main__":
    main()
