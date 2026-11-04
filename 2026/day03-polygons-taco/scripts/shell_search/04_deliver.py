"""Top-20 CSV, top-12 contact sheet with template outlines + reference cartoon, top-3 SVG/PNG silhouettes (flat edge down)."""
import os, sys, re, unicodedata, numpy as np, pandas as pd, geopandas as gpd, pyogrio, shapely
from shapely import affinity
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); TACO = os.path.dirname(HERE); sys.path.insert(0, TACO); sys.path.insert(0, HERE)
from common import DATA, D3, local, parts
import importlib; D = importlib.import_module("01_dome")
TOP3 = [int(x) for x in sys.argv[1].split(",")] if len(sys.argv) > 1 else [0, 1, 2]
df = pd.read_pickle(os.path.join(HERE, "dome_ranked.pkl")).reset_index(drop=True).head(20)
df["rank"] = np.arange(1, len(df) + 1)
cols = ["rank", "name", "country", "admin_level", "area_km2", "source", "src_id", "licence", "score2", "iou_dome", "aspect_tmpl", "iou_decoy", "margin",
        "base_dev", "arc_convexity", "arc_monotone", "arc_corner_share", "width_height", "nv", "rot_ccw"]
out = df[cols].rename(columns={"score2": "score", "rot_ccw": "best_rotation_ccw_deg", "nv": "n_vertices_simplified", "width_height": "width_to_height"})
out["best_rotation_ccw_deg"] = out.best_rotation_ccw_deg.round(1)
out.to_csv(os.path.join(HERE, "shell_dome_candidates.csv"), index=False, float_format="%.4f")

def he(A, ang):
    return affinity.rotate(D.HE[A], ang, origin=(0, 0))
fig = plt.figure(figsize=(16, 13), facecolor="#F3EDE0")
fig.text(0.02, 0.975, "Taco shell search: closed half-dome, flat edge down (equal area, true shape)", size=18, weight="bold", va="top", color="#2A2620")
fig.text(0.02, 0.945, "Black = real polygon rotated flat side down. Orange line = best half-ellipse template (aspect 1.6-2.2). score = IoU + (IoU - best rect/ellipse IoU) - straight-base / smooth-arc penalties.",
         size=9.5, va="top", color="#6B6255")
for i in range(12):
    r = df.iloc[i]; ax = fig.add_axes([0.02 + (i % 4) * 0.245, 0.64 - (i // 4) * 0.30, 0.22, 0.25]); ax.set_aspect("equal"); ax.axis("off")
    g = affinity.rotate(shapely.from_wkb(r.wkb), r.rot_ccw, origin=(0, 0)); t = he(r.aspect_tmpl, r.rot_ccw + r.rot_tmpl)
    for p in parts(g): ax.fill(*p.exterior.xy, color="#2A2620", lw=0)
    ax.plot(*t.exterior.xy, color="#E07A1F", lw=1.6)
    ax.set_xlim(-1.3, 1.3); ax.set_ylim(-0.9, 0.9)
    nm = r["name"] if len(r["name"]) < 34 else r["name"][:32] + "…"
    ax.set_title(f"#{i+1} {nm}\n{r.country} · {r.area_km2:,.0f} km² · {r.source.split(' ')[0]} {'CC BY' if 'CC BY' in r.licence else 'PD'}\n"
                 f"score {r.score2:.2f} · IoU {r.iou_dome:.2f} · margin {r.margin:+.2f} · base dev {r.base_dev*100:.1f}% · W:H {r.width_height:.2f}", size=8.5, color="#2A2620")
ref = Image.open(os.path.join(HERE, "ref.png")); ax = fig.add_axes([0.80, 0.885, 0.18, 0.105]); ax.imshow(ref); ax.axis("off"); ax.set_title("reference (funkchan)", size=8, color="#6B6255")
fig.savefig(os.path.join(HERE, "shell_dome_contact_sheet.png"), dpi=110, facecolor=fig.get_facecolor()); plt.close(fig)

def full_geom(r):
    s, i = r.source, r.src_id
    if s.startswith("US Census"):
        f = "cb_2023_us_place_500k.shp" if "places" in s else "cb_2023_us_county_500k.shp"
        g = gpd.read_file(os.path.join(HERE, "data", f), where=f"GEOID='{i}'").to_crs(4326); return g.geometry.iloc[0]
    if s == "geoBoundaries CGAZ ADM2":
        return pyogrio.read_dataframe(os.path.join(DATA, "geoBoundariesCGAZ_ADM2.gpkg"), where=f"shapeID='{i}'").geometry.iloc[0]
    if s == "Natural Earth 10m admin-1":
        a = gpd.read_file(os.path.join(D3, "ne_10m_admin_1_states_provinces.shp"), where=f"adm1_code='{i}'"); return a.geometry.iloc[0]
    raise ValueError(s)
def slug(s): return re.sub(r"[^A-Za-z0-9]+", "-", unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()).strip("-")
SIL = os.path.join(TACO, "silhouettes")
for i in TOP3:
    r = df.iloc[i]; g = local(full_geom(r)).buffer(0); m = max(parts(g), key=lambda p: p.area); m = shapely.Polygon(m.exterior)
    c = m.centroid; m = affinity.rotate(affinity.translate(m, -c.x, -c.y), r.rot_ccw, origin=(0, 0))
    x0, y0, x1, y1 = m.bounds; ext = max(x1 - x0, y1 - y0); pad = ext * 0.02; W, H = x1 - x0 + 2 * pad, y1 - y0 + 2 * pad; k = 2000 / max(W, H)
    tx = lambda xy: np.c_[(xy[:, 0] - x0 + pad) * k, (y1 + pad - xy[:, 1]) * k]
    xy = tx(np.asarray(m.exterior.coords)); d = "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in xy[:-1]) + " Z"
    nm = r["name"].split(",")[0].replace(" city", "").replace(" County", "-County")
    base = f"shell-dome_{slug(nm)}_{slug(r.country if r.country not in ('BRB',) else 'Barbados')}_rot{int(round(r.rot_ccw)) % 360:03d}ccw"
    open(os.path.join(SIL, base + ".svg"), "w").write(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W*k:.0f}" height="{H*k:.0f}" viewBox="0 0 {W*k:.1f} {H*k:.1f}" data-metres-per-px="{1/k:.3f}">\n'
        f'<title>{r["name"]}, {r.country} ({r.admin_level}). Taco shell (closed dome) silhouette, flat edge down, rotated {r.rot_ccw:.0f}° CCW from north-up, '
        f'true area {r.area_km2:,.1f} km², main polygon only. Source: {r.source}, id {r.src_id}. Licence: {r.licence}</title>\n'
        f'<path fill="#2A2620" d="{d}"/>\n</svg>\n')
    ss = 3; im = Image.new("L", (int(W * k * ss), int(H * k * ss)), 0); ImageDraw.Draw(im).polygon([tuple(v) for v in xy * ss], fill=255)
    a = im.resize((int(W * k), int(H * k)), Image.LANCZOS); rgba = Image.new("RGBA", a.size, (0x2A, 0x26, 0x20, 0)); rgba.putalpha(a); rgba.save(os.path.join(SIL, base + ".png"))
    print(base, len(m.exterior.coords))
