"""Day 4 outlier marks: skull-and-crossbones, drawn from simple geometry. python3 make_skulls.py
Writes skull_ink/skull_bone SVG + PNGs (20, 40, 128 px), proof.png. Reads ../glyphs/wreck_t2.png (read only)."""
import os, io, random, math, datetime, cairosvg
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
INK, OX, BRASS, BONE, PARCH = '#17120E', '#7A1A1A', '#B8893A', '#F1E4C3', '#E8D4A2'
TAN, SHALLOW, DEEP = '#DCC38B', '#C1C19C', '#475C62'   # TAN/SHALLOW/DEEP sampled from outputs/day04_v5_skulls.png
SIZE = 20                                             # on-map px tall at 2400x3000 (10 px at 1200)

def keep(p):
    if os.path.exists(p):
        d = datetime.date.today().strftime('%Y%m%d'); b, e = os.path.splitext(p); n = f'{b}_old-{d}{e}'; i = 0
        while os.path.exists(n): i += 1; n = f'{b}_old-{d}{chr(97+i)}{e}'
        os.rename(p, n)

from shapely.geometry import Point, LineString, Polygon, box
from shapely.ops import unary_union
from shapely import affinity

def bone(x0, y0, x1, y1, w=2.3, k=1.45):
    a = math.atan2(y1-y0, x1-x0); nx, ny = -math.sin(a)*k*.75, math.cos(a)*k*.75
    parts = [LineString([(x0, y0), (x1, y1)]).buffer(w/2, cap_style=2)]
    for (x, y) in ((x0, y0), (x1, y1)):
        for sg in (1, -1): parts.append(Point(x+sg*nx, y+sg*ny).buffer(k, 32))
    return unary_union(parts)

def rrect(x, y, w, h, r): return box(x+r, y+r, x+w-r, y+h-r).buffer(r, 16)
def skull(r=6.6, dy=0):
    g = unary_union([Point(12, 10).buffer(r, 48), rrect(8.4, 12, 7.2, 6.4, 1.6)])
    return affinity.translate(g, 0, dy)
def holes(dy=0):
    g = unary_union([Point(9.5, 10.6).buffer(2.0, 32), Point(14.5, 10.6).buffer(2.0, 32), Polygon([(12, 12.9), (10.9, 15), (13.1, 15)]),
                     box(10.35, 16.4, 11.1, 18.6), box(12.9, 16.4, 13.65, 18.6)])
    return affinity.translate(g, 0, dy)
# A (winner): bones crossed behind the skull; B: bones crossed under the jaw; C: skull only
def shape(d):
    if d == 'A': return unary_union([bone(3.6, 3.6, 20.4, 20.4), bone(20.4, 3.6, 3.6, 20.4), skull()]).difference(holes())
    if d == 'B': return unary_union([skull(dy=-1.6), bone(4.2, 17.2, 19.8, 22.4), bone(19.8, 17.2, 4.2, 22.4)]).difference(holes(-1.6))
    return skull(7.4).difference(holes())

def pd_(g):
    out = []
    for poly in getattr(g, 'geoms', [g]):
        for ring in [poly.exterior, *poly.interiors]:
            c = list(ring.coords); out.append('M' + 'L'.join(f'{x:.2f} {y:.2f}' for x, y in c[:-1]) + 'Z')
    return ''.join(out)

def svg(variant, d='A'):
    g = shape(d)
    head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" data-anchor="12 12" data-anchor-frac="0.5 0.5">\n'
            f'<!-- Day 4 outlier mark ({variant}, design {d}). Original geometry. Anchor = centre (12,12) = (0.5,0.5). Scale uniformly. -->\n')
    if variant == 'ink':
        return head + f'<path fill="{INK}" fill-rule="evenodd" d="{pd_(g)}"/>\n</svg>\n'
    halo = g.buffer(0.9, 16)   # ~0.75 px halo at 20 px; sockets shrink but stay dark
    return (head + f'<path fill="{INK}" fill-opacity=".65" fill-rule="evenodd" d="{pd_(halo)}"/>\n'
            f'<path fill="{BONE}" fill-rule="evenodd" d="{pd_(g)}"/>\n</svg>\n')

def png(s, px): return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=s.encode(), output_width=px, output_height=px))).convert('RGBA')

def L(h):
    c = [int(h[i:i+2], 16)/255 for i in (1, 3, 5)]; c = [x/12.92 if x <= .03928 else ((x+.055)/1.055)**2.4 for x in c]
    return .2126*c[0]+.7152*c[1]+.0722*c[2]
def cr(a, b): a, b = L(a), L(b); return (max(a, b)+.05)/(min(a, b)+.05)

def plus(d, x, y, s=18, w=3):
    d.line((x-s/2, y, x+s/2, y), fill=OX, width=w); d.line((x, y-s/2, x, y+s/2), fill=OX, width=w)

