#!/usr/bin/env python3
"""Multi-piece protein deliverables: candidate geometries (true shape, local LAEA), contact sheet with S2 thumbnails,
landcover check sheet for every current pick, SVG/PNG silhouettes for the two protein picks. Reuses 08_sheet.py styling."""
import os, numpy as np, pandas as pd, shapely
from shapely import affinity, wkt
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
from PIL import Image, ImageDraw
from common import HERE, DATA, local, parts, mrr_aspect
import importlib; S = importlib.import_module("08_sheet")   # NB: importing 08_sheet re-runs it (rewrites the original contact sheet; harmless)
PAPER, INK, MUTE, ACC = S.PAPER, S.INK, S.MUTE, S.ACC
REG = pd.read_pickle(os.path.join(DATA, "colour_geoms.pkl")); CC = pd.read_csv(os.path.join(DATA, "colour_check.csv")).set_index("key")
pc = pd.read_csv(os.path.join(DATA, "protein_clusters.csv")); ph = pd.read_csv(os.path.join(DATA, "protein_handpicks.csv")).set_index("name")
# key, kind, rank, display name, country, NE admin-1 (for the record), shape score, colour note, colour match, verdict
C = [
 ("beef_aisen", "ground_beef", 1, "Chonos Archipelago (Aysén)", "Chile", "Aisén", pc.loc[290].score, "dark green forest and grey rock", "poor",
  "Tightest clump of chunky, ragged crumbs: 20 pieces of similar size. Strong."),
 ("beef_maddalena", "ground_beef", 2, "La Maddalena Archipelago (Sardinia)", "Italy", "Olbia-Tempio", pc.loc[341].score, "tan and pinkish-brown granite with scrub", "good",
  "12 chunky crumbs, looser clump. Moderate to strong; the best colour of any beef shape."),
 ("beef_turku", "ground_beef", 3, "Turku Archipelago (Archipelago Sea)", "Finland", "Finland Proper", pc.loc[291].score, "dark green forest", "poor",
  "55 fine crumbs: the most 'minced' look, but bits are tiny at taco scale. Moderate to strong."),
 ("beef_bijagos", "ground_beef", 4, "Bijagós Archipelago", "Guinea-Bissau", "-", ph.loc["Bijagós"].beef_score, "green forest and mangrove, sandy rims", "poor",
  "11 big rounded lumps in a neat clump: meatballs more than mince. Moderate."),
 ("beef_pellew", "ground_beef", 5, "Sir Edward Pellew Group", "Australia", "Northern Territory", pc.loc[347].score, "olive-tan scrub on sandstone", "fair",
  "9 lumpy pieces, a loose clump. Moderate."),
 ("chk_magallanes", "chicken", 1, "Islands W of Strait of Magellan (Reina Adelaida area)", "Chile", "Magallanes", pc.loc[15].score, "pale grey bare granite with snow patches", "fair to good (pale)",
  "12 long, fanned shreds with frayed ends: pulled chicken. Strong."),
 ("chk_kvarner", "chicken", 2, "Kvarner islands (Krk, Cres, Lošinj, Rab, Pag)", "Croatia", "Primorje-Gorski Kotar / Lika-Senj", ph.loc["Kvarner islands (Krk, Cres, Lošinj, Rab, Pag)"].chicken_score, "green-grey; bare pale limestone on Pag, Rab and the east shores", "fair",
  "20 pieces from big slabs to thin slivers: shredded chicken. Strong, but the same coast as the cheese."),
 ("chk_dubrovnik", "chicken", 3, "Korčula, Mljet, Lastovo and islets", "Croatia", "Dubrovnik-Neretva", pc.loc[5].score, "dark green pine and maquis", "poor",
  "10 parallel slices of mixed size: sliced chicken breast. Strong, but very like the cheese bundle."),
 ("chk_wfrisian", "chicken", 4, "West Frisian Islands (Texel to Schiermonnikoog)", "Netherlands", "Noord-Holland / Friesland", ph.loc["West Frisian Islands"].chicken_score, "pale beige dunes and beach with green polders", "fair to good (pale)",
  "5 long slices in an arc. Moderate (too few, too evenly spaced)."),
 ("chk_dernieres", "chicken", 5, "Isles Dernieres and Timbalier barrier islands", "United States", "Louisiana", ph.loc["Isles Dernieres & Timbalier"].chicken_score, "white-beige sand barrier strips", "good (pale)",
  "10 very thin slivers in a line: closer to julienne than shreds. Weak to moderate."),
]
def orient(k, kind):
    g = local(REG[k][1]).buffer(0); c = g.centroid; g = affinity.translate(g, -c.x, -c.y); rot = 0.0
    if kind == "chicken":
        _, _, o = mrr_aspect(g.convex_hull); rot = -o; g = affinity.rotate(g, rot, origin=(0, 0))
    return g, rot % 360
