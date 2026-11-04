#!/usr/bin/env python3
"""Taco Tuesday candidate deliverables: candidates.csv, contact sheet, stack mockup, silhouettes (SVG + transparent PNG)."""
import os, re, unicodedata, numpy as np, pandas as pd, shapely, geopandas as gpd
from shapely import affinity, wkt as W
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import PathPatch
from matplotlib.path import Path as MPath
from common import HERE, DATA, local, parts, norm, mrr_aspect
from geomcache import fetch
import importlib; M = importlib.import_module("02_match")
FD = "/usr/share/fonts/truetype/sand-box/google/"
for f in os.listdir(FD):
    if f.endswith(".ttf"): fm.fontManager.addfont(os.path.join(FD, f))
PAPER, INK, MUTE, ACC = "#F2EDDF", "#2A2620", "#6E675A", "#B5532F"
NE_A1, NE_ISL, CG2 = "Natural Earth 10m admin-1", "Natural Earth 10m land, named by geography_regions_polys", "geoBoundaries CGAZ ADM2"
LIC = {NE_A1: "Public domain (Natural Earth)", NE_ISL: "Public domain (Natural Earth)", "bundle": "Public domain (Natural Earth)",
       "JPN": "CC BY-SA 2.0 (gbOpen JPN ADM2: OpenStreetMap, Wambacher)", "BOL": "Public domain (gbOpen BOL: GeoBolivia)",
       "GTM": "CC BY 3.0 IGO (gbOpen GTM: CONRED, OCHA)", "ROU": "CC BY 4.0 (gbOpen ROU: ANCPI)", "TUR": "ODbL 1.0 (gbOpen TUR: OpenStreetMap, OSM Boundaries)",
       "VEN": "ODbL 1.0 (gbOpen VEN: Efraín Porto Tapiquén, Geografía SIG y Estudios Ambientales)", "AUS": "CC BY 4.0 (gbOpen AUS: Australian Bureau of Statistics)",
       "USA": "Public domain (gbOpen USA: US Census Bureau TIGER)", "ARG": "CC BY 3.0 IGO (gbOpen ARG: Instituto Geográfico Nacional, UNHCR, OCHA)",
       "LSO": "CC BY 3.0 IGO (gbOpen LSO: FAO, Ministry of Local Government, OCHA)", "NZL": "CC BY 4.0 (gbOpen NZL: Stats NZ)", "IDN": "CC BY 3.0 IGO (gbOpen IDN: BPS, WFP, OCHA)"}
ISO = {"JPN": "Japan", "BOL": "Bolivia", "GTM": "Guatemala", "ROU": "Romania", "TUR": "Türkiye", "VEN": "Venezuela", "AUS": "Australia", "USA": "United States",
       "ARG": "Argentina", "LSO": "Lesotho", "NZL": "New Zealand", "IDN": "Indonesia", "FRA": "France", "PAN": "Panama"}

