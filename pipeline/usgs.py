"""USGS 3DEP elevation from the public S3 staging bucket: 1 m DEM tiles read by window, with the 1/3 arc-second
DEM as the fallback, plus a lookup of which LiDAR projects cover a point.

aw.fetch_dem asks the 3DEP ImageServer, which is slow, 5xx-prone and unreachable from some networks. The same
bare-earth DEMs sit on S3 as 10 km GeoTIFF tiles (512 px blocks, LZW, overviews), so a 2 km site box costs a few
MB of range requests instead of a 150 MB download. A 1 m tile is named USGS_1M_<utm zone>_x<E/10km>y<N/10km + 1>_<project>.tif:
x is its west edge and y its NORTH edge, each tile carrying a 6 m overlap on every side.

usage: python3 pipeline/usgs.py <lon> <lat> [width_m height_m]     which 3DEP LiDAR covers the point, and the tiles
"""
import concurrent.futures as cf
import csv
import json
import math
import os
import re
import sys
import time

import numpy as np
import pyproj
import rasterio
from rasterio.enums import Resampling
from rasterio.transform import from_bounds
from rasterio.vrt import WarpedVRT

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aw  # noqa: E402
import s3  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw", "usgs")
BUCKET, EPT_BUCKET = "prd-tnm", "usgs-lidar-public"
ELEV = "StagedProducts/Elevation/"
GDAL = {"GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR", "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": ".tif",
        "GDAL_HTTP_MAX_RETRY": "4", "GDAL_HTTP_RETRY_DELAY": "3", "VSI_CACHE": "TRUE"}


def _cached(name, build, max_age_days=30):
    path = os.path.join(RAW, name)
    if not os.path.exists(path) or time.time() - os.path.getmtime(path) > max_age_days * 86400:
        os.makedirs(RAW, exist_ok=True)
        build(path)
    return path


def wesm():
    """Work Unit Extent Spatial Metadata: one row per 3DEP LiDAR work unit (collection dates, quality level)."""
    path = _cached("WESM.csv", lambda p: s3.get(s3.url(BUCKET, ELEV + "metadata/WESM.csv"), p))
    return {r["workunit"]: r for r in csv.DictReader(open(path, newline=""))}


def ept_bounds():
    """Conforming extent (EPSG:3857) of every EPT point-cloud project on usgs-lidar-public: {name: [x0, y0, x1, y1]}."""
    def build(path):
        names = [p.rstrip("/") for p in s3.ls(EPT_BUCKET, "")[0]]

        def one(n):
            try:
                j = json.loads(s3.get(s3.url(EPT_BUCKET, n + "/ept.json")))
                b = j.get("boundsConforming") or j["bounds"]
                return n, [b[0], b[1], b[3], b[4]]
            except Exception:
                return n, None
        with cf.ThreadPoolExecutor(16) as ex:
            out = dict(ex.map(one, names))
        json.dump({k: v for k, v in out.items() if v}, open(path, "w"))
    return json.load(open(_cached("ept_bounds.json", build, 90)))


def wesm_row(name, meta=None):
    """WESM row of an EPT folder: the folder is a work unit name, or USGS_LPC_<work unit>_LAS_<year> (the older point-cloud releases)."""
    meta = meta or wesm()
    if name in meta:
        return meta[name]
    m = re.match(r"^USGS_LPC_(.+?)(?:_LAS_\d{4})?$", name or "")
    if m:
        for cand in (m.group(1), m.group(1).replace("_B1_", "_B1_"), re.sub(r"_(?:[A-Z]\d{2}|D\d{2}|\d{4})$", "", m.group(1))):
            if cand in meta:
                return meta[cand]
        hits = [r for k, r in meta.items() if k == m.group(1) or k.startswith(m.group(1))]
        if len(hits) == 1:
            return hits[0]
    return {}


def lidar_projects(lon, lat):
    """3DEP LiDAR work units whose extent contains the point, newest first: name, collection dates, quality level."""
    x, y = aw.to_merc(lon, lat)
    meta = wesm()
    out = []
    for name, (x0, y0, x1, y1) in ept_bounds().items():
        if x0 <= x <= x1 and y0 <= y <= y1:
            m = wesm_row(name, meta)
            out.append({"workunit": name, "project": m.get("project"), "collect_start": m.get("collect_start"),
                        "collect_end": m.get("collect_end"), "ql": m.get("ql"), "dem_gsd_m": m.get("dem_gsd_meters")})
    return sorted(out, key=lambda p: p["collect_end"] or "", reverse=True)


