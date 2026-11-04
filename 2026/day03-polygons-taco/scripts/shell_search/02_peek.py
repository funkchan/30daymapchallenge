import sys, numpy as np, pandas as pd, shapely
from shapely import affinity
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
df = pd.read_pickle(sys.argv[3] if len(sys.argv)>3 else "dome_scored.pkl")
df["nv"] = [len(shapely.from_wkb(w).exterior.coords) for w in df.wkb]
q = df.query(sys.argv[1]) if len(sys.argv) > 1 else df
q = q.sort_values("score2" if "score2" in q else "score", ascending=False).head(48)
fig, axs = plt.subplots(6, 8, figsize=(24, 15))
for ax, (_, r) in zip(axs.flat, q.iterrows()):
    g = affinity.rotate(shapely.from_wkb(r.wkb), r.rot_ccw, origin=(0, 0)); x, y = g.exterior.xy
    ax.fill(x, y, "k"); ax.set_aspect("equal"); ax.axis("off"); ax.set_title(f"{r['name'][:28]}\n{r.country[:14]} {r.area_km2:.0f}km² nv{r.nv} s{r.score:.2f} m{r.margin:.2f}", fontsize=7)
plt.tight_layout(); plt.savefig(sys.argv[2] if len(sys.argv) > 2 else "_peek.png", dpi=60)
print(df.nv.describe())
