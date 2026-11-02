"""Fetch every OpenStreetMap feature tagged leisure=hackerspace from a public Overpass API.

Writes data/raw/hackerspaces_overpass.json. Data © OpenStreetMap contributors, ODbL.
Usage: python scripts/01_fetch_overpass.py [--endpoint URL]
"""
import argparse, json, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUERY = '[out:json][timeout:180];nwr["leisure"="hackerspace"];out center;'
DEFAULT = 'https://overpass-api.de/api/interpreter'  # public instance; overpass.openstreetmap.fr also works

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--endpoint', default=DEFAULT, help='public Overpass API interpreter URL')
    ap.add_argument('--out', default=str(ROOT / 'data' / 'raw' / 'hackerspaces_overpass.json'))
    a = ap.parse_args()
    req = urllib.request.Request(a.endpoint, data=urllib.parse.urlencode({'data': QUERY}).encode(),
                                 headers={'User-Agent': '30daymapchallenge-day01'})
    with urllib.request.urlopen(req, timeout=240) as r:
        raw = json.load(r)
    raw['source'] = a.endpoint; raw['query'] = QUERY
    out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    json.dump(raw, open(out, 'w'), ensure_ascii=False)
    print(f"{len(raw['elements'])} elements, OSM base {raw['osm3s']['timestamp_osm_base']} -> {out}")

if __name__ == '__main__':
    main()
