#!/usr/bin/env python3
"""Day 2 (Lines) final render: landscape + portrait. Usage: python render.py [landscape|portrait|both]"""
import json, os, sys
import numpy as np, geopandas as gpd, shapely
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties as FP
from matplotlib import patheffects as pe
from matplotlib.patches import Circle, Rectangle, FancyBboxPatch
from pyproj import Transformer
import longest_lines as ll, imagery as I

HERE = ll.HERE; OUT = os.path.join(ll.ROOT, "outputs"); os.makedirs(OUT, exist_ok=True)
G = os.path.join(ll.ROOT, "fonts") + os.sep  # see scripts/00_fetch_data.py
F = dict(title=FP(fname=G + "Alegreya SC/AlegreyaSC-ExtraBold.ttf"), serif=FP(fname=G + "Alegreya SC/AlegreyaSC-Bold.ttf"),
         body=FP(fname=G + "Alegreya Sans/AlegreyaSans-Regular.ttf"), ital=FP(fname=G + "Alegreya Sans/AlegreyaSans-Italic.ttf"),
         med=FP(fname=G + "Alegreya Sans/AlegreyaSans-Medium.ttf"),
         cond=FP(fname=G + "Barlow Condensed/BarlowCondensed-SemiBold.ttf"), condb=FP(fname=G + "Barlow Condensed/BarlowCondensed-Bold.ttf"),
         condr=FP(fname=G + "Barlow Condensed/BarlowCondensed-Medium.ttf"))
PAPER, INK, MUTE, OCEAN, LAND = "#F3EFE4", "#23211C", "#6B665B", "#DDE5E6", "#E2DCCD"
# colour-blind-aware (Okabe-Ito-derived) line colours, themed to each biome
B = {  # code: (label, colour, from -> to, callout fraction along line, along_km, across_km)
    1: ("Tropical rainforest", "#009E73", ("Loja, Ecuador", "near São Luís, Brazil"), 0.31, 50, 1.15),
    2: ("Boreal forest · taiga", "#1F5F8B", ("Tver Oblast, Russia", "Amur Oblast"), 0.81, 50, 1.15),
    3: ("Temperate forest", "#7A9A01", ("La Rioja, Spain", "Bashkortostan, S Urals"), 0.31, 50, 1.15),
    4: ("Desert & xeric shrubland", "#D55E00", ("Nouadhibou, Mauritania", "near Port Sudan, Sudan"), 0.59, 50, 1.25),
    5: ("Grassland & savanna", "#C9A100", ("Quinara, Guinea-Bissau", "Tigray, Ethiopia"), 0.19, 50, 1.15),
    6: ("Tundra", "#9B6BB3", ("Nadym, Yamal-Nenets, Russia", "Lena Delta"), 0.81, 50, 1.15),
    7: ("Ice sheet", "#4FA3D9", ("Queen Maud Land coast", "Wilkes Land coast"), 500 / 4667, 110, None),
}
LINES = {o["code"]: o for o in json.load(open(os.path.join(ll.RESULTS, "final_lines.json")))}
EOX = I.ATTRIB
CREDITS = ("Biomes: RESOLVE Ecoregions 2017 (Dinerstein et al. 2017), CC BY 4.0  ·  Coastlines: Natural Earth (public domain)  ·  "
           f"Imagery: {EOX}, CC BY 4.0  ·  {I.GIBS_ATTRIB}")
TAG = "#30DayMapChallenge · Day 2 · Lines"
HANDLE = "@funkchan"
tf = Transformer.from_crs(4326, "EPSG:8857", always_xy=True); ti = Transformer.from_crs("EPSG:8857", 4326, always_xy=True)
XMAX = tf.transform(180, 0)[0]; YMAX = tf.transform(0, 90)[1]

def mix(c, w, base=LAND):
    a = np.array(matplotlib.colors.to_rgb(c)); b = np.array(matplotlib.colors.to_rgb(base)); return a * w + b * (1 - w)

