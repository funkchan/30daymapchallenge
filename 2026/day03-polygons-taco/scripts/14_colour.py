#!/usr/bin/env python3
"""True-colour check: EOX Sentinel-2 cloudless 2016 mosaic (layer 's2cloudless', CC BY 4.0) via WMS, masked to each polygon.
Reports median RGB of land pixels (water-like pixels dropped) and a coarse colour class. Thumbnails cached in data/s2/."""
import os, io, colorsys, urllib.request, numpy as np, pandas as pd, geopandas as gpd, shapely
from shapely import wkt
from PIL import Image, ImageDraw
from common import DATA
from geomcache import fetch
S2 = os.path.join(DATA, "s2"); os.makedirs(S2, exist_ok=True)
WMS = "https://tiles.maps.eox.at/wms?service=WMS&version=1.1.1&request=GetMap&layers=s2cloudless&srs=EPSG:4326&format=image/jpeg&bbox={},{},{},{}&width={}&height={}"
pc = pd.read_csv(os.path.join(DATA, "protein_clusters.csv")); ph = pd.read_csv(os.path.join(DATA, "protein_handpicks.csv")).set_index("name")
wd = pd.read_csv(os.path.join(DATA, "match_white_dollop.csv")); ch = pd.read_csv(os.path.join(DATA, "cheese_bundles.csv"))
cand = pd.read_csv("candidates.csv"); ids = {r.ingredient: (r.source, r.src_id) for _, r in cand[cand.recommended].iterrows()}
cg = fetch([("Natural Earth 10m admin-1", "JPN-1834"), ("Natural Earth 10m land, named by geography_regions_polys", "NE-isl-65"),
            ("Natural Earth 10m land, named by geography_regions_polys", "NE-isl-231"), ("Natural Earth 10m land, named by geography_regions_polys", "NE-isl-180"),
            ("geoBoundaries CGAZ ADM2", ids["sour_cream"][1])] + [("geoBoundaries CGAZ ADM2", x) for k in ("tomato", "onion") for x in ids[k][1].split(";")])
U = lambda k: shapely.union_all([cg[("geoBoundaries CGAZ ADM2", x)] for x in ids[k][1].split(";")])
REG = {  # key: (label, geometry lon/lat)
 "shell": ("Kōchi Prefecture (shell)", cg[("Natural Earth 10m admin-1", "JPN-1834")]),
 "protein_old": ("São Miguel (old protein)", cg[("Natural Earth 10m land, named by geography_regions_polys", "NE-isl-65")]),
 "lettuce": ("Iceland (lettuce)", cg[("Natural Earth 10m land, named by geography_regions_polys", "NE-isl-231")]),
 "cheese": ("Zadar islands (cheese)", wkt.loads(ch[ch.src_id == "NE-land-bundle-371"].wkt.iloc[0])),
 "tomato": ("6 NW Iowa counties (tomato)", U("tomato")), "onion": ("5 La Pampa depts (onion)", U("onion")),
 "cilantro": ("Halmahera (cilantro)", cg[("Natural Earth 10m land, named by geography_regions_polys", "NE-isl-180")]),
 "sour_cream": ("Montalbán (sour cream)", cg[("geoBoundaries CGAZ ADM2", ids["sour_cream"][1])]),
 "sc_salinas": ("Salinas Grandes playa (sour cream alt)", wkt.loads(wd[(wd.source == "NE 10m playas") & (wd.idx == 33)].wkt.iloc[0])),
 "sc_svalbard": ("Svalbard ice cap (sour cream alt)", wkt.loads(wd[(wd.source == "NE 10m glaciated areas") & (wd.idx == 841)].wkt.iloc[0])),
 "beef_bijagos": ("Bijagós Archipelago", wkt.loads(ph.loc["Bijagós"].wkt)), "beef_aisen": ("Aisén islands (Chonos)", wkt.loads(pc.loc[290].wkt)),
 "beef_turku": ("Turku Archipelago", wkt.loads(pc.loc[291].wkt)), "beef_aland": ("Åland Islands", wkt.loads(ph.loc["Åland Islands"].wkt)),
 "beef_maddalena": ("La Maddalena Archipelago", wkt.loads(pc.loc[341].wkt)), "beef_pellew": ("Sir Edward Pellew Group", wkt.loads(pc.loc[347].wkt)),
 "beef_jeolla": ("South Jeolla islands", wkt.loads(pc.loc[292].wkt)),
 "chk_kvarner": ("Kvarner islands", wkt.loads(ph.loc["Kvarner islands (Krk, Cres, Lošinj, Rab, Pag)"].wkt)),
 "chk_wfrisian": ("West Frisian Islands", wkt.loads(ph.loc["West Frisian Islands"].wkt)),
 "chk_dernieres": ("Isles Dernieres & Timbalier", wkt.loads(ph.loc["Isles Dernieres & Timbalier"].wkt)),
 "chk_magallanes": ("Magallanes islands", wkt.loads(pc.loc[15].wkt)), "chk_dubrovnik": ("Dubrovnik islands (Korčula, Mljet, Lastovo…)", wkt.loads(pc.loc[5].wkt)),
 "chk_louisiana": ("Louisiana islands (4 slices)", wkt.loads(pc.loc[3].wkt)),
}
def cls(rgb):
    h, l, s = colorsys.rgb_to_hls(*(np.array(rgb) / 255)); h *= 360
    if l > 0.62 and s < 0.35: return "white / pale"
    if s < 0.12: return "grey" if l > 0.25 else "dark grey"
    if 60 <= h < 160: return "green" if l < 0.5 else "pale green"
    if 15 <= h < 60: return "brown / tan" if l < 0.5 else "beige / sand"
    if h < 15 or h >= 330: return "red-brown"
    return "blue-grey"
