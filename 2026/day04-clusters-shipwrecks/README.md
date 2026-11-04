# Day 4 (Clusters): Graveyards of the Sea, US shipwreck clusters

## FINAL (4 Nov, funkchan picked Version B)
- `outputs/day04_final.png` (2400×3000) and `outputs/day04_final_1200.png`: "The Graveyard of the Atlantic", Virginia Beach to Cape Lookout.
- Built by `render_b.py`, using the shared styling in `pirate.py`. Data comes from `merge_cluster.py`, which writes `data/merged_l48.gpkg` and `data/clusters.csv`.
- Numbers:
  - 403 wrecks in the frame.
  - Clusters at Virginia Beach (171) and Hatteras/Diamond Shoals (36).
  - Legend vs. chart for the Outer Banks: "more than 2,000" (NOAA ONMS estimate) vs. 177 in the ENC + AWOIS records.
  - 40 AWOIS names labelled.
- The caption, methods replies and alt text are in `caption.md`. Sources are in `SOURCES_AND_CREDITS.md`.

## Pipeline
1. `fetch.py`: ENC Direct wreck points. The AWOIS 2016 snapshot comes from the Library of Congress archive.
2. `merge_cluster.py`:
   - Merges ENC coastal wrecks, ENC general wrecks more than 1 km from coastal, and AWOIS records more than 1 km from ENC.
   - Lower 48 total: 8,226.
   - DBSCAN in EPSG:5070 with eps 20 km and at least 30 wrecks, giving 35 clusters holding 4,516 wrecks.
3. `render_b.py` (final) and `render_a.py`: Version A, the national insets version, not chosen (`outputs/day04_A_insets*.png`).

Glyphs and fonts are in `glyphs/`. NatGeo's "Ghost Fleet" map was used only for verification; nothing was traced from it.

## v2 (4 Nov PM): `outputs/day04_final_v2.png` and `_1200.png`, built by `render_c.py` (`render_b.py` and its outputs are untouched)
- Regional DBSCAN on the 403 wrecks in the frame: eps 5 km, min 6, giving 9 clusters. Glyph tiers by count: t1 ≤8, t2 9–19, t3 20–49, t4 ≥50.
- Density glow: Gaussian KDE on a 500 m grid, 5 km bandwidth, ember ramp, clipped to sea.
- Depth: CRM Vol 2 (≤200 m) and ETOPO 2022 15″ (deeper water and gaps), with hillshade, stepped tints and isobaths at 10/20/50/100/200/1000/2000 m. The rasters (`data/crm2.nc` 93 MB, `data/et_*.nc`) are **not** for the repo.
- Ship names are prefixed with † in italic sepia; places are in red capitals.

## v3 (4 Nov, approved direction): `outputs/day04_final_v3.png` and `_1200.png`, built by `render_d.py` (v1, v2 and B are untouched)
- Story: two kinds of graveyard. A tight cluster at the Chesapeake mouth (Cape Henry 82, 90% within 20 km of the centre; Hampton Roads 23), shown in a zoom inset. The scattered Outer Banks: 156 of 177 wrecks are DBSCAN outliers.
- Additions: dashed convex hulls (buffered 1.5 km), red + for clustered wrecks vs. grey × for outliers, glow hidden beyond 200 m depth, larger isobath labels, stronger halos on † ship names, and the shortened data credit.
- `pirate.basemap` gained optional kwargs (`outc`, `outa`, `outlw`, `cg_`); the defaults reproduce the older renders.

## v4 (render_e.py → outputs/day04_final_v4.png, _1200.png)
Graphic Design's seven fixes: the header legend is replaced by a symbol key at bottom-right and a methods line above the credits. The main-map Chesapeake area shows only the frame and glow, with a leader to the inset. Inset: + marks in the 82 hull are faded, the 11 and 23 badges sit on leaders, glyphs get a parchment halo, and glyph size is capped. All three boxes share one style, and Legend vs. Chart is folded into the scattered-graveyard callout. Outliers deeper than 200 m are drawn in bone. † names are limited to wrecks within 5 km of a cluster hull plus well-known AWOIS wrecks, in a lighter ink. The compass is about 70% of its old size.

### v4 correctness pass (2026-11-04)
- I recomputed everything from data/merged_l48.gpkg. Result: 403 wrecks in the frame. DBSCAN (eps 5 km, min 6, EPSG:5070) gives 9 clusters: 82, 23, 11, 9, 8, 6, 6, 6, 6.
- Cape Henry: 88% of its wrecks lie within 20 km of the centroid (r90 = 20.3 km). The callout text now says 88%.
- Outer Banks figures use the box 76.9–74.8°W, 34.4–36.6°N (Currituck to Cape Lookout, including the sounds). The same box gives both the callout count and the Legend vs. chart count: 177 wrecks, 156 of them outliers (88%).
- Ship names are now cased properly (USS, U-numbers, initials).
- USS Huron: the AWOIS position (36.495N, 75.85W, off Corolla) is about 55 km north of the wreck site given in public accounts (off Nags Head, ~35.98N). The wreck point is kept but its label is omitted (render_e.py).
- Alternate version: render_f.py writes outputs/day04_v4_noinset.png. It has no inset; the Chesapeake clusters are drawn in place, with glyphs on offset leaders.