# ---------- candidate list: (ingredient, rank, source, src_id, display name, country, level, template, reads_as, pick) ----------
C = [
 ("shell", 1, NE_A1, "JPN-1834", "Kōchi Prefecture", "Japan", "admin-1 (prefecture)", "shell", "Open taco shell end-on: clean crescent wrapped round Tosa Bay. Strong.", True),
 ("shell", 2, NE_A1, "TUR-2271", "Antalya Province", "Türkiye", "admin-1 (province)", "shell", "Wide, shallow shell; reads as a taco when you're told it is one.", False),
 ("shell", 3, CG2, "22064153B45062448622882", "Nakasatsunai", "Japan", "ADM2 (village)", "shell", "Cleanest U of all, but tiny and CC BY-SA. Strong.", False),
 ("shell", 4, CG2, "80513517B32228914297156", "Sud Yungas", "Bolivia", "ADM2 (province)", "shell", "Lopsided U; reads as a shell that's been bitten. Moderate.", False),
 ("protein", 1, NE_ISL, "NE-isl-65", "São Miguel Island (Azores)", "Portugal", "island", "chorizo", "Chorizo link: smooth, slightly curved capsule, rounded ends. Strong.", True),
 ("protein", 2, CG2, "79465075B32919336538902", "La Libertad", "Guatemala", "ADM2 (municipality)", "chorizo", "Curved sausage, very clean. Strong.", False),
 ("protein", 3, CG2, "54988432B95992453735660", "Almus", "Türkiye", "ADM2 (district)", "drumstick", "Chicken drumstick (bulb plus shaft). Moderate to strong; switch if chicken is wanted.", False),
 ("protein", 4, CG2, "2599482B33158001098606", "Dăbâca", "Romania", "ADM2 (commune)", "chorizo", "Stubby sausage. Moderate.", False),
 ("lettuce", 1, NE_ISL, "NE-isl-231", "Iceland", "Iceland", "island", "leaf", "Crinkly, ruffled leaf (fjord edges read as torn lettuce). Moderate to strong.", True),
 ("lettuce", 2, NE_ISL, "NE-isl-229", "Ireland", "Ireland", "island", "leaf", "Rounded leaf with a ragged west edge. Moderate.", False),
 ("lettuce", 3, CG2, "76426892B14162355231744", "Marlborough District", "New Zealand", "ADM2 (district)", "leaf", "Torn leaf with frilly Sounds edge. Moderate.", False),
 ("lettuce", 4, CG2, "35544464B93152851867893", "La Chorrera", "Panama", "ADM2 (district)", "leaf", "Ragged leaf. Moderate.", False),
 ("cheese", 1, "bundle", "NE-land-bundle-371", "Zadar islands (Dugi Otok, Ugljan, Pašman…)", "Croatia", "island group (constructed)", "-", "Pile of parallel shreds of grated cheese. Strong, the best of the bunch.", True),
 ("cheese", 2, "bundle", "NE-land-bundle-328", "Nunavut islands (3 strips)", "Canada", "island group (constructed)", "-", "Three fat shreds, a bit sparse. Moderate.", False),
 ("cheese", 3, "bundle", "NE-land-bundle-170", "Florida coastal islands (NE bundle)", "United States", "island group (constructed)", "-", "Long thin strands in a line, more string cheese than grated. Moderate.", False),
 ("cheese", 4, "bundle", "NE-land-bundle-371x", "Eysturoy-region islands", "Faroe Islands (Denmark)", "island group (constructed)", "-", "Three thick curled strands. Moderate.", False),
 ("tomato", 1, "cluster", "IA-NW6", "Six NW Iowa counties (Clay, Palo Alto, O'Brien, Cherokee, Buena Vista, Pocahontas)", "United States", "ADM2 (county) cluster", "square", "Diced cubes: six near-square counties, pulled apart a little. Strong with the explode treatment.", True),
 ("tomato", 2, CG2, "25037944B37494903355321", "Belyuen", "Australia", "ADM2 (LGA)", "square", "One perfect square, 41 km². Reads as a single cube only.", False),
 ("tomato", 3, CG2, "61730980B5115619218657", "Limay Mahuida", "Argentina", "ADM2 (department)", "square", "One perfect square. Reads as a single cube only.", False),
 ("onion", 1, "cluster", "AR-LP5", "Five La Pampa departments (Realicó, Chapaleufú, Maracó, Quemú Quemú, Catriló)", "Argentina", "ADM2 (department) cluster", "square", "Diced cubes: five almost exact squares, pulled apart. Strong with the explode treatment.", True),
 ("onion", 2, "cluster", "IA-C4", "Four E Iowa counties (Jones, Cedar, Delaware, Buchanan)", "United States", "ADM2 (county) cluster", "square", "2×2 dice. Strong, but the same country as the tomato.", False),
 ("onion", 3, CG2, "61730980B5115619218657", "Limay Mahuida", "Argentina", "ADM2 (department)", "square", "Single cube fallback.", False),
 ("cilantro", 1, NE_ISL, "NE-isl-180", "Halmahera Island", "Indonesia", "island", "cilantro_deep", "Cilantro sprig: stalk with spreading leaflets. Moderate; the best 'branching' read on the globe.", True),
 ("cilantro", 2, CG2, "TBD-maoa", "'Maoa-Mafubelu", "Lesotho", "ADM2 (constituency)", "cilantro_deep", "Three-lobed leaflet. Moderate (lobes shallow).", False),
 ("cilantro", 3, NE_A1, "GRC-2885", "Peloponnese", "Greece", "admin-1 (region)", "cilantro_deep", "Lobed, fingered leaf. Moderate; the fallback if the sprig doesn't land.", False),
 ("cilantro", 4, NE_ISL, "NE-isl-211", "Sulawesi", "Indonesia", "island", "cilantro_deep", "Branching sprig, but too spidery. Weak to moderate.", False),
 ("sour_cream", 1, CG2, "TBD-montalban", "Montalbán", "Venezuela", "ADM2 (municipality)", "dollop", "Dollop with a swirl tip, smooth outline. Strong.", True),
 ("sour_cream", 2, NE_ISL, "TBD-reunion", "Réunion", "France", "island", "dollop", "Smooth rounded blob, with a weak tip. Strong as a blob. Licence-clean alternative.", False),
 ("sour_cream", 3, CG2, "TBD-tarakan", "Kota Tarakan", "Indonesia", "ADM2 (city)", "dollop", "Teardrop dollop with a slightly ragged edge. Moderate to strong.", False),
 ("sour_cream", 4, NE_ISL, "NE-isl-223", "Sri Lanka", "Sri Lanka", "island", "dollop", "Teardrop and instantly recognisable, so it reads as Sri Lanka first. Moderate.", False),
]
c2 = pd.read_csv(os.path.join(DATA, "match_cilantro2.csv")); d2 = pd.read_csv(os.path.join(DATA, "match_dollop2.csv"))
def sid(df, name, country=None):
    r = df[(df.name == name) & ((df.country == country) if country else True)].iloc[0]; return r.source, r.src_id
