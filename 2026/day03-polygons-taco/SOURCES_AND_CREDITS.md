# Taco Tuesday (#30DayMapChallenge 2026, Day 3 "Polygons"): sources and credits

Every silhouette is a real boundary polygon. None has been redrawn or idealised. The only changes are rotation and uniform scaling, plus a slight pull-apart ("explode") of the diced-cube clusters, which is a graphic treatment and is noted in `results/candidates.csv`. Each shape was compared in its own local Lambert azimuthal equal-area projection.

## Data
- **Natural Earth** 1:10m: Admin-1 States/Provinces v5.1.1, Land v5.1.1, Geography Regions (polygons) v5.0.0 (used for island names). Public domain. https://www.naturalearthdata.com. Credit (optional): "Made with Natural Earth."
- **US Census Bureau** TIGER/Line cartographic boundary files, places 2023, 1:500k (public domain): the shell (Wainwright, Alaska). https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html
- **Natural Earth** 1:10m Minor Islands v5.x, Playas and Glaciated Areas (public domain): used for the multi-piece protein clusters and the white sour-cream search.
- **geoBoundaries** CGAZ ADM2 (Comprehensive Global Administrative Zones) and the gbOpen per-country metadata (https://www.geoboundaries.org). Cite: Runfola, D. et al. (2020) *geoBoundaries: A global database of political administrative boundaries.* PLoS ONE 15(4): e0231866. https://doi.org/10.1371/journal.pone.0231866
  - CGAZ uses US Department of State boundaries for disputed areas. None of the picks are in a disputed area, and names are kept neutral.

## Per-pick licence (checked against the gbOpen API on 3 Nov 2026)
| Ingredient | Pick | Source | Licence / attribution |
|---|---|---|---|
| Shell (final, 3 Nov 2026) | Wainwright city, Alaska, USA (place, GEOID 0282750; main polygon, 37.3 km²) | US Census Bureau TIGER/Line cartographic boundary file, places 2023, 1:500k | Public domain (US Census Bureau) |
| ~~Shell~~ superseded | Kōchi Prefecture, Japan | Natural Earth admin-1 (cross-checked against geoBoundaries ADM1: IoU 0.706) | Public domain |
| Protein: ground beef (pick, multi-piece) | Chonos Archipelago, Aysén, Chile (20 islands) | Natural Earth land + minor islands (constructed cluster) | Public domain |
| Protein: chicken (alt pick, multi-piece) | Islands west of the Strait of Magellan (Reina Adelaida area), Chile (10 islands) | Natural Earth land + minor islands (constructed cluster) | Public domain |
| ~~Protein (chorizo)~~ superseded | São Miguel Island, Azores, Portugal | Natural Earth land | Public domain |
| Lettuce | Iceland | Natural Earth land | Public domain |
| Cheese | Zadar islands (Dugi Otok, Ugljan, Pašman…), Croatia | Natural Earth land (constructed bundle) | Public domain |
| Diced tomato | 6 NW Iowa counties, USA | geoBoundaries USA ADM2, from US Census Bureau TIGER | Public domain |
| Diced onion | 5 La Pampa departments, Argentina | geoBoundaries ARG ADM2, from Instituto Geográfico Nacional, UNHCR, OCHA ROLAC | **CC BY 3.0 IGO**: attribution required |
| Cilantro | Halmahera Island, Indonesia | Natural Earth land | Public domain |
| Sour cream | Montalbán, Carabobo, Venezuela | geoBoundaries VEN ADM2, from Efraín Porto Tapiquén, *Geografía, SIG y Estudios Ambientales* | **ODbL 1.0**: attribution required. A rendered image is a "produced work", so share-alike doesn't apply to the PNG. Réunion (public domain) is the licence-clean swap; Salinas Grandes salt flat (NE playas, public domain) is the colour-true swap. |

Runner-up licences are in `results/candidates.csv`. Watch out for these:
- Nakasatsunai (JPN ADM2): CC BY-SA 2.0, OSM-derived
- Almus and Antalya-level Turkish data from gbOpen: ODbL, OSM-derived
- GTM, IDN and LSO: CC BY 3.0 IGO
- ROU, AUS and NZL: CC BY 4.0
- BOL and USA: public domain

All ten multi-piece protein candidates (5 beef, 5 chicken) are Natural Earth only, so public domain, no credit required. No OpenStreetMap data was pulled directly.

Protein cluster names are descriptive: Natural Earth gives the island parts but not group names, so each cluster is named after the NE admin-1 unit it sits in and identified by location (Chonos at 44.6°S 74.1°W; La Maddalena 41.2°N 9.4°E; Sir Edward Pellew Group 15.7°S 136.8°E; the Magallanes chicken cluster 52.0°S 74.4°W, west of the Strait of Magellan near the Reina Adelaida archipelago). Salinas Grandes is likewise an unnamed NE playa at 29.8°S 65.1°W.

## Land-cover colour check (review only, not in the final graphic)
- **Sentinel-2 cloudless 2016** by EOX IT Services GmbH, layer `s2cloudless` via https://tiles.maps.eox.at/wms. Licence: **CC BY 4.0**. Credit: "Sentinel-2 cloudless – https://s2maps.eu by EOX IT Services GmbH (Contains modified Copernicus Sentinel data 2016)". The 2017+ mosaics are CC BY-NC-SA 4.0, so they weren't used.
- The method takes the median RGB of the pixels inside each polygon, dropping bluish-dark sea pixels that bleed in from coarse 1:10m coastlines. The colour verdicts were judged by eye from the thumbnails (`scripts/data/s2/*_thumb.png`, downloaded locally and not committed) and are recorded in `results/candidates.csv` (`s2_median_rgb`, `ground_colour`, `colour_match`). The mosaic is a mostly-summer composite, so cropland reads green.
- If any satellite imagery goes into the final graphic, add the EOX credit above.

## Credits as set in the final graphic (v13, bottom-left)
Only the required outside data credits and the map line; no fill credit (the illustrated fills are original, per funkchan, 3 Nov).
> Data: Natural Earth and US Census TIGER/Line (public domain). Via geoBoundaries (Runfola et al. 2020): Iowa counties, US Census (public domain); La Pampa departments © IGN Argentina, UNHCR, OCHA ROLAC (CC BY 3.0 IGO); Montalbán contains information from Efraín Porto Tapiquén, Geografía, SIG y Estudios Ambientales, made available under the ODbL 1.0.
> Map: @funkchan · #30DayMapChallenge Day 3: Polygons

## Tools and fonts
Python (shapely, geopandas, pyproj, matplotlib, Pillow). Fonts: Alegreya SC, Alegreya Sans and Barlow Condensed (SIL OFL).

## Display liberties (documented here; dropped from the image on 3 Nov at funkchan's request)
- Only uniform scaling and rotation: no stretching and no mirroring.
- Repeats are marked ×N on the stack labels: shell ×2 (front and back wall), lettuce ×7, cheese ×4, cilantro ×4.
- 3 extra dice in the assembled taco repeat real pieces (2 Iowa counties, 1 La Pampa department); they are not on the labels.
- Dice (tomato and onion) are spaced apart (pulled 10% from the cluster centroid) and shrunk 8% (to 92%) for display; the true-scale strip shows their true sizes.
