#!/usr/bin/env python3
"""Coarse feasibility test: longest great-circle segment that stays inside each biome.

Data (place in ./data, all relative paths):
  RESOLVE Ecoregions 2017 (CC BY 4.0): https://storage.googleapis.com/teow2016/Ecoregions2017.zip
  Natural Earth 10m admin-0 countries (public domain): https://naciscdn.org/naturalearth/10m/cultural/ne_10m_admin_0_countries.zip

Method
  1. Rasterize ecoregions once to a 0.05 deg grid, coded by biome group.
  2. Per biome: gaps exactly 1 fine cell wide (0.05 deg, <=5.5 km) are bridged
     (narrow rivers, lakes, digitising slivers). Coarse 0.25 deg mask = >=50% of fine cells.
  3. Coarse search: N great circles (poles on a Fibonacci hemisphere), walked at fixed step;
     longest cyclic run inside the biome.
  4. Refine top distinct candidates by hill-climbing the pole on the fine mask (~2 km step).
  5. Final: ellipsoidal geodesic between endpoints (pyproj Geod, WGS84), re-checked at 1 km.
Usage: python longest_lines.py [--poles 40000]
"""
import argparse, json, os
import numpy as np
from scipy import ndimage
from pyproj import Geod, Transformer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RESULTS = os.path.join(ROOT, "results")
WORK = os.path.join(ROOT, "work")  # intermediates, not committed
os.makedirs(RESULTS, exist_ok=True); os.makedirs(WORK, exist_ok=True)
DATA = os.path.join(ROOT, "data")
R = 6371.0088
FINE = 0.05
COARSE = 0.25
GEOD = Geod(ellps="WGS84")

# biome group code -> (label, RESOLVE BIOME_NUM list)
GROUPS = {
    1: ("Tropical rainforest", [1]),
    2: ("Boreal forest / taiga", [6]),
    3: ("Temperate forest", [4, 5]),
    4: ("Desert & xeric shrubland", [13]),
    5: ("Grassland & savanna", [7, 8]),
    6: ("Tundra", [11], "Tundra"),
    7: ("Ice sheet (Rock & Ice)", [11], "N/A"),
}


def build_fine_raster():
    cache = os.path.join(DATA, "biome_codes_005.npy")
    if os.path.exists(cache):
        return np.load(cache)
    import pyogrio
    from rasterio import features
    from rasterio.transform import from_origin
    df = pyogrio.read_dataframe(os.path.join(DATA, "Ecoregions2017.shp"),
                                columns=["BIOME_NUM", "BIOME_NAME"])
    code = np.zeros(len(df), np.uint8)
    for k, g in GROUPS.items():
        m = df.BIOME_NUM.isin(g[1])
        if len(g) > 2:
            m &= df.BIOME_NAME == g[2]
        code[m.values] = k
    df["code"] = code
    df = df[df.code > 0]
    W, H = int(360 / FINE), int(180 / FINE)
    arr = features.rasterize(((geom, c) for geom, c in zip(df.geometry, df.code)),
                             out_shape=(H, W), transform=from_origin(-180, 90, FINE, FINE),
                             fill=0, dtype="uint8")
    np.save(cache, arr)
    return arr