FIX = {"TBD-maoa": sid(c2, "'Maoa-Mafubelu"), "TBD-montalban": sid(d2, "Montalbán", "VEN"), "TBD-tarakan": sid(d2, "Kota Tarakan"),
       "TBD-reunion": sid(d2[d2.source == NE_ISL], "Réunion (Mascarene Islands)") if (d2.name == "Réunion (Mascarene Islands)").any() else sid(d2, "La Réunion")}
C = [(i, k, *(FIX[s] if s in FIX else (src, s)), n, c, l, t, ra, p) for i, k, src, s, n, c, l, t, ra, p in C]

# ---------- geometries ----------
bund = pd.read_csv(os.path.join(DATA, "cheese_bundles.csv"))
sq = gpd.read_file(os.path.join(DATA, "squares.gpkg"))
CL = {"IA-NW6": ("USA", ["Clay", "Palo Alto", "O'Brien", "Cherokee", "Buena Vista", "Pocahontas"], (-96.2, 42.3, -94.3, 43.3)),
      "IA-C4": ("USA", ["Jones", "Cedar", "Delaware", "Buchanan"], (-92.2, 41.5, -90.8, 42.7)),
      "AR-LP5": ("ARG", ["Realicó", "Chapaleufú", "Maracó", "Quemú Quemú", "Catriló"], (-65, -37, -63, -35))}
G = fetch([(s, i) for _, _, s, i, *_ in C if s in (NE_A1, NE_ISL, CG2)])
def raw(src, i):
    if src == "bundle":
        if i == "NE-land-bundle-371x": r = bund[bund.name.str.startswith("Eysturoy")].iloc[0]
        else: r = bund[bund.src_id == i].iloc[0]
        return W.loads(r.wkt), r
    if src == "cluster":
        iso, names, bb = CL[i]; s = sq[(sq.country == iso) & sq.name.isin(names)].cx[bb[0]:bb[2], bb[1]:bb[3]]
        assert len(s) == len(names), (i, list(s.name)); return shapely.union_all(list(s.geometry)), s
    return G[(src, i)], None

