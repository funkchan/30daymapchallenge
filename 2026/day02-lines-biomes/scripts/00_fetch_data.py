#!/usr/bin/env python3
"""Download the inputs into ../data and the fonts into ../fonts (none of these are committed).

  RESOLVE Ecoregions 2017 (CC BY 4.0, Dinerstein et al. 2017)  -> data/Ecoregions2017.*  (~150 MB zip)
  Natural Earth 10m admin-0 countries + 10m land (public domain) -> data/ne_10m_*.*
  Fonts (SIL OFL, Google Fonts): Alegreya SC, Alegreya Sans, Barlow Condensed -> fonts/<Family>/
Satellite tiles are not fetched here: imagery.py downloads and caches only the tiles it needs
(EOxCloudless 2016 WMTS, NASA GIBS MODIS WMS) into data/tiles/ when render.py runs.
Usage: python scripts/00_fetch_data.py
"""
import io, os, urllib.request, zipfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA, FONTS = os.path.join(ROOT, "data"), os.path.join(ROOT, "fonts")
ZIPS = [
    ("https://storage.googleapis.com/teow2016/Ecoregions2017.zip", "Ecoregions2017.shp"),
    ("https://naciscdn.org/naturalearth/10m/cultural/ne_10m_admin_0_countries.zip", "ne_10m_admin_0_countries.shp"),
    ("https://naciscdn.org/naturalearth/10m/physical/ne_10m_land.zip", "ne_10m_land.shp"),
]
GF = "https://github.com/google/fonts/raw/main/ofl/"
FONTFILES = {
    "Alegreya SC": ("alegreyasc", ["AlegreyaSC-ExtraBold.ttf", "AlegreyaSC-Bold.ttf"]),
    "Alegreya Sans": ("alegreyasans", ["AlegreyaSans-Regular.ttf", "AlegreyaSans-Italic.ttf", "AlegreyaSans-Medium.ttf"]),
    "Barlow Condensed": ("barlowcondensed", ["BarlowCondensed-SemiBold.ttf", "BarlowCondensed-Bold.ttf", "BarlowCondensed-Medium.ttf"]),
}

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "30daymapchallenge-day02"})
    return urllib.request.urlopen(req, timeout=600).read()

def main():
    os.makedirs(DATA, exist_ok=True)
    for url, check in ZIPS:
        if os.path.exists(os.path.join(DATA, check)):
            print("have", check); continue
        print("downloading", url, flush=True)
        with zipfile.ZipFile(io.BytesIO(get(url))) as z:
            for m in z.infolist():
                if m.is_dir(): continue
                open(os.path.join(DATA, os.path.basename(m.filename)), "wb").write(z.read(m))
    for fam, (slug, files) in FONTFILES.items():
        d = os.path.join(FONTS, fam); os.makedirs(d, exist_ok=True)
        for f in files:
            p = os.path.join(d, f)
            if not os.path.exists(p):
                print("font", f, flush=True); open(p, "wb").write(get(GF + slug + "/" + f))
    print("done")

if __name__ == "__main__":
    main()
