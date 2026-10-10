"""Point-cloud LiDAR from the open-lidar-data mirror (registry.opendata.aws/open-lidar-data): national airborne surveys
as COPC tiles on S3 for England, the Netherlands, Denmark, France, Switzerland, Spain, Poland, the Nordics and more,
gridded to a bare-earth DEM on the site's Mercator grid.

Each survey folder (data/<CC>/<agency>/<survey>/) holds copc/<tile>.copc.laz and shp/files_bbox_<survey>.shp, an index with
every tile's extent, CRS and point density. The best survey for a box is the one covering most of it, then the densest, then
the newest. Only the octree nodes inside the box are fetched (HTTP range requests, via laspy), thinned to what the grid
resolution needs. Ground returns (class 2) are averaged per cell; holes are filled by normalised convolution and cells
farther than FILL_M from any ground return stay empty.

usage: python3 pipeline/lidar_pc.py <lon> <lat> [width_m height_m]     the surveys that cover the box, best first
"""
import json
import math
import os
import sys

import numpy as np
import pyproj
import rasterio
import shapefile
from rasterio.enums import Resampling
from rasterio.transform import Affine, from_bounds
from rasterio.warp import reproject
from scipy.ndimage import gaussian_filter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aw  # noqa: E402
import s3  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw", "lidar_pc")
BUCKET, REGION = "open-lidar-data", "eu-central-1"
FILL_M = 6.0
# country folders on the mirror -> rough lon/lat box, so only that country's tile indexes are fetched
COUNTRY = {"UK": (-8.7, 49.8, 1.9, 60.9), "IE": (-10.7, 51.3, -5.3, 55.5), "NL": (3.2, 50.7, 7.3, 53.6), "BE": (2.5, 49.4, 6.5, 51.6),
           "LU": (5.7, 49.4, 6.6, 50.2), "FR": (-5.3, 41.3, 9.7, 51.2), "DE": (5.8, 47.2, 15.1, 55.1), "DK": (7.9, 54.5, 15.3, 57.8),
           "SE": (10.9, 55.3, 24.2, 69.1), "FI": (19.0, 59.7, 31.7, 70.2), "EE": (21.7, 57.5, 28.3, 59.8), "LV": (20.9, 55.6, 28.3, 58.1),
           "LT": (20.9, 53.8, 26.9, 56.5), "PL": (14.0, 49.0, 24.2, 54.9), "SI": (13.3, 45.4, 16.7, 46.9), "CH": (5.9, 45.7, 10.6, 47.9),
           "ES": (-9.5, 35.9, 4.4, 43.9)}


AGENCY = {"DEFRA": "Environment Agency (England)", "NYU_EDU": "Dublin City Council survey, NYU archive", "IGN": "IGN France", "AHN": "AHN (Rijkswaterstaat, Kadaster)",
          "SDFI": "Danish Agency for Data Supply and Infrastructure", "GeoSN": "GeoSN, Free State of Saxony", "CNIG": "CNIG / IGN Spain",
          "Swiss_federal_authorities": "swisstopo", "EODaS": "Wallonia (EODaS)", "SPW": "Service public de Wallonie", "GUGiK": "GUGiK, Poland",
          "LANTMATERIET": "Lantmäteriet, Sweden", "NLS": "National Land Survey of Finland", "Maa_amet": "Estonian Land Board", "GeoRiga": "GeoRiga",
          "LGIA": "LGIA, Latvia", "NZT": "NZT, Lithuania", "Gouvernement_LUX": "Luxembourg government", "GURS": "GURS, Slovenia"}


def countries_at(lon, lat):
    return [c for c, (a, b, c2, d) in COUNTRY.items() if a <= lon <= c2 and b <= lat <= d]


def surveys(cc):
    """[(prefix, name)] of every survey folder of a country (data/<CC>/<agency>/<survey>/), cached."""
    path = os.path.join(RAW, f"surveys_{cc}.json")
    if not os.path.exists(path):
        os.makedirs(RAW, exist_ok=True)
        out = []
        for agency in s3.ls(BUCKET, f"data/{cc}/", region=REGION)[0]:
            for sv in s3.ls(BUCKET, agency, region=REGION)[0]:
                out.append(sv)
        json.dump(out, open(path, "w"))
    return json.load(open(path))


