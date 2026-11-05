# Day 4 · Clusters · Graveyards of the Sea

Posted map: `outputs/day04_v6.png` (1200 px: `outputs/day04_v6_1200.png`). The sections below keep captions and alt text from earlier drafts. Those PNGs are not in this folder.

The `tree/main` links in the method replies only work after this folder is merged to `main`.

## Version A (national insets; PNG not in the repo)
**Caption:** Graveyards of the Sea ☠️ 8,226 NOAA-recorded wrecks off the Lower 48, 4,516 in 35 DBSCAN clusters. Legend vs. chart: NOAA says "more than 2,000" wrecks lie off the Outer Banks, but only 177 are in its records. #30DayMapChallenge Day 4: Clusters

**Alt text:** Treasure-map-style poster of US shipwreck clusters. Seven inset maps (Outer Banks, Chesapeake Bay, New York Bight to Cape Cod, Florida Keys, Louisiana–Texas Gulf, Lakes Michigan and Huron, Puget Sound) show every NOAA-recorded wreck as a small cross. Wrecked-ship glyphs sized by cluster size and density mark the clusters. The biggest is the New York Bight with 1,351 wrecks. Boxes compare published estimates with recorded counts: Outer Banks, more than 2,000 vs 177; Florida Keys, about 2,000 vs 309; Thunder Bay, over 200 vs 49.

## Version B (regional draft; PNG not in the repo)
**Caption:** The Graveyard of the Atlantic ☠️ Virginia Beach to Cape Lookout, every NOAA-recorded wreck, with named wrecks around Diamond Shoals. History says "more than 2,000" were lost off the Outer Banks. NOAA's charts and AWOIS hold 177. #30DayMapChallenge Day 4: Clusters

**Alt text:** Parchment-style map of the North Carolina and southern Virginia coast from Virginia Beach to Cape Lookout. Bold marks show the 403 NOAA-recorded wrecks in the frame: oxblood plus signs for wrecks in a cluster, black crosses for outliers. Italic labels name AWOIS wrecks clustered off Cape Hatteras and Diamond Shoals, including U-85, Liberator, Empire Gem, British Splendour and E.M. Clark. Ship glyphs mark DBSCAN clusters at Virginia Beach (171) and off Hatteras (36). A box reads: "more than 2,000" historical wrecks (published estimate, NOAA ONMS) vs. 177 charted and recorded.

## Methods replies (both)
1/ Points: NOAA ENC Direct wreck points from the coastal band (3,790) and general band (679 that are >1 km from any coastal point), plus AWOIS records (4,700 that are >1 km from any ENC point; 2016 snapshot archived by the Library of Congress). Harbour and approach bands are left out, because detailed charts exist only around ports and would bias the map.
2/ Clusters: DBSCAN in US Albers equal-area (EPSG:5070), eps 20 km, min 30 wrecks, giving 35 clusters with 4,516 of 8,226 Lower-48 wrecks. Glyph tier = mean of rank(size) and rank(density).
3/ Caveats: these are charted or recorded wrecks only. Clusters partly reflect survey effort. Some points may be artificial reefs, and de-duplication is approximate. The "legend" figures are NOAA sanctuary estimates, not counts. Code + sources: https://github.com/funkchan/30daymapchallenge/tree/main/2026/day04-clusters-shipwrecks

## v2 methods replies (PNG not in the repo)
2/ Clusters (v2): regional DBSCAN on the 403 wrecks in the frame, in EPSG:5070 metres, eps 5 km, min 6, giving 9 clusters (82, 23, 11, 9, 8, 6, 6, 6, 6). Glow = Gaussian KDE of all 403 wrecks, 5 km bandwidth.
3/ Depth: NOAA NCEI Coastal Relief Model (3″) to 200 m, ETOPO 2022 (15″) beyond; both public domain. Caveats: recorded wrecks only, survey bias. Code: https://github.com/funkchan/30daymapchallenge/tree/main/2026/day04-clusters-shipwrecks

## v3 (PNG not in the repo)
**Title:** Graveyards of the Atlantic. **Subtitle:** Chesapeake to Cape Lookout: one tight cluster, one scattered graveyard

**Caption:** Graveyards of the Atlantic ☠️ Two kinds of graveyard: 82 wrecks pack one tight DBSCAN cluster off Cape Henry at the Chesapeake mouth, while the Outer Banks graveyard is scattered, with 177 charted vs "more than 2,000" lost (NOAA). #30DayMapChallenge Day 4: Clusters

**Methods replies:**
1/ Points: NOAA ENC coastal + general wreck points, plus AWOIS records >1 km from any chart point (2016 snapshot, Library of Congress archive). 403 wrecks in the frame. Harbour and approach charts are excluded to limit chart-scale bias.
2/ Clusters: DBSCAN on the frame's wrecks in EPSG:5070, eps 5 km, min 6, giving 9 clusters (82 Cape Henry, 23 Hampton Roads, 11, 9 Diamond Shoals, 8, 6×4). Dashed = convex hulls. Glow = 5 km KDE, hidden beyond 200 m. Outer Banks: 156 of 177 are outliers.
3/ Depth: NOAA NCEI Coastal Relief Model (3″) to 200 m, ETOPO 2022 (15″) beyond; both public domain. Caveats: recorded wrecks only, survey bias. Code: https://github.com/funkchan/30daymapchallenge/tree/main/2026/day04-clusters-shipwrecks

