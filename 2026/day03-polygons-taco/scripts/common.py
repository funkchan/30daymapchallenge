"""Shared helpers for the Taco Tuesday candidate search (Day 3, #30DayMapChallenge 2026)."""
import os, numpy as np, shapely
from shapely import affinity
from pyproj import Transformer, Geod
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, "data")
D3 = os.path.join(os.path.dirname(HERE), "day03-polygons-shapes", "data")  # NE admin-1 / land / CGAZ ADM1 from Day 3
GEOD = Geod(ellps="WGS84")

def local(g):
    """Project lon/lat geometry to a Lambert azimuthal equal-area centred on it (true shape, metres)."""
    c = g.representative_point()
    t = Transformer.from_crs(4326, f"+proj=laea +lat_0={c.y:.5f} +lon_0={c.x:.5f} +datum=WGS84 +units=m", always_xy=True)
    return shapely.transform(g, lambda xy: np.column_stack(t.transform(xy[:, 0], xy[:, 1])))

def parts(g):
    return list(g.geoms) if g.geom_type in ("MultiPolygon", "GeometryCollection") else [g]

def norm(g):
    """Centre on centroid, scale to unit area."""
    c = g.centroid; g = affinity.translate(g, -c.x, -c.y); s = 1 / np.sqrt(g.area)
    return affinity.scale(g, s, s, origin=(0, 0))

def mrr_aspect(p):
    r = shapely.minimum_rotated_rectangle(p)
    xy = np.asarray(r.exterior.coords)[:4]; e = np.linalg.norm(np.diff(np.vstack([xy, xy[:1]]), axis=0), axis=1)
    a, b = max(e[0], e[1]), max(min(e[0], e[1]), 1e-9)
    d = xy[1] - xy[0] if e[0] >= e[1] else xy[2] - xy[1]
    return a / b, p.area / max(r.area, 1e-12), np.degrees(np.arctan2(d[1], d[0])) % 180

def descriptors(g_ll):
    """Cheap shape descriptors on the true-shape (local equal-area) geometry."""
    g = local(g_ll).buffer(0)
    if g.is_empty or g.area <= 0: return None
    tot = g.area; ps = sorted(parts(g), key=lambda p: -p.area)
    ps = [p for p in ps if p.geom_type == "Polygon"]
    big = [p for p in ps if p.area >= 0.005 * tot]
    m = ps[0]; s = 1 / np.sqrt(m.area); mn = affinity.scale(m, s, s, origin=(0, 0))
    asp, rect, _ = mrr_aspect(mn)
    fine, coarse = mn.simplify(0.002), mn.simplify(0.05)
    d = dict(area_km2=tot / 1e6, n_parts=len(big), main_share=m.area / tot, solidity=mn.area / mn.convex_hull.area,
             aspect=asp, rectangularity=rect, pp=4 * np.pi * mn.area / mn.length ** 2,
             rough=fine.length / max(coarse.length, 1e-9), n_holes=len(m.interiors))
    # multipart descriptors (parts >= 2% of total area)
    sig = [p for p in ps if p.area >= 0.02 * tot]
    if len(sig) >= 2:
        pa = [mrr_aspect(p) for p in sig]; ar = np.array([p.area for p in sig])
        long_ = [(a, o, ar_) for (a, r_, o), ar_ in zip(pa, ar) if a >= 3.5]
        d["n_sig"] = len(sig); d["n_long"] = len(long_); d["long_share"] = sum(x[2] for x in long_) / tot
        if len(long_) >= 2:
            th = np.radians([x[1] for x in long_]) * 2; R = np.hypot(np.cos(th).mean(), np.sin(th).mean())
            d["long_orient_std"] = np.degrees(np.sqrt(-2 * np.log(max(R, 1e-9))) / 2)
        cubes = [ar_ for (a, r_, o), ar_ in zip(pa, ar) if a <= 1.5 and r_ >= 0.8]
        d["n_cube"] = len(cubes); d["cube_share"] = sum(cubes) / tot
        d["size_cv"] = ar.std() / ar.mean()
    return d
