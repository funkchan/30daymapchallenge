"""Clean the Overpass result, join each hackerspace to a Natural Earth country, compute
nearest-neighbour distances and summary stats.

Input : data/raw/hackerspaces_overpass.json (from 01_fetch_overpass.py)
        or the bundled snapshot data/hackerspaces_osm_2026-08-10.csv
Output: data/hackerspaces.geojson (EPSG:4326) and data/stats.json
Usage : python scripts/03_prepare_points.py [--input PATH]
"""
import argparse, json, math
from pathlib import Path
import numpy as np, geopandas as gpd, pandas as pd
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'
NE = DATA / 'naturalearth'
R = 6371.0088  # mean Earth radius, km
LATMIN, LATMAX = -58.0, 84.0  # map clip (Antarctica trimmed)
SNAPSHOT_BASE = '2026-08-10T00:10:23Z'

def load(path):
    path = Path(path)
    if path.suffix == '.csv':
        df = pd.read_csv(path, keep_default_na=False, na_values={'name': ['']})
        return df, SNAPSHOT_BASE  # bundled CSV is the 2026-08-10 Overpass snapshot
    raw = json.load(open(path)); rows = []
    for e in raw['elements']:
        if e['type'] == 'node': lat, lon = e['lat'], e['lon']
        else:
            c = e.get('center')
            if not c: continue
            lat, lon = c['lat'], c['lon']
        rows.append(dict(osm_type=e['type'], osm_id=e['id'], name=e.get('tags', {}).get('name'), lat=lat, lon=lon))
    return pd.DataFrame(rows), raw['osm3s']['timestamp_osm_base']

def xyz(lat, lon):
    la, lo = np.radians(lat), np.radians(lon)
    return np.c_[np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)]

def ch(km): return 2 * math.sin(km / R / 2)  # great-circle km -> unit-sphere chord

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--input', default=str(DATA / 'raw' / 'hackerspaces_overpass.json'))
    a = ap.parse_args()
    df, base = load(a.input)
    g = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat), crs=4326)
    ad = gpd.read_file(NE / 'ne_10m_admin_0_countries' / 'ne_10m_admin_0_countries.shp')[['ADMIN', 'ADM0_A3', 'CONTINENT', 'geometry']].to_crs(4326)
    j = gpd.sjoin(g, ad, how='left', predicate='within').drop(columns='index_right')
    j = j[~j.index.duplicated()]
    miss = j.ADMIN.isna()
    if miss.any():  # offshore/coastal: nearest country within 30 km, measured in Equal Earth metres
        nn = gpd.sjoin_nearest(g[miss].to_crs(8857), ad.to_crs(8857), how='left', max_distance=30000, distance_col='d')
        nn = nn[~nn.index.duplicated()]
        for col in ['ADMIN', 'ADM0_A3', 'CONTINENT']: j.loc[nn.index, col] = nn[col]
    j['country_method'] = np.where(miss, 'nearest<=30km', 'within')
    j.loc[j.ADMIN.isna(), 'country_method'] = 'unassigned'
    j = j.rename(columns={'ADMIN': 'country', 'ADM0_A3': 'country_a3', 'CONTINENT': 'continent'})
    # nearest-neighbour great-circle distance
    P = xyz(j.lat.values, j.lon.values); tr = cKDTree(P)
    dd, _ = tr.query(P, k=2); nnkm = 2 * R * np.arcsin(np.clip(dd[:, 1] / 2, 0, 1)); j['nn_km'] = np.round(nnkm, 1)
    # 25 km greedy density clusters
    nb = tr.query_ball_point(P, ch(25)); left = set(range(len(j))); clusters = []
    while left:
        best = max(left, key=lambda i: len([k for k in nb[i] if k in left]))
        mem = [k for k in nb[best] if k in left]; clusters.append((best, mem)); left -= set(mem)
    clusters.sort(key=lambda c: -len(c[1]))
    pp = gpd.read_file(NE / 'ne_10m_populated_places_simple' / 'ne_10m_populated_places_simple.shp')
    pt = cKDTree(xyz(pp.latitude.values, pp.longitude.values)); popw = pp.pop_max.values
    def cityname(i):
        idx = pt.query_ball_point(P[i], ch(30)) or [pt.query(P[i])[1]]
        k = max(idx, key=lambda t: popw[t]); return f"{pp.name.values[k]}, {pp.adm0name.values[k]}"
    N = len(j); cc = j.country.value_counts(); cont = j.continent.value_counts()
    far = j.sort_values('nn_km', ascending=False).head(5)
    north = j.sort_values('lat', ascending=False).head(3); south = j.sort_values('lat').head(3)
    stats = dict(osm_base=base, total=N, by_type=j.osm_type.value_counts().to_dict(), named=int(j.name.notna().sum()),
        countries_count=int(j.country.nunique()), top_countries=[[k, int(v), round(100 * v / N, 1)] for k, v in cc.head(10).items()],
        continents={k: [int(v), round(100 * v / N, 1)] for k, v in cont.items()},
        unassigned=int((j.country_method == 'unassigned').sum()), nearest_fallback=int((j.country_method == 'nearest<=30km').sum()),
        clusters_25km=[dict(center=cityname(b), count=len(m), center_lat=float(j.lat.values[b]), center_lon=float(j.lon.values[b])) for b, m in clusters[:8]],
        singletons_25km=sum(1 for c in clusters if len(c[1]) == 1), n_clusters=len(clusters),
        most_remote=far[['name', 'country', 'lat', 'lon', 'nn_km', 'osm_type', 'osm_id']].to_dict('records'),
        northernmost=north[['name', 'country', 'lat', 'lon', 'osm_type', 'osm_id']].to_dict('records'),
        southernmost=south[['name', 'country', 'lat', 'lon', 'osm_type', 'osm_id']].to_dict('records'),
        median_nn_km=float(np.median(nnkm)), share_nn_lt_25km=round(100 * float(np.mean(nnkm < 25)), 1),
        southern_hemisphere=int((j.lat < 0).sum()), out_of_frame=int(((j.lat < LATMIN) | (j.lat > LATMAX)).sum()),
        attribution='© OpenStreetMap contributors (ODbL)')
    DATA.mkdir(exist_ok=True)
    json.dump(stats, open(DATA / 'stats.json', 'w'), indent=1, default=str, ensure_ascii=False)
    cols = ['osm_type', 'osm_id', 'name', 'lat', 'lon', 'country', 'country_a3', 'continent', 'country_method', 'nn_km']
    j = j.sort_values(['osm_type', 'osm_id']).reset_index(drop=True)
    j[cols + ['geometry']].to_file(DATA / 'hackerspaces.geojson', driver='GeoJSON')
    print(f"{N} points, {stats['countries_count']} countries -> data/hackerspaces.geojson, data/stats.json")

if __name__ == '__main__':
    main()