**Alt text:** Pirate-chart-style map from the Chesapeake Bay mouth to Cape Lookout, titled "Graveyards of the Atlantic", with seafloor shading and depth contours. Red plus signs mark wrecks inside DBSCAN clusters, grey crosses mark scattered wrecks, and an ember glow shows wreck density. A zoom inset of the Chesapeake mouth shows the biggest cluster: 82 wrecks off Cape Henry, 90% within 20 km of its centre, with 23 more at Hampton Roads. Off the Outer Banks, wrecks are spread out: 156 of 177 lie outside any cluster, and only small clusters appear at Oregon Inlet (6) and Diamond Shoals (9). A box compares NOAA's published "more than 2,000" historical wrecks with the 177 charted and recorded. Italic names with a dagger label AWOIS-named wrecks such as U-85, U-701, City of Atlanta and Empire Gem.

## v4 (PNG not in the repo; script: `scripts/render_e.py`)
Main caption: unchanged from v3 (265 chars).

Alt text: Antique-chart-style map of the US coast from the Chesapeake Bay mouth to Cape Lookout, titled "Graveyards of the Atlantic". 403 charted and recorded wrecks (NOAA ENC + AWOIS) on stepped depth tints with isobaths. An amber glow shows wreck density. Ship icons with counts mark 9 DBSCAN clusters; dashed outlines show their hulls. A zoom inset of the bay mouth shows the tight cluster: 82 wrecks off Cape Henry and 23 at Hampton Roads. A callout in the open ocean off the Outer Banks notes 177 wrecks there, 88% outside any cluster, and contrasts "more than 2,000" historical wrecks (NOAA ONMS) with the 177 charted. Dagger labels name selected ships, including U-85, U-701 and U-576. The zoom inset sits at top right with a compass rose below it. A symbol key, a methods line and credits sit at the bottom.

Methods replies: 1/ and 2/ same as v3 (236 / 254 chars). Reply 3 is updated because the caveats box was removed from the image (274 chars as counted by X):
3/ Depth: NOAA NCEI Coastal Relief Model (3″) to 200 m, ETOPO 2022 (15″) beyond. Caveats: charted/recorded wrecks only (most losses never located); clusters also reflect survey effort; some points may be artificial reefs; AWOIS = 2016 snapshot. Code: https://github.com/funkchan/30daymapchallenge/tree/main/2026/day04-clusters-shipwrecks Alt text for the no-inset alternate: same as v4, except the Chesapeake clusters are drawn in place on the main map rather than in a zoom inset.

## FINAL alt text (v6, `outputs/day04_v6.png`)

Vintage parchment map of the US Atlantic coast from the Chesapeake Bay mouth to Cape Lookout, titled "Graveyards of the Atlantic". 405 NOAA-charted wrecks are drawn as small skulls (dark in shallow water, pale beyond 200 m) over a warm density glow. A zoom inset at top right shows the Chesapeake Bay mouth, where ship icons mark clusters of 82, 23, 11, 8 and 6 wrecks; a strip under the inset reads: 82 wrecks off Cape Henry, 88% within 20 km, where shipping converges on the bay mouth, 23 more at Hampton Roads. Off the Outer Banks, a callout in open ocean (no arrow) notes 177 wrecks, 156 (88%) outside any cluster, losses spread along the whole barrier coast. Named wrecks include U-85, U-701, U-576, Monitor, Dixie Arrow, E.M. Clark, Empire Gem, Empire Thrush, Tenas, City of Atlanta and City of New York. A compass rose sits in deep water; a key at bottom right explains ship sizes, density, hulls and skulls. Two credit lines (data sources; map by @funkchan, #30DayMapChallenge Day 4: Clusters) sit below the map; methods are in the replies.

## FINAL methods replies (v6)
(Methods line removed from the image; these replies carry it. Counts as X counts them: 236 / 260 / 274.)

1/ Points: NOAA ENC coastal + general wreck points, plus AWOIS records >1 km from any chart point (2016 snapshot, Library of Congress archive). 405 wrecks in the frame. Harbour and approach charts are excluded to limit chart-scale bias.
2/ Clusters: DBSCAN on the frame's wrecks in EPSG:5070, eps 5 km, min 6, giving 9 clusters (82 Cape Henry, 23 Hampton Roads, 11, 9 Diamond Shoals, 8, 6×4). Hull = convex hull + 1.5 km. Glow = 5 km KDE, hidden beyond 200 m. Outer Banks: 156 of 177 are outliers.
3/ Depth: NOAA NCEI Coastal Relief Model (3″) to 200 m, ETOPO 2022 (15″) beyond. Caveats: charted/recorded wrecks only (most losses never located); clusters also reflect survey effort; some points may be artificial reefs; AWOIS = 2016 snapshot. Code: https://github.com/funkchan/30daymapchallenge/tree/main/2026/day04-clusters-shipwrecks
