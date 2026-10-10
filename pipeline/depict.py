"""Historical map and aerial layers per site, pre-built from tile services onto the site box.

usage: depict.py data/sites/<id>/site.json [layer ...]      (default: every layer that covers the site)
Writes web/data/sites/<id>/<layer>.webp and lists it in web/data/sites/<id>/depictions.json (the same file
topo.py writes). Pre-building keeps the site working offline and sidesteps services without CORS
(NLS tiles) or outside Web Mercator (Dutch Topotijdreis, RD New). Sources: docs/sources.md.
"""
import io
import json
import math
import os
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pyproj
from PIL import Image
from scipy.ndimage import map_coordinates, zoom

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aw  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "data", "raw", "tiles")
WEB = os.path.join(ROOT, "web", "data", "sites")
IGN = ("https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER={layer}&STYLE={style}"
       "&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&FORMAT={fmt}")
TT = "https://tiles.arcgis.com/tiles/nSZVuSZjHpEZZbRo/arcgis/rest/services/Historische_tijdreis_{year}/MapServer"

# box = rough lon/lat extent where the layer exists (a tile service still answers blank outside its data)
LAYERS = {
    "os1inch": {"kind": "map", "year": 1900, "label": "Ordnance Survey One-inch map, Revised New Series (c. 1900)",
                "box": (-8.7, 49.8, 2.0, 60.9), "grid": "xyz", "maxz": 16,
                "url": "https://mapseries-tilesets.s3.amazonaws.com/1inch_2nd_ed/{z}/{x}/{y}.png",
                "source": "Ordnance Survey One-inch, Revised New Series; georeferenced tiles: National Library of Scotland (CC-BY)"},
    "cassini": {"kind": "map", "year": 1780, "label": "Cassini map of France (1756-1815)",
                "box": (-5.2, 42.3, 8.3, 51.1), "grid": "xyz", "maxz": 14,
                "url": IGN.format(layer="BNF-IGNF_GEOGRAPHICALGRIDSYSTEMS.CASSINI", style="normal", fmt="image/png", z="{z}", x="{x}", y="{y}"),
                "source": "Carte de Cassini, Bibliotheque nationale de France; tiles: IGN Geoplateforme"},
    "etatmajor": {"kind": "map", "year": 1840, "label": "Etat-major map of France (1820-1866)",
                  "box": (-5.2, 42.3, 8.3, 51.1), "grid": "xyz", "maxz": 15,
                  "url": IGN.format(layer="GEOGRAPHICALGRIDSYSTEMS.ETATMAJOR40", style="normal", fmt="image/jpeg", z="{z}", x="{x}", y="{y}"),
                  "source": "Carte de l'etat-major (1:40,000 minutes); tiles: IGN Geoplateforme"},
    "fr_ortho1950": {"kind": "aerial", "year": 1957, "label": "Aerial photographs of France (1950-1965)",
                     "box": (-5.2, 42.3, 8.3, 51.1), "grid": "xyz", "maxz": 17,
                     "url": IGN.format(layer="ORTHOIMAGERY.ORTHOPHOTOS.1950-1965", style="BDORTHOHISTORIQUE", fmt="image/png", z="{z}", x="{x}", y="{y}"),
                     "source": "BD ORTHO historique 1950-1965, IGN"},
    "tmk1850": {"kind": "map", "year": 1850, "label": "Topographic and Military Map of the Netherlands (TMK, c. 1850)",
                "box": (3.3, 50.7, 7.3, 53.6), "grid": "rd", "url": TT.format(year=1850),
                "source": "Topographische en Militaire Kaart; tiles: Kadaster / Esri Nederland (Topotijdreis)"},
    "iowa1930": {"kind": "aerial", "year": 1938, "label": "USDA aerial photographs of Iowa (1936-1941)",
                 "box": (-96.7, 40.37, -90.1, 43.51), "grid": "xyz", "maxz": 17,
                 "url": "https://programs.iowadnr.gov/geospatial/rest/services/reference/imagery1930x/MapServer/tile/{z}/{y}/{x}",
                 "source": "USDA 1930s aerial photography; scans and mosaic: Iowa DNR / Iowa State University GIS Facility"},
}


