"""Stretched true-colour thumbnails with the polygon outline, for review sheets. Uses data/s2/*.jpg from 14_colour.py."""
import os, numpy as np, pandas as pd
from PIL import Image, ImageDraw
from common import DATA
REG = pd.read_pickle(os.path.join(DATA, "colour_geoms.pkl")); CC = pd.read_csv(os.path.join(DATA, "colour_check.csv")).set_index("key")
def thumb(k, outline=(255, 214, 64)):
    im = np.asarray(Image.open(os.path.join(DATA, "s2", k + ".jpg")).convert("RGB")).astype(float)
    im = Image.fromarray(np.clip(255 * (im / 255) ** 0.7 * 1.25, 0, 255).astype("uint8")); W, H = im.size
    x0, y0, x1, y1 = map(float, CC.loc[k, "bbox"].split(",")); d = ImageDraw.Draw(im); g = REG[k][1]
    T = lambda xy: [((a - x0) / (x1 - x0) * W, (y1 - b) / (y1 - y0) * H) for a, b in xy]
    for p in (g.geoms if hasattr(g, "geoms") else [g]): d.line(T(p.exterior.coords), fill=outline, width=1)
    return im
for k in REG: thumb(k).save(os.path.join(DATA, "s2", k + "_thumb.png"))
