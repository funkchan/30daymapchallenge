"""Download the Natural Earth layers used by the map (public domain, naturalearthdata.com).

  ne_10m_admin_0_countries       -> country polygons (country join + base map)
  ne_10m_populated_places_simple -> city names for the cluster labels in stats.json
Unzips into data/naturalearth/<layer>/.
Usage: python scripts/02_fetch_naturalearth.py
"""
import argparse, io, urllib.request, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = 'https://naciscdn.org/naturalearth/10m/cultural/'
LAYERS = ['ne_10m_admin_0_countries', 'ne_10m_populated_places_simple']

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--dest', default=str(ROOT / 'data' / 'naturalearth'))
    a = ap.parse_args()
    for name in LAYERS:
        d = Path(a.dest) / name; d.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(BASE + name + '.zip', headers={'User-Agent': '30daymapchallenge-day01'})
        with urllib.request.urlopen(req, timeout=300) as r:
            zipfile.ZipFile(io.BytesIO(r.read())).extractall(d)
        print('ok', d)

if __name__ == '__main__':
    main()