def base_raster(W, H):
    xs = np.linspace(-XMAX, XMAX, W); ys = np.linspace(YMAX, -YMAX, H); X, Y = np.meshgrid(xs, ys)
    lon, lat = ti.transform(X, Y); valid = np.isfinite(lon) & np.isfinite(lat) & (np.abs(lat) <= 90)
    lon = np.where(valid, lon, 0); lat = np.where(valid, lat, 0)
    X2, Y2 = tf.transform(lon, lat); valid &= (np.abs(X2 - X) < 2000) & (np.abs(Y2 - Y) < 2000)  # round-trip: drop wrapped points outside the globe
    codes = ll.build_fine_raster(); c = ll.lookup(codes, ll.FINE, lat, lon)
    rgba = np.zeros((H, W, 4)); rgba[valid] = (*matplotlib.colors.to_rgb(OCEAN), 1)
    land = gpd.read_file(os.path.join(ll.DATA, "ne_10m_land.shp"))
    from rasterio import features
    from rasterio.transform import from_bounds
    lp = land.to_crs("EPSG:8857")
    lm = features.rasterize(((g, 1) for g in lp.geometry), out_shape=(H, W), transform=from_bounds(-XMAX, -YMAX, XMAX, YMAX, W, H), fill=0, dtype="uint8").astype(bool)
    lm |= (c > 0)
    rgba[valid & lm] = (*matplotlib.colors.to_rgb(LAND), 1)
    for k, v in B.items():
        rgba[valid & (c == k)] = (*mix(v[1], 0.36), 1)
    rgba[~valid] = 0
    return rgba, lp

def coast_lines(lp):
    segs = []
    for g in lp.geometry:
        for poly in getattr(g, "geoms", [g]):
            xy = np.asarray(poly.exterior.coords)
            lon, lat = ti.transform(xy[:, 0], xy[:, 1]); bad = (lat < -89.5) | (np.abs(lon) > 179.99)
            for part in np.split(np.arange(len(xy)), np.where(bad)[0]):
                part = part[~bad[part]] if len(part) else part
                if len(part) > 2: segs.append(xy[part])
    return segs

def line_xy(o, n=1500):
    p = I.line_pts(o["lon1"], o["lat1"], o["lon2"], o["lat2"], n); x, y = tf.transform(p[:, 0], p[:, 1]); return np.c_[x, y], p

def draw_map(ax, W, H):
    rgba, lp = base_raster(W, H)
    ax.imshow(rgba, extent=[-XMAX, XMAX, -YMAX, YMAX], interpolation="lanczos", zorder=1)
    from matplotlib.collections import LineCollection
    ax.add_collection(LineCollection(coast_lines(lp), colors="#8F8877", linewidths=0.35, zorder=2))
    # globe outline + faint 30-degree graticule
    lat = np.linspace(-90, 90, 200)
    for lo in (-180, 180):
        x, y = tf.transform(np.full_like(lat, lo), lat); ax.plot(x, y, color="#A9A291", lw=0.8, zorder=3)
    for lo in range(-150, 180, 30):
        x, y = tf.transform(np.full_like(lat, lo), lat); ax.plot(x, y, color="#FFFFFF", lw=0.35, alpha=0.6, zorder=1.5)
    for la in range(-60, 90, 30):
        lon = np.linspace(-180, 180, 200); x, y = tf.transform(lon, np.full_like(lon, la)); ax.plot(x, y, color="#FFFFFF", lw=0.35, alpha=0.6, zorder=1.5)
    for k, v in B.items():
        xy, _ = line_xy(LINES[k])
        ax.plot(xy[:, 0], xy[:, 1], color="white", lw=5.2, solid_capstyle="round", zorder=5)
        ax.plot(xy[:, 0], xy[:, 1], color=v[1], lw=3.0, solid_capstyle="round", zorder=6)
        ax.plot(xy[[0, -1], 0], xy[[0, -1], 1], "o", ms=4.2, color=v[1], mec="white", mew=1.0, zorder=7)
    ax.set_xlim(-XMAX * 1.002, XMAX * 1.002); ax.set_ylim(-YMAX * 1.004, YMAX * 1.004); ax.set_aspect("equal"); ax.axis("off")

def callout_point(k):
    o = LINES[k]; f = B[k][3]; p = I.line_pts(o["lon1"], o["lat1"], o["lon2"], o["lat2"], 2001)
    i = int(round(f * 2000)); i = min(i, 1999); lo, la = p[i]; az = I.GEOD.inv(lo, la, *p[i + 1])[0]
    return lo, la, az

_img_cache = {}
def boost(img, f):
    """mean-preserving contrast boost (keeps hue; makes dune/sastrugi texture readable)"""
    if f is None:  # ice: percentile stretch into 0.42-1.0 with a faint cool tint
        g = img.mean(-1); lo, hi = np.percentile(g, [0.5, 99.7])
        g = np.clip(0.52 + (g - lo) / (hi - lo) * 0.48, 0, 1); return np.clip(g[..., None] * np.array([0.93, 0.965, 1.0]) + np.array([0.0, 0.01, 0.02]), 0, 1)
    m = img.mean(axis=(0, 1), keepdims=True); return np.clip(m + (img - m) * f, 0, 1)

