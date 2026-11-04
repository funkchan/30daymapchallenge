#!/usr/bin/env python3
"""Final handoff package: shared 2400x3000 canvas. Each ingredient path is stored at its ASSEMBLED position (identity transform);
the EXPLODED placement is a uniform scale + translate of the same path. Writes final/*.svg, final/standalone/*.svg, final/layout.json/svg, preview PNG."""
import os, json, numpy as np, pandas as pd, shapely
from shapely import affinity
from common import HERE, DATA, parts
OUT = os.path.join(HERE, "final"); W, H, BG = 2400, 3000, "#F3EDE0"
ORDER = ["shell", "protein", "lettuce", "cheese", "tomato", "onion", "cilantro", "sour_cream"]   # bottom -> top
LAB = {"shell": "Taco shell", "protein": "Ground beef", "lettuce": "Shredded lettuce", "cheese": "Shredded cheese", "tomato": "Diced tomato",
       "onion": "Diced onion", "cilantro": "Cilantro", "sour_cream": "Sour cream"}
# ---- SHELL CONFIG: the one place to swap the shell. (v8: geom = silhouette SVG in metres via data-metres-per-px, already rotated so the flat edge is down.)
#      Previous (Kochi, open crescent) config is in data/18_final_v7.py. rim = how the outline is read: the arc is the rim the fillings peek over,
#      the flat edge is the base. All filling positions derive from the front outline (dome centre on the flat edge + radial rays to the arc).
#      place/short/strip feed the labels; csv_rank marks the pick in candidates.csv.
SHELL_CFG = dict(geom="silhouettes/shell-dome_Wainwright_United-States_rot126ccw.svg", rim="arc up, flat edge down (front wall = closed dome; fillings peek over the arc)",
                 place=("Wainwright city, Alaska", "United States"), short="Wainwright, Alaska", strip="Wainwright", csv_rank="dome-1")
PLACE = {"shell": SHELL_CFG["place"], "protein": ("Chonos Archipelago", "Chile"), "lettuce": ("Iceland", "Iceland"),
         "cheese": ("Zadar islands (Dugi Otok, Ugljan, Pašman…)", "Croatia"), "tomato": ("Six NW Iowa counties", "United States"),
         "onion": ("Five La Pampa departments", "Argentina"), "cilantro": ("Halmahera", "Indonesia"), "sour_cream": ("Montalbán, Carabobo", "Venezuela")}
# ---- mark final picks in candidates.csv
c = pd.read_csv(os.path.join(HERE, "candidates.csv"), dtype={"rank": object})
c["final"] = False
for ing in ORDER:
    rk = "ground_beef-1" if ing == "protein" else (SHELL_CFG["csv_rank"] if ing == "shell" else "1"); c.loc[(c.ingredient == ing) & (c["rank"] == rk), "final"] = True
c["recommended"] = c["final"]; c.to_csv(os.path.join(HERE, "candidates.csv"), index=False)
F = c[c.final].set_index("ingredient"); assert len(F) == 8
# ---- base geometries (local equal-area metres, y up, best-fit rotation already applied)
GEO = pd.read_pickle(os.path.join(DATA, "final_geoms.pkl")); PG = pd.read_pickle(os.path.join(DATA, "protein_geoms.pkl"))
base = {ing: (PG["beef_aisen"][0] if ing == "protein" else GEO[(ing, 1)]) for ing in ORDER}
def svg_poly_m(path):   # silhouette SVG -> polygon in metres, y up
    import re as _re; t = open(os.path.join(HERE, path)).read(); mpp = float(_re.search(r'data-metres-per-px="([\d.]+)"', t).group(1))
    xy = [(float(a) * mpp, -float(b) * mpp) for a, b in _re.findall(r"([\d.]+),([\d.]+)", _re.search(r' d="([^"]+)"', t).group(1))]
    return shapely.Polygon(xy).buffer(0)
base["shell"] = svg_poly_m(SHELL_CFG["geom"])
EXTRA = {"lettuce": 90, "onion": 90}     # extra display rotation so the layer lies flat (lettuce as in the mockup)
# target size in canvas px for the ASSEMBLED taco (readable, not true scale): (max width, max height)
SIZE = {"shell": (1300, 720), "protein": (520, 430), "lettuce": (900, 420), "cheese": (820, 200), "tomato": (220, 150),
        "onion": (320, 90), "cilantro": (300, 330), "sour_cream": (250, 270)}
def to_canvas(g, ing):
    g = affinity.rotate(g, EXTRA.get(ing, 0), origin=(0, 0)); x0, y0, x1, y1 = g.bounds
    s = min(SIZE[ing][0] / (x1 - x0), SIZE[ing][1] / (y1 - y0))
    g = affinity.scale(affinity.translate(g, -(x0 + x1) / 2, -(y0 + y1) / 2), s, -s, origin=(0, 0))   # flip to y-down, centred at 0,0
    tol = max(SIZE[ing]) / 1500; return g.simplify(tol), s
# ---- matrices (canvas px, y down). geo0 = each layer centred at (0,0) at its exploded-base size (SIZE); the EXPLODED stack is built from geo0
#      exactly as before. The ASSEMBLED taco = A_i(geo0); stored paths are at the assembled position, so exploded matrix = E_i @ inv(A_i).
def MT(x, y): return np.array([[1, 0, x], [0, 1, y], [0, 0, 1.]])
def MS(sx, sy=None): return np.array([[sx, 0, 0], [0, sx if sy is None else sy, 0], [0, 0, 1.]])
def MR(deg):   # visual clockwise rotation in a y-down frame for positive deg
    t = np.radians(deg); return np.array([[np.cos(t), -np.sin(t), 0], [np.sin(t), np.cos(t), 0], [0, 0, 1.]])