G = {k: orient(k, kind) for k, kind, *_ in C}
rows = []
for k, kind, rk, nm, ctry, a1, sc, cnote, cm, verdict in C:
    g = G[k][0]; ps = parts(g); tot = g.area
    cc = CC.loc[k]
    rows.append(dict(ingredient="protein", rank=f"{kind}-{rk}", recommended=rk == 1, name=nm, country=ctry, admin_level="island group (constructed)",
                     source="Natural Earth 10m land + minor islands (constructed island cluster)", src_id=f"NE-protein-{k}", licence="Public domain (Natural Earth)",
                     template=kind, score=round(float(sc), 3), score_metric=f"{kind} cluster score", rotation_ccw_deg=round(G[k][1], 1), area_km2=round(tot / 1e6, 1),
                     main_part_only=False, reads_as=verdict, n_pieces=len(ps), s2_median_rgb=f"{int(cc.med_r)},{int(cc.med_g)},{int(cc.med_b)}",
                     ground_colour=cnote, colour_match=cm))
P = pd.DataFrame(rows)
# ---------- contact sheet ----------
fig = plt.figure(figsize=(17, 15), dpi=150, facecolor=PAPER)
fig.text(0.5, 0.985, "TACO TUESDAY · multi-piece protein candidates", ha="center", va="top", family="Alegreya SC", size=26, color=INK)
fig.text(0.5, 0.958, "Real island clusters (Natural Earth 10m land + minor islands), true shape (local equal-area), each scaled to its cell. Beef north-up; chicken turned so the cluster lies flat. "
         "Thumbnail: Sentinel-2 cloudless 2016 (EOX), polygon outline in yellow.", ha="center", va="top", family="Alegreya Sans", size=10, color=MUTE, wrap=True)
for ri, kind in enumerate(["ground_beef", "chicken"]):
    sub = [c for c in C if c[1] == kind]
    fig.text(0.012, 0.70 - ri * 0.45, ("Ground beef" if kind == "ground_beef" else "Chicken").upper(), family="Barlow Condensed", size=20, color=ACC, weight="bold", rotation=90, va="center")
    for ci, (k, _, rk, nm, ctry, a1, sc, cnote, cm, verdict) in enumerate(sub):
        x0 = 0.04 + ci * 0.192; ytop = 0.925 - ri * 0.45
        ax = fig.add_axes([x0, ytop - 0.20, 0.175, 0.20]); S.draw(ax, G[k][0], INK)
        th = Image.open(os.path.join(DATA, "s2", k + "_thumb.png")); th.thumbnail((360, 230))
        ax2 = fig.add_axes([x0, ytop - 0.345, 0.175, 0.135]); ax2.imshow(np.asarray(th)); ax2.set_axis_off()
        r = P[P.src_id == f"NE-protein-{k}"].iloc[0]; yl = ytop - 0.355
        fig.text(x0, yl, ("PICK · " if rk == 1 else f"#{rk} · ") + nm[:40], family="Alegreya Sans", weight="bold", size=10, color=ACC if rk == 1 else INK, va="top")
        fig.text(x0, yl - 0.014, f"{ctry} · {r.n_pieces} pieces · {r.area_km2:,.0f} km² · score {r.score:.2f}", family="Alegreya Sans", size=8.5, color=INK, va="top")
        fig.text(x0, yl - 0.027, __import__("textwrap").fill(f"Ground: {cnote} ({cm})", 52), family="Alegreya Sans", size=8, color=MUTE, va="top", linespacing=1.1)