def oriented(ing, src, i, tmpl):
    """Return local (metres) geometry in best orientation, plus rotation (deg CCW applied), score, area_km2, main_only flag."""
    g_ll, extra = raw(src, i); g = local(g_ll).buffer(0); area = g.area / 1e6
    if ing == "cheese":
        ps = sorted(parts(g), key=lambda p: -p.area); _, _, o = mrr_aspect(ps[0]); rot = -(o - 20)  # strands ~20° off horizontal, like a pinch of grated cheese
        c = g.centroid; out = affinity.rotate(affinity.translate(g, -c.x, -c.y), rot, origin=(0, 0)); return out, rot, float(extra.score), area, False, "bundle score"
    if src == "cluster":  # north-up, each cube pulled apart 8% about its own centroid
        ps = [p.buffer(0) for p in local(shapely.GeometryCollection(list(extra.geometry))).geoms]; c = shapely.union_all(ps).centroid
        cc = np.array([[p.centroid.x, p.centroid.y] for p in ps]); out = []
        for p in ps:
            q = affinity.translate(p, *((np.array([p.centroid.x, p.centroid.y]) - [c.x, c.y]) * 0.10)); out.append(affinity.scale(q, 0.92, 0.92, origin="centroid"))
        m = norm(max(ps, key=lambda p: p.area)); iou = M.best_iou(m.simplify(0.004), "square")[0]
        g2 = shapely.MultiPolygon(out); g2 = affinity.translate(g2, -c.x, -c.y); return g2, 0, iou, sum(p.area for p in ps) / 1e6, False, "square IoU (largest cube)"
    main = max(parts(g), key=lambda p: p.area); m = norm(main).simplify(0.004)
    iou, rot, refl = M.best_iou(m, tmpl); keep_all = ing in ("lettuce",) and False
    gg = main; c = gg.centroid; out = affinity.rotate(affinity.translate(gg, -c.x, -c.y), -rot, origin=(0, 0))
    if tmpl == "drumstick" and refl: out = affinity.rotate(out, 180, origin=(0, 0))
    return out, -rot, iou, area, len(parts(g)) > 1, f"{tmpl} IoU"

rows, GEO = [], {}
for ing, rank, src, i, name, country, level, tmpl, reads, pick in C:
    g, rot, score, area, dropped, metric = oriented(ing, src, i, tmpl)
    if src in (NE_A1, NE_ISL, "bundle"): lic = LIC[src if src != "bundle" else "bundle"]; srcname = src if src != "bundle" else "Natural Earth 10m land (constructed island bundle)"
    else: iso = "USA" if i.startswith("IA") else ("ARG" if i.startswith("AR") else None); lic = None; srcname = CG2 + (" (cluster of units)" if src == "cluster" else "")
    if lic is None:
        iso = iso or {v: k for k, v in ISO.items()}.get(country, ""); lic = LIC.get(iso, "CC BY 4.0 (geoBoundaries CGAZ; check gbOpen)")
    ids = i if src != "cluster" else ";".join(raw(src, i)[1].src_id)
    rows.append(dict(ingredient=ing, rank=rank, recommended=pick, name=name, country=country, admin_level=level, source=srcname, src_id=ids, licence=lic,
                     template=tmpl, score=round(score, 3), score_metric=metric, rotation_ccw_deg=round(rot, 1), area_km2=round(area, 1),
                     main_part_only=dropped, reads_as=reads))
    GEO[(ing, rank)] = g
df = pd.DataFrame(rows); df.to_csv(os.path.join(DATA, "candidates_raw.csv"), index=False)
pd.to_pickle(GEO, os.path.join(DATA, "deliver_geoms.pkl")); print(df[["ingredient", "rank", "name", "score", "rotation_ccw_deg", "area_km2"]].to_string())