def ap(g, M): return affinity.affine_transform(g, [M[0, 0], M[0, 1], M[1, 0], M[1, 1], M[0, 2], M[1, 2]])
def svgm(M): return [round(float(v), 5) for v in (M[0, 0], M[1, 0], M[0, 1], M[1, 1], M[0, 2], M[1, 2])]
geo0, scale_m = {}, {}
for ing in ORDER: geo0[ing], scale_m[ing] = to_canvas(base[ing], ing)
def wh(g): b = g.bounds; return b[2] - b[0], b[3] - b[1]
# ---- exploded (unchanged from v1): uniform scale K, centred on guide axis EX, spaced bottom-up
EX, K, GAP, Y_BOTTOM = 1500, 0.55, 146, 2800   # v11: GAP 146 so both columns start right under the taller title block (y ~ 345)
E = {}; yb = Y_BOTTOM
for ing in ORDER:
    h = wh(geo0[ing])[1] * K; E[ing] = MT(EX, yb - h / 2) @ MS(K); yb = yb - h - GAP
# ---- ASSEMBLED v8: classic side-view hard-shell taco (cartoon reference shell_search/ref.png). FRONT wall = the shell dome (flat edge down, arc up);
#      fillings sit BEHIND it and peek out along the arc; the LEFT open end shows the inside (beef + lettuce) against the BACK wall = a second real copy
#      offset up-left. Built untilted in a local frame (y down), then tilted about the dome centre and translated. Uniform scale + rotation only.
TILT, SHW = -3, 1080                     # tilt deg (neg = ccw on screen), front shell width px
BACK_OFF = (-0.09 * SHW, -0.03 * SHW)    # back wall offset: 9% of width to the left (the open end reads as a filled opening), 3% up
PEEK = 0.15                             # lettuce peeks this fraction of shell height beyond the front arc
REG = (60, None, 1340, 2060); LCX = (REG[0] + REG[2]) / 2
def put_m(ing, width, cx, cy, rot=0, g=None):
    g = ap(geo0[ing] if g is None else g, MR(rot)); b = g.bounds; s = width / (b[2] - b[0])
    return MT(cx - s * (b[0] + b[2]) / 2, cy - s * (b[1] + b[3]) / 2) @ MS(s) @ MR(rot), s * (b[3] - b[1])
def place_n(ing, s, p, rot):   # geo0 (centred at 0,0) scaled s, turned rot, centred at p
    return MT(*p) @ MR(rot) @ MS(s)
Lm, REP, PIECE = {}, {}, {}
L0 = MS(SHW / wh(geo0["shell"])[0]); front0 = ap(geo0["shell"], L0); SHH = wh(front0)[1]
fb = front0.bounds; CX = (fb[0] + fb[2]) / 2
def col(g, x): return g.intersection(shapely.LineString([(x, -1e5), (x, 1e5)])).bounds
CY = float(np.median([col(front0, x)[3] for x in np.linspace(fb[0] + 0.1 * SHW, fb[2] - 0.25 * SHW, 15)]))   # the flat edge (ignores the bottom-right hook)
C = np.array([CX, CY])
def u(ph): r = np.radians(ph); return np.array([np.cos(r), -np.sin(r)])
def ray(g, ph, R=3000):
    hit = g.intersection(shapely.LineString([tuple(C), tuple(C + R * u(ph))]))
    if hit.is_empty: return 0.0
    return max(np.hypot(*(np.asarray(gg.coords) - C).T).max() for gg in (hit.geoms if hasattr(hit, "geoms") else [hit]))
_PH = np.arange(0, 181, 1.0); _RF = np.array([ray(front0, p) for p in _PH])
def rF(ph): return float(np.interp(ph, _PH, _RF))
REP["shell"] = [MT(*BACK_OFF) @ L0]; back0 = ap(geo0["shell"], REP["shell"][0]); Lm["shell"] = L0
# lettuce x5 along the arc: each Iceland turned to the local normal, mostly hidden behind the front wall, top frills PEEK beyond the arc
LET_I = []; _w0, _h0 = wh(geo0["lettuce"])
for ph, w, jit in [(145, 0.24, 8), (128, 0.28, -6), (108, 0.28, 5), (90, 0.28, -4), (72, 0.28, 6), (54, 0.28, -7), (41, 0.24, 4)]:
    s = w * SHW / _w0; h = s * _h0; p = C + rF(ph) * u(ph) + u(ph) * (PEEK * SHH - h / 2)
    LET_I.append(place_n("lettuce", s, p, 90 - ph + jit))
_low = shapely.box(-1e5, CY - 0.45 * SHH, 1e5, 1e5).difference(shapely.union_all([front0, back0]))
print("lettuce outside shell low px2", [round(ap(geo0["lettuce"], m).intersection(_low).area) for m in LET_I])
Lm["lettuce"], REP["lettuce"] = LET_I[0], LET_I[1:]
LETU0 = shapely.union_all([ap(geo0["lettuce"], m) for m in LET_I])
_RL0 = np.array([ray(LETU0, p) for p in np.arange(-3, 184, 0.5)]); _RL = np.array([np.median(_RL0[k:k + 11]) for k in range(len(_RL0) - 10)])   # median over +/-2.5 deg
def rL(ph): return float(np.interp(ph, np.arange(-0.5, -0.5 + 0.5 * len(_RL), 0.5)[:len(_RL)] + 0.0, _RL))
# beef: the whole Chonos Archipelago (real arrangement, one uniform scale + turn) sitting inside the shell; its islands show as crumbs at the LEFT open end
ps = parts(geo0["protein"]); BACKIN = back0.buffer(-0.009 * SHW); OPEN0 = BACKIN.difference(front0)
OK = shapely.union_all([BACKIN, front0.buffer(-0.01 * SHW)])
# 8 latitude bands of Chonos (each keeps its real island arrangement; one uniform scale, each band a rigid group, turned) packed into the open end
cy_ = np.array([p.centroid.y for p in ps]); NB = 8; band = np.searchsorted(np.quantile(cy_, np.arange(1, NB) / NB), cy_); PIECE["protein"] = [None] * len(ps)
def pack(sB):   # one shared uniform scale for all bands; returns visible area and per-piece matrices
    seen, vis, P = shapely.Polygon(), 0.0, [None] * len(ps)
    for bi in range(NB):
        idx = [k for k in range(len(ps)) if band[k] == bi]; bg = shapely.MultiPolygon([ps[k] for k in idx]); c_ = bg.centroid; best = None
        for rot in range(0, 180, 15):
            for dx in np.linspace(-0.10, 0.06, 9):
                for dy in np.linspace(-0.06, -0.66, 13):
                    m = MT(fb[0] + dx * SHW, CY + dy * SHH) @ MR(rot) @ MS(sB) @ MT(-c_.x, -c_.y); g = ap(bg, m)
                    if g.difference(OK).area > 0.003 * g.area: continue
                    gi = g.intersection(OPEN0)
                    if seen.area and gi.intersection(seen).area > 0.15 * gi.area: continue
                    v = gi.difference(seen).area
                    if best is None or v > best[0]: best = (v, m, gi)
        if best is None: m = MT(CX, CY - 0.4 * SHH) @ MS(sB) @ MT(-c_.x, -c_.y); best = (0, m, shapely.Polygon())   # hidden behind the front wall
        vis += best[0]; seen = seen.union(best[2])
        for k in idx: P[k] = best[1]
    return vis, P, sB