def panel_img(k, w, h):
    key = (k, w, h)
    if key in _img_cache: return _img_cache[key]
    lo, la, az = callout_point(k); along = B[k][4]; across = along * h / w
    if k == 7:
        img = I.panel_polar(lo, la, az, along, across, w, h)
    else:
        img, _ = I.panel(lo, la, az, along, across, w, h)
    img = boost(img, B[k][5])
    if k == 4: img = img ** 1.35  # richer sand tones (Sahara mosaic is near-white at this boost)
    _img_cache[key] = (img, along, across, az); return _img_cache[key]

def ribbon_img(k, w, h, across=60):
    key = ("r", k, w, h)
    if key in _img_cache: return _img_cache[key]
    o = LINES[k]
    if k == 7:
        img = boost(I.ribbon_polar(o["lon1"], o["lat1"], o["lon2"], o["lat2"], w, across, h), None)
    else:
        img = boost(I.ribbon(o["lon1"], o["lat1"], o["lon2"], o["lat2"], w, across, h, z=7), 1.1)
    _img_cache[key] = img; return img

def callout(fig, k, x, y, w, h, FW, FH, rib_h=26, fs=1.0, number=None):
    """x,y = top-left in px of the image panel; header drawn above (~70px), ribbon below."""
    label, col, route = B[k][0], B[k][1], B[k][2]; o = LINES[k]
    km = int(round(o["km"]))
    # header: BIOME (colour) + route on one line, big length below
    def T(px, py, txt, fp, size, color, ha="left", **kw):
        return fig.text(px / FW, 1 - py / FH, txt, fontproperties=fp, fontsize=size * fs, color=color, ha=ha, va="baseline", **kw)
    T(x + (58 * fs if number is not None else 0), y - 60 * fs, label.upper(), F["condb"], 12.5, col)
    T(x + (58 * fs if number is not None else 0), y - 12 * fs, f"{km:,} km", F["serif"], 21, INK)
    if number is not None:
        fig.text((x + 4 * fs) / FW, 1 - (y - 34 * fs) / FH, str(number), fontproperties=F["condb"], fontsize=13 * fs, color="white", ha="left", va="center",
                 bbox=dict(boxstyle="circle,pad=0.3", fc=col, ec="none"))
    # image
    img, along, across, az = panel_img(k, w, h)
    ax = fig.add_axes([x / FW, 1 - (y + h) / FH, w / FW, h / FH]); ax.imshow(img, extent=[0, along, 0, across], interpolation="lanczos")
    ax.plot([0, along], [across / 2] * 2, color="white", lw=4.4 * fs, alpha=0.9, solid_capstyle="butt")
    ax.plot([0, along], [across / 2] * 2, color=col, lw=2.4 * fs, solid_capstyle="butt")
    ax.set_xlim(0, along); ax.set_ylim(0, across); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_edgecolor(col); s.set_linewidth(2.2 * fs)
    sb = 10 if along <= 60 else 25
    x0, y0 = along * 0.035, across * 0.08
    ax.add_patch(Rectangle((x0, y0), sb, across * 0.022, color="white", ec=INK, lw=0.6))
    ax.text(x0 + sb + along * 0.012, y0 + across * 0.011, f"{sb} km", fontproperties=F["cond"], fontsize=8 * fs, color="white", va="center",
            path_effects=[pe.withStroke(linewidth=2.0, foreground="#000000AA")])
    # north arrow (panel is rotated so the line runs left-to-right)
    nx, ny = np.cos(np.radians(az)), np.sin(np.radians(az)); cx, cy = along * 0.955, across * 0.8; L = across * 0.11
    an = ax.annotate("", xy=(cx + nx * L, cy + ny * L), xytext=(cx - nx * L * 0.4, cy - ny * L * 0.4),
                arrowprops=dict(arrowstyle="-|>,head_width=0.25,head_length=0.5", color="white", lw=1.2 * fs, shrinkA=0, shrinkB=0))
    an.arrow_patch.set_path_effects([pe.withStroke(linewidth=2.6 * fs, foreground="#000000AA")])
    ax.text(cx + nx * L * 1.9, cy + ny * L * 1.9, "N", fontproperties=F["condb"], fontsize=7.5 * fs, color="white", ha="center", va="center",
            path_effects=[pe.withStroke(linewidth=1.8, foreground="#000000AA")])
    if k == 7:
        ax.text(along * 0.965, across * 0.07, "NASA MODIS imagery", fontproperties=F["cond"], fontsize=7 * fs, color=INK, ha="right", va="bottom", alpha=0.75)
    # ribbon (whole line, compressed along-track)
    rib = ribbon_img(k, w, rib_h)
    rax = fig.add_axes([x / FW, 1 - (y + h + 8 * fs + rib_h) / FH, w / FW, rib_h / FH]); rax.imshow(rib, aspect="auto", interpolation="lanczos")
    rax.axhline(rib_h / 2 - 0.5, color=col, lw=1.1 * fs, alpha=0.9)
    f = B[k][3]; half = along / o["km"] / 2 * w
    rax.add_patch(Rectangle((f * w - half - 1.5, -0.5), 2 * half + 3, rib_h, fill=False, ec="white", lw=1.4 * fs))
    rax.set_xticks([]); rax.set_yticks([]); [s.set_visible(False) for s in rax.spines.values()]
    yy = 1 - (y + h + 12 * fs + rib_h) / FH
    fig.text(x / FW, yy, route[0], fontproperties=F["ital"], fontsize=8.8 * fs, color=MUTE, va="top", ha="left")
    fig.text((x + w) / FW, yy, route[1], fontproperties=F["ital"], fontsize=8.8 * fs, color=MUTE, va="top", ha="right")

    return ax

