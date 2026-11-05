"""Graveyards of the Sea: 4-tier shipwreck glyphs (flat SVG, no gradients/filters). python3 make_glyphs.py"""
import os, math, datetime, cairosvg
HERE = os.path.dirname(os.path.abspath(__file__))
C = dict(ox='#7A1A1A', black='#17120E', brass='#B8893A', bone='#F1E4C3')
AX, AY = 256, 400            # anchor: hull base centre at the waterline (viewBox px)
OUT = 14                     # final outline weight in viewBox px, same for every tier
TIERS = {1: .55, 2: .70, 3: .85, 4: 1.0}

def keep(path):
    if os.path.exists(path):
        d = datetime.date.today().strftime('%Y%m%d'); b, e = os.path.splitext(path); n = f'{b}_old-{d}{e}'; i = 0
        while os.path.exists(n): i += 1; n = f'{b}_old-{d}{chr(97+i)}{e}'
        os.rename(path, n)

def P(d, fill, sw=1, extra=''):
    return f'<path d="{d}" fill="{fill}" stroke="{C["black"]}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round" {extra}/>'

HULL = 'M-200 -40L-200 -125L-115 -125L-115 -82L150 -82L218 -118L172 -10L140 0L-160 0Z'
STRIPE = 'M-196 -80L154 -80L168 -48L-196 -48Z'
def flame(x, y, k, sw):
    def shape(kk):
        return (f'M{x} {y}C{x-42*kk} {y-8*kk} {x-52*kk} {y-70*kk} {x-14*kk} {y-128*kk}'
                f'C{x-4*kk} {y-92*kk} {x+24*kk} {y-86*kk} {x+18*kk} {y-150*kk}'
                f'C{x+62*kk} {y-92*kk} {x+60*kk} {y-18*kk} {x} {y}Z')
    return P(shape(k), C['ox'], sw) + P(shape(k*.62), C['brass'], sw*.8) + P(shape(k*.3), C['bone'], sw*.6)
def puff(cx, cy, r, sw):
    return P(f'M{cx-r} {cy}a{r} {r} 0 1 1 {2*r} 0a{r} {r} 0 1 1 {-2*r} 0Z', C['black'], sw)
def star(cx, cy, ro, ri, n, fill, sw, rot=0):
    pts = []
    for i in range(2*n):
        r = ro if i % 2 == 0 else ri; a = math.pi*i/n + rot
        pts.append(f'{cx+r*math.sin(a):.1f} {cy-r*math.cos(a):.1f}')
    return P('M' + 'L'.join(pts) + 'Z', fill, sw)
def plank(x, y, ang, sw, w=58, h=20):
    return f'<g transform="translate({x} {y}) rotate({ang})">' + P(f'M{-w/2} {-h/2}h{w}v{h}h{-w}Z', C['brass'], sw) + '</g>'
def keg(x, y, ang, sw):
    return (f'<g transform="translate({x} {y}) rotate({ang})">' + P('M-30 -40Q-42 0 -30 40H30Q42 0 30 -40Z', C['brass'], sw)
            + P('M-36 -16H36M-36 16H36', 'none', sw) + '</g>')
def water(sw, w=250):
    return P(f'M{-w} 50L{-w} 0Q{-w+40} -26 {-w+80} 0Q{-w+120} -26 {-w+160} 0L{w-160} 0Q{w-120} -26 {w-80} 0Q{w-40} -26 {w} 0L{w} 50Z', C['bone'], sw)
def ship(sw, mast, tilt, drop=0, holes=3):
    s = f'<g transform="translate(0 {drop}) rotate({tilt})">'
    if mast: s += P(f'M-18 -82V{-82-mast}l12 18 10 -22 14 16V-82Z', C['black'], sw)
    s += P(HULL, C['black'], sw) + P(STRIPE, C['ox'], sw*.7)
    for i in range(holes): s += P(f'M{-70+i*70-12} -28a12 12 0 1 1 24 0a12 12 0 1 1 -24 0Z', C['brass'], sw*.6)
    return s + '</g>'

def glyph(t):
    k = TIERS[t]; sw = OUT / k; g = []
    if t == 1:
        g += [ship(sw, 0, -24, drop=22, holes=2), water(sw, 230),
              P('M-150 -10Q-215 -70 -190 -150Q-160 -80 -120 -40Z', C['bone'], sw), P('M150 -10Q215 -70 196 -150Q160 -80 122 -40Z', C['bone'], sw),
              P('M-60 -150a22 22 0 1 1 44 0a22 22 0 1 1 -44 0Z', C['bone'], sw), P('M40 -170a16 16 0 1 1 32 0a16 16 0 1 1 -32 0Z', C['bone'], sw)]
    if t == 2:
        g += [puff(40, -265, 44, sw), puff(-15, -330, 56, sw), puff(75, -375, 38, sw),
              ship(sw, 150, -14), water(sw)]
    if t == 3:
        g += [puff(-60, -330, 56, sw), puff(20, -385, 46, sw),
              ship(sw, 100, -11), flame(-95, -100, 1.25, sw), flame(85, -100, 1.5, sw),
              plank(-225, -160, -30, sw, 70, 24), plank(215, -250, 25, sw, 70, 24), water(sw)]
    if t == 4:
        g += [star(0, -180, 210, 115, 8, C['ox'], sw, math.pi/8), star(0, -180, 120, 70, 8, C['brass'], sw, .39), star(0, -180, 55, 32, 6, C['bone'], sw*.8),
              ship(sw, 0, -8), flame(-120, -95, 1.15, sw), flame(130, -100, 1.15, sw), flame(5, -95, .8, sw),
              keg(200, -330, 30, sw), plank(-190, -310, -40, sw, 70, 24), plank(-205, -105, 20, sw, 70, 24), plank(210, -175, 60, sw, 70, 24),
              water(sw)]
    body = ''.join(g)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512" data-tier="{t}" data-scale="{k}" '
            f'data-anchor="{AX} {AY}" data-anchor-frac="0.5 0.78125">\n'
            f'<!-- Graveyards of the Sea, tier {t}. Anchor = hull base centre at the waterline: viewBox ({AX},{AY}) = (0.5, 0.78125) of the box. '
            f'Same for all tiers. Scale uniformly only. -->\n'
            f'<g id="anchor" data-anchor="{AX} {AY}"/>\n'
            f'<g transform="translate({AX} {AY}) scale({k})">{body}</g>\n</svg>\n')

if __name__ == '__main__':
    for t in TIERS:
        svg = glyph(t)
        for ext in ('svg', 'png'):
            p = os.path.join(HERE, f'wreck_t{t}.{ext}'); keep(p)
            if ext == 'svg': open(p, 'w').write(svg)
            else: cairosvg.svg2png(bytestring=svg.encode(), write_to=p, output_width=512, output_height=512)