vis_total, PIECE["protein"], sB = max((pack(v) for v in [1.0, 1.3, 1.6, 2.0]), key=lambda r: r[0])
print("beef visible px2", round(vis_total), "of open-end", round(OPEN0.area), "scale", sB)

# cheese x4 (v11): short Zadar shreds lying ALONG the rim (tangent to the arc), between the lettuce and the shell lip.
#   "tuck" shreds are drawn between lettuce copies and before the front wall: the front wall hides their lower edge, the next lettuce copy covers part.
#   "drape" shreds are drawn after the front wall but before the dice: centred just outside the lip so they hang a little over it; dice/cilantro occlude bits.
CHEESE_SPEC = [(118, "tuck", 2, 0.42), (63, "tuck", 5, 0.42), (139, "drape", None, 0.06), (47, "drape", None, 0.06)]   # (phi, mode, after lettuce #, radial frac of rF..rL)
CHW = 0.15 * SHW; CH = []; SUPPORT = shapely.union_all([LETU0, front0, back0])   # nothing may hang in empty air: search a small window for the best-supported spot
for ph, mode, after, fr in CHEESE_SPEC:
    s_ = CHW / wh(geo0["cheese"])[0]; th = s_ * wh(geo0["cheese"])[1]; best = None
    for dph in np.arange(-8, 8.1, 1):
        for f_ in (np.linspace(0.05, 0.6, 12) if mode == "tuck" else np.linspace(0.10, 0.50, 9)):
            p_ = ph + dph; r_ = rF(p_) + (f_ * (rL(p_) - rF(p_)) if mode == "tuck" else th * (0.5 - f_))   # drape: fraction f_ of the shred's thickness over the lip
            m = place_n("cheese", s_, C + u(p_) * r_, 90 - p_); out = ap(geo0["cheese"], m).difference(SUPPORT).area
            sc = out + 2 * abs(dph) + 30 * abs(f_ - (fr if mode == "tuck" else 0.3))
            if best is None or sc < best[0]: best = (sc, m, out, p_, f_)
    print("cheese", mode, "phi", best[3], "frac", round(best[4], 2), "px2 over empty air", round(best[2], 1)); CH.append(best[1])
Lm["cheese"], REP["cheese"] = CH[0], CH[1:]
# cilantro x4: small sprigs spread across the crown, 45% sunk into the lettuce
CI, CIH = [], 0.20 * SHH
for ph, j in [(140, -10), (116, 12), (64, -12), (40, 10)]:
    s = CIH / wh(geo0["cilantro"])[1]; CI.append(place_n("cilantro", s, C + u(ph) * (rL(ph) + CIH / 2 - 0.45 * CIH), 0.5 * (90 - ph) + j))
Lm["cilantro"], REP["cilantro"] = CI[0], CI[1:]
ci_top = min(ap(geo0["cilantro"], m).bounds[1] for m in CI)
# sour cream: horizontal centre of the crown, base sunk 30% into the lettuce, top = highest point of the taco
_h1 = wh(geo0["sour_cream"])[1]; base_y = CY - rL(90); top_need = min(ci_top, LETU0.bounds[1], back0.bounds[1]) - 0.06 * SHH
shh = max(0.26 * SHH, (base_y - top_need) / 0.70)
Lm["sour_cream"] = place_n("sour_cream", shh / _h1, (CX, base_y + 0.30 * shh - shh / 2), 0)
SC0 = ap(geo0["sour_cream"], Lm["sour_cream"])
# dice resting on the lettuce along the crown (centre just inside the lettuce surface); 3 extra dice repeat real pieces (assembled view only)
DIE = 0.048 * SHW; rng = np.random.default_rng(2026); placed = []   # fixed seed
_pre = shapely.union_all([front0, back0, LETU0, SC0] + [ap(geo0[i], m) for i in ["cheese", "cilantro"] for m in [Lm[i]] + REP[i]])
SEEDS = [shapely.Polygon(r).centroid for pp in parts(_pre) for r in pp.interiors if shapely.Polygon(r).area > 20]   # enclosed gaps in the lettuce: rest a die there
SEEDS = [p for p in SEEDS if not SC0.buffer(0.2 * DIE).contains(p)]
def die_spot(clear):
    while SEEDS:
        sd = SEEDS.pop(0); x, y = sd.x, sd.y
        if all((x - a) ** 2 + (y - b) ** 2 > (0.8 * DIE) ** 2 for a, b in placed):
            placed.append((x, y)); return x, y, 0
    for _ in range(20000):   # random scatter over the crown: random angle, depth (nestled to proud) and spacing (some overlap)
        ph = rng.uniform(32, 148); r = rF(ph) + rng.uniform(-0.15, 1.05) * max(rL(ph) - rF(ph), 0.5 * DIE); x, y = C + r * u(ph)
        dmin = rng.uniform(0.7, 1.6) * DIE
        if not SC0.buffer(clear * DIE).contains(shapely.Point(x, y)) and all((x - a) ** 2 + (y - b) ** 2 > dmin ** 2 for a, b in placed): break
    placed.append((x, y)); return x, y, 0
_n = len(parts(geo0["tomato"])) + len(parts(geo0["onion"])); SPOTS = [die_spot(0.1) for _ in range(_n)]; SPOTS = [SPOTS[k] for k in rng.permutation(_n)]   # mix tomato and onion along the crown
for ing in ["tomato", "onion"]:
    PIECE[ing] = []
    for p in parts(geo0[ing]):
        s_ = DIE / max(wh(p)); c = p.centroid; x, y, a = SPOTS.pop()
        PIECE[ing].append(MT(x, y) @ MR(rng.uniform(-50, 50)) @ MS(s_ * rng.uniform(0.9, 1.1)) @ MT(-c.x, -c.y))
