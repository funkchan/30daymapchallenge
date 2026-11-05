# Day 4 (Clusters): Graveyards of the Atlantic, US shipwreck clusters

## FINAL: v6 (`scripts/render_h.py` → `outputs/day04_v6.png`, `outputs/day04_v6_1200.png`)
Skull-and-crossbones outlier marks (`glyphs/skulls_gd/`, 20 px, ink ≤200 m, bone beyond). The Chesapeake inset is shaded by water depth (CRM 3″) with 5/10/20 m isobaths. The callout is shorter. The key shows the four ship tiers. Crops: `outputs/day04_v6_crop_hatteras.png`, `outputs/day04_v6_crop_inset.png`, `outputs/day04_v6_crop_key.png`, and `outputs/day04_v6_preview600.png`. Earlier renders are not in the repo. `scripts/render_e.py` (v4) and `scripts/render_f.py` (no inset) are kept for reference; their PNGs are not committed.

## Local data
`data/` is gitignored. Land comes from this folder's own Natural Earth 10m land shapefile, `data/ne_10m_land.shp` (public domain). Download it locally:

```
mkdir -p data
curl -L -o /tmp/ne_10m_land.zip https://naciscdn.org/naturalearth/10m/physical/ne_10m_land.zip
unzip -o /tmp/ne_10m_land.zip -d data
```

`scripts/pirate.py` also expects `data/ne_10m_lakes.shp`, `data/ne_10m_bathymetry_K_200.shp`, `data/cb_2023_us_state_500k.shp`, and `data/awois/2020445569/aw/AWOIS_Wrecks.shp`. `scripts/merge_cluster.py` writes `data/merged_l48.gpkg` and `data/clusters.csv`. Depth rasters (`data/crm2.nc`, `data/et_*.nc`) stay local and are not committed.

## Fonts
Scripts read `.ttf` files from the `FONT_DIR` environment variable. If `FONT_DIR` is unset, they use the bundled faces in `glyphs/fonts/` (Pirata One and IM Fell English, SIL OFL). Those bundled faces are still loaded when `FONT_DIR` points somewhere else, so the title and labels resolve. No system font path is used. A third family in `FONT_DIR` is used for numbers. The posted map used Alegreya Sans (SIL OFL) for numbers; that face is not bundled. Without a third family, numbers use IM Fell English.

```
FONT_DIR=/path/to/fonts python scripts/render_h.py
```

## Run
Each script changes to this folder on startup, so `data/`, `glyphs/` and `outputs/` resolve here from any working directory. Packages are listed in `requirements.txt`.

```
python scripts/fetch.py coastal:33 general:29
python scripts/merge_cluster.py
python scripts/render_h.py
```

Glyph generators stay next to their art: `glyphs/make_glyphs.py` and `glyphs/skulls_gd/make_skulls.py`.

## Earlier: Version B (4 Nov)
- Regional draft of Virginia Beach to Cape Lookout, titled "The Graveyard of the Atlantic". The PNG is not in the repo.
- Shared styling is `scripts/pirate.py`. `scripts/merge_cluster.py` writes `data/merged_l48.gpkg` and `data/clusters.csv`.
- Numbers:
  - 405 wrecks in the frame.
  - Clusters at Virginia Beach (171) and Hatteras/Diamond Shoals (36).
  - Legend vs. chart for the Outer Banks: "more than 2,000" (NOAA ONMS estimate) vs. 177 in the ENC + AWOIS records.
  - 40 AWOIS names labelled.
- The caption, methods replies and alt text are in `caption.md`. Sources are in `SOURCES_AND_CREDITS.md`.

## Pipeline
1. `scripts/fetch.py`: ENC Direct wreck points. The AWOIS 2016 snapshot comes from the Library of Congress archive.
2. `scripts/merge_cluster.py`:
   - Merges ENC coastal wrecks, ENC general wrecks more than 1 km from coastal, and AWOIS records more than 1 km from ENC.
   - Lower 48 total: 8,226.
   - DBSCAN in EPSG:5070 with eps 20 km and at least 30 wrecks, giving 35 clusters holding 4,516 wrecks.
