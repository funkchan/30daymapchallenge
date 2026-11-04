"""Add an arc-smoothness (corner) test and a vertex-detail floor; re-rank. Reads dome_scored.pkl from 01_dome.py."""
import numpy as np, pandas as pd, shapely
from shapely import affinity
import importlib; D = importlib.import_module("01_dome")
df = pd.read_pickle("dome_scored.pkl")
def corner(r):
    u = affinity.rotate(shapely.from_wkb(r.wkb), -r.rot_tmpl, origin=(0, 0)); lo, up = D.chains(u)
    rs = D.resample(up, 60); d = np.diff(rs, axis=0); tr = np.abs(np.diff(np.unwrap(np.arctan2(d[:, 1], d[:, 0]))))
    # curvature spread: share of turning in the 3 sharpest steps (smooth half-disc ~0.05-0.1, trapezoid ~0.9)
    return float(np.sort(tr)[-3:].sum() / max(tr.sum(), 1e-9)), len(up), len(lo)
c = [corner(r) for r in df.itertuples()]
df["arc_corner_share"] = [x[0] for x in c]; df["nv_arc"] = [x[1] for x in c]; df["nv"] = [len(shapely.from_wkb(w).exterior.coords) for w in df.wkb]
df["score2"] = df.score - 0.8 * np.clip(df.arc_corner_share - 0.25, 0, None)
ok = df.query("nv_arc>=12 and margin>0.03 and base_dev<=0.10 and 1.4<=width_height<=2.6").copy()
ok = ok.sort_values("score2", ascending=False).drop_duplicates(["name", "area_km2"])
ok.to_pickle("dome_ranked.pkl"); pd.set_option("display.width", 250)
print(len(ok)); print(ok.head(50)[["name", "country", "source", "area_km2", "nv", "iou_dome", "margin", "base_dev", "arc_corner_share", "width_height", "score2"]].to_string())
