"""EOxCloudless 2016 (CC BY 4.0) tile sampling along geodesic lines. Tiles cached in data/tiles (not repo-bound)."""
import os, io, math, concurrent.futures as cf, urllib.request
import numpy as np
from PIL import Image
from pyproj import Geod
from scipy.ndimage import map_coordinates
HERE = os.path.dirname(os.path.abspath(__file__)); CACHE = os.path.join(os.path.dirname(HERE), "data", "tiles"); os.makedirs(CACHE, exist_ok=True)
URL = "https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless_3857/default/GoogleMapsCompatible/{z}/{y}/{x}.jpg"
ATTRIB = "EOxCloudless https://cloudless.eox.at by EOX IT Services GmbH (Contains modified Copernicus Sentinel data 2016 & 2017)"
GEOD = Geod(ellps="WGS84")

def tile(z, x, y):
    p = os.path.join(CACHE, f"{z}_{x}_{y}.jpg")
    if not os.path.exists(p):
        req = urllib.request.Request(URL.format(z=z, x=x, y=y), headers={"User-Agent": "funkchan-30DayMapChallenge/1.0"})
        data = urllib.request.urlopen(req, timeout=60).read()
        open(p, "wb").write(data)
    im = Image.open(p).convert("RGB")
    return np.asarray(im.resize((256, 256))) if im.size != (256, 256) else np.asarray(im)

def pix(lon, lat, z):
    lat = np.clip(lat, -85.05, 85.05); n = 256 * 2 ** z
    x = (np.asarray(lon) + 180) / 360 * n
    y = (1 - np.log(np.tan(np.radians(lat)) + 1 / np.cos(np.radians(lat))) / np.pi) / 2 * n
    return x, y

def sample(lon, lat, z):
    """bilinear sample RGB at arrays lon/lat from zoom z tiles"""
    x, y = pix(lon, lat, z); n = 2 ** z
    tx = np.floor(x / 256).astype(int) % n; ty = np.clip(np.floor(y / 256).astype(int), 0, n - 1)
    keys = sorted(set(zip(tx.ravel().tolist(), ty.ravel().tolist())))
    with cf.ThreadPoolExecutor(8) as ex: tiles = dict(zip(keys, ex.map(lambda k: tile(z, k[0], k[1]), keys)))
    out = np.zeros(x.shape + (3,), np.float32)
    # mosaic by bbox of tiles (handles small areas); for long ribbons process per tile
    for (kx, ky), t in tiles.items():
        m = (tx == kx) & (ty == ky)
        lx = x[m] - kx * 256 - 0.5; ly = y[m] - ky * 256 - 0.5
        for c in range(3):
            out[..., c][m] = map_coordinates(t[..., c].astype(np.float32), [ly, lx], order=1, mode="nearest")
    return out / 255.0

def grid_along(lon0, lat0, az, along_km, across_km, w, h):
    """local grid centred on (lon0,lat0); x along azimuth az, y across (positive = left of travel)."""
    a = np.linspace(-along_km / 2, along_km / 2, w) * 1000
    c = np.linspace(across_km / 2, -across_km / 2, h) * 1000
    A, C = np.meshgrid(a, c)
    lo1, la1, az1 = GEOD.fwd(np.full(A.shape, lon0), np.full(A.shape, lat0), np.full(A.shape, az), A)
    lo2, la2, _ = GEOD.fwd(lo1, la1, az1 - 90, C)
    return lo2, la2

def zoom_for(m_per_px, lat):
    return int(np.clip(math.ceil(math.log2(156543.03 * math.cos(math.radians(lat)) / m_per_px)), 1, 15))

def panel(lon0, lat0, az, along_km, across_km, w, h, oversample=1.4):
    lo, la = grid_along(lon0, lat0, az, along_km, across_km, w, h)
    z = zoom_for(along_km * 1000 / w / oversample, lat0)
    return sample(lo, la, z), z