def proof():
    W, H = 1500, 1360; im = Image.new('RGB', (W, H), PARCH); d = ImageDraw.Draw(im)
    d.text((24, 16), f'Day 4 outlier skulls - proof. Design A (winner). On-map size {SIZE} px at 2400 (= {SIZE//2} px at 1200). Zoom panels are x4 nearest-neighbour of the 1x pixels.', fill=INK)
    bgs = [('parchment', PARCH, 'ink'), ('tan', TAN, 'ink'), ('shallow water', SHALLOW, 'ink'), ('deep teal', DEEP, 'bone')]
    for i, (nm, bg, v) in enumerate(bgs):
        x = 24 + i*368; d.rectangle((x, 44, x+350, 330), fill=bg)
        d.text((x+8, 50), f'{nm} {bg} - {v} (and the other variant, right)', fill=INK if v == 'ink' else BONE)
        for j, vv in enumerate((v, 'bone' if v == 'ink' else 'ink')):
            xo = x + 10 + j*175
            g1, g2, gp = png(svg(vv), SIZE), png(svg(vv), SIZE//2), png(svg(vv), 128)
            im.paste(gp, (xo, 70), gp); im.paste(g1, (xo, 210), g1); im.paste(g2, (xo+40, 215), g2)
            z1 = Image.new('RGBA', (SIZE, SIZE), bg); z1.alpha_composite(g1); z1 = z1.resize((SIZE*4, SIZE*4), Image.NEAREST); im.paste(z1, (xo, 238))
            z2 = Image.new('RGBA', (SIZE//2, SIZE//2), bg); z2.alpha_composite(g2); z2 = z2.resize((SIZE*2, SIZE*2), Image.NEAREST); im.paste(z2, (xo+90, 238))
            d.text((xo, 322), f'{vv}: 128 / {SIZE} / {SIZE//2} px', fill=INK if bg != DEEP else BONE)
    # density patch at 1x: left half parchment->shallow, right deep
    py = 370; pw, ph = 900, 440
    patch = Image.new('RGB', (pw, ph), SHALLOW); pd = ImageDraw.Draw(patch)
    pd.rectangle((0, 0, 330, ph), fill=PARCH); pd.rectangle((330, 0, 560, ph), fill=TAN); pd.rectangle((560, 0, pw, ph), fill=DEEP)
    r = random.Random(4); pts = []
    while len(pts) < 60:
        x, y = r.uniform(12, pw-12), r.uniform(12, ph-12)
        if all((x-a)**2+(y-b)**2 > 20**2 for a, b in pts) and not (380 < x < 520 and 120 < y < 300): pts.append((x, y))
    gi, gb = png(svg('ink'), SIZE), png(svg('bone'), SIZE)
    for x, y in pts:
        g = gb if x > 560 else gi; patch.paste(g, (int(x-SIZE/2), int(y-SIZE/2)), g)
    for x, y in ((420, 140), (440, 158), (405, 165), (470, 150), (450, 185), (430, 200), (480, 210), (700, 120), (690, 140)):
        plus(pd, x, y)
    t2 = Image.open(os.path.join(HERE, '..', 'glyphs', 'wreck_t2.png')).convert('RGBA').resize((90, 90), Image.LANCZOS)
    patch.paste(t2, (400, 200), t2)
    im.paste(patch, (24, py + 20)); d.text((24, py), 'Density patch at 1x (2400 render): 60 skulls, min spacing 20 px; red + cluster marks (18 px, 3 px) and a t2 ship (90 px, guess)', fill=INK)
    sm = patch.resize((pw//2, ph//2), Image.LANCZOS); im.paste(sm, (950, py + 20)); d.text((950, py), 'same patch at 1200 px equivalent (50%)', fill=INK)
    # design comparison
    cy = 860; d.text((24, cy), 'Design options (ink on parchment, bone on deep): 128 / 20 / 10 px. A = bones behind skull (WINNER), B = bones under jaw, C = skull only', fill=INK)
    for i, dz in enumerate('ABC'):
        x = 24 + i*490; d.rectangle((x, cy+20, x+470, cy+200), fill=PARCH); d.rectangle((x+235, cy+20, x+470, cy+200), fill=DEEP)
        for j, vv in enumerate(('ink', 'bone')):
            xo = x + 10 + j*235
            for k_, s in enumerate((128, SIZE, SIZE//2)):
                g = png(svg(vv, dz), s); im.paste(g, (xo + (0, 140, 180)[k_], cy + 40), g)
        d.text((x+8, cy+184), f'{dz}' + (' - winner' if dz == 'A' else ''), fill=INK)
    # contrast table
    ty = 1090; d.text((24, ty), 'Contrast (WCAG):', fill=INK)
    for i, (nm, bg) in enumerate((('parchment', PARCH), ('tan', TAN), ('shallow', SHALLOW), ('deep teal', DEEP))):
        d.text((24, ty+20+i*16), f'{nm} {bg}: ink {cr(INK, bg):.2f}  bone {cr(BONE, bg):.2f}  oxblood + {cr(OX, bg):.2f}', fill=INK)
    p = os.path.join(HERE, 'proof.png'); keep(p); im.crop((0, 0, W, 1180)).save(p)

if __name__ == '__main__':
    for v in ('ink', 'bone'):
        s = svg(v); p = os.path.join(HERE, f'skull_{v}.svg'); keep(p); open(p, 'w').write(s)
        for px in (SIZE, SIZE*2, 128):
            p = os.path.join(HERE, f'skull_{v}_{px}.png'); keep(p); png(s, px).save(p)
    for dz in 'BC':
        for v in ('ink', 'bone'):
            p = os.path.join(HERE, f'option_{dz}_skull_{v}.svg'); keep(p); open(p, 'w').write(svg(v, dz))
    proof()
    for bg in (PARCH, TAN, SHALLOW, DEEP): print(bg, 'ink', round(cr(INK, bg), 2), 'bone', round(cr(BONE, bg), 2), 'ox', round(cr(OX, bg), 2))
    print('bone vs halo-ink', round(cr(BONE, INK), 2))
