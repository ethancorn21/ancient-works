"""Scotland's open LiDAR (Scottish Government / Historic Environment Scotland / Orkney): ready-made bare-earth DTM GeoTIFFs
in British National Grid on the srsp-open-data bucket (eu-west-2), read by window onto the site's Mercator grid.

Datasets (lidar/<set>/dtm/27700/gridded/), finest first (the survey years in DATASETS are approximate: check the NLS/SRSP
metadata before quoting one): HES heritage surveys at 25 cm and 50 cm, the National LiDAR Programme and
Orkney 2023 at 50 cm in 1 km tiles, phases 3-6 at 50 cm in 5 km tiles, phases 1-2 at 1 m in 10 km tiles. Tile names start with an
OS grid reference: HY21 (10 km), NS16NE (5 km quadrant), NG2004 (1 km). Open Government Licence.

usage: python3 pipeline/lidar_scot.py <lon> <lat> [width_m height_m]     which datasets cover the box
"""
import concurrent.futures as cf
import json
import math
import os
import re
import sys

import numpy as np
import pyproj
import rasterio
from rasterio.windows import Window
from scipy.ndimage import map_coordinates, zoom

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aw  # noqa: E402
import s3  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw", "lidar_scot")
BUCKET, REGION = "srsp-open-data", "eu-west-2"
pyproj.datadir.append_data_dir(os.path.join(ROOT, "data", "tilecache", "proj"))  # OSTN15 (dem_sources.py fetches it), so OSGB36 <-> WGS84 is exact
LETTERS = "ABCDEFGHJKLMNOPQRSTUVWXYZ"
GDAL = {"GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR", "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": ".tif", "GDAL_HTTP_MAX_RETRY": "4",
        "GDAL_HTTP_RETRY_DELAY": "3", "VSI_CACHE": "TRUE"}
# prefix, label, finest cell in m, survey year (the newest wins among equally fine sets that cover the box)
DATASETS = [
    ("lidar/hes/hes-2016/", "HES 2016", 0.25, 2016), ("lidar/hes/hes-2016-2017/", "HES 2016-17", 0.25, 2017), ("lidar/hes/hes-2017/", "HES 2017", 0.25, 2017),
    ("lidar/hes/hes-2017sp3/", "HES 2017 (Orkney)", 0.5, 2017), ("lidar/hes/hes-2010s10/", "HES 2010 (Orkney)", 0.5, 2010), ("lidar/hes/hes_2010/", "HES 2010", 0.5, 2010),
    ("lidar/hes/luing/", "HES Luing", 0.5, 2013), ("lidar/national-lidar-programme/", "National LiDAR Programme", 0.5, 2022),
    ("lidar/orkney-islands-council-23/", "Orkney 2023", 0.5, 2023), ("lidar/phase-6/", "Phase 6", 0.5, 2022), ("lidar/phase-5/", "Phase 5", 0.5, 2014),
    ("lidar/phase-4/", "Phase 4", 0.5, 2013), ("lidar/phase-3/", "Phase 3", 0.5, 2012), ("lidar/phase-2/", "Phase 2", 1.0, 2012), ("lidar/phase-1/", "Phase 1", 1.0, 2011),
]
YEAR = {p: y for p, _, _, y in DATASETS}


