import os, numpy as np, pandas as pd, shapely
from shapely import affinity
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
from matplotlib.path import Path as MPath
from common import HERE, DATA, parts, register_fonts
register_fonts()
PAPER, INK, MUTE, ACC = "#F2EDDF", "#2A2620", "#6E675A", "#B5532F"
df = pd.read_csv(os.path.join(DATA, "candidates_raw.csv")); GEO = pd.read_pickle(os.path.join(DATA, "deliver_geoms.pkl"))
# manual orientation overrides (deg CCW, applied on top of template orientation) after visual review
OVR = pd.read_csv(os.path.join(DATA, "orient_override.csv")) if os.path.exists(os.path.join(DATA, "orient_override.csv")) else pd.DataFrame(columns=["ingredient", "rank", "extra"])
for _, r in OVR.iterrows():
    k = (r.ingredient, int(r["rank"])); GEO[k] = affinity.rotate(GEO[k], r.extra, origin=(0, 0))
    i = df.index[(df.ingredient == r.ingredient) & (df["rank"] == int(r["rank"]))][0]; df.loc[i, "rotation_ccw_deg"] += r.extra
df["rotation_ccw_deg"] = df.rotation_ccw_deg % 360; df.to_csv(os.path.join(HERE, "candidates.csv"), index=False); pd.to_pickle(GEO, os.path.join(DATA, "final_geoms.pkl"))
def path_of(g):
    v, c = [], []
    for p in parts(g):
        for ring in [p.exterior, *p.interiors]:
            xy = np.asarray(ring.coords); v += list(xy); c += [MPath.MOVETO] + [MPath.LINETO] * (len(xy) - 2) + [MPath.CLOSEPOLY]
    return MPath(v, c)
def draw(ax, g, color=INK):
    ax.add_patch(PathPatch(path_of(g), fc=color, ec="none")); x0, y0, x1, y1 = g.bounds; s = max(x1 - x0, y1 - y0) * 0.56; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    ax.set_xlim(cx - s, cx + s); ax.set_ylim(cy - s, cy + s); ax.set_aspect("equal"); ax.set_axis_off()
ING = ["shell", "protein", "lettuce", "cheese", "tomato", "onion", "cilantro", "sour_cream"]
LAB = {"shell": "Shell / tortilla", "protein": "Protein", "lettuce": "Shredded lettuce", "cheese": "Shredded cheese", "tomato": "Diced tomato", "onion": "Diced onion", "cilantro": "Cilantro", "sour_cream": "Sour cream"}
cols = 4; W, H = 3.3, 3.5
fig = plt.figure(figsize=(1.9 + cols * W, 1.5 + len(ING) * H), dpi=150, facecolor=PAPER)
fig.text(0.5, 1 - 0.45 / (1.5 + len(ING) * H), "TACO TUESDAY · candidate polygons per ingredient", ha="center", va="top", family="Alegreya SC", size=26, color=INK)
fig.text(0.5, 1 - 0.95 / (1.5 + len(ING) * H), "Clean silhouettes in best-fit orientation, each scaled to fit its cell (not to a common scale). PICK = recommended. Score: template IoU, rotation every 5° plus reflection (cheese: bundle score).",
         ha="center", va="top", family="Alegreya Sans", size=11, color=MUTE)
for r_i, ing in enumerate(ING):
    sub = df[df.ingredient == ing].sort_values("rank"); top = 1 - (1.3 + r_i * H) / (1.5 + len(ING) * H)
    fig.text(0.012, top - 0.45 * H / (1.5 + len(ING) * H), LAB[ing].upper(), family="Barlow Condensed", size=17, color=ACC, weight="bold", rotation=90, va="center")
    for c_i, (_, r) in enumerate(sub.iterrows()):
        x0 = (1.9 + c_i * W) / (1.9 + cols * W); w = (W * 0.86) / (1.9 + cols * W); h = (H * 0.62) / (1.5 + len(ING) * H)
        ax = fig.add_axes([x0, top - h - 0.05 * H / (1.5 + len(ING) * H), w, h]); draw(ax, GEO[(ing, r["rank"])], INK)
        yl = top - h - 0.1 * H / (1.5 + len(ING) * H); f = 1.5 + len(ING) * H
        nm = ("PICK · " if r.recommended else "") + (r["name"] if len(r["name"]) < 38 else r["name"][:36] + "…")
        fig.text(x0, yl, nm, family="Alegreya Sans", weight="bold", size=10.5, color=ACC if r.recommended else INK, va="top")
        fig.text(x0, yl - 0.2 / f, f"{r.country} · {r.admin_level}", family="Alegreya Sans", size=9, color=INK, va="top")
        fig.text(x0, yl - 0.38 / f, f"{r.area_km2:,.0f} km² · {r.score_metric} {r.score:.3f} · rot {r.rotation_ccw_deg:.0f}°", family="Alegreya Sans", size=8.5, color=MUTE, va="top")
fig.savefig(os.path.join(HERE, "sheets", "taco_candidates_contact_sheet.png"), facecolor=PAPER); plt.close(fig)
print("ok")
