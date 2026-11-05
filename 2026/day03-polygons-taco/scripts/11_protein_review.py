import os, sys, pandas as pd, shapely, numpy as np
from shapely import wkt
from common import DATA, local
from review import grid
df = pd.read_csv(os.path.join(DATA, "protein_clusters.csv"))
df = df[~df.name.str.startswith("Zadarska")]
df = df.drop_duplicates(subset=["kind", "name", "n_pieces", "area_km2"])
for k in ("ground_beef", "chicken"):
    s = df[df.kind == k].head(30)
    items = []
    for i, r in s.iterrows():
        g = local(wkt.loads(r.wkt)); items.append((g, f"[{i}] {r['name'][:28]}\n{r.country[:20]} n={r.n_pieces} {r.area_km2:.0f}km² s={r.score:.2f}"))
    grid(items, os.path.join(DATA, f"rev_{k}.png"), cols=6, title=k)
