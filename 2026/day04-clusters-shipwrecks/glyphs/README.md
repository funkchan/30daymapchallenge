# Graveyards of the Sea: wreck glyphs (#30DayMapChallenge 2026, Day 4: Clusters)

Flat, hand-built SVG: no gradients, filters or blur. Each tier has a transparent 512×512 PNG.

## Files
| File | What |
|---|---|
| `wreck_t1.svg` / `wreck_t1.png` … `wreck_t4.svg` / `wreck_t4.png` | glyphs |
| `make_glyphs.py` | source; `python3 make_glyphs.py` re-renders the SVG and PNG (cairosvg) |
| `fonts/` | the two TTFs plus their OFL texts |

If a glyph file is already there, `make_glyphs.py` renames it aside before writing. Those backups are not in the repo.

## Tiers
All tiers share one hull silhouette (stern castle, raked bow, oxblood gunwale stripe, brass ports) and one bone wave base. The outline is 14 viewBox px on every tier.

| Tier | Footprint scale | Content | Oxblood |
|---|---|---|---|
| T1 | 0.55 | sinking hull, stern down, bone splash | stripe only |
| T2 | 0.70 | listing wreck, broken mast, 3 smoke puffs | stripe |
| T3 | 0.85 | burning wreck: 2 flames, 2 smoke puffs, 2 planks | stripe + flames |
| T4 | 1.00 | powder-keg blast: 8-point burst, 3 flames, flying keg, 3 planks | burst + flames + stripe |

## Anchor (same for all tiers)
Hull base centre at the waterline: viewBox **(256, 400)** = **(0.5, 0.78125)** of the box. In each SVG it's `data-anchor="256 400"` and `data-anchor-frac="0.5 0.78125"` on the root, plus a comment and `<g id="anchor">`.

To place a glyph of size S at a map point (x, y): `left = x − 0.5·S`, `top = y − 0.78125·S`.

## Palette
| Role | Hex | vs parchment #E8D4A2 | vs stain #DCC38B | vs mid parchment #B8995F |
|---|---|---|---|---|
| Gunpowder black (all outlines, smoke, hull) | `#17120E` | 12.72 | 10.82 | 6.87 |
| Oxblood | `#7A1A1A` | 7.22 | 6.14 | 3.90 |
| Brass | `#B8893A` | 2.15 | 1.83 | 1.16 |
| Bone (highlight: wave, splash, flame core) | `#F1E4C3` | 1.16 | 1.36 | 2.14 |

- The black outline passes 4.5:1 on every parchment.
- Brass and bone only ever sit inside a black outline.
- Oxblood text works on light parchment; on mid parchment use it only at 14 px+ or keep labels black.
- Test parchments: `#E8D4A2` base, `#DCC38B` stains, `#B8995F` mid-tone.

## Scaling
- Scale uniformly only (keep 1:1, with the anchor fixed).
- Minimum size is 40 px for every tier; T1 is the limiting case. Below 40 px the 14 px outline drops under ~1 px and the splash and ports merge.
- Suggested sizes are 40 / 56 / 72 / 96 px, or one size for all, letting the built-in footprint carry the intensity.
- At 40 px the tiers separate by silhouette:
  - T1: low, with splashes
  - T2: a black smoke column
  - T3: red flames
  - T4: a red star burst

## Type pairing
**Pirata One** for the title + **IM Fell English** for the labels (12–14 px is legible).
- Pirata One: https://fonts.google.com/specimen/Pirata+One. SIL Open Font License 1.1.
- IM Fell English: https://fonts.google.com/specimen/IM+Fell+English. SIL Open Font License 1.1.
- IM Fell uses old-style figures. If label numbers need to line up, set them in Alegreya Sans (OFL) instead.
