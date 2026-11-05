import os, re, unicodedata, numpy as np, pandas as pd, shapely
from shapely import affinity
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import PathPatch
from PIL import Image, ImageDraw
from common import HERE, DATA, parts
import importlib; S = importlib.import_module("08_sheet")
PAPER, INK, MUTE, ACC = S.PAPER, S.INK, S.MUTE, S.ACC
df = pd.read_csv(os.path.join(HERE, "candidates.csv")); GEO = pd.read_pickle(os.path.join(DATA, "final_geoms.pkl"))
picks = df[df.recommended].set_index("ingredient")
def slug(s): return re.sub(r"[^A-Za-z0-9]+", "-", unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()).strip("-")
SHORT = {"Zadar islands (Dugi Otok, Ugljan, Pašman…)": "Zadar-islands", "Six NW Iowa counties (Clay, Palo Alto, O'Brien, Cherokee, Buena Vista, Pocahontas)": "NW-Iowa-6-counties",
         "Five La Pampa departments (Realicó, Chapaleufú, Maracó, Quemú Quemú, Catriló)": "La-Pampa-5-departments", "São Miguel Island (Azores)": "Sao-Miguel-Azores"}
out = os.path.join(HERE, "silhouettes"); files = []
for ing, r in picks.iterrows():
    g = GEO[(ing, r["rank"])]; x0, y0, x1, y1 = g.bounds; ext = max(x1 - x0, y1 - y0); g = g.simplify(ext / 5000)
    base = f"{ing}_{SHORT.get(r['name'], slug(r['name']))}_{slug(r.country)}_rot{int(round(r.rotation_ccw_deg)) % 360:03d}ccw"
    pad = ext * 0.02; W, H = (x1 - x0) + 2 * pad, (y1 - y0) + 2 * pad; k = 2000 / max(W, H)
    def tx(xy): return np.c_[(xy[:, 0] - x0 + pad) * k, (y1 + pad - xy[:, 1]) * k]
    d = []
    for p in parts(g):
        for ring in [p.exterior, *p.interiors]:
            xy = tx(np.asarray(ring.coords)); d.append("M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in xy[:-1]) + " Z")
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W*k:.0f}" height="{H*k:.0f}" viewBox="0 0 {W*k:.1f} {H*k:.1f}">\n'
           f'<title>{r["name"]}, {r.country} ({r.admin_level}). {ing} silhouette, rotated {r.rotation_ccw_deg:.0f}° CCW from north-up, true area {r.area_km2:,.0f} km². Source: {r.source}. Licence: {r.licence}</title>\n'
           f'<path fill="{INK}" fill-rule="evenodd" d="{" ".join(d)}"/>\n</svg>\n')
    open(os.path.join(out, base + ".svg"), "w").write(svg)
    ss = 3; im = Image.new("L", (int(W * k * ss), int(H * k * ss)), 0); dr = ImageDraw.Draw(im)
    for p in parts(g):
        dr.polygon([tuple(v) for v in tx(np.asarray(p.exterior.coords)) * ss], fill=255)
        for h in p.interiors: dr.polygon([tuple(v) for v in tx(np.asarray(h.coords)) * ss], fill=0)
    a = im.resize((int(W * k), int(H * k)), Image.LANCZOS); rgba = Image.new("RGBA", a.size, (0x2A, 0x26, 0x20, 0)); rgba.putalpha(a)
    rgba.save(os.path.join(out, base + ".png")); files.append(base)
print("\n".join(files))

