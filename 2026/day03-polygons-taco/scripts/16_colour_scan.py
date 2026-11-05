"""Colour scan of the top multi-piece protein clusters (same S2 cloudless 2016 WMS + mask as 14_colour.py): looking for brown (beef) or pale (chicken) ground."""
import os, urllib.request, numpy as np, pandas as pd
from shapely import wkt
from PIL import Image, ImageDraw
from common import DATA
WMS = "https://tiles.maps.eox.at/wms?service=WMS&version=1.1.1&request=GetMap&layers=s2cloudless&srs=EPSG:4326&format=image/jpeg&bbox={},{},{},{}&width={}&height={}"
df = pd.read_csv(os.path.join(DATA, "protein_clusters.csv")); df = df[~df.name.str.startswith("Zadarska")].drop_duplicates(subset=["kind", "name", "n_pieces", "area_km2"])
sel = pd.concat([df[df.kind == "ground_beef"].head(60), df[df.kind == "chicken"].head(60)]); res = []
for i, r in sel.iterrows():
    g = wkt.loads(r.wkt); x0, y0, x1, y1 = g.bounds; W = 400; H = max(40, min(800, int(W * (y1 - y0) / max((x1 - x0) * np.cos(np.radians((y0 + y1) / 2)), 1e-6))))
    try: im = Image.open(__import__("io").BytesIO(urllib.request.urlopen(WMS.format(x0, y0, x1, y1, W, H), timeout=60).read())).convert("RGB")
    except Exception as e: print("fail", i, e); continue
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m); T = lambda xy: [((a - x0) / (x1 - x0) * W, (y1 - b) / (y1 - y0) * H) for a, b in xy]
    for p in (g.geoms if hasattr(g, "geoms") else [g]): d.polygon(T(p.exterior.coords), fill=255)
    px = np.asarray(im).astype(float)[np.asarray(m) > 0]; px = px[~((px[:, 2] >= px[:, 1]) & (px[:, 2] > px[:, 0]) & (px.sum(1) < 330))]
    if len(px) < 30: continue
    med = np.median(px, 0); res.append(dict(idx=i, kind=r.kind, name=r["name"], country=r.country, n=r.n_pieces, score=r.score, R=med[0], G=med[1], B=med[2],
                                            brown=med[0] - med[1], bright=med.mean()))
o = pd.DataFrame(res); o.to_csv(os.path.join(DATA, "protein_colour_scan.csv"), index=False); pd.set_option("display.width", 200)
print(o[o.kind == "ground_beef"].sort_values("brown", ascending=False).head(12).round(2).to_string())
print(o[o.kind == "chicken"].sort_values("bright", ascending=False).head(12).round(2).to_string())
