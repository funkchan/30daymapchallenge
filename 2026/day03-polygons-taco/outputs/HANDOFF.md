# Taco Tuesday: handoff for Director and Illustration
**#30DayMapChallenge 2026, Day 3 "Polygons". Prepared by Atlas, 3 Nov 2026.**

**FINAL v13 (3 Nov 2026; v12 dropped the display-liberties line and set the ×N multipliers at full heading size; v13 drops the fills credit), title "CARTO TO TACO" / "Real places shaped like taco ingredients." with a small "TACO TUESDAY" kicker:** Director passed the Wainwright taco and funkchan's tweaks are in (realistic cheese, new title, phone-readable layout); the final graphic is `final/day03_taco_tuesday.png` (2400 × 3000) plus `day03_taco_tuesday_1200.png`, with the caption, methods reply and alt text in `final/caption.md`. Not posted: funkchan posts it himself.

**The idea:** eight real places, one taco. Each taco layer is a real-world polygon whose outline looks like that ingredient. funkchan locked the picks on 3 Nov.

## The composition: an exploded-view breakout
Think of a modern scientific breakout diagram, the kind used in medical atlases and automotive exploded diagrams. There are two parts on one 2400 × 3000 px canvas (4:5), with a warm cream background, **#F3EDE0**:

1. **The assembled taco (left column, top), v8: Wainwright shell, classic side-view hard-shell taco** (modelled on `shell_search/ref.png`). The front wall is about 1080 px wide (enlarged from 1000 in v11) and the taco is tilted 3° counter-clockwise. Every outline is undistorted: only uniform scale and rotation, never stretched.
   - **Nothing is labelled inside the taco.**
   - **Two real Wainwright outlines** (Wainwright city, Alaska: a closed half-dome, flat edge down, arc up).
     - Shell #1 is the front wall: the full real outline. `standalone/shell_front.svg` is identical to `standalone/shell.svg`.
     - Shell #2 is the back wall (shell_back tile), offset 90 px left (9% of width) and 30 px up. That opens the LEFT end as a clear filled opening (as in `ref.png`), and the back wall also shows as a thin far rim behind the lettuce along the arc.
   - **The fillings sit behind the front wall and peek out along the arc.**
     - **Lettuce:** 7× Iceland, each turned to the arc's normal. They are mostly hidden behind the front wall; their frills peek about 15% of the shell height beyond the arc.
     - **Ground beef:** Chonos is cut into 8 latitude bands. Each band is moved and turned as a rigid group (one shared uniform scale; in-band arrangement and outlines unchanged) and packed into the left open end. There its islands show as dense crumbs against the back wall (about 37% of the opening); the rest is hidden by the front wall. No extra copies, so the label stays without a repeat count.
     - **Cheese (v11):** 4× short Zadar shreds (0.15 × shell width) lying along the rim, tangent to the arc, between the lettuce and the shell lip. Two are tucked: drawn after lettuce #2 / #5 and before the front wall, so the wall hides their lower edge and the next lettuce copy covers part. Two drape: drawn after the front wall but before the dice, about 30–50% of their thickness over the lip, so dice and cilantro occlude bits. Each spot is searched in a ±8° window to minimise cheese over empty air (now 0–41 px² per shred). Thin 1.2 px warm-grey edge (the tile is unchanged). This replaces the long v10 shreds, which hovered over the shell face.
     - **Dice:** the tomato and onion dice are scattered at random over the lettuce crown (fixed seed 2026). Their angle along the arc, depth (from nestled at the shell lip to sitting proud on the frills), spacing (0.7–1.6 die widths, so some overlap) and rotation (±50°) are all random, with ±10% uniform size jitter. Tomato and onion are mixed together, and any enclosed gaps in the lettuce are filled with a die first. Three extra dice repeat real pieces (2 Iowa counties, 1 La Pampa department): `standalone/tomato_extra.svg` and `onion_extra.svg`, assembled view only. Onion dice get a 1.5 px warm-grey (#6E675A) stroke.
     - **Cilantro:** 4× Halmahera, small sprigs spread across the crown, about 45% sunk into the lettuce.
     - **Sour cream:** the highest point of the taco, at the horizontal centre of the crown, with its base sunk about 30% into the lettuce.
   - **No cream background inside the taco:** the open end is entirely back wall or filling. Enclosed background specks between the lettuce frills total about 244 px² (largest about 17 × 22 px; `layout.json → assembled_taco.enclosed_cream_px2`).
   - **Cast shadow:** a flat #E4DCCB shadow (derived; the two shells' silhouette squashed onto the ground).
   - **Draw order is explicit:** `layout.json → assembled_taco.draw_list`, back to front. Each entry gives its mask SVG, an optional matrix, the tile (or `flat_fill`) and a stroke flag. The order is:
     1. cast shadow
     2. shell #2 (back wall)
     3. beef
     4. lettuce ×7
     5. shell #1 (front wall); the two tucked cheese shreds sit between lettuce copies (after #2 and #5)
     6. the two draped cheese shreds (1.2 px warm-grey edge)
     7. tomato, then the tomato extra dice
     8. onion, then the onion extra die (stroke)
     9. cilantro ×4
     10. sour cream (stroke)
   - **Display liberty:** none taken on the shell. The small coastal hook at Wainwright's bottom-right corner is kept; it doesn't hurt the read.
2. **The exploded stack (right).** It's the same eight shapes at 0.55 scale, spaced bottom to top along a dashed vertical guide axis (x = 1500). The shell is at the bottom and the sour cream at the top.
   - It has **exactly one shape per ingredient, with no ghost outlines.** A repeat shows only on the label: a small `×7` after the heading and `7× Iceland` on the place line.
   - Each layer has a leader line: a dot on the shape, a horizontal rule, then the label.
   - The labels sit in a column at x = 1950.

**Balance (v11, phone-readable):** a small TACO TUESDAY kicker, then CARTO TO TACO (124 px) and the subtitle (50 px). The stack gap is 146 px so both columns start at y ≈ 347. The left column runs: the taco (to y ≈ 1140), then ALL EIGHT AT TRUE SCALE in two rows at one shared scale (1.11 px/km; row 1 Iceland, Halmahera, La Pampa, Iowa; row 2 Chonos, Zadar, Montalbán, Wainwright with circle markers; 100 km bar), then the credits wrapped in the bottom-left (v13: y ≈ 2588–2960, kept left of the exploded shell). The methods block is dropped; its one-line essence ("every outline is a real boundary: only uniform scaling and rotation") is in the strip subtitle. Text sizes at 2400 px: stack labels 48/38 (v12: the ×N multiplier is part of the heading at the full 48 px, same accent colour; every label ends by x ≈ 2344, asserted in code), strip labels 40/38/36, credits 38 (about 19 px at 1200 px), map line 42.

## What I need from Illustration: one texture tile per ingredient
Please make **8 square texture tiles**, ideally 2048 × 2048 PNG and seamless.

- **Style:** flat illustration with a light texture and subtle grain.
- **Shadow:** a slight inner shadow at each polygon edge, so the layers read as stacked. Apply it after clipping, or tell me and I'll do it in code.
- **Clipping:** the tiles are clipped into the exact paths in code. Please don't redraw the outlines; they're real boundaries.
- **Lighting:** keep it consistent across all tiles, from the top left.

| # | Ingredient | Place (polygon) | Tile brief |
|---|---|---|---|
| 1 | Taco shell | Wainwright city, Alaska, USA (front + back wall) | Golden fried corn shell, warm yellow-tan, toasted speckles, faint blistering |
| 2 | Ground beef | Chonos Archipelago, Chile (20 islands) | Browned crumbles, warm red-brown with darker seared bits. Each island is one crumble, so the texture should read at crumb scale |
| 3 | Shredded lettuce | Iceland | Crisp iceberg green, pale ribs, fresh light-green to yellow-green |
| 4 | Shredded cheese | Zadar islands, Croatia (5 strips) | Cheddar shreds, yellow-orange, slight sheen along each strip |
| 5 | Diced tomato | 6 NW Iowa counties, USA (6 dice) | Ripe red tomato flesh with seed gel. The dice are near-square, so a cut-face look works |
| 6 | Diced onion | 5 La Pampa departments, Argentina (5 dice) | White onion, translucent, with faint layer rings |
| 7 | Cilantro | Halmahera, Indonesia | Deep green sprig, leaf veins, slightly darker edges |
| 8 | Sour cream | Montalbán, Carabobo, Venezuela | Glossy off-white dollop, soft swirl highlights |

The two dice layers (5 and 6) and the multi-piece layers (2 and 4) use one compound path each. Use a single tile across all the pieces.

## Files (`/workspace/atlas/30dmc/2026/day03-taco/final/`)
- **`0_shell_back.svg` / `standalone/shell_back.svg`:** shell #2, the back wall (a real Wainwright copy). **`standalone/shell_front.svg`:** the front wall (identical to the real outline). **`0_cast_shadow.svg` / `standalone/cast_shadow.svg`:** the flat shadow (derived). All three are for the assembled view only.
- **`1_shell.svg` … `8_sour_cream.svg`**
  - One file per ingredient, all in **one shared 2400 × 3000 coordinate space**.
  - Each is a single `<path id="<ingredient>">` (multi-piece is allowed) with `fill-rule="evenodd"`.
  - Each path is stored at its **assembled** position, already tilted and nested, so the assembled transform is the identity.
- **`standalone/<ingredient>.svg`**
  - The same path, with a tight viewBox, for clip masks.
  - The coordinates are still canvas px, so a mask lines up with no offset.
- **`standalone/protein_exploded.svg`, `tomato_exploded.svg` and `onion_exploded.svg`**: clip masks for the beef and dice in their exploded (original) arrangement.
- **`layout.json`**
  - Canvas size and background, `assembled_taco` (tilt, bbox, draw order, back wall, front-overlay note, repeats note, dice note), the guide axis and the label column.
  - Per ingredient: stack order, label, place, country, `display_place` (the label text), true area in km², piece count, source, licence, rotation, and m/px for both the assembled and exploded sizes.
  - The exploded transform is an SVG `matrix(a,b,c,d,e,f)` applied to the stored path. It includes the inverse of the tilt and the shell exaggeration, so the stack comes out upright and undistorted.
  - Protein, tomato and onion instead have `per_piece_transforms`: one matrix per subpath, in path order. That's because their pieces are rearranged in the assembled taco.
  - `assembled.repeat_count` and `assembled.repeats`. The repeat counts are shell 2, lettuce 7, cheese 2 and cilantro 4: the stored path, plus one matrix per extra copy.
  - Each bbox, plus `leader` points (anchor on the shape, the elbow, and the label anchor).
- **`layout.svg`:** the full layout, including the shell front overlay.
- **`preview_filled.png` and `preview_filled_300px.png`:** Illustration's tiles clipped into this geometry by `19_filled.py`, which uses `fill/clip_fill.py` and the shadow settings from `fill/NOTES.md`. The onion and sour cream get a 1.75 px ink stroke at 45% opacity.
- **`preview_silhouettes.png`:** a 2400 × 3000 render of `layout.svg`.

**Workflow:** follow `assembled_taco.draw_list` for the assembled taco; `19_filled.py` does exactly that. For the stack, use `exploded.transform`, or the `_exploded` masks for the beef and dice.

**Note for Illustration:** `fill/src/make_fills.py` still regenerates every standalone fill, but its QA exploded preview stops with `KeyError: 'matrix_abcdef'` on the protein, because the beef is now per-piece. The fix is to add `'protein'` to its `('tomato', 'onion')` `_exploded` special case. I did not edit it. It also doesn't fill `shell_front`, `cast_shadow` or `protein_exploded`; `19_filled.py` clips those itself.

**Display liberties** (all recorded in `layout.json`):
- The taco is tilted 3°.
- Repeats in the assembled taco: shell ×2, lettuce ×7, cheese ×4, cilantro ×4, plus 3 repeated dice.
- The beef is cut into 8 rigid latitude bands.
- The dice are re-scattered at random (seed 2026), rotated by up to ±50°, with ±10% size jitter; in the stack they are pulled 10% apart and shrunk to 92%.
- No mirroring anywhere.
- Lettuce and onion get an extra 90° display rotation.
- Nothing is stretched.

**Labels:** when the place name equals the country, the label shows it once, so the lettuce reads "7× Iceland", not "Iceland, Iceland". Repeat counts appear only on the stack labels (×2 shell, ×7 lettuce, ×4 cheese, ×4 cilantro; checked against `draw_list`: shell 2, lettuce 7, cheese 4, cilantro 4). The 3 repeated dice are not on the labels; the credits' display-liberties line states them..

## Scale note
The shapes are sized to read as a taco, **not to true scale**. Iceland is about 770 times the size of Montalbán. The real areas are in `layout.json` (`true_area_km2`), and the final graphic has a true-scale strip of all eight, north up at one shared scale (1.11 px/km in v11, two rows, 100 km bar). The strip's areas are computed by `18_final.py` from the equal-area geometries (dice restored to true size first) and stored in `layout.json → true_scale_strip`; they match candidates.csv (Iceland 102,362 km², Montalbán 133 km², Wainwright 37 km²; Iceland/Montalbán = 768×, Iceland/Wainwright = 2,744×).

## What Atlas handles
- All labels, leader lines, the title and subtitle, and the credits. Labels are final type, not part of the art.
- Final assembly in code once the tiles arrive.
- The caption and alt text for funkchan's review.

**Credits as set in the final graphic (v13, wrapped bottom-left, y ≈ 2588–2960): only the required outside data credits and the map line. The display-liberties line (v12) and the fills credit (v13) were dropped at funkchan's request; the liberties now live in `SOURCES_AND_CREDITS.md` and the methods reply. No fill credit anywhere: the fills are made in-house.**
> Data: Natural Earth and US Census TIGER/Line (public domain). Via geoBoundaries (Runfola et al. 2020): Iowa counties, US Census (public domain); La Pampa departments © IGN Argentina, UNHCR, OCHA ROLAC (CC BY 3.0 IGO); Montalbán contains information from Efraín Porto Tapiquén, Geografía, SIG y Estudios Ambientales, made available under the ODbL 1.0.
> Map: @funkchan · #30DayMapChallenge Day 3: Polygons

- Onion: CC BY 3.0 IGO, attribution required.
- Sour cream: ODbL, attribution required.
- Everything else is public domain.

## Swapping the shell
The shell is set in one place: `SHELL_CFG` at the top of `18_final.py`. It holds the silhouette SVG (read in metres through `data-metres-per-px`), how the outline is read (arc = rim, flat edge = base), the place and short label, and the candidates.csv rank. Every filling position is derived from the front outline: the dome centre on the flat edge, plus radial rays to the arc. The previous Kōchi build (open crescent, fillings in a bay) is saved as `data/18_final_v7.py`. The true-scale strip, methods note and final credits are on (`FINAL_TEXT = True`); the placeholders are gone. Backups: v8 = `data/18_final_v8.py`, pre-cheese-fix = `data/18_final_v9.py`, v10 (Taco Tuesday title, methods block) = `data/18_final_v10.py`, v11 (liberties line, small ×N) = `data/18_final_v11.py`, v12 (with the fills credit) = `data/18_final_v12.py`.