fig.text(0.04, 0.012, "Data: Natural Earth (public domain). Imagery: Sentinel-2 cloudless 2016 by EOX IT Services GmbH (contains modified Copernicus Sentinel data 2016), CC BY 4.0. Review draft, not for posting.",
         family="Alegreya Sans", size=8, color=MUTE)
fig.savefig(os.path.join(HERE, "sheets", "protein_candidates_contact_sheet.png"), facecolor=PAPER); plt.close(fig)
# ---------- landcover check sheet ----------
LC = [("shell", "Shell / tortilla", "Kōchi Prefecture, Japan", "golden tan", "dense dark-green forest", "poor"),
      ("protein_old", "Protein (old: chorizo)", "São Miguel, Azores", "red-brown", "green pasture and forest", "poor"),
      ("beef_aisen", "Protein: ground beef pick", "Chonos Archipelago, Chile", "brown", "dark green forest, grey rock", "poor"),
      ("beef_maddalena", "Protein: ground beef alt", "La Maddalena, Italy", "brown", "tan and pink-brown granite", "good"),
      ("chk_magallanes", "Protein: chicken pick", "Magallanes islands, Chile", "pale beige", "pale grey granite, snow", "fair to good"),
      ("lettuce", "Shredded lettuce", "Iceland", "bright green", "grey-brown lava and moss, white ice caps, green lowland fringe", "poor to fair"),
      ("cheese", "Shredded cheese", "Zadar islands, Croatia", "yellow-orange", "grey-green limestone and scrub", "poor"),
      ("tomato", "Diced tomato", "6 NW Iowa counties, USA", "red", "green and tan cropland (summer mosaic)", "poor"),
      ("onion", "Diced onion", "5 La Pampa departments, Argentina", "white / translucent", "green and tan cropland and grassland", "poor"),
      ("cilantro", "Cilantro", "Halmahera, Indonesia", "deep green", "dense dark-green rainforest", "excellent"),
      ("sour_cream", "Sour cream (current)", "Montalbán, Venezuela", "white", "green hills, brown farmland", "poor"),
      ("sc_salinas", "Sour cream (white alt)", "Salinas Grandes (NE playa), Argentina", "white", "cream-white salt crust", "excellent"),
      ("sc_svalbard", "Sour cream (white alt 2)", "Svalbard ice cap", "white", "white ice in grey rock", "good")]
fig = plt.figure(figsize=(17, 20), dpi=130, facecolor=PAPER)
fig.text(0.5, 0.99, "TACO TUESDAY · does the ground match the ingredient?", ha="center", va="top", family="Alegreya SC", size=26, color=INK)
fig.text(0.5, 0.967, "Sentinel-2 cloudless 2016 (EOX) true colour, same brightness stretch for every tile. Swatch = median land colour inside the polygon (sea pixels dropped).",
         ha="center", va="top", family="Alegreya Sans", size=10.5, color=MUTE)
for i, (k, ing, place, want, got, m) in enumerate(LC):
    cx, cy = i % 4, i // 4; x0 = 0.03 + cx * 0.245; yt = 0.945 - cy * 0.232
    th = Image.open(os.path.join(DATA, "s2", k + "_thumb.png")); th.thumbnail((520, 360))
    ax = fig.add_axes([x0, yt - 0.165, 0.225, 0.165]); ax.imshow(np.asarray(th)); ax.set_axis_off()
    ax3 = fig.add_axes([x0, yt - 0.186, 0.02, 0.016]); ax3.set_facecolor(CC.loc[k, "disp_hex"]); ax3.set_xticks([]); ax3.set_yticks([])
    fig.text(x0 + 0.025, yt - 0.178, f"{ing.upper()}", family="Barlow Condensed", weight="bold", size=12, color=ACC, va="center")
    fig.text(x0, yt - 0.196, place, family="Alegreya Sans", weight="bold", size=10, color=INK, va="top")
    fig.text(x0, yt - 0.209, __import__("textwrap").fill(f"Want {want}; ground is {got}", 62), family="Alegreya Sans", size=8.5, color=INK, va="top")
    fig.text(x0, yt - 0.232, f"Match: {m}", family="Alegreya Sans", size=9, weight="bold", color=MUTE, va="top")
