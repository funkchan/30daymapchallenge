#!/usr/bin/env python3
"""Search real polygons for a closed half-dome (flat edge down) taco-shell silhouette. Discriminative score:
IoU vs half-ellipse (aspect 1.6-2.2) minus best IoU vs rectangles/full ellipses, plus base-straightness and arc-convexity tests."""
import os, sys, numpy as np, pandas as pd, geopandas as gpd, pyogrio, shapely
from shapely import affinity
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); TACO = os.path.dirname(HERE); sys.path.insert(0, TACO)
from common import DATA, D3, local, parts, norm, mrr_aspect
SD = os.path.join(HERE, "data")
ASP = (1.6, 1.8, 2.0, 2.2)
def half_ellipse(A):  # width/height = A, flat side down
    t = np.linspace(0, np.pi, 181); return norm(shapely.Polygon(np.c_[A / 2 * np.cos(t), np.sin(t)]))
HE = {A: half_ellipse(A) for A in ASP}
ANG = np.arange(0, 360, 5)
HER = {A: np.array([affinity.rotate(t, a, origin=(0, 0)) for a in ANG]) for A, t in HE.items()}
DA = np.arange(1.0, 3.01, 0.25)
DEC = np.array([affinity.rotate(norm(g), a, origin=(0, 0)) for A in DA for g in (shapely.box(-A, -1, A, 1), affinity.scale(shapely.Point(0, 0).buffer(1, 64), A, 1)) for a in range(0, 180, 5)])

def iou(arr, m):
    i = shapely.area(shapely.intersection(arr, m)); return i / (2 - i)

def chains(m):
    """split exterior at min-x and max-x points; return (lower, upper) chains, each left->right"""
    xy = np.asarray(m.exterior.coords)[:-1]; i0, i1 = int(xy[:, 0].argmin()), int(xy[:, 0].argmax())
    r = np.roll(xy, -i0, axis=0); k = (i1 - i0) % len(xy)
    a, b = r[:k + 1], np.vstack([r[k:], r[:1]])[::-1]
    return (a, b) if a[:, 1].mean() < b[:, 1].mean() else (b, a)

def resample(c, n):
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(c, axis=0), axis=1))]; s = np.linspace(0, d[-1], n)
    return np.c_[np.interp(s, d, c[:, 0]), np.interp(s, d, c[:, 1])]

def score(m):
    best = (0, None, None)
    for A, arr in HER.items():
        v = iou(arr, m); j = int(v.argmax())
        if v[j] > best[0]: best = (float(v[j]), A, int(ANG[j]))
    v0, A, a0 = best; fine = np.arange(a0 - 4, a0 + 5); arr = np.array([affinity.rotate(HE[A], a, origin=(0, 0)) for a in fine])
    v = iou(arr, m); j = int(v.argmax()); dome, ang = float(v[j]), int(fine[j]) % 360
    dec = float(iou(DEC, m).max())
    u = affinity.rotate(m, -ang, origin=(0, 0))  # into template frame: flat side down
    lo, up = chains(u); p0, p1 = lo[0], lo[-1]; ch = p1 - p0; L = np.linalg.norm(ch); nrm = np.array([-ch[1], ch[0]]) / L
    base_dev = float(np.abs((lo - p0) @ nrm).max() / L); tilt = float(np.degrees(np.arctan2(ch[1], ch[0])))
    h = float(((up - p0) @ nrm).max()); hr = L / max(h, 1e-9)
    arcp = shapely.Polygon(np.vstack([up, up[:1]])).buffer(0); arc_conv = float(arcp.area / arcp.convex_hull.area) if arcp.area > 0 else 0
    rs = resample(up, 60); d = np.diff(rs, axis=0); th = np.unwrap(np.arctan2(d[:, 1], d[:, 0])); tr = np.diff(th)
    mono = float(abs(tr.sum()) / max(np.abs(tr).sum(), 1e-9))
    rough = float(np.linalg.norm(np.diff(up, axis=0), axis=1).sum() / np.linalg.norm(np.diff(resample(up, 40), axis=0), axis=1).sum())
    s = dome + (dome - dec) - 3 * max(0, base_dev - 0.03) - 0.5 * (1 - arc_conv) - 0.3 * (1 - mono) - 0.2 * max(0, rough - 1.15)
    return dict(iou_dome=dome, aspect_tmpl=A, iou_decoy=dec, margin=dome - dec, base_dev=base_dev, base_len_frac=float(L),
                width_height=hr, arc_convexity=arc_conv, arc_monotone=mono, arc_rough=rough, rot_tmpl=ang,
                rot_ccw=(-(ang + tilt)) % 360, score=s)

