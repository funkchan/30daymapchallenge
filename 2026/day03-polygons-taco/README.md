# Day 3 (Taco Tuesday): Carto to Taco, real places shaped like taco ingredients

**#30DayMapChallenge 2026, Day 3 (Polygons).**

Eight real boundary polygons, one taco. The finished graphic is an exploded-view diagram: the assembled taco on the left, the same layers spaced along a guide axis on the right, with leader lines to the place names. Only uniform scaling and rotation are used.

## Deliverables

- `outputs/taco_candidates_contact_sheet.png`: 3 or 4 candidates per ingredient. Clean silhouettes in best-fit rotation, no template overlay, labelled with place, country, level, area, score and rotation.
- `outputs/taco_stack_mockup.png`: rough stack of the picks with placeholder tints, plus a strip showing them at true relative scale.
- `results/candidates.csv`: source, ID, licence, rotation (degrees CCW from north-up), score, area and the "reads as" verdict. Rows with `final` True are the picks; `recommended` matches `final`.
- `results/shell_dome_candidates.csv`: closed-dome shell search.
- `outputs/silhouettes/`: SVG plus transparent PNG (2000 px on the long side) for each pick.
- `SOURCES_AND_CREDITS.md`

## Update 3 Nov (round 3): multi-piece protein and land-cover colour

- The protein is in **multiple pieces**, like the cheese. `scripts/10_protein.py` groups Natural Earth 10m land and minor-island parts by proximity and scores the groups:
  - **Ground beef:** many similar-size, irregular pieces in a round, dense clump.
  - **Chicken:** several elongated pieces, any orientation.
  - `scripts/12_handpicks.py` scores named archipelagos with the same metrics.
- `scripts/13_white_dollop.py` matches the dollop template against Natural Earth playas and glaciated areas.
- `scripts/14_colour.py`, `scripts/15_thumbs.py` and `scripts/16_colour_scan.py` check Sentinel-2 cloudless 2016 true colour. The thumbnails they write (`data/s2/*_thumb.png`) stay in the local `data/` folder and are not committed.
- `scripts/17_protein_deliver.py` builds:
  - `outputs/protein_candidates_contact_sheet.png`
  - `outputs/landcover_check.png`
  - the silhouettes `outputs/silhouettes/protein-beef_*` and `protein-chicken_*`. The SVGs carry `data-metres-per-px` so they can be put back at true relative scale.
- `results/candidates.csv`:
  - The protein rows use string ranks (`ground_beef-N`, `chicken-N`, and `single-N` for the superseded single-shape protein rows).
  - The colour columns are included.
  - The pre-update copy (`candidates_pre_protein_v2.csv`) and `candidates_raw.csv` are pipeline products under `scripts/data/`. They are not in the repo.
  - Re-running `scripts/08_sheet.py` rewrites its working `candidates.csv` from `scripts/data/candidates_raw.csv`. The committed table is `results/candidates.csv`.
- **Layout:** the final graphic is a modern scientific exploded view, like a medical or automotive breakout diagram. The assembled taco sits on one side, and the same layers are spaced out along a guide axis, with leader lines to the place-name labels. All silhouettes share one coordinate space, with stack order and offsets in `outputs/layout.json`, so the same paths work in both the assembled and the exploded placement.

## Final picks (3 Nov)

- Shell: Wainwright city, Alaska (US Census places 1:500k; replaced Kōchi on 3 Nov)
- Protein: ground beef, Chonos Archipelago
- Lettuce: Iceland
- Cheese: Zadar islands
- Tomato: 6 NW Iowa counties
- Onion: 5 La Pampa departments
- Cilantro: Halmahera
- Sour cream: Montalbán

`scripts/18_final.py` lays out the shared-canvas SVGs, standalone clip masks, `layout.json`, `layout.svg` and the silhouette preview. The committed copies of those files are under `outputs/` (not a `final/` directory). `scripts/19_filled.py` clips the illustrated fills and writes the finished PNGs. A separate tile generator is not part of this folder and is not required.

## Final graphic (3 Nov 2026)