fig.text(0.03, 0.006, "Imagery: Sentinel-2 cloudless 2016 by EOX IT Services GmbH (modified Copernicus Sentinel data 2016), CC BY 4.0. Outlines: Natural Earth; geoBoundaries. Review draft, not for posting.",
         family="Alegreya Sans", size=8, color=MUTE)
fig.savefig(os.path.join(HERE, "sheets", "landcover_check.png"), facecolor=PAPER); plt.close(fig)
# ---------- silhouettes for the two protein picks (same format as 09_export.py, plus true scale metadata) ----------
out = os.path.join(HERE, "silhouettes"); SL = {"beef_aisen": "protein-beef_Chonos-Archipelago_Chile", "chk_magallanes": "protein-chicken_Magallanes-islands_Chile",
                                               "beef_maddalena": "protein-beef_La-Maddalena-Archipelago_Italy"}
for k, stem in SL.items():
    g, rot = G[k]; x0, y0, x1, y1 = g.bounds; ext = max(x1 - x0, y1 - y0); g = g.simplify(ext / 5000)
    base = f"{stem}_rot{int(round(rot)) % 360:03d}ccw"; pad = ext * 0.02; W, H = (x1 - x0) + 2 * pad, (y1 - y0) + 2 * pad; kk = 2000 / max(W, H)
    tx = lambda xy: np.c_[(xy[:, 0] - x0 + pad) * kk, (y1 + pad - xy[:, 1]) * kk]
    d = ["M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in tx(np.asarray(ring.coords))[:-1]) + " Z" for p in parts(g) for ring in [p.exterior, *p.interiors]]
    r = P[P.src_id == f"NE-protein-{k}"].iloc[0]
    open(os.path.join(out, base + ".svg"), "w").write(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W*kk:.0f}" height="{H*kk:.0f}" viewBox="0 0 {W*kk:.1f} {H*kk:.1f}" data-metres-per-px="{1/kk:.2f}" data-pieces="{r.n_pieces}">\n'
        f'<title>{r["name"]}, {r.country} ({r.n_pieces} islands). {r.template} silhouette, rotated {rot:.0f}° CCW from north-up, true land area {r.area_km2:,.0f} km², {1/kk:.1f} m per px. Source: {r.source}. Licence: {r.licence}</title>\n'
        f'<path fill="{INK}" fill-rule="evenodd" d="{" ".join(d)}"/>\n</svg>\n')
    ss = 3; im = Image.new("L", (int(W * kk * ss), int(H * kk * ss)), 0); dr = ImageDraw.Draw(im)
    for p in parts(g):
        dr.polygon([tuple(v) for v in tx(np.asarray(p.exterior.coords)) * ss], fill=255)
        for h in p.interiors: dr.polygon([tuple(v) for v in tx(np.asarray(h.coords)) * ss], fill=0)
    a = im.resize((int(W * kk), int(H * kk)), Image.LANCZOS); rgba = Image.new("RGBA", a.size, (0x2A, 0x26, 0x20, 0)); rgba.putalpha(a); rgba.save(os.path.join(out, base + ".png")); print(base, a.size)
pd.to_pickle(G, os.path.join(DATA, "protein_geoms.pkl")); P.to_csv(os.path.join(DATA, "protein_candidates.csv"), index=False)
print(P[["rank", "name", "n_pieces", "area_km2", "score", "rotation_ccw_deg", "s2_median_rgb", "colour_match"]].to_string())