def prep(g_ll):
    g = local(g_ll).buffer(0)
    if g.is_empty or g.area <= 0: return None
    ps = [p for p in parts(g) if p.geom_type == "Polygon"]; m = max(ps, key=lambda p: p.area); share = m.area / g.area
    if share < 0.9: return None
    m = shapely.Polygon(m.exterior); mn = norm(m).simplify(0.004)
    sol = mn.area / mn.convex_hull.area; asp, rect, _ = mrr_aspect(mn)
    if sol < 0.86 or not (1.3 <= asp <= 2.7) or not (0.62 <= rect <= 0.93): return None
    return mn, g.area / 1e6, share, sol, asp, rect

def job(rows):
    out = []
    for meta, wkb in rows:
        try:
            p = prep(shapely.from_wkb(wkb))
            if p is None: continue
            mn, ar, sh, sol, asp, rect = p; d = score(mn)
            if d["iou_dome"] < 0.80: continue
            out.append({**meta, "area_km2": ar, "main_share": sh, "solidity": sol, "mrr_aspect": asp, "rectangularity": rect, **d, "wkb": shapely.to_wkb(mn)})
        except Exception as e:
            pass
    return out

def ch(rows, n=150): return [rows[i:i + n] for i in range(0, len(rows), n)]
def rows_of(gdf, src, lvl, idc, namec, ctry, lic):
    return [(dict(source=src, admin_level=lvl, src_id=str(r[idc]), name=r[namec], country=(r[ctry] if ctry in gdf else ctry), licence=lic), shapely.to_wkb(r.geometry))
            for _, r in gdf.iterrows() if r.geometry is not None and not r.geometry.is_empty]

def main():
    R = []
    pool = pd.read_csv(os.path.join(DATA, "pool.csv"), low_memory=False)
    keep = pool.query("main_share>=0.9 and solidity>=0.8 and 1.25<=aspect<=2.9 and area_km2>=1")
    keys = set(zip(keep.source, keep.src_id)); meta = {(r.source, r.src_id): r for r in keep.itertuples()}
    sys.path.insert(0, TACO); from importlib import import_module; M = import_module("02_match"); G = M.load_geoms(keys)
    for k, w in G.items():
        r = meta[k]; R.append((dict(source=k[0], admin_level=r.admin_level, src_id=k[1], name=r.name, country=r.country, licence=r.licence), w))
    print("pool rows", len(R), flush=True)
    a0 = gpd.read_file(os.path.join(D3, "ne_10m_admin_0_countries.shp"), columns=["ADM0_A3", "NAME", "SOVEREIGNT"])
    R += rows_of(a0, "Natural Earth 10m admin-0", "country", "ADM0_A3", "NAME", "SOVEREIGNT", "public domain")
    mi = gpd.read_file(os.path.join(DATA, "ne_10m_minor_islands.shp")).reset_index(); mi["nm"] = "minor island #" + mi["index"].astype(str)
    R += rows_of(mi, "Natural Earth 10m minor islands", "island", "index", "nm", "(unnamed)", "public domain")
    for f, lic in (("ne_10m_lakes", "public domain"), ("ne_10m_lakes_north_america", "public domain"), ("ne_10m_lakes_europe", "public domain")):
        lk = gpd.read_file(os.path.join(SD, f + ".shp")).reset_index(); lk["nm"] = lk["name"].fillna("(unnamed)") + " [" + lk["featurecla"].fillna("") + "]"
        lk["idx"] = f + ":" + lk["index"].astype(str)
        R += rows_of(lk, "Natural Earth 10m " + f[7:].replace("_", " "), "lake / reservoir", "idx", "nm", "(lake)", lic)
    co = gpd.read_file(os.path.join(SD, "cb_2023_us_county_500k.shp")).to_crs(4326); co["nm"] = co.NAMELSAD + ", " + co.STATE_NAME
    R += rows_of(co, "US Census cartographic boundary 2023 counties 1:500k", "county", "GEOID", "nm", "United States", "public domain (US Census)")
    pl = gpd.read_file(os.path.join(SD, "cb_2023_us_place_500k.shp")).to_crs(4326); pl["nm"] = pl.NAMELSAD + ", " + pl.STATE_NAME
    R += rows_of(pl, "US Census cartographic boundary 2023 places 1:500k", "place", "GEOID", "nm", "United States", "public domain (US Census)")
    print("total rows", len(R), flush=True)
    with Pool(7) as p:
        res = [x for part in p.imap_unordered(job, ch(R), chunksize=1) for x in part]
    df = pd.DataFrame(res).sort_values("score", ascending=False); df.to_pickle(os.path.join(HERE, "dome_scored.pkl"))
    pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 40)
    print(len(df)); print(df.head(40)[["name", "country", "source", "area_km2", "iou_dome", "iou_decoy", "margin", "base_dev", "arc_convexity", "arc_monotone", "width_height", "score"]].to_string())

if __name__ == "__main__":
    main()