3. Later renders. The national-insets poster and the first regional render scripts are not in the repo. Kept scripts: `scripts/render_e.py`, `scripts/render_f.py`, `scripts/render_h.py`.

Glyphs and fonts are in `glyphs/`. NatGeo's "Ghost Fleet" map was used only for verification; nothing was traced from it.

## v2 (4 Nov PM)
Regional DBSCAN on the 405 wrecks in the frame: eps 5 km, min 6, giving 9 clusters. Glyph tiers by count: t1 ≤8, t2 9–19, t3 20–49, t4 ≥50. The v2 render script and PNG are not in the repo.
- Density glow: Gaussian KDE on a 500 m grid, 5 km bandwidth, ember ramp, clipped to sea.
- Depth: CRM Vol 2 (≤200 m) and ETOPO 2022 15″ (deeper water and gaps), with hillshade, stepped tints and isobaths at 10/20/50/100/200/1000/2000 m. The rasters (`data/crm2.nc` 93 MB, `data/et_*.nc`) are **not** for the repo.
- Ship names are prefixed with † in italic sepia; places are in red capitals.

## v3 (4 Nov, approved direction)
Story: two kinds of graveyard. A tight cluster at the Chesapeake mouth (Cape Henry 82, 90% within 20 km of the centre; Hampton Roads 23), shown in a zoom inset. The scattered Outer Banks: 156 of 177 wrecks are DBSCAN outliers. The v3 render script and PNG are not in the repo.
- Additions: dashed convex hulls (buffered 1.5 km), red + for clustered wrecks vs. grey × for outliers, glow hidden beyond 200 m depth, larger isobath labels, stronger halos on † ship names, and the shortened data credit.
- `pirate.basemap` gained optional kwargs (`outc`, `outa`, `outlw`, `cg_`); the defaults reproduce the older renders.

## v4 (`scripts/render_e.py`)
The v4 PNG is not committed. v4 design fixes: the header legend is replaced by a symbol key at bottom-right and a methods line above the credits. The main-map Chesapeake area shows only the frame and glow, with a leader to the inset. Inset: + marks in the 82 hull are faded, the 11 and 23 badges sit on leaders, glyphs get a parchment halo, and glyph size is capped. All three boxes share one style, and Legend vs. Chart is folded into the scattered-graveyard callout. Outliers deeper than 200 m are drawn in bone. † names are limited to wrecks within 5 km of a cluster hull plus well-known AWOIS wrecks, in a lighter ink. The compass is about 70% of its old size.

### v4 correctness pass (2026-11-04)
- I recomputed everything from data/merged_l48.gpkg. Result: 405 wrecks in the frame. DBSCAN (eps 5 km, min 6, EPSG:5070) gives 9 clusters: 82, 23, 11, 9, 8, 6, 6, 6, 6.
- Cape Henry: 88% of its wrecks lie within 20 km of the centroid (r90 = 20.3 km). The callout text now says 88%.
- Outer Banks figures use the box 76.9–74.8°W, 34.4–36.6°N (Currituck to Cape Lookout, including the sounds). The same box gives both the callout count and the Legend vs. chart count: 177 wrecks, 156 of them outliers (88%).
- Ship names are now cased properly (USS, U-numbers, initials).
- USS Huron: the AWOIS position (36.495N, 75.85W, off Corolla) is about 55 km north of the wreck site given in public accounts (off Nags Head, ~35.98N). The wreck point is kept but its label is omitted (`scripts/render_e.py`).
- Alternate version: `scripts/render_f.py` has no inset. The Chesapeake clusters are drawn in place, with glyphs on offset leaders. Its PNG is not committed.

### v4 layout update (2026-11-04)
- The zoom inset moved to the top-right deep water, level with the Chesapeake source frame, so its leader line is shorter. The compass sits in the top-right corner just below the inset; there was no room beside it. The caveats box was removed; the caveats are now in methods reply 3 in caption.md. The symbol key moved into the bottom-right corner.

