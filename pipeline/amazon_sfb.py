"""Brazilian Forest Service (SFB) concession LiDAR as map tiles, for looking at by eye on the page (Finder tab).

usage: amazon_sfb.py list <area>                     survey units and years in the area's zip
       amazon_sfb.py build <area> [--units JAM01,JAM02] [--latest]

Ethan 2026-10-10: eye review over detectors ("b is cool"). The data: Fischer et al.'s processed SFB acquisitions on Zenodo
(1 m dtm.tif per survey and year; CC BY 4.0 for the products, the raw data belong to the Brazilian Forest Service, research and
education use, credit required). Ethan: never use their data publicly. So everything this writes is gitignored and the page
shows it only on the LAN: the DTMs in data/finder/amazon/sfb/<area>/, the tiles in web/data/amazon/tiles/, the index in
web/data/amazon/areas.json.

build: every survey (unit x year: each year's survey of a unit is mostly a different block, the year's harvest area; --latest
keeps only the newest per unit), the 1 m DTM is fetched out of the zip by range
requests (remote_zip.py), rendered as local relief in the page's sepia (the same render as the site reliefs, radius 20 m: ditches
and banks of a few metres show, hills do not), and cut into Web Mercator tiles z12-17 by reprojecting each tile from the DTM's own
UTM grid. Overlapping surveys: the newer one on top.
"""
import io
import json
import math
import os
import re
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aw  # noqa: E402
import remote_zip  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "finder", "amazon", "sfb")
OUT = os.path.join(ROOT, "web", "data", "amazon")
Z = "https://zenodo.org/api/records/{rec}/files/{name}/content"
AREAS = {
    "jamari": dict(rec=18683137, zip="Jamari.zip", label="Jamari National Forest", state="Rondonia"),
    "jacunda": dict(rec=18683137, zip="Jacunda.zip", label="Jacunda National Forest", state="Rondonia"),
    "altamira": dict(rec=18625750, zip="Altamira.zip", label="Altamira National Forest", state="Para"),
    "caxiuana": dict(rec=18709751, zip="Caxiuana.zip", label="Caxiuana National Forest", state="Para"),
    "saraca-taquera": dict(rec=18709751, zip="Saraca_Taquera.zip", label="Saraca-Taquera National Forest", state="Para"),
    "amapa": dict(rec=10845590, zip="Amapa.zip", label="Amapa National Forest", state="Amapa"),
    "bom-futuro": dict(rec=10845590, zip="Bom_Futuro.zip", label="Bom Futuro National Forest", state="Rondonia"),
    "crepori": dict(rec=10845590, zip="Crepori.zip", label="Crepori National Forest", state="Para"),
}
CREDIT = ("LiDAR: Brazilian Forest Service (SFB) forest-concession surveys, processed by Fischer et al. (Zenodo, CC BY 4.0); "
          "research and education use only")
ZMIN, ZMAX = 12, 17
RADIUS_M = 20.0
HALF = math.pi * aw.R


def url(area):
    a = AREAS[area]
    return Z.format(rec=a["rec"], name=a["zip"])


def surveys(area):
    """{(unit, year): member} for every dtm.tif in the area's zip (central directory only)."""
    out = {}
    for i in remote_zip.open_zip(url(area)).infolist():
        m = re.search(r"(?:^|/)(\d{4})/([^/]+)/dtm\.tif$", i.filename)
        if m:
            out[(m.group(2), int(m.group(1)))] = (i.filename, i.file_size)
    return out


def pick(found, units=None, all_years=True):
    by_unit = {}
    for (u, y), mem in found.items():
        if units and u not in units:
            continue
        by_unit.setdefault(u, []).append((y, mem))
    keep = []
    for u, ys in sorted(by_unit.items()):
        ys.sort()
        keep += [(u, y, m) for y, m in (ys if all_years else ys[-1:])]
    return sorted(keep, key=lambda k: k[1])  # oldest first: newer surveys are drawn over older ones


def relief_rgba(path):
    """(RGBA uint8 array, rasterio profile) of a DTM rendered as sepia local relief; transparent where the DTM has no data."""
    import rasterio
    import build_site
    with rasterio.open(path) as src:
        z = src.read(1).astype(np.float64)
        prof = src.profile
        if src.nodata is not None:
            z[z == src.nodata] = np.nan
    z[(z < -500) | (z > 9000)] = np.nan
    have = np.isfinite(z)
    # the forest-floor DTM is speckled at 1 m (tree throws, residual low vegetation); a 1-cell smoothing calms it and keeps
    # anything a few metres across, which is all an eye review for big geometric works needs
    from scipy.ndimage import gaussian_filter
    zf = aw.fill_nan(z)
    z = np.where(have, gaussian_filter(zf, 1.0), np.nan)
    img, _ = aw.render_relief(z, abs(prof["transform"].a), radius_m=RADIUS_M)
    rgb = build_site.duotone(img).astype(np.uint8)
    return np.dstack([rgb, np.where(have, 255, 0).astype(np.uint8)]), prof


def tile_bounds(z, x, y):
    s = 2 * HALF / 2 ** z
    return -HALF + x * s, HALF - (y + 1) * s, -HALF + (x + 1) * s, HALF - y * s