# ---------- rough stack mockup ----------
ORDER = ["shell", "protein", "lettuce", "cheese", "tomato", "onion", "cilantro", "sour_cream"]   # bottom -> top
WID = {"shell": 1.0, "protein": 0.78, "lettuce": 0.62, "cheese": 0.62, "tomato": 0.36, "onion": 0.34, "cilantro": 0.30, "sour_cream": 0.24}  # display width rel. to shell
DISP = {"lettuce": 90, "onion": 90}  # mockup-only extra rotation so these layers lie flat
HMAX = {"lettuce": 0.42, "cilantro": 0.34, "sour_cream": 0.26, "shell": 0.5, "protein": 0.3, "cheese": 0.25, "tomato": 0.25, "onion": 0.25}
TINT = {"shell": "#D9A441", "protein": "#9B3B26", "lettuce": "#7FA33A", "cheese": "#E8B23A", "tomato": "#C8402E", "onion": "#E9E2D0", "cilantro": "#3F7D33", "sour_cream": "#FBF8F0"}
fig = plt.figure(figsize=(12, 16), dpi=150, facecolor=PAPER); ax = fig.add_axes([0.03, 0.17, 0.55, 0.76]); ax.set_axis_off(); ax.set_aspect("equal")
y = 0; gap = 0.06; lab = []
for ing in ORDER:
    r = picks.loc[ing]; g = affinity.rotate(GEO[(ing, r["rank"])], DISP.get(ing, 0), origin=(0, 0)); x0, y0, x1, y1 = g.bounds; s = min(WID[ing] / (x1 - x0), HMAX[ing] / (y1 - y0))
    g = affinity.scale(affinity.translate(g, -(x0 + x1) / 2, -y0), s, s, origin=(0, 0)); h = g.bounds[3]
    ax.add_patch(PathPatch(S.path_of(affinity.translate(g, 0, y)), fc=TINT[ing], ec=INK, lw=1.1)); lab.append((ing, y + h / 2, r)); y += h + gap
ax.set_xlim(-0.6, 0.6); ax.set_ylim(-0.05, y)
fig.text(0.5, 0.975, "TACO TUESDAY · rough stack mockup", ha="center", va="top", family="Alegreya SC", size=26, color=INK)
fig.text(0.5, 0.945, "Recommended picks in stack order, shell at the bottom. Scaled to read as ingredients, NOT to true size. Flat tints are placeholders for the media team's fills.", ha="center", va="top", family="Alegreya Sans", size=10.5, color=MUTE)
tr = ax.transData; inv = fig.transFigure.inverted()
for ing, yy, r in lab:
    fx, fy = inv.transform(tr.transform((0.62, yy)))
    fig.text(0.60, fy + 0.008, S.LAB[ing].upper(), family="Barlow Condensed", weight="bold", size=14, color=ACC, va="center")
    nm = r["name"] if len(r["name"]) < 44 else r["name"].split(" (")[0]
    fig.text(0.60, fy - 0.006, f"{nm}, {r.country}", family="Alegreya Sans", weight="bold", size=10.5, color=INK, va="center")
    fig.text(0.60, fy - 0.018, f"{r.admin_level} · true area {r.area_km2:,.0f} km²" + (" · turned 90° for the mockup" if ing in DISP else ""), family="Alegreya Sans", size=9.5, color=MUTE, va="center")
# true-scale strip
ax2 = fig.add_axes([0.05, 0.02, 0.9, 0.11]); ax2.set_axis_off(); ax2.set_aspect("equal"); x = 0; LBL = []
for ing in ORDER:
    r = picks.loc[ing]; g = GEO[(ing, r["rank"])]; b = g.bounds; g = affinity.translate(g, x - b[0], -(b[1] + b[3]) / 2)
    ax2.add_patch(PathPatch(S.path_of(g), fc=INK, ec="none")); ax2.text(x + (b[2] - b[0]) / 2, -260e3, S.LAB[ing].split(" / ")[0], ha="center", va="top", family="Alegreya Sans", size=8, color=MUTE) if False else None
    LBL.append((x + (b[2] - b[0]) / 2, S.LAB[ing].split(" / ")[0]))
    x += (b[2] - b[0]) + 90e3
ax2.set_xlim(-50e3, x); ax2.set_ylim(-330e3, 260e3)
for j, (lx, lt) in enumerate(LBL): ax2.text(lx, -250e3 if j % 2 == 0 else 215e3, lt, ha="center", va="top" if j % 2 == 0 else "bottom", family="Alegreya Sans", size=8, color=MUTE)
fig.text(0.05, 0.142, "Same picks at TRUE relative scale (equal-area, same km scale): Iceland is 770× Montalbán.", family="Alegreya Sans", size=10, color=INK)
fig.text(0.05, 0.008, "Data: Natural Earth (public domain); geoBoundaries CGAZ / gbOpen, Runfola et al. 2020 (per-boundary licences in candidates.csv). Review draft, not for posting.", family="Alegreya Sans", size=8, color=MUTE)
fig.savefig(os.path.join(HERE, "sheets", "taco_stack_mockup.png"), facecolor=PAPER); plt.close(fig)