def line_pts(lon1, lat1, lon2, lat2, n):
    p = np.array(GEOD.npts(lon1, lat1, lon2, lat2, n - 2)); return np.vstack([[lon1, lat1], p, [lon2, lat2]])

def ribbon(lon1, lat1, lon2, lat2, ncols, across_km, nrows, z=8):
    """imagery sampled along the whole line (compressed along-track), +-across_km/2 across."""
    p = line_pts(lon1, lat1, lon2, lat2, ncols)
    az = np.array(GEOD.inv(p[:-1, 0], p[:-1, 1], p[1:, 0], p[1:, 1])[0]); az = np.r_[az, az[-1]]
    c = np.linspace(across_km / 2, -across_km / 2, nrows) * 1000
    C = np.repeat(c[:, None], ncols, 1)
    lo, la, _ = GEOD.fwd(np.repeat(p[None, :, 0], nrows, 0), np.repeat(p[None, :, 1], nrows, 0), np.repeat(az[None] - 90, nrows, 0), C)
    return sample(lo, la, z)

# ---- Antarctica: EOxCloudless 2016 has no texture over the ice sheet, so the ice panels use
# NASA GIBS MODIS Terra Corrected Reflectance (true colour) in EPSG:3031 (NASA imagery, no copyright).
GIBS = ("https://gibs.earthdata.nasa.gov/wms/epsg3031/best/wms.cgi?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0"
        "&LAYERS=MODIS_Terra_CorrectedReflectance_TrueColor&CRS=EPSG:3031&BBOX={x0},{y0},{x1},{y1}&WIDTH={w}&HEIGHT={h}&FORMAT=image/jpeg&TIME={d}")
MODIS_DATE = "2017-01-10"
GIBS_ATTRIB = f"Antarctic imagery: NASA EOSDIS GIBS/Worldview, MODIS Terra true colour, {MODIS_DATE}"

def sample_polar(lon, lat, m_per_px, date=MODIS_DATE, maxpx=4000):
    from pyproj import Transformer
    import hashlib
    tf = Transformer.from_crs(4326, 3031, always_xy=True)
    x, y = tf.transform(lon, lat)
    x0, x1, y0, y1 = x.min() - 2000, x.max() + 2000, y.min() - 2000, y.max() + 2000
    w = int(min(maxpx, (x1 - x0) / m_per_px)); h = int(min(maxpx, (y1 - y0) / m_per_px))
    u = GIBS.format(x0=x0, y0=y0, x1=x1, y1=y1, w=w, h=h, d=date)
    p = os.path.join(CACHE, "gibs_" + hashlib.md5(u.encode()).hexdigest() + ".jpg")
    if not os.path.exists(p):
        open(p, "wb").write(urllib.request.urlopen(u, timeout=180).read())
    im = np.asarray(Image.open(p).convert("RGB")).astype(np.float32)
    col = (x - x0) / (x1 - x0) * w - 0.5; row = (y1 - y) / (y1 - y0) * h - 0.5
    out = np.stack([map_coordinates(im[..., c], [row, col], order=1, mode="nearest") for c in range(3)], -1)
    return out / 255.0

def panel_polar(lon0, lat0, az, along_km, across_km, w, h):
    lo, la = grid_along(lon0, lat0, az, along_km, across_km, w, h)
    return sample_polar(lo, la, max(250, along_km * 1000 / w / 1.2))

def ribbon_polar(lon1, lat1, lon2, lat2, ncols, across_km, nrows):
    p = line_pts(lon1, lat1, lon2, lat2, ncols)
    az = np.array(GEOD.inv(p[:-1, 0], p[:-1, 1], p[1:, 0], p[1:, 1])[0]); az = np.r_[az, az[-1]]
    C = np.repeat(np.linspace(across_km / 2, -across_km / 2, nrows)[:, None] * 1000, ncols, 1)
    lo, la, _ = GEOD.fwd(np.repeat(p[None, :, 0], nrows, 0), np.repeat(p[None, :, 1], nrows, 0), np.repeat(az[None] - 90, nrows, 0), C)
    return sample_polar(lo, la, 1500)
