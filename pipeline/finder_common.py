"""Shared bits for the Finder: areas, distances, terrain strata, Wilson intervals, 1 m DEM crops (cached).

Areas are fixed in docs/finder.md section 1 (tune vs held out); do not edit their boxes after the gate.
"""
import hashlib
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aw  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FD = os.path.join(ROOT, "data", "finder")

AREAS = {  # name: (lon0, lat0, lon1, lat1, role)
    "ross": (-83.12, 39.24, -82.88, 39.42, "tune"),
    "newark": (-82.53, 39.97, -82.33, 40.09, "heldout"),
    "fortancient": (-84.29, 39.30, -84.06, 39.43, "heldout"),
    "miamisburg": (-84.47, 39.57, -84.20, 39.68, "heldout"),
}


def area_of(lon, lat):
    for k, (a, b, c, d, _) in AREAS.items():
        if a <= lon <= c and b <= lat <= d:
            return k
    return None


def area_km2(box):
    lon0, lat0, lon1, lat1 = box[:4]
    w = (lon1 - lon0) * 111.32 * math.cos(math.radians((lat0 + lat1) / 2))
    return w * (lat1 - lat0) * 110.95


def hav_m(lon1, lat1, lon2, lat2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 2 * 6371008.8 * math.asin(math.sqrt(a))


def local_xy(lons, lats, lon0, lat0):
    """Equirectangular metres around (lon0, lat0): fine for distances under ~50 km."""
    lons, lats = np.asarray(lons, float), np.asarray(lats, float)
    return ((lons - lon0) * 111320.0 * math.cos(math.radians(lat0)), (lats - lat0) * 110950.0)


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(c - h, 3), round(c + h, 3))


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def load_jsonl(path):
    return [json.loads(l) for l in open(path)] if os.path.exists(path) else []


def save_jsonl(path, rows):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    os.replace(tmp, path)


CROP_DIR = os.path.join(FD, "dem1m")


def dem_crop(lon, lat, half_m=180, px_m=1.0):
    """Bare-earth DEM around a point at 1 m/px, cached as .npz (float32). Returns z, mercator bbox."""
    os.makedirs(CROP_DIR, exist_ok=True)
    key = f"{lon:.5f}_{lat:.5f}_{int(half_m)}_{px_m:g}"
    p = os.path.join(CROP_DIR, key + ".npz")
    bbox = aw.site_bbox(lon, lat, 2 * half_m, 2 * half_m)
    n = int(round(2 * half_m / px_m))
    if os.path.exists(p):
        return np.load(p)["z"], bbox
    z = aw.fetch_dem(bbox, n, n).astype(np.float32)
    np.savez_compressed(p, z=z)
    return z, bbox


def terrain_class(z, px_m, row, col, r_m=1000.0):
    """'valley' if the point is less than 15 m above the lowest ground within r_m (sampled on the given DEM)."""
    r = int(r_m / px_m)
    r0, r1 = max(0, row - r), min(z.shape[0], row + r + 1)
    c0, c1 = max(0, col - r), min(z.shape[1], col + r + 1)
    sub = z[r0:r1:4, c0:c1:4]
    lo = np.nanmin(sub) if np.isfinite(sub).any() else np.nan
    h = z[row, col] - lo
    return ("valley" if h < 15 else "upland"), float(h)
