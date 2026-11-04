# Day 4 Phase 1: sources and cross-reference (Nov 4, 2026)

## Sources checked
| Source | Count | Coverage | Licence | Downloadable? |
|---|---|---|---|---|
| NOAA OCS ENC Direct wreck points (current, weekly) | 17,450 raw across 5 scale bands; 12,731 after removing duplicates within 200 m; 3,861 in the Lower 48 at coastal and general scale | all US charted waters | US Gov, public domain | yes (REST, pulled) |
| NOAA OCS AWOIS Wrecks, 2016/2018 snapshot (Library of Congress archive) | 6,222 wrecks (2,673 named; only 197 have a year sunk) + an AWOIS Obstructions layer | US waters (5,816 in the Lower 48, 151 AK, 30 HI, 109 PR) | US Gov, public domain | yes: https://tile.loc.gov/storage-services/master/gdc/gdcdatasets/2020445569/2020445569.zip (6.9 MB; SHP, KML, XLS; also includes the 2018 ENC_Wrecks.xls) |
| NOAA OCM "Wrecks and Obstructions" (AWOIS + ENC synthesis) | 41,941 points per the AWOIS metadata (all classes) | US waters | CC0 (data.gov) | listed on marinecadastre.gov; direct file not found, and its service host (wrecks.nauticalcharts.noaa.gov) didn't respond |
| BOEM Gulf/Atlantic archaeology | n/a | Gulf/Atlantic | n/a | no public shipwreck points (site locations are protected); only historic sailing routes |
| NOAA ONMS sanctuaries (Monitor, Florida Keys, Thunder Bay) | published figures only (below) | sanctuary areas | US Gov | no point downloads found |
| Dave Swayze Great Lakes Shipwreck DB (shipwreck.info) | "over 5,000" verified commercial total losses | Great Lakes | private website, no open licence | searchable only; don't use |
| Wikipedia shipwreck lists | varies | global | CC BY-SA | last resort; inconsistent coordinates |
| Wrecksite.eu | large | global | proprietary, subscription | not usable |
| NatGeo "Ghost Fleet of the Outer Banks" | the 750×1354 attachment is too small to count labels; visibly several hundred | NC coast | © NatGeo | verification only |

## Published figures vs NOAA charts (same boxes)
| Area | Published historical figure | ENC coastal + general | ENC all bands (deduped) | AWOIS |
|---|---|---|---|---|
| Outer Banks (lat 34.4–36.6, lon −76.9 to −74.8) | "more than 2,000 ships" (NOAA ONMS); "more than 2,000" between Cape Lookout and Hatteras (NOAA Ocean Explorer 2004 survey); "~2,000" (NCpedia); "5,000+" (Wikipedia, weak sourcing) | 88 | 322 | 160 (109 named) |
| ±60 km of Cape Hatteras | "more than 600" off Hatteras Island (Wikipedia) | 43 | 71 | 84 |
| Florida Keys | "an estimated 2,000"; 669 archival loss accounts; 400+ recorded sites (NOAA FKNMS) | 233 | 389 | 111 |
| Thunder Bay, MI | "over 200 vessels"; 100 discovered (NOAA ONMS) | 47 | 51 | 15 |
| Chesapeake Bay | no single authoritative figure found | 223 | 878 | 318 |
| Louisiana shelf | no single authoritative figure found | 318 | 503 | 121 |

**Finding:** in the Outer Banks, NOAA's charts hold about 4–16% of the published loss count. Hatteras isn't a top cluster *of charted wrecks*. That isn't a claim about where ships actually sank.