def _folders():
    """Names of the 1 m DEM project folders on S3."""
    def build(path):
        json.dump([p.rstrip("/").split("/")[-1] for p in s3.ls(BUCKET, ELEV + "1m/Projects/")[0]], open(path, "w"))
    return set(json.load(open(_cached("folders_1m.json", build, 7))))


def zone_of(lon):
    return int((lon + 180) // 6) + 1


def tile_names(bbox):
    """10 km tiles covering a Mercator bbox, per UTM zone it touches: [(zone, x, y)] in the file-name convention."""
    (lon0, lat0), (lon1, lat1) = aw.to_lonlat(bbox[0], bbox[1]), aw.to_lonlat(bbox[2], bbox[3])
    out = []
    for zone in range(zone_of(lon0), zone_of(lon1) + 1):
        tr = pyproj.Transformer.from_crs(4326, 32600 + zone, always_xy=True)
        pts = [tr.transform(lo, la) for lo in (lon0, lon1) for la in (lat0, lat1)]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        out += [(zone, x, y) for x in range(int(min(xs) // 1e4), int(max(xs) // 1e4) + 1)
                for y in range(int(min(ys) // 1e4) + 1, int(max(ys) // 1e4) + 2)]
    return out


def tile_url(project, zone, x, y):
    return s3.url(BUCKET, f"{ELEV}1m/Projects/{project}/TIFF/USGS_1M_{zone}_x{x}y{y}_{project}.tif")


def tile_sources(bbox, lon, lat, states=()):
    """For each 10 km tile the box needs, the 1 m projects that have it (newest first): [((zone, x, y), [(project, url)])].

    Candidate projects: the work units whose point-cloud extent holds the site, mapped to the folder names S3 uses, plus every 1 m
    folder of the states those work units belong to (and `states`, two-letter codes): work-unit names in the point-cloud bucket do
    not always match the folder names (GA_Central_1_2018 there, GA_Central_2019_B19 here), so a tile is looked for by name."""
    folders = _folders()
    meta = wesm()
    cands = []
    projects = lidar_projects(lon, lat)
    codes = set(states)
    for p in projects:  # work units whose extent holds the site, mapped to the folder names S3 uses
        for name in (p["workunit"], p["project"]):
            if name in folders and name not in cands:
                cands.append(name)
            m = re.match(r"^(?:USGS_LPC_)?([A-Z]{2})_", name or "")
            if m:
                codes.add(m.group(1))
    for code in sorted(codes):
        cands += [f for f in sorted(folders) if f.startswith(code + "_") and f not in cands]

    def year(name):
        ends = [m["collect_end"] for m in meta.values() if name in (m["workunit"], m["project"]) and m["collect_end"]]
        return max(ends) if ends else ""
    cands.sort(key=year, reverse=True)
    jobs = [(t, c) for t in tile_names(bbox) for c in cands]
    with cf.ThreadPoolExecutor(12) as ex:
        have = list(ex.map(lambda j: s3.size(tile_url(j[1], *j[0])) is not None, jobs))
    out = {}
    for (t, c), ok in zip(jobs, have):
        out.setdefault(t, [])
        if ok:
            out[t].append((c, tile_url(c, *t)))
    return list(out.items())


def _warp(u, bbox, w, h, overview=None):
    """One GeoTIFF resampled (bilinear) onto the Mercator grid; NaN where it has no data. Reads only the blocks it needs.
    overview: index into the file's overviews (0 = half size, 1 = quarter ...) for wide, coarse reads."""
    with rasterio.Env(**GDAL), rasterio.open(u, overview_level=overview) as src, WarpedVRT(
            src, crs="EPSG:3857", transform=from_bounds(*bbox, w, h), width=w, height=h,
            resampling=Resampling.bilinear, src_nodata=src.nodata, nodata=np.nan, dtype="float32") as vrt:
        z = vrt.read(1).astype(np.float64)
    z[(z < -1000) | ~np.isfinite(z)] = np.nan
    return z


def _fill_from_point_clouds(z, bbox, w, h, lon, lat, used):
    """Fill the NaN cells of z from the 3DEP point clouds (ept.py), newest work unit first, reading only the rectangle that holds the gap."""
    import ept
    gap = np.isnan(z)
    ys, xs = np.nonzero(gap)
    sx, sy = (bbox[2] - bbox[0]) / w, (bbox[3] - bbox[1]) / h
    pad = 30.0
    region = (bbox[0] + xs.min() * sx - pad, bbox[3] - (ys.max() + 1) * sy - pad, bbox[0] + (xs.max() + 1) * sx + pad, bbox[3] - ys.min() * sy + pad)
    for p in lidar_projects(lon, lat):
        if not np.isnan(z).mean() > 0.001:
            break
        try:
            part, observed = ept.ground_grid(p["workunit"], bbox, w, h, region, log=lambda *a: None)
        except Exception as e:  # unknown vertical units, too many nodes, a work unit with no points here: try the next
            print(f"    point cloud {p['workunit']}: {type(e).__name__} {str(e)[:90]}")
            continue
        fill = np.isnan(z) & ~np.isnan(part)
        if fill.sum() < 0.002 * z.size or observed < 0.02:
            continue
        z[fill] = part[fill]
        used[p["workunit"] + " (point cloud)"] = int(used.get(p["workunit"] + " (point cloud)", 0) + fill.sum())
        print(f"    point cloud {p['workunit']}: filled {fill.mean():.0%} of the box")
    return z


def read_dem(bbox, w, h, lon=None, lat=None, coarse=False, states=()):
    """Bare-earth DEM (metres, NAVD88) for a Mercator bbox at w x h pixels, same grid and contract as aw.fetch_dem.

    Returns (z, info): info says which project and collection year each part came from. 1 m LiDAR tiles first (newest
    project wins, older ones fill its gaps), then the 1/3 arc-second DEM where no 1 m tile exists."""
    if lon is None:
        lon, lat = aw.to_lonlat((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)
    z = np.full((h, w), np.nan)
    used = {}
    px = (bbox[2] - bbox[0]) * math.cos(math.radians(lat)) / w
    ov = max(0, int(math.log2(px)) - 1) if coarse and px >= 2 else None  # a wide, coarse box reads an overview, not every 1 m block
    for t, srcs in tile_sources(bbox, lon, lat, states):
        for project, u in srcs:
            part = _warp(u, bbox, w, h, ov)
            fill = np.isnan(z) & ~np.isnan(part)
            if fill.any():
                z[fill] = part[fill]
                used[project] = int(used.get(project, 0) + fill.sum())
            if not np.isnan(z).any():
                break
    if np.isnan(z).mean() > 0.02:  # a tile that stops short of the box, or no 1 m DEM published for the area: the point clouds it is made from
        z = _fill_from_point_clouds(z, bbox, w, h, lon, lat, used)
    if np.isnan(z).mean() > 0.001:  # holes or no 1 m coverage at all: 1/3 arc-second DEM
        (lon0, lat0), (lon1, lat1) = aw.to_lonlat(bbox[0], bbox[1]), aw.to_lonlat(bbox[2], bbox[3])
        for la in range(math.ceil(lat0), math.ceil(lat1) + 1):
            for lo in range(math.ceil(-lon1), math.ceil(-lon0) + 1):
                name = f"n{la:02d}w{lo:03d}"
                u = s3.url(BUCKET, f"{ELEV}13/TIFF/current/{name}/USGS_13_{name}.tif")
                if s3.size(u) is None:
                    continue
                part = _warp(u, bbox, w, h)
                fill = np.isnan(z) & ~np.isnan(part)
                if fill.any():
                    z[fill] = part[fill]
                    used["USGS 1/3 arc-second " + name] = int(fill.sum())
    meta = wesm()
    info = []
    for project, n in used.items():
        ends = [m["collect_end"] for m in meta.values() if project in (m["workunit"], m["project"]) and m["collect_end"]]
        kind = "1/3 arc-second DEM" if "1/3" in project else ("point cloud, ground returns gridded at 1 m" if project.endswith("(point cloud)") else "1 m DEM")
        ends = ends or [m["collect_end"] for m in [wesm_row(project.replace(" (point cloud)", ""), meta)] if m.get("collect_end")]
        info.append({"source": project, "credit": f"USGS 3DEP, {kind} ({project.replace(' (point cloud)', '')})",
                     "share": round(n / z.size, 3), "collect_end": max(ends) if ends else None})
    return z, info


if __name__ == "__main__":
    lon, lat = float(sys.argv[1]), float(sys.argv[2])
    wm, hm = (float(sys.argv[3]), float(sys.argv[4])) if len(sys.argv) > 4 else (2000.0, 2000.0)
    print("3DEP LiDAR work units containing the point:")
    for p in lidar_projects(lon, lat):
        print(f"  {p['workunit']:<34} {p['collect_start']} .. {p['collect_end']}  {p['ql']}  dem {p['dem_gsd_m']} m")
    for t, srcs in tile_sources(aw.site_bbox(lon, lat, wm, hm), lon, lat):
        print("tile", t, "->", [s[0] for s in srcs] or "no 1 m tile")
