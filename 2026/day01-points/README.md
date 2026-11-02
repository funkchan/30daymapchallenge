# Day 1 · Points: Hackerspaces Across the World

**#30DayMapChallenge 2026, Day 1 (Points).**

Every hackerspace mapped on OpenStreetMap: **1,898 hackerspaces in 92 countries** (OSM snapshot of 2026-08-10). Each dot is one space, and its brightness shows how many other hackerspaces are within 100 km (none, 1–5, 6–25, 26+). Europe holds 65% of them (1,230), so it gets its own close-up. France (438), the USA (287) and Germany (276) lead the top-5 chart. Callouts mark the loneliest space (AfrexLab, Uganda, 2,063 km from the nearest other one), the northernmost (Luleå, Sweden, 65.6°N) and the southernmost (Christchurch, New Zealand, 43.5°S).

## Outputs

| File | Size | What it is |
|---|---|---|
| `outputs/day01_map_still.png` | 2048×1280 | Landscape still |
| `outputs/day01_map_still_portrait.png` | 1080×1350 | Portrait still (4:5) |
| `outputs/day01_points.gif` | 1080×1080, 10 s loop | Animated version |

## Data sources

| Data | Use | License | Link |
|---|---|---|---|
| OpenStreetMap: every node, way and relation tagged `leisure=hackerspace` (ways and relations use their centre point), fetched with the Overpass API | The points | ODbL 1.0, © OpenStreetMap contributors | [openstreetmap.org/copyright](https://www.openstreetmap.org/copyright) · [Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API) |
| Natural Earth 1:10m Admin 0 Countries | Base map and country join | Public domain | [naturalearthdata.com](https://www.naturalearthdata.com/downloads/10m-cultural-vectors/) |
| Natural Earth 1:10m Populated Places (simple) | City names for the cluster stats | Public domain | [naturalearthdata.com](https://www.naturalearthdata.com/downloads/10m-cultural-vectors/) |

`data/hackerspaces_osm_2026-08-10.csv` is a small extract of the exact OSM snapshot behind the map (type, id, name, lat, lon). Because it's derived from OpenStreetMap, it's licensed under the ODbL, © OpenStreetMap contributors. The Natural Earth layers and the IBM Plex Sans font (SIL OFL, [github.com/IBM/plex](https://github.com/IBM/plex)) are downloaded, not committed.

## Method

- **Query:** `nwr["leisure"="hackerspace"]; out center;` on a public Overpass API instance.
- **Country join:** point-in-polygon against Natural Earth admin-0. The 19 offshore or coastal points that fall outside every polygon go to the nearest country within 30 km.
- **Density:** great-circle neighbour counts within 100 km, using a k-d tree on unit-sphere coordinates.
- **Projection:** Equal Earth (EPSG:8857), WGS84, central meridian 0°, clipped at 58°S–84°N. The Europe close-up uses the same projection.
- **Rendering:** Python with geopandas, shapely, pyproj, scipy and matplotlib. The glow is rasterized and capped so dense clusters don't wash out. Text is set in IBM Plex Sans.

### Reproduce

```bash
pip install -r requirements.txt
python scripts/01_fetch_overpass.py        # optional: live OSM pull -> data/raw/ (counts will differ from the 2026-08-10 snapshot)
python scripts/02_fetch_naturalearth.py    # Natural Earth -> data/naturalearth/
python scripts/03_prepare_points.py --input data/hackerspaces_osm_2026-08-10.csv   # or omit --input to use the live pull
# put IBMPlexSans-400/500/600/700.ttf in fonts/
python scripts/04_render_stills.py         # -> outputs/day01_map_still.png, outputs/day01_map_still_portrait.png
```

The labels, callouts and top-5 chart in `04_render_stills.py` are written for the 2026-08-10 snapshot. If you use a fresh pull, check them against `data/stats.json`.

## Credits and license

- Map data © OpenStreetMap contributors, ODbL.
- Thanks to [Natural Earth](https://www.naturalearthdata.com/) for free, public-domain map data.
- Map images are licensed CC BY 4.0, @funkchan. Code is MIT (see the repository `LICENSE`).