def tile_index(prefix):
    """Tiles of a survey: [{fname, epsg, bbox (native CRS), density, points}], from its shapefile index (cached as JSON)."""
    name = prefix.rstrip("/").split("/")[-1]
    path = os.path.join(RAW, f"index_{prefix.strip('/').replace('/', '_')}.json")
    if not os.path.exists(path):
        keys = [k for k, _, _ in s3.ls(BUCKET, prefix + "shp/", delim="", region=REGION)[1]]
        base = next((k[:-4] for k in keys if k.endswith(".shp")), None)
        if base is None:
            out = []
        else:
            d = os.path.join(RAW, "shp", name)
            for ext in ("shp", "shx", "dbf"):
                s3.get(s3.url(BUCKET, f"{base}.{ext}", REGION), os.path.join(d, f"i.{ext}"))
            r = shapefile.Reader(os.path.join(d, "i"))
            fields = [f[0] for f in r.fields[1:]]
            out = []
            for sr in r.iterShapeRecords():
                rec = dict(zip(fields, sr.record))
                out.append({"fname": rec.get("fname"), "epsg": int(rec.get("epsg") or 0), "bbox": [round(v, 2) for v in sr.shape.bbox],
                            "density": float(rec.get("density") or 0), "points": int(rec.get("points") or 0)})
        os.makedirs(RAW, exist_ok=True)
        json.dump(out, open(path, "w"))
    return json.load(open(path))


def native_box(bbox, epsg):
    """Mercator bbox -> (x0, y0, x1, y1) envelope in another CRS (edges densified)."""
    t = pyproj.Transformer.from_crs(3857, epsg, always_xy=True)
    xs = np.concatenate([np.linspace(bbox[0], bbox[2], 9), np.full(9, bbox[2]), np.linspace(bbox[2], bbox[0], 9), np.full(9, bbox[0])])
    ys = np.concatenate([np.full(9, bbox[1]), np.linspace(bbox[1], bbox[3], 9), np.full(9, bbox[3]), np.linspace(bbox[3], bbox[1], 9)])
    X, Y = t.transform(xs, ys)
    return min(X), min(Y), max(X), max(Y)


def candidates(lon, lat, width_m, height_m):
    """Surveys with tiles on the box, best first: [{survey, prefix, epsg, tiles, coverage, density, year}]."""
    bbox = aw.site_bbox(lon, lat, width_m, height_m)
    out = []
    for cc in countries_at(lon, lat):
        for prefix in surveys(cc):
            idx = tile_index(prefix)
            by_epsg = {}
            for t in idx:
                by_epsg.setdefault(t["epsg"], []).append(t)
            for epsg, tiles in by_epsg.items():
                if not epsg:
                    continue
                x0, y0, x1, y1 = native_box(bbox, epsg)
                hit = [t for t in tiles if t["bbox"][0] < x1 and t["bbox"][2] > x0 and t["bbox"][1] < y1 and t["bbox"][3] > y0]
                if not hit:
                    continue
                n = 40  # coverage of the box by the union of tile extents, on a coarse grid
                gx, gy = np.linspace(x0, x1, n), np.linspace(y0, y1, n)
                cov = np.zeros((n, n), bool)
                for t in hit:
                    cov |= ((gx >= t["bbox"][0]) & (gx <= t["bbox"][2]))[None, :] & ((gy >= t["bbox"][1]) & (gy <= t["bbox"][3]))[:, None]
                dens = [t["density"] for t in hit if t["density"]]
                name = prefix.rstrip("/").split("/")[-1]
                yrs = [int(y) for y in __import__("re").findall(r"(?<!\d)(20\d\d|19\d\d)(?!\d)", name + " " + " ".join(t["fname"] or "" for t in hit[:3]))]
                out.append({"survey": f"{cc}/{name}", "prefix": prefix, "epsg": epsg, "tiles": hit, "coverage": round(float(cov.mean()), 3),
                            "density": round(float(np.median(dens)), 2) if dens else 0.0, "year": max(yrs) if yrs else None})
    out.sort(key=lambda c: (c["coverage"] >= 0.9, c["density"] >= 1.0, c["coverage"] >= 0.99, c["density"], c["year"] or 0), reverse=True)
    return out


