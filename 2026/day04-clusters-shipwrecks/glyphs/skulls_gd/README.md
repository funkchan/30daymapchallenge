# Day 4 outlier marks: skull and crossbones (glyphs_gd)

Original mark, built from circles, rounded rects and buffered lines (shapely), then exported as one flat path. Nothing is traced or taken from any reference map. Regenerate everything with `python3 make_skulls.py` (cairosvg). Earlier renders are kept as `_old-20261104`.

## Files
| File | What |
|---|---|
| `skull_ink.svg`, `skull_ink_20.png`, `skull_ink_40.png`, `skull_ink_128.png` | ink `#17120E`, single fill, transparent sockets, nose and teeth |
| `skull_bone.svg`, `skull_bone_20.png`, `skull_bone_40.png`, `skull_bone_128.png` | bone `#F1E4C3` over an ink halo at 65% (0.9 viewBox units, ~0.75 px at 20 px); sockets read dark |
| `option_B_*.svg`, `option_C_*.svg` | explored alternatives, not used |
| `proof.png` | backgrounds at 1× and 1200-equivalent, ×4 zooms, density patch, design comparison, contrast |
| `make_skulls.py` | source |

## Design
Winner **A**: bones crossed diagonally behind a rounded cranium, with knobbed ends, two sockets, a nose notch and two tooth slits. The viewBox is 24×24 and the silhouette is nearly square.
- **B** (bones under the jaw) is taller and reads as a pictogram rather than a point.
- **C** (skull only) turns into a dot at 10 px.

## Size and anchor
- **Anchor:** centre (12, 12) = **(0.5, 0.5)**. Each SVG carries `data-anchor` and `data-anchor-frac`.
- **Target:** **20 px** tall on the 2400×3000 render (10 px at 1200). Both variants use the same size.
- Why 20 px:
  - The current `×` is `s=170` pt² → √170 ≈ 13 pt ≈ 18 px at dpi 100.
  - Atlas's placeholder skull is `s=170×1.05` → ~18.5 px.
  - 20 px keeps the same visual weight but gives the sockets ~3 px each, the minimum that survives at 1200 (1.5 px).
  - In the Hatteras crop, neighbouring outliers mostly sit 20–40 px apart, so 20 px marks just touch in the tightest pairs and don't pile up. Going to 24 px would start overlapping in the Diamond Shoals scatter.
- **matplotlib:** with the marker scaled to its box, `s ≈ (20 px × 72/100)² ≈ 207` pt². Alternatively, place the PNG with an `OffsetImage` at its native 20 px with zoom 1 (40 px PNG at zoom 0.5 for crisper edges).
- Scale uniformly only.

## Which variant
- **Rule:** use **ink** where depth ≤ 200 m (shelf: parchment, tan or shallow-water tones), and **bone** beyond 200 m (deep teal). This matches render_g.py's existing `deep = od > 200`.
- **Luminance fallback:** use bone when the background's relative luminance is below 0.18.

## Colours and contrast (WCAG)
Sampled backgrounds from day04_v5_skulls.png: tan `#DCC38B`, shallow water `#C1C19C`, deep teal `#475C62`.

| Background | ink #17120E | bone #F1E4C3 | oxblood + #7A1A1A |
|---|---|---|---|
| parchment #E8D4A2 | **12.72** | 1.16 | 7.22 |
| tan #DCC38B | **10.82** | 1.36 | 6.14 |
| shallow #C1C19C | **10.07** | 1.46 | 5.72 |
| deep teal #475C62 | 2.63 | **5.59** | 1.49 |

On deep water, bone against its composited halo (`#282C2B`) is 11.19:1, and the halo against the teal is 2.0:1. The halo is a separator, not the main contrast.

## Distinct from the other marks
- The skull has no red, no plus and no hull. Cluster marks are oxblood `+` and the ships are horizontal hulls with smoke or fire, so the three differ in colour, shape and orientation (see the density patch in proof.png).

## Ship tiers
- **Unchanged.** `../glyphs/wreck_t1–t4` have no skulls or flags, so there's no clash. They're still valid with anchor (0.5, 0.78125).

## Caveats
- I estimated the spacing from the Hatteras crop rather than from the point data.
- The t2 size in the density patch (90 px) is a guess.
- At 10 px the teeth vanish (expected) and the mark reads as a dark blob with eyes.
- `matplotlib` path markers normalise to their bounding box, so check the final `s` against a 20 px tall mark.
