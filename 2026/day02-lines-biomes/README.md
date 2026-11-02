# Day 2 · Lines: The World's Longest Straight Lines, by Biome

**#30DayMapChallenge 2026, Day 2 (Lines).**

For each of seven major biomes, the longest geodesic (the straightest possible path over Earth's surface) that stays inside that biome, using RESOLVE Ecoregions 2017. **Grassland & savanna wins at 5,806 km** (Guinea-Bissau to Ethiopia), followed by desert & xeric shrubland 5,615 km (Mauritania to Sudan), boreal forest / taiga 5,414 km (Russia), ice sheet 4,667 km (Antarctica), temperate forest 4,543 km (Spain to the southern Urals), tropical rainforest 3,995 km (Ecuador to Brazil) and tundra 2,232 km (Russia, to the Lena Delta). Each line gets a magnifier callout of satellite imagery along its route, plus a thin strip of the whole line.

## Outputs

| File | Size | What it is |
|---|---|---|
| `outputs/day02_lines_biomes.png` | 3000×1688 | Landscape |
| `outputs/day02_lines_biomes_portrait.png` | 2400×3000 | Portrait (4:5) |

## Results

| File | What it is |
|---|---|
| `results/final_lines.json` | Final endpoints, length, % inside, bridged gaps, countries crossed, source step |
| `results/final_lines.csv` | Same, flat table |
| `results/final_lines.geojson` | Final lines as WGS84 geodesics, densified every ~10 km |
| `results/validation.json` | ~1 km vector validation of the raster-search lines |

## Data sources

| Data | Use | License | Link |
|---|---|---|---|
| RESOLVE Ecoregions 2017 (Dinerstein et al. 2017, *BioScience* 67(6):534–545) | Biome polygons | CC BY 4.0 | [ecoregions.appspot.com](https://ecoregions.appspot.com/) |
| Natural Earth 1:10m Land and Admin 0 Countries | Base map; countries-crossed lists (no borders drawn) | Public domain | [naturalearthdata.com](https://www.naturalearthdata.com/) |
| EOxCloudless 2016 | Satellite callouts and strips (all biomes except ice) | CC BY 4.0. EOxCloudless https://cloudless.eox.at by EOX IT Services GmbH (Contains modified Copernicus Sentinel data 2016 & 2017) | [cloudless.eox.at](https://cloudless.eox.at) |
| NASA EOSDIS GIBS/Worldview, MODIS Terra Corrected Reflectance (true colour), 2017-01-10 | Antarctic ice callout and strip | NASA imagery, no copyright | [earthdata.nasa.gov/gibs](https://www.earthdata.nasa.gov/engage/open-data-services-software/earthdata-developer-portal/gibs-api) |

Only the 2016 EOxCloudless mosaic is CC BY 4.0 (later years are CC BY-NC-SA), so 2016 is used. It is plain white over Antarctica, so the ice panels use MODIS instead. Endpoint place names on the map were written by hand. The data, imagery tiles and fonts (Alegreya SC, Alegreya Sans, Barlow Condensed; SIL OFL, [Google Fonts](https://github.com/google/fonts)) are downloaded, not committed.

## Method

- **Biomes:** RESOLVE biomes grouped into 7: tropical rainforest (1), temperate forest (4+5), boreal forest / taiga (6), grassland & savanna (7+8), desert & xeric shrubland (13), tundra (11, "Tundra") and ice sheet (11, the "Rock & Ice" ecoregion).
- **Search:** ecoregions rasterized once to a 0.05° grid. Gaps one cell wide (≤5.5 km) are bridged, and a 0.25° coarse mask is built. 40,000 great circles (poles on a Fibonacci hemisphere) are walked for the longest unbroken run per biome. The top distinct candidates are hill-climbed on the fine mask.
- **Refinement:** grassland and boreal get an extra hill-climb on a 0.01° rasterization of the vector polygons with 1 km samples (`refine_raster.py`). That's kept if it beats the validated line.
- **Validation:** every line is densified every ~1 km along the WGS84 geodesic and tested point-in-polygon against the vector ecoregions. Only water gaps (no polygon: rivers, lakes, bays) ≤5.5 km are bridged; any other biome ends the line, and endpoints are trimmed to the longest run. Lengths are pyproj `Geod` (WGS84) between the final endpoints.
- **Bridged water:** tundra crosses 12 km of Lena Delta channels in 3 gaps (5, 2 and 5 km). Ice crosses 1 km. All other lines cross none.
- **Ice:** "ice sheet" is the RESOLVE Rock & Ice ecoregion. About 42 km of the line touches Natural Earth ice-shelf outlines in the northeast; it's kept as drawn by RESOLVE.
- **Projection:** Equal Earth (EPSG:8857). No country borders are drawn.

### Reproduce

```bash
pip install -r requirements.txt
python scripts/00_fetch_data.py        # RESOLVE + Natural Earth -> data/, fonts -> fonts/
python scripts/longest_lines.py        # 40,000 great circles -> work/_raw_results.json (slow; caches data/biome_codes_005.npy)
python scripts/validate.py             # ~1 km vector check -> results/validation.json
python scripts/refine_raster.py 5      # grassland refinement -> work/refine_raster_5.json
python scripts/refine_raster.py 2      # boreal refinement   -> work/refine_raster_2.json
python scripts/finalize.py             # -> results/final_lines.json, results/final_lines.csv
python scripts/export_geojson.py       # -> results/final_lines.geojson
python scripts/render.py               # fetches imagery tiles to data/tiles/ -> outputs/*.png
python scripts/postprocess.py          # optional: coarse-test diagnostics and preview -> work/
```

`render.py` only needs `results/final_lines.json`, Natural Earth land and the fonts, so you can rebuild the images without rerunning the search. The labels, callout positions and place names in `render.py` are written for these results.

## Credits and license

- Biomes: RESOLVE Ecoregions 2017, Dinerstein et al. 2017, CC BY 4.0.
- EOxCloudless https://cloudless.eox.at by EOX IT Services GmbH (Contains modified Copernicus Sentinel data 2016 & 2017), CC BY 4.0.
- Antarctic imagery: NASA EOSDIS GIBS/Worldview, MODIS Terra.
- Thanks to [Natural Earth](https://www.naturalearthdata.com/) for free, public-domain map data.
- Map images are licensed CC BY 4.0, @funkchan. Code is MIT (see the repository `LICENSE`).