def grid_ground(cand, bbox, px, log=print):
    """Ground DEM of the survey on a native-CRS grid covering the Mercator bbox: (array, affine, epsg)."""
    import laspy
    epsg = cand["epsg"]
    x0, y0, x1, y1 = native_box(bbox, epsg)
    x0, y0 = math.floor(x0 - 20), math.floor(y0 - 20)
    w, h = int(math.ceil((x1 + 20 - x0) / px)), int(math.ceil((y1 + 20 - y0) / px))
    sums, cnts = np.zeros(w * h), np.zeros(w * h)
    top = y0 + h * px
    for t in cand["tiles"]:
        bx0, by0, bx1, by1 = max(t["bbox"][0], x0), max(t["bbox"][1], y0), min(t["bbox"][2], x0 + w * px), min(t["bbox"][3], top)
        if bx0 >= bx1 or by0 >= by1:
            continue
        url = s3.url(BUCKET, cand["prefix"] + "copc/" + t["fname"], REGION)
        with laspy.CopcReader.open(url) as rd:
            step = 1000.0
            for sx in np.arange(bx0, bx1, step):
                for sy in np.arange(by0, by1, step):
                    b = laspy.copc.Bounds(mins=np.array([sx, sy]), maxs=np.array([min(sx + step, bx1), min(sy + step, by1)]))
                    p = rd.query(bounds=b, resolution=max(0.5, px * 0.7))  # thinned to what the grid needs: ~2 points/m2 for a 1 m cell
                    if len(p) == 0:
                        continue
                    x, y, z, c = np.asarray(p.x), np.asarray(p.y), np.asarray(p.z), np.asarray(p.classification)
                    g = c == 2
                    if not g.any():  # unclassified survey: last returns, lowest per cell is the best guess at ground
                        g = np.asarray(p.return_number) == np.asarray(p.number_of_returns)
                    x, y, z = x[g], y[g], z[g]
                    ix, iy = ((x - x0) / px).astype(np.int64), ((top - y) / px).astype(np.int64)
                    ok = (ix >= 0) & (ix < w) & (iy >= 0) & (iy < h)
                    flat = iy[ok] * w + ix[ok]
                    sums += np.bincount(flat, weights=z[ok], minlength=w * h)
                    cnts += np.bincount(flat, minlength=w * h)
        log(f"    {t['fname']}: {int(cnts.sum())} ground points so far")
    sums, cnts = sums.reshape(h, w), cnts.reshape(h, w)
    z = np.where(cnts > 0, sums / np.maximum(cnts, 1), np.nan)
    have = (cnts > 0).astype(float)
    grid_ground.observed = float(have.mean())  # share of cells with a real ground return, before any filling: the quality of the relief
    filled = z.copy()
    for sigma in (1.5 / 1.0, 4.0, 12.0):  # in cells
        s = sigma * (1.0 / px) if px < 1 else sigma
        num, den = gaussian_filter(np.where(have > 0, z, 0.0), s), gaussian_filter(have, s)
        fill = np.isnan(filled) & (den > 1e-3)
        filled[fill] = (num / np.maximum(den, 1e-9))[fill]
    reach = gaussian_filter(have, max(1.0, FILL_M / px / 2)) > 1e-3  # keep cells only where ground returns exist within reach
    filled[~reach] = np.nan
    return filled, Affine(px, 0, x0, 0, -px, top), epsg


def read_dem(bbox, w, h, lon=None, lat=None, log=print):
    """Ground DEM (metres) for a Mercator bbox at w x h pixels, same grid and contract as aw.fetch_dem. Returns (z, info)."""
    if lon is None:
        lon, lat = aw.to_lonlat((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)
    width_m = (bbox[2] - bbox[0]) * math.cos(math.radians(lat))
    height_m = (bbox[3] - bbox[1]) * math.cos(math.radians(lat))
    cands = candidates(lon, lat, width_m, height_m)
    if not cands or cands[0]["coverage"] < 0.5:
        raise aw.NoLidar("no open point-cloud LiDAR covers this box")
    c = cands[0]
    px = width_m / w
    log(f"  LiDAR survey {c['survey']} ({c['year']}), {len(c['tiles'])} tiles, {c['density']} pts/m2, {c['coverage']:.0%} of the box")
    arr, tf, epsg = grid_ground(c, bbox, px, log)
    z = np.full((h, w), np.nan, np.float32)
    reproject(arr.astype(np.float32), z, src_transform=tf, src_crs=f"EPSG:{epsg}", dst_transform=from_bounds(*bbox, w, h),
              dst_crs="EPSG:3857", resampling=Resampling.bilinear, src_nodata=np.nan, dst_nodata=np.nan)
    agency = AGENCY.get(c["prefix"].split("/")[2], c["prefix"].split("/")[2])
    info = [{"source": c["survey"], "credit": f"{agency}, {c['year'] or 'survey'} ({c['density']} points/m2)", "share": round(float(np.isfinite(z).mean()), 3),
             "collect_end": str(c["year"]) if c["year"] else None, "density_pts_m2": c["density"], "ground_cells": round(grid_ground.observed, 3)}]
    return z.astype(np.float64), info


if __name__ == "__main__":
    lon, lat = float(sys.argv[1]), float(sys.argv[2])
    wm, hm = (float(sys.argv[3]), float(sys.argv[4])) if len(sys.argv) > 4 else (2000.0, 2000.0)
    for c in candidates(lon, lat, wm, hm):
        print(f"{c['survey']:<44} year {c['year']}  {len(c['tiles']):>3} tiles  covers {c['coverage']:.0%}  median {c['density']} pts/m2  EPSG:{c['epsg']}")