def ring_and_leader(fig, mapax, k, anchor_px, FW, FH, ring_px=13, draw_leader=True, number=None, fs=1.0):
    lo, la, _ = callout_point(k); X, Y = tf.transform(lo, la)
    disp = mapax.transData.transform((X, Y)); fx, fy = fig.transFigure.inverted().transform(disp)
    col = B[k][1]
    ov = fig.add_axes([0, 0, 1, 1], facecolor="none"); ov.set_xlim(0, FW); ov.set_ylim(FH, 0); ov.axis("off"); ov.set_zorder(20)
    px, py = fx * FW, (1 - fy) * FH
    ov.add_patch(Circle((px, py), ring_px, fill=True, fc="#FFFFFF55", ec=INK, lw=1.3))
    ov.add_patch(Circle((px, py), ring_px, fill=False, ec="white", lw=0.6))
    if draw_leader:
        ax_, ay_ = anchor_px; dx, dy = ax_ - px, ay_ - py; d = np.hypot(dx, dy)
        sx, sy = px + dx / d * ring_px, py + dy / d * ring_px
        ov.plot([sx, ax_], [sy, ay_], color=INK, lw=0.8, alpha=0.8)
        ov.plot([ax_], [ay_], "o", ms=3, color=INK)
    if number is not None:
        ov.text(px + ring_px * 0.9, py - ring_px * 0.9, str(number), fontproperties=F["condb"], fontsize=10 * fs, color="white", ha="center", va="center",
                bbox=dict(boxstyle="circle,pad=0.2", fc=col, ec="white", lw=0.8))
    return ov

def landscape():
    FW, FH, DPI = 3000, 1688, 200
    fig = plt.figure(figsize=(FW / DPI, FH / DPI), dpi=DPI, facecolor=PAPER)
    mx0, mw = 535, 1930; mh = mw * YMAX / XMAX; my0 = 205
    mapax = fig.add_axes([mx0 / FW, 1 - (my0 + mh) / FH, mw / FW, mh / FH]); draw_map(mapax, int(mw * 2), int(mh * 2))
    fig.text(0.5, 1 - 28 / FH, "The World's Longest Straight Lines, by Biome", fontproperties=F["title"], fontsize=38, color=INK, ha="center", va="top")
    fig.text(0.5, 1 - 138 / FH, "The longest single geodesic, the straightest possible path over Earth's surface, that stays inside each biome",
             fontproperties=F["ital"], fontsize=14.5, color=MUTE, ha="center", va="top")
    PW, PH, RH = 465, 212, 24
    slots = {3: (45, 300), 4: (45, 715), 5: (45, 1130), 6: (FW - 45 - PW, 300), 2: (FW - 45 - PW, 715), 7: (FW - 45 - PW, 1130),
             1: (640, 1300)}
    for k, (x, y) in slots.items():
        callout(fig, k, x, y, PW, PH, FW, FH, rib_h=RH)
    for k, (x, y) in slots.items():
        if k == 1: anchor = (x + PW / 2, y - 92)
        elif x < FW / 2: anchor = (x + PW + 4, y + PH / 2)
        else: anchor = (x - 4, y + PH / 2)
        ring_and_leader(fig, mapax, k, anchor, FW, FH)
    import textwrap
    bx = 1235; by = my0 + mh + 75
    fig.text(bx / FW, 1 - by / FH, "How to read it", fontproperties=F["condb"], fontsize=12, color=INK, va="baseline")
    fig.text(bx / FW, 1 - (by + 18) / FH, "\n".join(textwrap.wrap(
        "Each bold line is one ellipsoidal geodesic (WGS84) that stays inside a single biome end to end; dots mark its ends. "
        "Soft fills show the seven biomes, grey land is every other biome. Close-ups follow each line for 50 km "
        "(110 km on the ice) and are rotated so the line runs left to right; the strip under each one squeezes the whole line, "
        "end to end, into one ribbon, and its white box marks the close-up.", 105)),
        fontproperties=F["body"], fontsize=9.6, color=MUTE, va="top", linespacing=1.3)
    fig.text(bx / FW, 1 - (by + 205) / FH, "Sources", fontproperties=F["condb"], fontsize=12, color=INK, va="baseline")
    fig.text(bx / FW, 1 - (by + 223) / FH, "\n".join([
        "Biomes: RESOLVE Ecoregions 2017 (Dinerstein et al. 2017), CC BY 4.0  ·  Land: Natural Earth (public domain)",
        "Imagery: " + EOX + ", CC BY 4.0",
        I.GIBS_ATTRIB + "  ·  Imagery contrast-adjusted"]),
        fontproperties=F["body"], fontsize=8.4, color=MUTE, va="top", linespacing=1.35)
    fig.text(bx / FW, 1 - (FH - 40) / FH, f"{TAG}   ·   {HANDLE}", fontproperties=F["condb"], fontsize=15, color=INK, va="baseline")
    out = os.path.join(OUT, "day02_lines_biomes.png"); fig.savefig(out, dpi=DPI, facecolor=PAPER); plt.close(fig); print(out)

