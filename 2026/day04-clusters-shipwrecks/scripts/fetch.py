import os,json,urllib.request,time,sys
os.chdir(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')))
B="https://encdirect.noaa.gov/arcgis/rest/services/encdirect/enc_%s/MapServer/%d/query"
def get(u,tries=6):
    for i in range(tries):
        try:
            d=json.load(urllib.request.urlopen(u,timeout=90))
            if 'error' not in d: return d
        except Exception as e: pass
        time.sleep(3+i*3)
    raise SystemExit("fail "+u)
for band,lid in [(a,int(b)) for a,b in (x.split(':') for x in sys.argv[1:])]:
    base=B%(band,lid); n=get(base+"?where=1%3D1&returnCountOnly=true&f=json")['count']
    feats=[];off=0
    while off<n:
        d=get(base+f"?where=1%3D1&outFields=*&outSR=4326&f=geojson&resultOffset={off}&resultRecordCount=1000")
        feats+=d['features'];off+=1000
    json.dump({"type":"FeatureCollection","features":feats},open(f"{band}_{lid}.geojson","w"))
    print(band,lid,n,len(feats),flush=True)
