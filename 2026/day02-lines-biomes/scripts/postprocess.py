#!/usr/bin/env python3
"""Turn _raw_results.json into results.csv, lines.geojson, gap diagnostics and a rough preview PNG."""
import csv, json, os
import numpy as np
import geopandas as gpd
from shapely.geometry import LineString, Point
from pyproj import Geod, Transformer
import longest_lines as ll

HERE = ll.HERE
GEOD = Geod(ellps="WGS84")
COLORS = {1: "#1b9e3a", 2: "#0b5d4b", 3: "#8fbf3a", 4: "#e08a1e", 5: "#d4c13a", 6: "#7a5fb0", 7: "#2c7fb8"}


def runs(b):
    """contiguous False runs -> list of (start, end) indices"""
    out, s = [], None
    for i, v in enumerate(b):
        if not v and s is None: s = i
        if v and s is not None: out.append((s, i - 1)); s = None
    if s is not None: out.append((s, len(b) - 1))
    return out


def main():
    res = json.load(open(os.path.join(ll.WORK, "_raw_results.json")))
    codes = ll.build_fine_raster()
    fine, coarse = ll.masks(codes)
    adm = gpd.read_file(os.path.join(ll.DATA, "ne_10m_admin_0_countries.shp"))[["NAME_EN", "geometry"]]
    rows, feats, diag = [], [], {}
    for r in res:
        k = r["code"]
        az, baz, dist = GEOD.inv(r["lon1"], r["lat1"], r["lon2"], r["lat2"])
        n = int(dist / 1000)
        gl = np.concatenate([[[r["lon1"], r["lat1"]]], GEOD.npts(r["lon1"], r["lat1"], r["lon2"], r["lat2"], n), [[r["lon2"], r["lat2"]]]])
        raw = ll.lookup(codes == k, ll.FINE, gl[:, 1], gl[:, 0])
        clo = ll.lookup(fine[k], ll.FINE, gl[:, 1], gl[:, 0])
        g_raw = [(a, b, b - a + 1) for a, b in runs(raw)]
        g_clo = [(a, b, b - a + 1) for a, b in runs(clo)]
        other = {}
        for a, b, L in g_raw:
            vals = codes[np.clip(((90 - gl[a:b+1, 1]) / ll.FINE).astype(int), 0, 3599), ((gl[a:b+1, 0] + 180) / ll.FINE).astype(int) % 7200]
            for v in vals: other[int(v)] = other.get(int(v), 0) + 1
        diag[r["biome"]] = dict(samples_km=len(gl), raw_out_km=int((~raw).sum()), raw_gaps=len(g_raw),
                                max_raw_gap_km=max([g[2] for g in g_raw], default=0),
                                closed_out_km=int((~clo).sum()), closed_gaps=[(round(float(gl[a,1]),2), round(float(gl[a,0]),2), L) for a, b, L in g_clo],
                                raw_gap_codes_km=other,
                                worst_raw_gaps=[(round(float(gl[a,1]),2), round(float(gl[a,0]),2), L) for a, b, L in sorted(g_raw, key=lambda g: -g[2])[:5]])
        pts = gpd.GeoDataFrame(geometry=[Point(x, y) for x, y in gl[::5]], crs=4326)
        j = gpd.sjoin(pts, adm, how="left", predicate="within")
        seq = []
        for nm in j.sort_index()["NAME_EN"].fillna("(sea/none)"):
            if not seq or seq[-1] != nm: seq.append(nm)
        countries = []
        for nm in seq:
            if nm not in countries and nm != "(sea/none)": countries.append(nm)
        rows.append(dict(biome=r["biome"], length_km=round(dist / 1000), start_lon=round(r["lon1"], 3), start_lat=round(r["lat1"], 3),
                         end_lon=round(r["lon2"], 3), end_lat=round(r["lat2"], 3), countries_crossed="; ".join(countries),
                         country_sequence=" > ".join(seq)))
        feats.append({"type": "Feature", "properties": {**rows[-1], "colour": COLORS[k]},
                      "geometry": {"type": "LineString", "coordinates": [[round(x, 4), round(y, 4)] for x, y in gl[::10]] + [[round(gl[-1][0], 4), round(gl[-1][1], 4)]]}})
    with open(os.path.join(ll.WORK, "results.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(ll.WORK, "lines.geojson"), "w"))
    json.dump(diag, open(os.path.join(ll.WORK, "gap_diagnostics.json"), "w"), indent=1)
    for k, v in diag.items(): print(k, v)
    for r in rows: print(r)
    preview(coarse, feats)


def preview(coarse, feats):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    tf = Transformer.from_crs(4326, "+proj=eqearth", always_xy=True)
    ti = Transformer.from_crs("+proj=eqearth", 4326, always_xy=True)
    W, H = 2400, 1170
    xmax = tf.transform(180, 0)[0]; ymax = tf.transform(0, 90)[1]
    xs = np.linspace(-xmax, xmax, W); ys = np.linspace(ymax, -ymax, H)
    X, Y = np.meshgrid(xs, ys)
    lon, lat = ti.transform(X, Y)
    valid = np.isfinite(lon) & (np.abs(lon) <= 180)
    lon = np.where(valid, lon, 0); lat = np.where(valid, lat, 0)
    img = np.ones((H, W, 3)) * 0.97
    img[~valid] = 1.0
    land = ll.lookup(ll.build_fine_raster() > 0, ll.FINE, lat, lon)
    for k, m in coarse.items():
        c = np.array(matplotlib.colors.to_rgb(COLORS[k]))
        inside = ll.lookup(m, ll.COARSE, lat, lon) & valid
        img[inside] = 0.72 * 1 + 0.28 * c
    fig, ax = plt.subplots(figsize=(16, 8.3), dpi=150)
    ax.imshow(img, extent=[-xmax, xmax, -ymax, ymax])
    for f in feats:
        c = np.array(f["geometry"]["coordinates"])
        x, y = tf.transform(c[:, 0], c[:, 1])
        brk = np.where(np.abs(np.diff(c[:, 0])) > 180)[0] + 1
        for sx, sy in zip(np.split(x, brk), np.split(y, brk)):
            ax.plot(sx, sy, color=f["properties"]["colour"], lw=2.6, solid_capstyle="round")
        ax.plot([x[0], x[-1]], [y[0], y[-1]], "o", color=f["properties"]["colour"], ms=4, mec="k", mew=0.5)
        ax.plot([], [], color=f["properties"]["colour"], lw=3, label=f'{f["properties"]["biome"]}: {f["properties"]["length_km"]:,} km')
    ax.legend(loc="lower left", fontsize=9, frameon=True)
    ax.set_axis_off()
    ax.set_title("Longest straight (geodesic) line inside each biome - coarse test, RESOLVE Ecoregions 2017 (CC BY 4.0)", fontsize=11)
    fig.savefig(os.path.join(ll.WORK, "preview.png"), bbox_inches="tight")


if __name__ == "__main__":
    main()