def portrait():
    FW, FH, DPI = 2400, 3000, 200
    fig = plt.figure(figsize=(FW / DPI, FH / DPI), dpi=DPI, facecolor=PAPER)
    fig.text(0.5, 1 - 50 / FH, "The World's Longest\nStraight Lines, by Biome", fontproperties=F["title"], fontsize=44, color=INK, ha="center", va="top", linespacing=0.95)
    fig.text(0.5, 1 - 360 / FH, "The longest single geodesic, the straightest possible path over Earth's surface, that stays inside each biome",
             fontproperties=F["ital"], fontsize=14.5, color=MUTE, ha="center", va="top")
    mx0, mw = 60, FW - 120; mh = mw * YMAX / XMAX; my0 = 430
    mapax = fig.add_axes([mx0 / FW, 1 - (my0 + mh) / FH, mw / FW, mh / FH]); draw_map(mapax, int(mw * 1.6), int(mh * 1.6))
    order = [3, 4, 5, 1, 6, 2, 7]
    for n, k in enumerate(order, 1): ring_and_leader(fig, mapax, k, None, FW, FH, ring_px=16, draw_leader=False, number=n)
    cols, PW, PH, RH = 3, 720, 270, 26; gx = (FW - 3 * PW) / 4
    y0 = my0 + mh + 120; rowh = 480
    for n, k in enumerate(order):
        r, c = divmod(n, cols); x = gx + c * (PW + gx); y = y0 + r * rowh
        callout(fig, k, x, y, PW, PH, FW, FH, rib_h=RH, number=n + 1)
    import textwrap
    x = gx + 1 * (PW + gx); y = y0 + 2 * rowh - 70
    fig.text(x / FW, 1 - y / FH, "Sources", fontproperties=F["condb"], fontsize=12, color=INK, va="baseline")
    txt = "\n".join(["Biomes: RESOLVE Ecoregions 2017 (Dinerstein et al. 2017), CC BY 4.0", "Land: Natural Earth (public domain)",
                     "Imagery: " + EOX + ", CC BY 4.0", I.GIBS_ATTRIB, "Imagery contrast-adjusted. Grey land = other biomes.",
                     "Lines are ellipsoidal geodesics (WGS84) in Equal Earth projection."])
    txt = "\n".join(sum([textwrap.wrap(t, 118) for t in txt.split("\n")], []))
    fig.text(x / FW, 1 - (y + 18) / FH, txt, fontproperties=F["body"], fontsize=8.6, color=MUTE, va="top", linespacing=1.35)
    fig.text(x / FW, 1 - (y + 330) / FH, f"{TAG}   ·   {HANDLE}", fontproperties=F["condb"], fontsize=17, color=INK, va="baseline")
    out = os.path.join(OUT, "day02_lines_biomes_portrait.png"); fig.savefig(out, dpi=DPI, facecolor=PAPER); plt.close(fig); print(out)

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    if which in ("landscape", "both"): landscape()
    if which in ("portrait", "both"): portrait()