## v5/v6 (2026-11-04)
- v5: added inset depth bands and isobaths. Dropped the legend-vs-chart sentence from the scattered-graveyard callout. The inset now covers 4 outliers (all deep) instead of 13. The v5 PNGs are not in the repo.
- v6: skull icons placed at native 20 px via AnnotationBbox. In the Diamond Shoals scatter (43 outliers), 10 pairs overlap at 20 px and 6 by more than half; 18 px leaves 10 pairs, 4 by more than half, so 20 px is kept.

### v6 final fixes (2026-11-04, funkchan OK'd)
- Key: the bone skull now sits on a deep-teal swatch (#475C62). The single "cluster (n)" entry is replaced by all four ship tiers: t1 ≤8, t2 9–19, t3 20–49, t4 50+, with "ships: cluster size / badge = wrecks in cluster". The key grew to 840×222 px, still bottom-right, and covers 0 marks.
- Labels move, wreck points never do. Ship names try 40 offsets around their wreck and pick one with no skull within 4 px. U-576 flipped to the left and clears. DIAMOND SHOALS shifted ~42 px (up and slightly right) and clears every skull.
- The same 11 ship names place as in v6.
- Other labels are nudged off skulls where possible: NAGS HEAD 18 px, the 50 m and 100 m isobath labels.
- Residual near-touches within the 4 px margin: Tenas, E.M. Clark and Empire Thrush (dense scatter, no clear slot), the "9" and "6" cluster badges, and CAPE HATTERAS / CAPE LOOKOUT. All of these labels and badges draw over the skulls with a halo, so nothing is hidden.

### v6 phone-readability pass (2026-11-04)
- Sizes, 2400 render → 1200 export (em size): ship names 26 pt (~18 px em / ~12 px caps at 1200), place names 34 pt, DIAMOND SHOALS 30 pt, inset badges 30 pt, inset title 32 pt, callout body 30 pt (scattered) / 28 pt (tight cluster), key 28–31 pt, depth labels 26 pt (inset 22 pt), methods 24 pt, credits 25 pt, subtitle 50 pt.
- Ship glyphs ×1.18 (main 1.1→1.3, inset 0.8→0.95). Skulls 20→22 px. Compass radius .042→.05.
- Key ×1.4 (1176×380 px), 4 rows, top line "Ship size and number = wrecks in each cluster" over the tier icons; covers 2 marks (best of a placement search).
- THE SCATTERED GRAVEYARD moved to open deep water right of Diamond Shoals (searched; covers 0 marks). Methods line shortened to fit.
- All 11 ship names still place; nothing dropped.

### v6 collision fixes (2026-11-04 evening)
- Scattered-graveyard callout placed with a 6 px margin; it now sits lower right, 141 px clear of DIAMOND SHOALS, covering 0 marks. Its arrow now targets the barrier island at 35.72N (Nags Head side) and crosses no labels or ship glyphs (checked along the flattened curve).
- TIGHT CLUSTER reflowed to 6 shorter lines at 26 pt and moved to the inset top-right. The Cape Henry galleon and the 82/23/8 badges are fully clear; the box covers 17 marks. The 11 badge moved to the left of its ship.
- VIRGINIA BEACH nudged 6 px clear of the inset leader frame.
- Key ship-tier icons ×1.5 (relative tier sizes kept); key now 1176×394 px, covers 2 marks.

## v6 final layout
Final = variant B: no callout arrow; THE SCATTERED GRAVEYARD callout sits in open ocean off the Outer Banks, clear of the key; THE TIGHT CLUSTER strip sits under the inset; compass in deep water. Place names carry parchment halos; glow inside the Chesapeake source frame dimmed 30% (display only, KDE unchanged). The arrow variant is not kept in the repo. The methods line was removed from the image (methods live in the caption.md replies) and the map frame extended down into that space; only the two credit lines remain below the map.
