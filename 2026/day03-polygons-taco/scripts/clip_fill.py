#!/usr/bin/env python3
"""clip_fill.py - clip a seamless texture tile into an SVG mask with an exact-outline alpha.

Usage:
  python3 clip_fill.py TILE.png MASK.svg OUT.png [--scale 1] [--density 2] [--shadow 0.30] [--width 3]

* The mask SVG is rasterized with cairosvg at its own width/height (x --scale). The output alpha
  channel IS that rasterization, byte for byte; the outline is never redrawn, blurred, dilated or eroded.
* The tile is repeated to cover the mask, anchored to the shared canvas coordinates (viewBox origin), so
  the texture lines up between masks.  --density = tile px per canvas px (our tiles are 2x).
* Inner shadow: darkens RGB only, strictly inside the shape (alpha untouched). Uniform soft edge darkening
  plus a stronger bottom-right band (light from the top left). --width is in canvas px.
"""
import argparse, io, re
import numpy as np
import cairosvg
from PIL import Image
from scipy.ndimage import gaussian_filter, shift as ndshift


def render_mask(svg_path, scale=1.0):
    png = cairosvg.svg2png(url=svg_path, scale=scale)
    im = Image.open(io.BytesIO(png)).convert('RGBA')
    return np.array(im)[..., 3]


def viewbox(svg_path):
    txt = open(svg_path, encoding='utf-8').read()
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', txt).group(1).replace(',', ' ').split()]
    w = float(re.search(r'<svg[^>]*\swidth="([\d.]+)', txt).group(1))
    h = float(re.search(r'<svg[^>]*\sheight="([\d.]+)', txt).group(1))
    return vb, w, h


def clip_fill(tile_path, svg_path, scale=1.0, density=2.0, shadow=0.30, width=3.0):
    A = render_mask(svg_path, scale)
    H, W = A.shape
    vb, w, h = viewbox(svg_path)
    tile = Image.open(tile_path).convert('RGB')
    tn = max(1, round(tile.width * scale / density))           # tile period in output px
    t = np.array(tile.resize((tn, tn), Image.LANCZOS) if tn != tile.width else tile).astype(np.float32)
    ox = int(round(vb[0] * scale)) % tn; oy = int(round(vb[1] * scale)) % tn   # canvas-anchored
    ys = (np.arange(H) + oy) % tn; xs = (np.arange(W) + ox) % tn
    rgb = t[ys][:, xs]
    if shadow > 0:
        a = A.astype(np.float32) / 255.0
        wpx = width * scale
        pad = int(wpx * 4) + 2
        ap = np.pad(a, pad)
        uni = gaussian_filter(1 - ap, wpx)                              # soft all-round edge
        off = wpx * 0.9
        dirn = gaussian_filter(1 - ndshift(ap, (-off, -off), order=1, mode='constant'), wpx)  # bottom-right
        sh = np.clip(0.55 * uni + 0.65 * dirn, 0, 1)[pad:-pad, pad:-pad]
        sh = sh * (A > 0)
        rgb = rgb * (1 - shadow * sh[..., None])
    out = np.dstack([np.clip(rgb, 0, 255).astype(np.uint8), A])
    return out, A


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('tile'); p.add_argument('mask'); p.add_argument('out')
    p.add_argument('--scale', type=float, default=1.0)
    p.add_argument('--density', type=float, default=2.0)
    p.add_argument('--shadow', type=float, default=0.30)
    p.add_argument('--width', type=float, default=3.0)
    a = p.parse_args()
    img, A = clip_fill(a.tile, a.mask, a.scale, a.density, a.shadow, a.width)
    Image.fromarray(img, 'RGBA').save(a.out, optimize=True)
    print(a.out, img.shape[1], 'x', img.shape[0])
