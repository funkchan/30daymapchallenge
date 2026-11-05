"""Hand-named multi-piece protein candidates (all NE 10m land + minor island parts inside a bbox), scored with the same metrics as 10_protein.py."""
import os, numpy as np, pandas as pd, geopandas as gpd, shapely
from shapely.geometry import box
from common import DATA, D3, local, mrr_aspect
EQ = "EPSG:8857"
land = pd.concat([gpd.read_file(os.path.join(D3, "ne_10m_land.shp"))[["geometry"]],
                  gpd.read_file(os.path.join(DATA, "ne_10m_minor_islands.shp"))[["geometry"]]]).explode(index_parts=False).reset_index(drop=True)
land = gpd.GeoDataFrame(land, geometry="geometry", crs=4326); land["km2"] = land.to_crs(EQ).area / 1e6
BB = {"Galápagos Islands|Ecuador": (-92.1, -1.6, -89.0, 0.8), "Dahlak Archipelago|Eritrea": (39.4, 15.2, 40.9, 16.3),
      "Cape Verde (Cabo Verde)|Cabo Verde": (-25.5, 14.7, -22.6, 17.3), "Farasan Islands|Saudi Arabia": (41.4, 16.3, 42.4, 17.2),
      "Kornati|Croatia": (15.0, 43.6, 15.6, 44.0), "West Frisian Islands|Netherlands": (4.7, 52.95, 6.45, 53.6),
      "East Frisian Islands|Germany": (6.6, 53.55, 8.3, 53.85), "Chandeleur Islands|United States": (-89.2, 29.6, -88.75, 30.1),
      "Kvarner islands (Krk, Cres, Lošinj, Rab, Pag)|Croatia": (14.2, 44.3, 15.2, 45.3), "Aeolian Islands|Italy": (14.3, 38.3, 15.3, 38.85),
      "Isles Dernieres & Timbalier|United States": (-91.1, 28.95, -90.2, 29.15), "Abrolhos (Houtman)|Australia": (113.5, -29.2, 114.1, -28.2),
      "Kerkennah|Tunisia": (10.9, 34.55, 11.4, 34.85), "Bazaruto Archipelago|Mozambique": (35.25, -22.2, 35.6, -21.4),
      "Åland Islands|Finland": (19.3, 59.7, 21.2, 60.6), "Stockholm archipelago|Sweden": (18.2, 59.0, 19.3, 59.9),
      "Bijagós|Guinea-Bissau": (-16.6, 10.8, -15.4, 11.7), "Thousand Islands (Kepulauan Seribu)|Indonesia": (106.4, -5.9, 106.7, -5.4),
      "Mergui Archipelago|Myanmar": (97.4, 9.8, 98.6, 13.2), "Gulf of California midriff islands|Mexico": (-113.7, 28.6, -112.2, 29.6)}
rows = []
for k, bb in BB.items():
    nm, ctry = k.split("|"); g = land[land.intersects(box(*bb)) & (land.km2 < 20000)]
    g = g[g.representative_point().within(box(*bb))]
    if len(g) < 2: print("few:", nm, len(g)); continue
    w = g.km2.values; geom = shapely.union_all(g.geometry.values); L = local(geom).buffer(0); hull = L.convex_hull
    A = [mrr_aspect(local(p)) for p in g.geometry]; asp = np.array([a[0] for a in A]); sol = np.array([local(p).area / local(p).convex_hull.area for p in g.geometry])
    n_eff = w.sum() ** 2 / (w ** 2).sum(); hull_pp = 4 * np.pi * hull.area / hull.length ** 2; density = L.area / hull.area; irreg = 1 - np.average(sol, weights=w)
    beef = np.clip(n_eff / 12, 0, 1) * hull_pp * np.clip(density / 0.35, 0, 1) * (0.5 + np.clip(irreg / 0.3, 0, 1) / 2)
    ma = np.average(asp, weights=w); chick = np.clip(n_eff / 6, 0, 1) * np.clip((ma - 1.5) / 4, 0, 1) * np.clip(hull_pp / 0.5, 0, 1) * np.clip(density / 0.2, 0, 1)
    rows.append(dict(name=nm, country=ctry, bbox=bb, n_pieces=len(g), n_eff=n_eff, hull_pp=hull_pp, density=density, irregularity=irreg, mean_aspect=ma,
                     area_km2=w.sum(), beef_score=beef, chicken_score=chick, wkt=geom.wkt))
df = pd.DataFrame(rows); df.to_csv(os.path.join(DATA, "protein_handpicks.csv"), index=False)
pd.set_option("display.width", 250); print(df.drop(columns=["wkt", "bbox"]).round(3).to_string())
from review import grid
grid([(local(shapely.wkt.loads(r.wkt)), f"{r['name'][:30]}\nn={r.n_pieces} b={r.beef_score:.2f} c={r.chicken_score:.2f}") for _, r in df.iterrows()], os.path.join(DATA, "rev_handpicks.png"), cols=5, title="hand-named")
