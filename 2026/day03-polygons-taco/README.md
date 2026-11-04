# Day 3 (Taco Tuesday): Carto to Taco, real places shaped like taco ingredients

## Deliverables
- `sheets/taco_candidates_contact_sheet.png`: 3 or 4 candidates per ingredient. Clean silhouettes in best-fit rotation, no template overlay, labelled with place, country, level, area, score and rotation.
- `sheets/taco_stack_mockup.png`: rough stack of the picks with placeholder tints, plus a strip showing them at true relative scale.
- `candidates.csv`: source, ID, licence, rotation (degrees CCW from north-up), score, area and the "reads as" verdict.
- `silhouettes/`: SVG plus transparent PNG (2000 px on the long side) for each pick.
- `SOURCES_AND_CREDITS.md`

## Update 3 Nov (round 3): multi-piece protein and land-cover colour
- funkchan wants the protein in **multiple pieces**, like the cheese. `10_protein.py` groups Natural Earth 10m land and minor-island parts by proximity and scores the groups:
  - **Ground beef:** many similar-size, irregular pieces in a round, dense clump.
  - **Chicken:** several elongated pieces, any orientation.
  - `12_handpicks.py` scores named archipelagos with the same metrics.
- `13_white_dollop.py` matches the dollop template against Natural Earth playas and glaciated areas.
- `14_colour.py`, `15_thumbs.py` and `16_colour_scan.py` check Sentinel-2 cloudless 2016 true colour.
- `17_protein_deliver.py` builds:
  - `sheets/protein_candidates_contact_sheet.png`
  - `sheets/landcover_check.png`
  - the silhouettes `protein-beef_*` and `protein-chicken_*`. The SVGs carry `data-metres-per-px` so they can be put back at true relative scale.
- candidates.csv:
  - The protein rows now use string ranks (`ground_beef-N`, `chicken-N`, and `single-N` for the superseded single-shape protein rows).
  - The colour columns are added.
  - The pre-update copy is `data/candidates_pre_protein_v2.csv`.
  - Re-running `08_sheet.py` would overwrite this file from candidates_raw.csv, so don't.
- **Layout decision (from Atlas):** the final graphic is a modern scientific exploded view, like a medical or automotive breakout diagram. The assembled taco sits on one side, and the same layers are spaced out along a guide axis, with leader lines to the place-name labels. All silhouettes must export in one shared coordinate space, with stack order and offsets in JSON, so the same paths work in both the assembled and the exploded placement.

## FINAL (3 Nov, locked by funkchan)
The final picks are:
- Shell: Wainwright city, Alaska (US Census places 1:500k; replaced Kōchi on 3 Nov, approved by funkchan)
- Protein: ground beef, Chonos Archipelago
- Lettuce: Iceland
- Cheese: Zadar islands
- Tomato: 6 NW Iowa counties
- Onion: 5 La Pampa departments
- Cilantro: Halmahera
- Sour cream: Montalbán

In candidates.csv these rows have `final` set to True, and `recommended` matches `final`. `18_final.py` builds `final/` (the shared-canvas SVGs, standalone clip-mask SVGs, layout.json, layout.svg, the preview and HANDOFF.md).

## Pipeline
`01_pool.py`, then `02_match.py`, `03_cheese.py`, `04_round2.py`, `05_review2.py`, `06_review3.py` (review grids in data/), then `07_deliver.py`, `08_sheet.py`, `09_export.py`.

The silhouette rotation is the template best-fit angle. For cilantro, the north-up view reads better, so `data/orient_override.csv` sets it.

## Final graphic (3 Nov 2026, Director passed)
- `final/day03_taco_tuesday.png` (2400 × 3000) and `final/day03_taco_tuesday_1200.png` (1200 × 1500), built by `python3 18_final.py && python3 19_filled.py`.
- `final/caption.md`: caption (272 characters, starts "Carto to Taco:"), a two-part methods reply and alt text, for funkchan to post himself.
- `18_final.py` with `FINAL_TEXT = True` adds the title CARTO TO TACO (TACO TUESDAY kicker), a two-row true-scale strip (areas computed from the equal-area geometry, one shared scale, 100 km bar) and the full credits; the methods note was dropped in v11 for phone readability (it lives in the methods reply). Placeholders are gone.
- Assembled taco: Wainwright shell ×2 (front and back wall), 8-band Chonos beef in the open end, Iceland lettuce ×7, Zadar cheese ×4 tucked and draped along the rim, randomly scattered dice (seed 2026), Halmahera cilantro ×4, Montalbán sour cream on top. Details are in `final/HANDOFF.md`.
- Backups of earlier builds are in `data/18_final_v*.py`.
- `fill/src/make_fills.py` still stops with `KeyError: 'matrix_abcdef'`; it isn't needed, because `19_filled.py` clips the tiles itself.