def masks(codes):
    fine, coarse = {}, {}
    f = int(round(COARSE / FINE))
    for k in GROUPS:
        m = codes == k
        # wrap-aware closing: pad in longitude
        # bridge gaps exactly one fine cell wide: a cell is filled if the cells on BOTH
        # sides of it (E-W, N-S or either diagonal) are in the biome (lon wraps)
        E, Wn = np.roll(m, -1, 1), np.roll(m, 1, 1)
        N = np.vstack([m[:1], m[:-1]]); S = np.vstack([m[1:], m[-1:]])
        NE, SW = np.roll(N, -1, 1), np.roll(S, 1, 1)
        NW, SE = np.roll(N, 1, 1), np.roll(S, -1, 1)
        p = m | (E & Wn) | (N & S) | (NE & SW) | (NW & SE)
        fine[k] = p
        H, W = p.shape
        coarse[k] = p.reshape(H // f, f, W // f, f).mean(axis=(1, 3)) >= 0.5
    return fine, coarse


def lookup(mask, res, lat, lon):
    H, W = mask.shape
    i = np.clip(((90 - lat) / res).astype(np.int64), 0, H - 1)
    j = (((lon + 180) / res).astype(np.int64)) % W
    return mask[i, j]


def basis(poles):
    p = poles / np.linalg.norm(poles, axis=-1, keepdims=True)
    a = np.where(np.abs(p[..., 2:3]) < 0.9, np.array([0, 0, 1.0]), np.array([1.0, 0, 0]))
    u = np.cross(p, a); u /= np.linalg.norm(u, axis=-1, keepdims=True)
    v = np.cross(p, u)
    return u, v


def circle_pts(poles, n):
    u, v = basis(poles)
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    xyz = np.cos(t)[None, :, None] * u[:, None, :] + np.sin(t)[None, :, None] * v[:, None, :]
    lat = np.degrees(np.arcsin(np.clip(xyz[..., 2], -1, 1)))
    lon = np.degrees(np.arctan2(xyz[..., 1], xyz[..., 0]))
    return lat, lon, t


def longest_runs(inside):
    """Longest cyclic run of True per row. Returns (length, start_idx)."""
    n = inside.shape[1]
    x = np.concatenate([inside, inside], axis=1)
    c = np.cumsum(x, axis=1)
    last = np.maximum.accumulate(np.where(~x, c, 0), axis=1)
    run = c - last
    L = run.max(axis=1)
    end = run.argmax(axis=1)
    L = np.minimum(L, n)
    start = (end - L + 1) % n
    return L, start


def fib_hemisphere(N):
    i = np.arange(N) + 0.5
    z = i / N  # z in (0,1): upper hemisphere poles cover every great circle once
    phi = np.pi * (1 + 5 ** 0.5) * i
    r = np.sqrt(1 - z * z)
    return np.stack([r * np.cos(phi), r * np.sin(phi), z], axis=1)


def coarse_search(coarse, N, step_deg=0.1, chunk=500):
    n = int(round(360 / step_deg))
    poles = fib_hemisphere(N)
    res = {k: [] for k in coarse}
    for s in range(0, N, chunk):
        P = poles[s:s + chunk]
        lat, lon, _ = circle_pts(P, n)
        for k, m in coarse.items():
            L, st = longest_runs(lookup(m, COARSE, lat, lon))
            res[k].append(np.stack([L, st], 1))
    out = {}
    for k in res:
        a = np.concatenate(res[k])
        out[k] = (poles, a[:, 0] * step_deg, a[:, 1] * step_deg)  # length deg, start deg
    return out


def seg_mid(pole, start_deg, len_deg):
    u, v = basis(pole[None])
    t = np.radians(start_deg + len_deg / 2)
    x = np.cos(t) * u[0] + np.sin(t) * v[0]
    return x


def distinct_top(poles, L, st, k=15):
    order = np.argsort(-L)
    chosen = []
    for idx in order:
        if len(chosen) >= k or L[idx] <= 0:
            break
        m = seg_mid(poles[idx], st[idx], L[idx])
        ok = True
        for c in chosen:
            if np.dot(m, c[1]) > np.cos(np.radians(5)) and abs(np.dot(poles[idx], poles[c[0]])) > np.cos(np.radians(5)):
                ok = False; break
        if ok:
            chosen.append((idx, m))
    return [c[0] for c in chosen]


def eval_fine(fine, poles, n):
    lat, lon, _ = circle_pts(poles, n)
    L, st = longest_runs(lookup(fine, FINE, lat, lon))
    return L, st


def refine(fine, pole, rng, n=20000, batch=64):
    best = pole / np.linalg.norm(pole)
    bl, bs = eval_fine(fine, best[None], n)
    bl, bs = bl[0], bs[0]
    for sigma in (0.6, 0.25, 0.08, 0.025):
        for _ in range(8):
            cand = best[None] + np.radians(sigma) * rng.standard_normal((batch, 3))
            cand /= np.linalg.norm(cand, axis=1, keepdims=True)
            L, st = eval_fine(fine, cand, n)
            i = L.argmax()
            if L[i] > bl:
                best, bl, bs = cand[i], L[i], st[i]
    step = 360.0 / n
    return best, bl * step, bs * step


def endpoints(pole, start_deg, len_deg):
    u, v = basis(pole[None])
    out = []
    for t in (start_deg, start_deg + len_deg):
        tr = np.radians(t)
        x = np.cos(tr) * u[0] + np.sin(tr) * v[0]
        out.append((float(np.degrees(np.arctan2(x[1], x[0]))), float(np.degrees(np.arcsin(x[2])))))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--poles", type=int, default=40000)
    ap.add_argument("--top", type=int, default=15)
    a = ap.parse_args()
    rng = np.random.default_rng(42)
    codes = build_fine_raster()
    fine, coarse = masks(codes)
    np.savez_compressed(os.path.join(DATA, "coarse_masks.npz"), **{str(k): v for k, v in coarse.items()})
    cs = coarse_search(coarse, a.poles)
    results = []
    for k, (poles, L, st) in cs.items():
        cands = distinct_top(poles, L, st, a.top)
        best = None
        log = []
        for idx in cands:
            p, l, s = refine(fine[k], poles[idx], rng)
            log.append((round(L[idx] * np.pi / 180 * R), round(l * np.pi / 180 * R)))
            if best is None or l > best[1]:
                best = (p, l, s)
        p, l, s = best
        (lon1, lat1), (lon2, lat2) = endpoints(p, s, l)
        # ellipsoidal geodesic check
        az, baz, dist = GEOD.inv(lon1, lat1, lon2, lat2)
        npt = max(2, int(dist / 1000))
        pts = np.array(GEOD.npts(lon1, lat1, lon2, lat2, npt))
        gl = np.concatenate([[[lon1, lat1]], pts, [[lon2, lat2]]])
        in_closed = lookup(fine[k], FINE, gl[:, 1], gl[:, 0]).mean()
        in_raw = lookup(codes == k, FINE, gl[:, 1], gl[:, 0]).mean()
        results.append(dict(code=k, biome=GROUPS[k][0], sphere_km=l * np.pi / 180 * R,
                            length_km=dist / 1000, lon1=lon1, lat1=lat1, lon2=lon2, lat2=lat2,
                            frac_in_closed=in_closed, frac_in_raw=in_raw,
                            coarse_vs_refined_km=log, coords=gl[::5].tolist() + [gl[-1].tolist()]))
        print(f"{GROUPS[k][0]:28s} {dist/1000:8.0f} km  ({lat1:.2f},{lon1:.2f}) -> ({lat2:.2f},{lon2:.2f})"
              f" in_closed={in_closed:.4f} in_raw={in_raw:.4f}", flush=True)
        print("   coarse->refined km:", log, flush=True)
    with open(os.path.join(WORK, "_raw_results.json"), "w") as f:
        json.dump(results, f)


if __name__ == "__main__":
    main()