def get(url, path, tries=4):
    if os.path.exists(path):
        return open(path, "rb").read() or None
    os.makedirs(os.path.dirname(path), exist_ok=True)
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=aw.UA), timeout=60) as r:
                body = r.read()
                if not r.headers.get("Content-Type", "").startswith("image"):
                    body = b""
            break
        except urllib.error.HTTPError as e:
            if e.code in (400, 404):  # outside the layer's data
                body = b""
                break
            if i == tries - 1:
                raise
            time.sleep(3 * (i + 1))
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(3 * (i + 1))
    open(path, "wb").write(body)  # an empty file remembers a blank tile
    return body or None


def xyz_mosaic(L, name, bbox, px_m, lat):
    """Mosaic Web Mercator tiles covering bbox at the zoom closest to px_m. Returns (RGBA array, its bbox)."""
    mpp0 = 2 * math.pi * aw.R / 256  # Mercator metres per pixel at zoom 0
    z = int(min(L["maxz"], max(0, round(math.log2(mpp0 * math.cos(math.radians(lat)) / px_m)))))
    span = 2 * math.pi * aw.R / 2 ** z
    org = math.pi * aw.R
    tx0, tx1 = int((bbox[0] + org) // span), int((bbox[2] + org) // span)
    ty0, ty1 = int((org - bbox[3]) // span), int((org - bbox[1]) // span)
    out = np.zeros(((ty1 - ty0 + 1) * 256, (tx1 - tx0 + 1) * 256, 4), np.uint8)
    keys = [(tx, ty) for ty in range(ty0, ty1 + 1) for tx in range(tx0, tx1 + 1)]
    fetch = lambda k: get(L["url"].format(z=z, x=k[0], y=k[1]), os.path.join(CACHE, name, str(z), str(k[0]), f"{k[1]}.img"))
    with ThreadPoolExecutor(4) as ex:  # a few at a time: free services
        for (tx, ty), body in zip(keys, ex.map(fetch, keys)):
            if body:
                im = np.asarray(Image.open(io.BytesIO(body)).convert("RGBA"))
                out[(ty - ty0) * 256:(ty - ty0 + 1) * 256, (tx - tx0) * 256:(tx - tx0 + 1) * 256] = im
    mb = (tx0 * span - org, org - (ty1 + 1) * span, (tx1 + 1) * span - org, org - ty0 * span)
    return out, mb, z


def sample_xyz(L, name, bbox, ow, oh, lat):
    px_m = (bbox[2] - bbox[0]) / ow * math.cos(math.radians(lat))
    mos, mb, z = xyz_mosaic(L, name, bbox, px_m, lat)
    H, W = mos.shape[:2]
    cols = ((bbox[0] - mb[0]) + (np.arange(ow) + 0.5) * (bbox[2] - bbox[0]) / ow) / (mb[2] - mb[0]) * W - 0.5
    rows = ((mb[3] - bbox[3]) + (np.arange(oh) + 0.5) * (bbox[3] - bbox[1]) / oh) / (mb[3] - mb[1]) * H - 0.5
    C, R = np.meshgrid(cols, rows)
    return np.dstack([map_coordinates(mos[..., c].astype(np.float32), [R, C], order=1) for c in range(4)]).astype(np.uint8), z


_rd_info = {}


def sample_rd(L, name, bbox, ow, oh):
    """Dutch Topotijdreis tiles are in RD New (EPSG:28992): sample them through a coordinate transform."""
    if L["url"] not in _rd_info:
        with urllib.request.urlopen(urllib.request.Request(L["url"] + "?f=json", headers=aw.UA), timeout=60) as r:
            _rd_info[L["url"]] = json.load(r)["tileInfo"]
    ti = _rd_info[L["url"]]
    ox, oy = ti["origin"]["x"], ti["origin"]["y"]
    tr = pyproj.Transformer.from_crs("EPSG:3857", "EPSG:28992", always_xy=True)
    step = 8
    cols, rows = np.arange(0, ow + step, step), np.arange(0, oh + step, step)
    X, Y = np.meshgrid(bbox[0] + (cols + 0.5) * (bbox[2] - bbox[0]) / ow, bbox[3] - (rows + 0.5) * (bbox[3] - bbox[1]) / oh)
    E, N = tr.transform(X, Y)
    px_rd = (E.max() - E.min()) / ow
    lod = min(ti["lods"], key=lambda l: abs(math.log(l["resolution"] / px_rd)))
    res, lvl = lod["resolution"], lod["level"]
    span = res * 256
    tx0, tx1 = int((E.min() - ox) // span), int((E.max() - ox) // span)
    ty0, ty1 = int((oy - N.max()) // span), int((oy - N.min()) // span)
    mos = np.zeros(((ty1 - ty0 + 1) * 256, (tx1 - tx0 + 1) * 256, 4), np.uint8)
    keys = [(tx, ty) for ty in range(ty0, ty1 + 1) for tx in range(tx0, tx1 + 1)]
    fetch = lambda k: get(f"{L['url']}/tile/{lvl}/{k[1]}/{k[0]}", os.path.join(CACHE, name, str(lvl), str(k[0]), f"{k[1]}.img"))
    with ThreadPoolExecutor(4) as ex:
        for (tx, ty), body in zip(keys, ex.map(fetch, keys)):
            if body:
                mos[(ty - ty0) * 256:(ty - ty0 + 1) * 256, (tx - tx0) * 256:(tx - tx0 + 1) * 256] = np.asarray(Image.open(io.BytesIO(body)).convert("RGBA"))
    up = lambda a: zoom(a, step, order=1)[:oh, :ow]
    C = up((E - ox) / res - tx0 * 256 - 0.5)
    R = up((oy - N) / res - ty0 * 256 - 0.5)
    return np.dstack([map_coordinates(mos[..., c].astype(np.float32), [R, C], order=1) for c in range(4)]).astype(np.uint8), lvl


def covers(L, lon, lat):
    x0, y0, x1, y1 = L["box"]
    return x0 <= lon <= x1 and y0 <= lat <= y1


def build(site, names=None):
    sid = site["id"]
    bbox = aw.site_bbox(site["lon"], site["lat"], site["width_m"], site["height_m"])
    names = names or [n for n, L in LAYERS.items() if covers(L, site["lon"], site["lat"])]
    if not names:
        return []
    px = max(1.0, max(site["width_m"], site["height_m"]) / 2400)
    ow, oh = int(site["width_m"] / px), int(site["height_m"] / px)
    out_dir = os.path.join(WEB, sid)
    os.makedirs(out_dir, exist_ok=True)
    dep_path = os.path.join(out_dir, "depictions.json")
    deps = json.load(open(dep_path)) if os.path.exists(dep_path) else {"depictions": []}
    made = []
    for name in names:
        L = LAYERS[name]
        img, z = sample_rd(L, name, bbox, ow, oh) if L["grid"] == "rd" else sample_xyz(L, name, bbox, ow, oh, site["lat"])
        # blank tiles come back fully transparent or (some services) pure white/black
        rgb = img[..., :3].astype(int)
        blank = (img[..., 3] < 10) | (rgb.min(2) > 250) | (rgb.max(2) < 5)
        if (~blank).mean() < 0.2:
            print(sid, name, "no data here")
            continue
        file = f"{name}.webp"
        Image.fromarray(img, "RGBA").save(os.path.join(out_dir, file), quality=82, method=6)
        entry = {"kind": L["kind"], "file": file, "year": L["year"], "label": L["label"], "corners": aw.corners(bbox),
                 "coverage": round(float((~blank).mean()), 3), "source": L["source"], "zoom": z}
        deps["depictions"] = [d for d in deps["depictions"] if d.get("file") != file] + [entry]
        made.append(name)
        print(sid, name, f"zoom {z}", f"coverage {entry['coverage']:.0%}", os.path.getsize(os.path.join(out_dir, file)) // 1024, "KB")
    deps["depictions"].sort(key=lambda d: d.get("year", 0))
    aw.save_json(dep_path, deps)
    return made


if __name__ == "__main__":
    build(json.load(open(sys.argv[1])), sys.argv[2:] or None)