out = []
for k, (lab, g) in REG.items():
    x0, y0, x1, y1 = g.bounds; px = (x1 - x0) * 0.06 + 0.01; py = (y1 - y0) * 0.06 + 0.01; x0, x1, y0, y1 = x0 - px, x1 + px, y0 - py, y1 + py
    W = 700; H = max(80, int(W * (y1 - y0) / ((x1 - x0) * np.cos(np.radians((y0 + y1) / 2)))))
    if H > 900: H = 900; W = int(H * (x1 - x0) * np.cos(np.radians((y0 + y1) / 2)) / (y1 - y0))
    f = os.path.join(S2, k + ".jpg")
    if not os.path.exists(f): open(f, "wb").write(urllib.request.urlopen(WMS.format(x0, y0, x1, y1, W, H), timeout=90).read())
    im = np.asarray(Image.open(f).convert("RGB")).astype(float); H, W = im.shape[:2]
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
    T = lambda xy: [((a - x0) / (x1 - x0) * W, (y1 - b) / (y1 - y0) * H) for a, b in xy]
    for p in (g.geoms if hasattr(g, "geoms") else [g]):
        d.polygon(T(p.exterior.coords), fill=255)
        for h in p.interiors: d.polygon(T(h.coords), fill=0)
    m = np.asarray(m) > 0; px_ = im[m]
    water = (px_[:, 2] >= px_[:, 1]) & (px_[:, 2] > px_[:, 0]) & (px_.sum(1) < 330)            # dark bluish = sea/lake bleed from coarse coastlines
    land_ = px_[~water] if (~water).sum() > 50 else px_
    med = np.median(land_, 0); p90 = np.percentile(im.reshape(-1, 3).sum(1), 99.5) / 3
    disp = np.clip(255 * (med / 255) ** 0.7 * 1.25, 0, 255)          # fixed display stretch (same for all thumbnails)
    out.append(dict(key=k, label=lab, n_px=int(m.sum()), water_frac=float(water.mean()), med_r=med[0], med_g=med[1], med_b=med[2],
                    disp_hex="#%02x%02x%02x" % tuple(int(v) for v in disp), colour_class=cls(disp), bbox=f"{x0:.3f},{y0:.3f},{x1:.3f},{y1:.3f}"))
df = pd.DataFrame(out); df.to_csv(os.path.join(DATA, "colour_check.csv"), index=False); pd.to_pickle(REG, os.path.join(DATA, "colour_geoms.pkl"))
pd.set_option("display.width", 220); print(df.drop(columns="bbox").round(2).to_string())