- `outputs/day03_taco_tuesday.png` (2400 × 3000) and `outputs/day03_taco_tuesday_1200.png` (1200 × 1500), built by `python3 scripts/18_final.py && python3 scripts/19_filled.py`.
- `outputs/preview_silhouettes.png` and `outputs/preview_300px.png`: silhouette renders of `outputs/layout.svg`.
- `outputs/preview_filled_300px.png`: 300 × 375 preview of the filled graphic. The full-size `preview_filled.png` was a byte-for-byte copy of `day03_taco_tuesday.png` and is not kept.
- `outputs/caption.md`: caption (272 characters, starts "Carto to Taco:"), a two-part methods reply and alt text, for funkchan to post himself.
- `scripts/18_final.py` with `FINAL_TEXT = True` adds the title CARTO TO TACO (TACO TUESDAY kicker), a two-row true-scale strip (areas computed from the equal-area geometry, one shared scale, 100 km bar) and the full credits; the methods note was dropped in v11 for phone readability (it lives in the methods reply). Placeholders are gone.
- Assembled taco: Wainwright shell ×2 (front and back wall), 8-band Chonos beef in the open end, Iceland lettuce ×7, Zadar cheese ×4 tucked and draped along the rim, randomly scattered dice (seed 2026), Halmahera cilantro ×4, Montalbán sour cream on top. Details are in `outputs/HANDOFF.md`.
- Earlier drafts of `scripts/18_final.py` (v7–v12, including the Kōchi shell) are not in the repo. They were local working copies under `data/`.

## Data (not committed)

`data/` is downloaded or generated on your machine and is not committed (see `.gitignore`). Two local folders:

- `scripts/data/`: the layers and derived tables the scripts read and write (`common.DATA`). Examples: `ne_10m_geography_regions_polys.shp`, `ne_10m_minor_islands.shp`, `geoBoundariesCGAZ_ADM2.gpkg`, `islands.gpkg`, `pool.csv`, `candidates_raw.csv`, `orient_override.csv`, `final_geoms.pkl`, `protein_geoms.pkl`, and `s2/` thumbnails.
- `day03-polygons-shapes/data/`: Natural Earth 1:10m admin-1 and land, via `D3` in `scripts/common.py`.

Rebuild them from the sources in `SOURCES_AND_CREDITS.md`:

| Data | Where to get it |
|---|---|
| Natural Earth 1:10m Admin-1, Land, Geography Regions (polygons), Minor Islands, Playas, Glaciated Areas | [naturalearthdata.com](https://www.naturalearthdata.com) (public domain) |
| US Census TIGER/Line cartographic boundary places, 2023, 1:500k | [census.gov cartographic boundary files](https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html) (public domain) |
| geoBoundaries CGAZ ADM2 | [geoboundaries.org](https://www.geoboundaries.org) |

The checked-in candidate tables are only `results/candidates.csv` and `results/shell_dome_candidates.csv`.

## Fonts (not committed)

Measurement and the contact sheets use three SIL Open Font License families from [Google Fonts](https://fonts.google.com) ([github.com/google/fonts](https://github.com/google/fonts)):

| Family | Files | Put them here |
|---|---|---|
| Alegreya SC | `AlegreyaSC-Regular.ttf` | `fonts/Alegreya SC/` |
| Alegreya Sans | `AlegreyaSans-Regular.ttf`, `AlegreyaSans-Italic.ttf`, `AlegreyaSans-Medium.ttf` | `fonts/Alegreya Sans/` |
| Barlow Condensed | `BarlowCondensed-Bold.ttf` | `fonts/Barlow Condensed/` |

`fonts/` is the day folder (`2026/day03-polygons-taco/fonts/`), next to `scripts/`, and it is gitignored. Set `FONT_DIR` to use a different directory; the same relative subfolders are required, because `scripts/18_final.py` measures text from those paths. `scripts/07_deliver.py` and `scripts/08_sheet.py` register every `.ttf` / `.otf` under that directory.

## Pipeline

From `scripts/`: `01_pool.py`, then `02_match.py`, `03_cheese.py`, `04_round2.py`, `05_review2.py`, `06_review3.py` (review grids in `scripts/data/`), then `07_deliver.py`, `08_sheet.py`, `09_export.py`.

The silhouette rotation is the template best-fit angle. For cilantro, the north-up view reads better, so a local `scripts/data/orient_override.csv` sets it. That file is not committed.

The scripts write working copies next to themselves (`scripts/sheets/`, `scripts/silhouettes/`, `scripts/final/`). The copies in this repo are under `outputs/` and `results/`.

## Credits and license

See `SOURCES_AND_CREDITS.md`. Map images are licensed CC BY 4.0, @funkchan. Code is MIT (see the repository `LICENSE`).