EXTRA_DICE = {"tomato": [0, 3], "onion": [2]}; EXM = {}
for ing, ks in EXTRA_DICE.items():
    EXM[ing] = []
    for k in ks:
        p = parts(geo0[ing])[k]; s_ = DIE / max(wh(p)); c = p.centroid; x, y, a = die_spot(0.3)
        EXM[ing].append((k, MT(x, y) @ MR(rng.uniform(-50, 50)) @ MS(s_ * rng.uniform(0.9, 1.1)) @ MT(-c.x, -c.y)))
# tilt everything about the dome centre
RT = MT(*C) @ MR(TILT) @ MT(*(-C))
Lm = {i: RT @ m for i, m in Lm.items()}; REP = {i: [RT @ m for m in v] for i, v in REP.items()}
PIECE = {i: [RT @ m for m in v] for i, v in PIECE.items()}; EXM = {i: [(k, RT @ m) for k, m in v] for i, v in EXM.items()}
def inst(ing, m): return ap(geo0[ing], m)
def pieces(ing, Ms): return shapely.MultiPolygon([ap(p, m) for p, m in zip(parts(geo0[ing]), Ms)])
front = inst("shell", Lm["shell"]); back = inst("shell", REP["shell"][0]); LETU = shapely.union_all([inst("lettuce", m) for m in [Lm["lettuce"]] + REP["lettuce"]])
front_mask = front   # front wall = the full real outline (no frill breaks in this design)
# flat cast shadow: front+back silhouette flattened onto the ground
sil = shapely.union_all([front, back]); gy = sil.bounds[3]
shadow = ap(sil, MT(30, gy + 0.08 * SHH) @ MS(1.04, 0.14) @ MT(0, -gy))
# ---- translate: centre in the left column; top of the taco on the stack's top edge
locs = [front, back, shadow, LETU, pieces("protein", PIECE["protein"])] + [inst(i, m) for i in ["cheese", "cilantro"] for m in [Lm[i]] + REP[i]] + [inst("sour_cream", Lm["sour_cream"])]
lb_ = np.array([g.bounds for g in locs]); lx0, ly0, lx1 = lb_[:, 0].min(), lb_[:, 1].min(), lb_[:, 2].max()
TOP = ap(geo0["sour_cream"], E["sour_cream"]).bounds[1]; TT = MT(LCX - (lx0 + lx1) / 2, TOP - ly0)
AM = {i: TT @ Lm[i] for i in Lm}; XM = {i: E[i] @ np.linalg.inv(AM[i]) for i in AM}
PM = {i: [TT @ m for m in PIECE[i]] for i in PIECE}; XP = {i: [E[i] @ np.linalg.inv(m) for m in PM[i]] for i in PM}
geo = {i: (pieces(i, PM[i]) if i in PM else ap(geo0[i], AM[i])) for i in ORDER}
REPM = {i: [TT @ m @ np.linalg.inv(Lm[i]) @ np.linalg.inv(TT) for m in REP[i]] for i in REP}
REPG = {i: [ap(geo[i], m) for m in REPM[i]] for i in REPM}
FRONT_MASK, SHADOW, BACKG = ap(front_mask, TT), ap(shadow, TT), REPG["shell"][0]
EXG = {i: shapely.MultiPolygon([ap(parts(geo0[i])[k], TT @ m) for k, m in EXM[i]]) for i in EXM}
gexp = {i: ap(geo0[i], E[i]) for i in ORDER}
asm_scale = {i: float(np.sqrt(abs(np.linalg.det((AM[i] if i in AM else PM[i][0])[:2, :2])))) for i in ORDER}
# no-background check: no enclosed holes (cream) inside the drawn taco, and the open end (back wall minus front) is fully shell/filling
cover = shapely.union_all([geo[i] for i in ORDER] + [g for v in REPG.values() for g in v] + list(EXG.values()))
holes = shapely.union_all([shapely.Polygon(r) for p in parts(cover) for r in p.interiors]) if any(len(p.interiors) for p in parts(cover)) else shapely.Polygon()
gap = holes; print("enclosed cream holes px2", round(gap.area, 1), [tuple(round(v) for v in g.bounds) for g in parts(gap) if g.area > 20])
print("tacobbox", [round(v) for v in cover.bounds], "SHH", round(SHH), "DIE", round(DIE), "sour cream top", round(geo["sour_cream"].bounds[1]), "cover top", round(cover.bounds[1]))
LABEL_X = 1905
def d_of(g):
    out = []
    for p in parts(g):
        for ring in [p.exterior, *p.interiors]:
            xy = np.asarray(ring.coords)[:-1]; out.append("M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in xy) + " Z")
    return " ".join(out)
def disp_place(place, country): return place if place.split(",")[0].strip() == country else f"{place}, {country}"
def mstr(m): return "matrix(" + ",".join(f"{v:g}" for v in m) + ")"
def svgfile(path, gid, g): open(path, "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n<path id="{gid}" fill="#2A2620" fill-rule="evenodd" d="{d_of(g)}"/>\n</svg>\n')
def standalone(name, gid, g, title):
    b = g.bounds; pad = 6; tx0, ty0 = b[0] - pad, b[1] - pad; tw, th = b[2] - b[0] + 2 * pad, b[3] - b[1] + 2 * pad
    open(os.path.join(OUT, "standalone", f"{name}.svg"), "w").write(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{tw:.0f}" height="{th:.0f}" viewBox="{tx0:.1f} {ty0:.1f} {tw:.1f} {th:.1f}">\n<title>{title}</title>\n'
        f'<path id="{gid}" fill="#000" fill-rule="evenodd" d="{d_of(g)}"/>\n</svg>\n')
for f_ in os.listdir(os.path.join(OUT, "standalone")): os.remove(os.path.join(OUT, "standalone", f_))
# ---- assembled draw list (back to front). Each item: mask svg (+ optional matrix on it), tile or flat fill, stroke flag
DL = [dict(item="cast shadow (derived, flat)", mask_svg="final/standalone/cast_shadow.svg", transform=None, flat_fill="#E4DCCB", tile=None, stroke=False),
      dict(item="shell #2 = back wall (real Wainwright copy, offset up-left)", mask_svg="final/standalone/shell_back.svg", transform=None, tile="shell_back", stroke=False),
]
DL.append(dict(item="ground beef (whole Chonos inside the shell; shows at the left open end)", mask_svg="final/standalone/protein.svg", transform=None, tile="protein", stroke=False))
def cheese_item(j): return dict(item=f"cheese #{j+1} ({ {'tuck': 'tucked', 'drape': 'draped'}[CHEESE_SPEC[j][1]] } along the rim)", mask_svg="final/standalone/cheese.svg", transform=None if j == 0 else mstr(svgm(REPM["cheese"][j - 1])), tile="cheese", stroke=1.2)
for k in range(1 + len(REPM["lettuce"])):
    DL.append(dict(item=f"lettuce #{k+1} (peeks over the arc)", mask_svg="final/standalone/lettuce.svg", transform=None if k == 0 else mstr(svgm(REPM["lettuce"][k - 1])), tile="lettuce", stroke=False))
    DL += [cheese_item(j) for j, c_ in enumerate(CHEESE_SPEC) if c_[1] == "tuck" and c_[2] == k + 1]
DL.append(dict(item="shell #1 = front wall (the real Wainwright outline)", mask_svg="final/standalone/shell_front.svg", transform=None, tile="shell", stroke=False))
DL += [cheese_item(j) for j, c_ in enumerate(CHEESE_SPEC) if c_[1] == "drape"]
DL += [dict(item="tomato dice", mask_svg="final/standalone/tomato.svg", transform=None, tile="tomato", stroke=False),
       dict(item="tomato extra dice (repeats of 2 real counties)", mask_svg="final/standalone/tomato_extra.svg", transform=None, tile="tomato", stroke=False),
       dict(item="onion dice", mask_svg="final/standalone/onion.svg", transform=None, tile="onion", stroke=1.5),
       dict(item="onion extra die (repeat of 1 real department)", mask_svg="final/standalone/onion_extra.svg", transform=None, tile="onion", stroke=1.5)]
for k in range(1 + len(REPM["cilantro"])): DL.append(dict(item=f"cilantro #{k+1}", mask_svg="final/standalone/cilantro.svg", transform=None if k == 0 else mstr(svgm(REPM["cilantro"][k - 1])), tile="cilantro", stroke=False))
DL.append(dict(item="sour cream (crown)", mask_svg="final/standalone/sour_cream.svg", transform=None, tile="sour_cream", stroke=True))
lay = dict(canvas=dict(width=W, height=H, background=BG, units="px", y_axis="down"),
           notes="Each path in final/<n>_<ingredient>.svg is in canvas px at its (first) ASSEMBLED position (identity transform). EXPLODED = the SVG matrix given, applied to the same path "
                 "(protein/tomato/onion: one matrix per piece, in path subpath order, because those pieces are rearranged in the assembled taco). Shapes are sized to read as a taco, NOT to true scale; "
                 "true_area_km2 and metres_per_px_* record the real size. Stack order 1 = bottom. The assembled taco is drawn from assembled_taco.draw_list, NOT in stack order.",
           assembled_taco=dict(tilt_deg=-TILT, tilt_note=f"whole taco rotated {-TILT} deg counter-clockwise on screen; all outlines undistorted (uniform scale + rotation only)",
                               shell_width_px=round(SHW), lettuce_peek=f"{PEEK:.1%} of shell height beyond the front arc", back_wall_offset_px=[round(v, 1) for v in BACK_OFF],
                               draw_list=DL,
                               derived_masks=dict(cast_shadow="flat #E4DCCB: front+back shell silhouette squashed onto the ground (not a place)",
                                                  shell_front="front wall = the full real Wainwright outline (identical to standalone/shell.svg)"),
                               repeats_note=f"Assembled taco repeats: shell x2 (front + back wall), lettuce x{1+len(REP['lettuce'])}, cheese x{1+len(REP['cheese'])}, cilantro x{1+len(REP['cilantro'])} (same outline, same scale; transforms in ingredients[].assembled.repeats). "
                                            "The exploded stack keeps exactly one shape per ingredient; repeat counts show only on labels.",
                               pieces_note="Beef: Chonos cut into 8 latitude bands by island centroid; each band moved and turned as a rigid group (one uniform scale, in-band arrangement and outlines unchanged) and packed into the left open end, where its islands show as crumbs (the rest is hidden by the front wall). "
                                           "Tomato/onion: each county/department moved and turned (+/-50 deg, +/-10% size) as a die on the lettuce. Exploded stack shows original arrangements.",
                               enclosed_cream_px2=round(gap.area, 1)),
           guide_axis=dict(x=EX, y_top=yb + GAP, y_bottom=Y_BOTTOM), label_column_x=LABEL_X, ingredients=[])
for n, ing in enumerate(ORDER, 1):
    g = geo[ing]; r = F.loc[ing]; ge = gexp[ing]; bx = g.bounds
    svgfile(os.path.join(OUT, f"{n}_{ing}.svg"), ing, g)
    standalone(ing, ing, g, f"{LAB[ing]}: {disp_place(*PLACE[ing])}. Clip mask, assembled position #1 (shared canvas coordinates, tight viewBox).")
    if ing in XP: standalone(f"{ing}_exploded", ing, ge, f"{LAB[ing]}: {disp_place(*PLACE[ing])}. Clip mask, exploded position (original arrangement).")
    eb = ge.bounds; cyy = (eb[1] + eb[3]) / 2
    hit = ge.intersection(shapely.LineString([(eb[0] - 1, cyy), (eb[2] + 1, cyy)]))
    ax_ = max(np.asarray(gg.coords)[:, 0].max() for gg in (hit.geoms if hasattr(hit, "geoms") else [hit])) if not hit.is_empty else eb[2]
    if ing in XP: ex = dict(transform=None, per_piece_transforms=[mstr(svgm(M)) for M in XP[ing]], standalone_svg=f"final/standalone/{ing}_exploded.svg")
    else: ex = dict(transform=mstr(svgm(XM[ing])), matrix_abcdef=svgm(XM[ing]))
    ex["bbox"] = [round(v, 1) for v in eb]
    lay["ingredients"].append(dict(id=ing, stack_order=n, label=LAB[ing], place=PLACE[ing][0], country=PLACE[ing][1], display_place=disp_place(*PLACE[ing]), admin_level=r.admin_level,
        true_area_km2=round(float(r.area_km2), 1), n_pieces=len(parts(base[ing])), source=r.source, source_id=r.src_id, licence=r.licence,
        rotation_ccw_deg_from_north=float(r.rotation_ccw_deg) + EXTRA.get(ing, 0),
        metres_per_px_assembled=round(1 / (scale_m[ing] * asm_scale[ing]), 1), metres_per_px_exploded=round(1 / (scale_m[ing] * K), 1),
        svg=f"final/{n}_{ing}.svg", standalone_svg=f"final/standalone/{ing}.svg",
        assembled=dict(transform="matrix(1,0,0,1,0,0)", bbox=[round(v, 1) for v in bx], repeat_count=1 + len(REPM.get(ing, [])), repeats=[mstr(svgm(M)) for M in REPM.get(ing, [])]), exploded=ex,
        leader=dict(anchor_on_shape=[round(ax_ + 8, 1), round(cyy, 1)], elbow=[LABEL_X - 40, round(cyy, 1)], label_anchor=[LABEL_X, round(cyy, 1)])))
svgfile(os.path.join(OUT, "0_shell_back.svg"), "shell_back", BACKG); standalone("shell_back", "shell_back", BACKG, "Shell #2 = back wall: the real Wainwright outline, offset up-left. Assembled view only.")
standalone("shell_front", "shell_front", FRONT_MASK, "Shell #1 front wall: the real Wainwright outline. Assembled view only.")
for i in EXG: standalone(f"{i}_extra", i, EXG[i], f"{LAB[i]}: extra dice = repeats of real pieces (subpaths {EXTRA_DICE[i]}), assembled view only.")
lay["assembled_taco"]["extra_dice"] = {i: dict(piece_index=EXTRA_DICE[i], mask_svg=f"final/standalone/{i}_extra.svg", note="repeats of real pieces, assembled view only; stack and labels unchanged") for i in EXG}
svgfile(os.path.join(OUT, "0_cast_shadow.svg"), "cast_shadow", SHADOW); standalone("cast_shadow", "cast_shadow", SHADOW, "Flat cast shadow (derived, #E4DCCB). Assembled view only.")
for f_ in ["0_shell_back.svg", "0_cast_shadow.svg"]: pass
allg = [geo[i] for i in ORDER] + [g for v in REPG.values() for g in v] + [SHADOW] + list(EXG.values())
AB = np.array([g.bounds for g in allg]); TB = (AB[:, 0].min(), AB[:, 1].min(), AB[:, 2].max(), AB[:, 3].max())
lay["assembled_taco"]["bbox"] = [round(float(v), 1) for v in TB]
# ---- layout.svg + silhouette PNG: flat hint tones (Illustration's tiles replace them in 19_filled.py), guide axis, leaders, labels, true-scale strip, credits
TONE = {"shell": "#DDB767", "shell_back": "#B98E48", "protein": "#7A5038", "lettuce": "#A3B86C", "cheese": "#E9B640", "tomato": "#C95A42", "onion": "#F1ECE0", "cilantro": "#557D3B", "sour_cream": "#FBF8F1"}
INK, MUTE = "#2A2620", "#6E675A"
SHORT = {"shell": SHELL_CFG["short"], "cheese": "Zadar islands", "tomato": "6 NW Iowa counties", "onion": "5 La Pampa depts", "sour_cream": "Montalbán"}
def mpath(svgp): return re.search(r' d="([^"]+)"', open(os.path.join(HERE, svgp)).read()).group(1)
import re
s = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">', f'<rect width="{W}" height="{H}" fill="{BG}"/>',
     f'<text x="{W/2}" y="92" text-anchor="middle" font-family="Barlow Condensed" font-weight="bold" font-size="40" letter-spacing="8" fill="#B5532F">TACO TUESDAY</text>',
     f'<text x="{W/2}" y="212" text-anchor="middle" font-family="Alegreya SC" font-size="124" fill="{INK}">CARTO TO TACO</text>',
     f'<text x="{W/2}" y="284" text-anchor="middle" font-family="Alegreya Sans" font-size="50" fill="{MUTE}">Real places shaped like taco ingredients.</text>', '<g id="assembled">']
for it in DL:
    tr = f' transform="{it["transform"]}"' if it["transform"] else ""
    if it["flat_fill"] if "flat_fill" in it else False: s.append(f'<path d="{mpath(it["mask_svg"])}" fill="{it["flat_fill"]}" fill-rule="evenodd"/>')
    else: s.append(f'<path d="{mpath(it["mask_svg"])}"{tr} fill="{TONE[it["tile"]]}" fill-rule="evenodd" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>')
s += ["</g>", f'<line x1="{EX}" y1="{lay["guide_axis"]["y_top"]-40:.0f}" x2="{EX}" y2="{Y_BOTTOM+40}" stroke="{MUTE}" stroke-width="2" stroke-dasharray="14 10"/>', '<g id="exploded">']
for it in lay["ingredients"]:
    if it["id"] in XP: s.append(f'<path d="{d_of(gexp[it["id"]])}" fill-rule="evenodd" fill="{TONE[it["id"]]}" stroke="{INK}" stroke-width="3"/>')
    else: s.append(f'<path d="{d_of(geo[it["id"]])}" fill-rule="evenodd" transform="{it["exploded"]["transform"]}" fill="{TONE[it["id"]]}" stroke="{INK}" stroke-width="{3/np.sqrt(abs(np.linalg.det(XM[it["id"]][:2,:2]))):.2f}"/>')
s.append("</g><g id=\"leaders\">")
from PIL import ImageFont
for it in lay["ingredients"]:   # label fit check: heading (multiplier same size, part of the heading) and place line must end inside the canvas
    _rc = it["assembled"]["repeat_count"]; _h = f'{it["stack_order"]} · {it["label"].upper()}' + (f" ×{_rc}" if _rc > 1 else "")
    _p = (f"{_rc}× " if _rc > 1 else "") + disp_place(SHORT.get(it["id"], it["place"]), "USA" if it["country"] == "United States" else it["country"])
    _wh, _wp = ImageFont.truetype("/usr/share/fonts/truetype/sand-box/google/Barlow Condensed/BarlowCondensed-Bold.ttf", 48).getlength(_h), ImageFont.truetype("/usr/share/fonts/truetype/sand-box/google/Alegreya Sans/AlegreyaSans-Regular.ttf", 38).getlength(_p)
    assert LABEL_X + max(_wh, _wp) <= W - 40, (_h, _p, LABEL_X + max(_wh, _wp)); print("label right edge", round(LABEL_X + max(_wh, _wp)), _h)
for it in lay["ingredients"]:
    (x0, y0), (x1, y1), (x2, y2) = it["leader"]["anchor_on_shape"], it["leader"]["elbow"], it["leader"]["label_anchor"]; rc = it["assembled"]["repeat_count"]
    s.append(f'<circle cx="{x0}" cy="{y0}" r="7" fill="{INK}"/><polyline points="{x0},{y0} {x1},{y1} {x2-8},{y2}" fill="none" stroke="{INK}" stroke-width="2.5"/>'
             f'<text x="{x2}" y="{y2-8}" font-family="Barlow Condensed" font-weight="bold" font-size="48" fill="#B5532F">{it["stack_order"]} · {it["label"].upper()}{(" ×" + str(rc)) if rc > 1 else ""}</text>'
             f'<text x="{x2}" y="{y2+38}" font-family="Alegreya Sans" font-size="38" fill="{INK}">{(str(rc) + "× ") if rc > 1 else ""}{disp_place(SHORT.get(it["id"], it["place"]), "USA" if it["country"] == "United States" else it["country"])}</text>')
FINAL_TEXT = True   # final assembly: true-scale strip + credits (placeholders removed)
# ---- TRUE-SCALE strip (left column under the taco): all 8 places north-up at ONE shared scale. Areas are COMPUTED here from the equal-area geometries.
from PIL import ImageFont
FD = "/usr/share/fonts/truetype/sand-box/google/"
def tw(txt, f, sz): return ImageFont.truetype(FD + f, sz).getlength(txt)
REGF, ITF = "Alegreya Sans/AlegreyaSans-Regular.ttf", "Alegreya Sans/AlegreyaSans-Italic.ttf"
def true_geom(ing):   # undo the documented dice display treatment (each cube pulled 10% from the cluster centroid, shrunk to 92%) -> real geometry
    g = base[ing]
    if ing not in ("tomato", "onion"): return g
    c = g.centroid; out = []
    for q in parts(g):
        qc = q.centroid; pc = (c.x + (qc.x - c.x) / 1.10, c.y + (qc.y - c.y) / 1.10)
        out.append(affinity.translate(affinity.scale(q, 1 / 0.92, 1 / 0.92, origin=qc), pc[0] - qc.x, pc[1] - qc.y))
    return shapely.MultiPolygon(out)
TRUEG = {i: affinity.rotate(true_geom(i), -float(F.loc[i].rotation_ccw_deg), origin=(0, 0)) for i in ORDER}   # north up
AREA = {i: TRUEG[i].area / 1e6 for i in ORDER}
for i in ORDER: print("area", i, round(AREA[i], 1), "csv", F.loc[i].area_km2)
lay["true_scale_strip"] = {i: dict(area_km2_computed=round(AREA[i], 1)) for i in ORDER}
STRIP = {"shell": SHELL_CFG["strip"], "protein": "Chonos Is.", "lettuce": "Iceland", "cheese": "Zadar isl.", "tomato": "NW Iowa", "onion": "La Pampa", "cilantro": "Halmahera", "sour_cream": "Montalbán"}
STONE = dict(TONE, onion="#D8CCE2")   # strip only: onion tone darkened so it doesn't vanish into the cream background
BOLDF = "Barlow Condensed/BarlowCondensed-Bold.ttf"
# v11 layout (phone-readable): left column x 70..COLR. Strip in two rows at ONE shared scale (row 1 = the four big places, row 2 = the four small ones),
# then the credits fill the bottom-left. Everything left of the exploded stack.
X0, COLR, CRED_R = 70, 1225, 1125            # strip right edge (clear of the exploded lettuce), credits right edge (clear of the exploded shell)
SFH, SFN, SFA, SGAP = 40, 38, 36, 34         # strip: heading / name / area font sizes, gap between slots
ROW1 = ["lettuce", "cilantro", "onion", "tomato"]; ROW2 = ["protein", "cheese", "sour_cream", "shell"]
def lab_w(i): return max(tw(LAB[i].split()[-1].upper(), BOLDF, SFH), tw(STRIP[i], REGF, SFN), tw(f"{AREA[i]:,.0f} km²", REGF, SFA)) + 6
def sgeom(px):
    out = {}
    for i in ORDER:
        g = affinity.scale(TRUEG[i], px / 1000, -px / 1000, origin=(0, 0)); bb = g.bounds; out[i] = affinity.translate(g, -(bb[0] + bb[2]) / 2, -bb[3])
    return out
for PXKM in np.arange(2.0, 0.3, -0.01):   # largest shared scale at which row 1 fits the column
    sg = sgeom(PXKM); slot1 = {i: max(wh(sg[i])[0], lab_w(i)) for i in ROW1}; w1 = sum(slot1.values()) + SGAP * (len(ROW1) - 1)
    if w1 <= COLR - X0: break
hmax1 = max(wh(sg[i])[1] for i in ROW1); h2 = max(max(wh(sg[i])[1] for i in ROW2), 34)
print("strip px/km", round(PXKM, 2), "row1 width", round(w1), "row1 h", round(hmax1))
# credits block (wrapped by measured width, bottom-aligned at y 2960)
CFS, CLH = 38, 50
CPARA = [("Data: Natural Earth and US Census TIGER/Line (public domain). Via geoBoundaries (Runfola et al. 2020): Iowa counties, US Census (public domain); La Pampa departments © IGN Argentina, UNHCR, OCHA ROLAC (CC BY 3.0 IGO); Montalbán contains information from Efraín Porto Tapiquén, Geografía, SIG y Estudios Ambientales, made available under the ODbL 1.0.", MUTE, REGF, "", CFS),
         ("Map: @funkchan · #30DayMapChallenge Day 3: Polygons", INK, "Alegreya Sans/AlegreyaSans-Medium.ttf", ' font-weight="500"', 42)]
def wrap(txt, ff, fs, wmax):
    lines, cur = [], ""
    for w_ in txt.split(" "):
        t = (cur + " " + w_).strip()
        if tw(t, ff, fs) <= wmax: cur = t
        else: lines.append(cur); cur = w_
    return lines + [cur]
CLINES = []
for k, (txt, col, ff, ex, fs) in enumerate(CPARA):
    for ln in wrap(txt, ff, fs, CRED_R - X0): CLINES.append((ln, col, ff, ex, fs, k))
cred_h = sum(CLH if fs == CFS else 54 for (_, _, _, _, fs, _) in CLINES) + 18 * (len(CPARA) - 1)
CRED_TOP = 2960 - cred_h
# strip vertical stack: header (2 lines), row 1, labels, row 2, labels
HDR = ["North up at one shared scale; the taco above is resized to fit.", "Every outline is a real boundary: only uniform scaling and rotation."]
for t in HDR: assert tw(t, ITF, 37) <= COLR - X0, (round(tw(t, ITF, 34)), t)
LBLH = 46 + 44 + 42
strip_h = 52 + 2 * 44 + 30 + hmax1 + LBLH + 40 + h2 + LBLH
free = CRED_TOP - TB[3] - strip_h; assert free > 60, free
y0s = TB[3] + free * 0.45 + 40   # first baseline of the heading
base1 = y0s + 52 + 2 * 44 + 30 + hmax1; base2 = base1 + LBLH + 40 + h2
s.append(f'<g id="true_scale"><text x="{X0}" y="{y0s:.0f}" font-family="Barlow Condensed" font-weight="bold" font-size="54" letter-spacing="3" fill="#B5532F">ALL EIGHT AT TRUE SCALE</text>')
for k, t in enumerate(HDR): s.append(f'<text x="{X0}" y="{y0s + 50 + k * 44:.0f}" font-family="Alegreya Sans" font-style="italic" font-size="37" fill="{MUTE}">{t}</text>')
def slot_draw(i, cx, by):
    g = affinity.translate(sg[i], cx, by)
    s.append(f'<path d="{d_of(g)}" fill-rule="evenodd" fill="{STONE[i]}" stroke="{INK}" stroke-width="1.4" stroke-linejoin="round"/>')
    if max(wh(sg[i])) < 14: s.append(f'<circle cx="{cx:.1f}" cy="{by - wh(sg[i])[1] / 2:.1f}" r="{max(wh(sg[i])) / 2 + 11:.1f}" fill="none" stroke="{INK}" stroke-width="2"/>')
    s.append(f'<text x="{cx:.1f}" y="{by+46:.0f}" text-anchor="middle" font-family="Barlow Condensed" font-weight="bold" font-size="{SFH}" fill="#B5532F">{LAB[i].split()[-1].upper()}</text>'
             f'<text x="{cx:.1f}" y="{by+90:.0f}" text-anchor="middle" font-family="Alegreya Sans" font-size="{SFN}" fill="{INK}">{STRIP[i]}</text>'
             f'<text x="{cx:.1f}" y="{by+132:.0f}" text-anchor="middle" font-family="Alegreya Sans" font-size="{SFA}" fill="{MUTE}">{AREA[i]:,.0f} km²</text>')
x = X0
for i in ROW1: slot_draw(i, x + slot1[i] / 2, base1); x += slot1[i] + SGAP
slot2 = (COLR - X0) / len(ROW2)
for k, i in enumerate(ROW2): slot_draw(i, X0 + slot2 * (k + 0.5), base2)
# 100 km scale bar: top right of row 1, above the short tomato/onion shapes
SB_KM = 100; sb1 = X0 + w1; sb0 = sb1 - SB_KM * PXKM; sby = base1 - hmax1 + 40
assert sby + 10 < base1 - max(wh(sg[i])[1] for i in ["onion", "tomato"]) - 20, "scale bar hits a shape"
s.append(f'<line x1="{sb0:.1f}" y1="{sby:.0f}" x2="{sb1:.1f}" y2="{sby:.0f}" stroke="{INK}" stroke-width="4"/>'
         f'<line x1="{sb0:.1f}" y1="{sby-10:.0f}" x2="{sb0:.1f}" y2="{sby+10:.0f}" stroke="{INK}" stroke-width="4"/><line x1="{sb1:.1f}" y1="{sby-10:.0f}" x2="{sb1:.1f}" y2="{sby+10:.0f}" stroke="{INK}" stroke-width="4"/>'
         f'<text x="{(sb0+sb1)/2:.1f}" y="{sby-18:.0f}" text-anchor="middle" font-family="Alegreya Sans" font-size="36" fill="{INK}">{SB_KM} km</text></g>')
lay["true_scale_strip_px_per_km"] = round(float(PXKM), 3)
print("strip y", round(y0s - 50), "-", round(base2 + 132), " credits", round(CRED_TOP), "- 2960", len(CLINES), "lines")
# credits
y, prevk = CRED_TOP + 38, 0
for ln, col, ff, ex, fs, k in CLINES:
    if k != prevk and k == 1: y += 18   # gap between the data credits and the Map line
    prevk = k; assert X0 + tw(ln, ff, fs) <= CRED_R + 1
    s.append(f'<text x="{X0}" y="{y:.0f}" font-family="Alegreya Sans"{ex} font-size="{fs}" fill="{col}">{ln}</text>'); y += CLH if fs == CFS else 54
s.append("</g></svg>")
open(os.path.join(OUT, "layout.svg"), "w").write("\n".join(s))
json.dump(lay, open(os.path.join(OUT, "layout.json"), "w"), indent=1, ensure_ascii=False)
import cairosvg; cairosvg.svg2png(url=os.path.join(OUT, "layout.svg"), write_to=os.path.join(OUT, "preview_silhouettes.png"), output_width=W, output_height=H)
from PIL import Image; Image.open(os.path.join(OUT, "preview_silhouettes.png")).convert("RGB").resize((300, 375), Image.LANCZOS).save(os.path.join(OUT, "preview_300px.png"))
print("tacobbox", [round(v) for v in TB], "SHH", round(SHH))
