#!/usr/bin/env python3
"""Filled preview: clips Illustration's tiles (fill/tiles) into the final geometry with fill/clip_fill.py (imported, not modified),
composites assembled taco + exploded stack + Atlas text/leaders on #F3EDE0. Writes final/preview_filled.png (+ _300px)."""
import os, re, io, json, sys, numpy as np, cairosvg
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "fill"))
from clip_fill import clip_fill
F = os.path.join(HERE, "final"); TILES = os.path.join(HERE, "fill", "tiles"); TMP = os.path.join(HERE, "data", "filled_masks"); os.makedirs(TMP, exist_ok=True)
L = json.load(open(os.path.join(F, "layout.json"))); W, H, BG = L["canvas"]["width"], L["canvas"]["height"], L["canvas"]["background"]
SH = {"shell": (.30, 5), "shell_back": (.30, 5), "protein": (.38, 2), "lettuce": (.32, 3.5), "cheese": (.34, 2), "tomato": (.32, 2.5),
      "onion": (.55, 2.5), "cilantro": (.35, 2.5), "sour_cream": (.55, 4)}           # strength / width from fill/NOTES.md
SH_EXP = {"tomato": (.32, 1.5), "onion": (.55, 1.5)}
WARM_GREY = "#6E675A"   # onion dice: ~1.5 px warm-grey stroke (Director tweak); sour cream keeps the 45% ink stroke
STROKE = {"onion", "sour_cream"}; STROKE_CLR, STROKE_OP, STROKE_W = "#2A2620", 0.45, 1.75   # Illustration's request: thin warm ink stroke at 45%
canvas = Image.new("RGBA", (W, H), BG)
def d_of(svg): return re.search(r' d="([^"]+)"', open(svg).read()).group(1)
def bbox_pts(d, m=None):
    p = np.array([[float(a), float(b)] for a, b in re.findall(r"([-\d.]+),([-\d.]+)", d)])
    if m: a, b, c, dd, e, f = m; p = np.c_[a * p[:, 0] + c * p[:, 1] + e, b * p[:, 0] + dd * p[:, 1] + f]
    return p[:, 0].min(), p[:, 1].min(), p[:, 0].max(), p[:, 1].max()
def mask(name, d, m=None):
    x0, y0, x1, y1 = bbox_pts(d, m); x0, y0 = np.floor(x0) - 6, np.floor(y0) - 6; w, h = np.ceil(x1 - x0) + 7, np.ceil(y1 - y0) + 7
    tr = f' transform="matrix({",".join(f"{v:g}" for v in m)})"' if m else ""
    p = os.path.join(TMP, name + ".svg")
    open(p, "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" viewBox="{x0:.0f} {y0:.0f} {w:.0f} {h:.0f}"><path fill="#000" fill-rule="evenodd" d="{d}"{tr}/></svg>')
    return p, int(x0), int(y0), w, h, tr
def put(tile, name, d, m=None, sh=(.3, 3), stroke=False, sscale=1.0, sw=None):
    p, x0, y0, w, h, tr = mask(name, d, m)
    img, _ = clip_fill(os.path.join(TILES, tile + ".png"), p, 1.0, 2.0, sh[0], sh[1])
    canvas.alpha_composite(Image.fromarray(img, "RGBA"), (x0, y0))
    if stroke:
        s = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" viewBox="{x0} {y0} {w:.0f} {h:.0f}"><path fill="none" stroke="{STROKE_CLR if sw is None else WARM_GREY}" '
             f'stroke-opacity="{STROKE_OP if sw is None else 0.85}" stroke-width="{(STROKE_W if sw is None else sw) / sscale:.3f}" stroke-linejoin="round" fill-rule="evenodd" d="{d}"{tr}/></svg>')
        canvas.alpha_composite(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=s.encode()))).convert("RGBA"), (x0, y0))
ING = {i["id"]: i for i in L["ingredients"]}
def mat(sm): return [float(v) for v in sm[7:-1].split(",")]
# ---- assembled: follow layout.json assembled_taco.draw_list (back to front)
for k, it in enumerate(L["assembled_taco"]["draw_list"]):
    d = d_of(os.path.join(HERE, it["mask_svg"])); m = mat(it["transform"]) if it["transform"] else None
    if it.get("flat_fill"):
        canvas.alpha_composite(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><path fill="{it["flat_fill"]}" fill-rule="evenodd" d="{d}"/></svg>'.encode(), output_width=W, output_height=H))).convert("RGBA"))
    else: put(it["tile"], f"a_{k:02d}", d, m, sh=SH[it["tile"]], stroke=it["stroke"], sw=(it["stroke"] if not isinstance(it["stroke"], bool) else None))
# ---- guide axis under the stack, then exploded shapes (one per ingredient)
svg = open(os.path.join(F, "layout.svg")).read()
axis = re.search(r"<line [^>]*stroke-dasharray[^>]*/>", svg).group(0)
ov = lambda body: Image.open(io.BytesIO(cairosvg.svg2png(bytestring=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{body}</svg>'.encode(), output_width=W, output_height=H))).convert("RGBA")
canvas.alpha_composite(ov(axis))
for i in L["ingredients"]:
    ing = i["id"]; e = i["exploded"]
    if e["transform"]:
        m = mat(e["transform"]); put(ing, f"x_{ing}", d_of(os.path.join(HERE, i["svg"])), m, sh=SH[ing], stroke=ing in STROKE, sscale=float(np.sqrt(abs(m[0] * m[3] - m[1] * m[2]))))
    else:
        put(ing, f"x_{ing}", d_of(os.path.join(HERE, e["standalone_svg"])), sh=SH_EXP.get(ing, SH[ing]), stroke=ing in STROKE, sw=1.5 if ing == "onion" else None)
# ---- Atlas text layer: everything in layout.svg except background, shapes, axis
t = re.sub(r'<rect width="\d+" height="\d+" fill="[^"]+"/>', "", svg, count=1)
t = re.sub(r'<g id="assembled">.*?</g>', "", t, count=1, flags=re.S); t = re.sub(r'<g id="exploded">.*?</g>', "", t, count=1, flags=re.S); t = t.replace(axis, "")
canvas.alpha_composite(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=t.encode(), output_width=W, output_height=H))).convert("RGBA"))
out = canvas.convert("RGB"); out.save(os.path.join(F, "preview_filled.png"), optimize=True)
out.resize((300, 375), Image.LANCZOS).save(os.path.join(F, "preview_filled_300px.png"))
out.save(os.path.join(F, "day03_taco_tuesday.png"), optimize=True)                                   # FINAL graphic 2400x3000
out.resize((1200, 1500), Image.LANCZOS).save(os.path.join(F, "day03_taco_tuesday_1200.png"), optimize=True)   # web copy
print("ok", out.size)