def cut_tiles(rgba, prof, tiles_dir):
    """Reproject the relief into every z12-17 tile it touches; composite over tiles already there. Returns (lon/lat bounds, n tiles)."""
    import rasterio.warp
    from rasterio.enums import Resampling
    from rasterio.transform import from_bounds
    h, w = rgba.shape[:2]
    l, b, r, t = rasterio.warp.transform_bounds(prof["crs"], "EPSG:3857", *rasterio.transform.array_bounds(h, w, prof["transform"]))
    n = 0
    for z in range(ZMAX, ZMIN - 1, -1):
        s = 2 * HALF / 2 ** z
        x0, x1 = int((l + HALF) // s), int((r + HALF) // s)
        y0, y1 = int((HALF - t) // s), int((HALF - b) // s)
        rs = Resampling.bilinear if z == ZMAX else Resampling.average
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                dst = np.zeros((4, 256, 256), np.uint8)
                for k in range(4):
                    rasterio.warp.reproject(rgba[..., k], dst[k], src_transform=prof["transform"], src_crs=prof["crs"],
                                            dst_transform=from_bounds(*tile_bounds(z, x, y), 256, 256), dst_crs="EPSG:3857",
                                            resampling=Resampling.nearest if k == 3 else rs)
                if not dst[3].any():
                    continue
                im = Image.fromarray(np.moveaxis(dst, 0, -1), "RGBA")
                p = os.path.join(tiles_dir, str(z), str(x), f"{y}.webp")
                os.makedirs(os.path.dirname(p), exist_ok=True)
                if os.path.exists(p):
                    im = Image.alpha_composite(Image.open(p).convert("RGBA"), im)
                im.save(p, quality=82, method=4)
                n += 1
    lon0, lat0 = aw.to_lonlat(l, b)
    lon1, lat1 = aw.to_lonlat(r, t)
    return [round(lon0, 6), round(lat0, 6), round(lon1, 6), round(lat1, 6)], n


def outline(rgba, prof, step=16):
    """Lon/lat ring around the surveyed area (convex hull of the covered cells, every `step` cells)."""
    import rasterio.warp
    from scipy.spatial import ConvexHull
    rr, cc = np.nonzero(rgba[::step, ::step, 3])
    pts = np.stack([cc * step + 0.5, rr * step + 0.5], 1)
    hull = pts[ConvexHull(pts).vertices]
    tr = prof["transform"]
    xs, ys = tr.c + hull[:, 0] * tr.a, tr.f + hull[:, 1] * tr.e
    lon, lat = rasterio.warp.transform(prof["crs"], "EPSG:4326", xs.tolist(), ys.tolist())
    ring = [[round(a, 6), round(b, 6)] for a, b in zip(lon, lat)]
    return ring + ring[:1]


def build(area, units=None, all_years=True):
    found = surveys(area)
    todo = pick(found, units, all_years)
    print(area, len(found), "surveys in the zip;", len(todo), "to build:", " ".join(f"{u}-{y}" for u, y, _ in todo), flush=True)
    os.makedirs(os.path.join(RAW, area), exist_ok=True)
    idx_path = os.path.join(OUT, "areas.json")
    idx = json.load(open(idx_path)) if os.path.exists(idx_path) else {"areas": []}
    entry = next((a for a in idx["areas"] if a["name"] == area), None)
    if entry is None:
        entry = {"name": area, "label": AREAS[area]["label"], "state": AREAS[area]["state"], "credit": CREDIT,
                 "tiles": "data/amazon/tiles/{z}/{x}/{y}.webp", "minzoom": ZMIN, "maxzoom": ZMAX, "surveys": []}
        idx["areas"].append(entry)
    tiles_dir = os.path.join(OUT, "tiles")
    path_of = lambda u, y: os.path.join(RAW, area, f"{y}_{u}_dtm.tif")
    need = [(u, y, m) for u, y, (m, _) in todo if not os.path.exists(path_of(u, y))]
    if need:  # Zenodo serves ~0.7 MB/s per connection: fetch in parallel, then render one by one (tiles are composited)
        from concurrent.futures import ThreadPoolExecutor
        print(f"  fetching {len(need)} DTMs, {sum(found[(u, y)][1] for u, y, _ in need) / 1e6:.0f} MB", flush=True)
        with ThreadPoolExecutor(5) as ex:
            list(ex.map(lambda t: remote_zip.get(url(area), t[2], path_of(t[0], t[1])), need))
    for u, y, (member, size) in todo:
        sid = f"{u}-{y}"
        path = path_of(u, y)
        rgba, prof = relief_rgba(path)
        bounds, n = cut_tiles(rgba, prof, tiles_dir)
        km2 = float((rgba[..., 3] > 0).sum()) * abs(prof["transform"].a * prof["transform"].e) / 1e6
        rec = {"id": sid, "unit": u, "year": y, "bounds": bounds, "outline": outline(rgba, prof), "km2": round(km2, 2)}
        entry["surveys"] = [s for s in entry["surveys"] if s["id"] != sid] + [rec]
        print(f"  {sid}: {km2:.1f} km2, {n} tiles", flush=True)
    entry["surveys"].sort(key=lambda s: (s["unit"], s["year"]))
    bs = [s["bounds"] for s in entry["surveys"]]
    entry["bounds"] = [min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs)]
    os.makedirs(OUT, exist_ok=True)
    aw.save_json(idx_path, idx)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "list":
        for (u, y), (m, size) in sorted(surveys(a[1]).items()):
            print(f"{u:10} {y}  {size / 1e6:7.1f} MB  {m}")
    elif a[0] == "build":
        units = set(a[a.index("--units") + 1].split(",")) if "--units" in a else None
        build(a[1], units, "--latest" not in a)