def square_origin(l1, l2):
    """South-west corner (E, N) of a 100 km OS grid square from its two letters."""
    a, b = LETTERS.index(l1), LETTERS.index(l2)
    return (((a - 2) % 5) * 5 + b % 5) * 100000, ((19 - (a // 5) * 5) - b // 5) * 100000


def tile_bounds(name):
    """(x0, y0, x1, y1) in British National Grid of an OS-referenced tile name, or None."""
    m = re.match(r"^([A-HJ-Z])([A-HJ-Z])(\d\d)(\d\d)?(NE|NW|SE|SW)?(?=_)", name)
    if not m:
        return None
    e0, n0 = square_origin(m.group(1), m.group(2))
    if m.group(4):  # 1 km: letters + 4 digits
        x, y, size = e0 + int(m.group(3)) * 1000, n0 + int(m.group(4)) * 1000, 1000
    else:
        x, y, size = e0 + int(m.group(3)[0]) * 10000, n0 + int(m.group(3)[1]) * 10000, 10000
        if m.group(5):
            x, y, size = x + (5000 if m.group(5) in ("NE", "SE") else 0), y + (5000 if m.group(5) in ("NE", "NW") else 0), 5000
    return x, y, x + size, y + size


def index():
    """[{set, label, cell_m, key, bounds, size}] for every DTM tile, cached."""
    path = os.path.join(RAW, "index.json")
    if not os.path.exists(path):
        os.makedirs(RAW, exist_ok=True)
        out = []
        for prefix, label, cell, _ in DATASETS:
            for key, size, _ in s3.ls(BUCKET, prefix + "dtm/27700/gridded/", delim="", region=REGION)[1]:
                b = tile_bounds(os.path.basename(key)) if key.endswith(".tif") else None
                if b:
                    m = re.search(r"_(\d+)(CM|cm)_", key)
                    out.append({"set": prefix, "label": label, "cell_m": int(m.group(1)) / 100 if m else cell, "key": key, "bounds": b, "size": size})
        json.dump(out, open(path, "w"))
    return json.load(open(path))


def native_box(bbox):
    t = pyproj.Transformer.from_crs(3857, 27700, always_xy=True)
    xs = np.concatenate([np.linspace(bbox[0], bbox[2], 9), np.full(9, bbox[2]), np.linspace(bbox[2], bbox[0], 9), np.full(9, bbox[0])])
    ys = np.concatenate([np.full(9, bbox[1]), np.linspace(bbox[1], bbox[3], 9), np.full(9, bbox[3]), np.linspace(bbox[3], bbox[1], 9)])
    X, Y = t.transform(xs, ys)
    return min(X), min(Y), max(X), max(Y)


def actual_bounds(keys):
    """The real extent of each GeoTIFF, from its header (cached): tiles are clipped to where there is data, so a '10 km' tile can be
    5 km by 3 km. {key: (x0, y0, x1, y1)}"""
    path = os.path.join(RAW, "bounds.json")
    cache = json.load(open(path)) if os.path.exists(path) else {}
    need = [k for k in keys if k not in cache]
    if need:
        def one(k):
            try:
                with rasterio.Env(**GDAL), rasterio.open(s3.url(BUCKET, k, REGION)) as src:
                    b = src.bounds
                    return k, [round(b.left, 1), round(b.bottom, 1), round(b.right, 1), round(b.top, 1)]
            except Exception:
                return k, None
        with cf.ThreadPoolExecutor(12) as ex:
            cache.update(ex.map(one, need))
        os.makedirs(RAW, exist_ok=True)
        aw.save_json(path, cache)
    return {k: cache[k] for k in keys if cache.get(k)}


def candidates(lon, lat, width_m, height_m):
    """Datasets with tiles on the box, best first: [{set, label, cell_m, tiles, coverage}]."""
    bbox = aw.site_bbox(lon, lat, width_m, height_m)
    x0, y0, x1, y1 = native_box(bbox)
    nominal = [t for t in index() if t["bounds"][0] < x1 and t["bounds"][2] > x0 and t["bounds"][1] < y1 and t["bounds"][3] > y0]
    real = actual_bounds([t["key"] for t in nominal])
    by = {}
    for t in nominal:
        b = real.get(t["key"])
        if b and b[0] < x1 and b[2] > x0 and b[1] < y1 and b[3] > y0:
            by.setdefault(t["set"], []).append(dict(t, bounds=b))
    out = []
    n = 50
    gx, gy = np.linspace(x0, x1, n), np.linspace(y0, y1, n)
    for pref, tiles in by.items():
        cov = np.zeros((n, n), bool)
        for t in tiles:
            b = t["bounds"]
            cov |= ((gx >= b[0]) & (gx < b[2]))[None, :] & ((gy >= b[1]) & (gy < b[3]))[:, None]
        out.append({"set": pref, "label": tiles[0]["label"], "cell_m": tiles[0]["cell_m"], "tiles": tiles, "coverage": round(float(cov.mean()), 3)})
    out.sort(key=lambda c: (c["coverage"] >= 0.95, -c["cell_m"], YEAR[c["set"]]), reverse=True)  # full cover, then finest, then newest
    return out


def _sample(src, bbox, w, h, step=16):
    """One GeoTIFF sampled bilinearly onto the Mercator grid; NaN where it has no data."""
    t = pyproj.Transformer.from_crs(3857, 27700, always_xy=True)
    x0, y0, x1, y1 = bbox
    cols, rows = np.arange(0, w + step, step), np.arange(0, h + step, step)
    X, Y = np.meshgrid(x0 + (cols + 0.5) * (x1 - x0) / w, y1 - (rows + 0.5) * (y1 - y0) / h)
    E, N = t.transform(X, Y)
    up = lambda a: zoom(a, step, order=1)[:h, :w]
    E, N = up(E), up(N)
    tr = src.transform
    C, R = (E - tr.c) / tr.a - 0.5, (N - tr.f) / tr.e - 0.5
    c0, c1, r0, r1 = int(np.floor(np.nanmin(C))) - 2, int(np.ceil(np.nanmax(C))) + 3, int(np.floor(np.nanmin(R))) - 2, int(np.ceil(np.nanmax(R))) + 3
    cc0, cc1, rr0, rr1 = max(c0, 0), min(c1, src.width), max(r0, 0), min(r1, src.height)
    if cc0 >= cc1 or rr0 >= rr1:
        return np.full((h, w), np.nan)
    a = src.read(1, window=Window(cc0, rr0, cc1 - cc0, rr1 - rr0)).astype(np.float64)
    a[(a == src.nodata) | (a < -500) | ~np.isfinite(a)] = np.nan
    pad = np.full((r1 - r0, c1 - c0), np.nan)
    pad[rr0 - r0:rr1 - r0, cc0 - c0:cc1 - c0] = a
    z = map_coordinates(pad, [R - r0, C - c0], order=1, cval=np.nan, prefilter=False)
    edge = np.isnan(z)  # a sample half a pixel past a tile's last row/column has a NaN neighbour: take the nearest pixel instead,
    if edge.any():      # or every 1 km tile boundary shows up as a dashed gap
        z0 = map_coordinates(pad, [R - r0, C - c0], order=0, cval=np.nan, prefilter=False)
        z[edge] = z0[edge]
    return z


def read_dem(bbox, w, h, lon=None, lat=None):
    """Bare-earth DTM (metres, ODN) for a Mercator bbox at w x h pixels, same contract as aw.fetch_dem. Returns (z, info)."""
    if lon is None:
        lon, lat = aw.to_lonlat((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)
    width_m = (bbox[2] - bbox[0]) * math.cos(math.radians(lat))
    height_m = (bbox[3] - bbox[1]) * math.cos(math.radians(lat))
    cands = [c for c in candidates(lon, lat, width_m, height_m) if c["coverage"] > 0.05]
    if not cands:
        raise RuntimeError("no Scottish LiDAR tiles on this box")
    z = np.full((h, w), np.nan)
    info = []
    for c in cands:  # best dataset first, the others fill what it lacks
        got = 0
        for t in c["tiles"]:
            with rasterio.Env(**GDAL), rasterio.open(s3.url(BUCKET, t["key"], REGION)) as src:
                part = _sample(src, bbox, w, h)
            fill = np.isnan(z) & ~np.isnan(part)
            z[fill] = part[fill]
            got += int(fill.sum())
        if got:
            who = ("Historic Environment Scotland" if "/hes/" in c["set"] else "Orkney Islands Council" if "orkney" in c["set"] else "Scottish Government")
            info.append({"source": f"Scotland {c['label']} ({c['cell_m']} m DTM)", "credit": f"{who}, {c['cell_m']} m DTM ({c['label']})",
                         "share": round(got / z.size, 3), "collect_end": None})
        if not np.isnan(z).any():
            break
    return z, info


if __name__ == "__main__":
    lon, lat = float(sys.argv[1]), float(sys.argv[2])
    wm, hm = (float(sys.argv[3]), float(sys.argv[4])) if len(sys.argv) > 4 else (2000.0, 2000.0)
    for c in candidates(lon, lat, wm, hm):
        print(f"{c['label']:<28} {c['cell_m']:>5} m  {len(c['tiles']):>3} tiles  covers {c['coverage']:.0%}  {c['set']}")
