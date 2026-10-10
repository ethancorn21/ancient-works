"""USGS 3DEP point clouds (Entwine Point Tiles on s3://usgs-lidar-public/<work unit>/): ground returns gridded onto a site's Mercator box.

usgs.read_dem uses this where the 1 m DEM tiles have gaps (a tile that stops short of the box, a project with no 1 m DEM published
yet), before it falls back to the 10 m 1/3 arc-second DEM. The point clouds are the source the 1 m DEMs are made from, so the
bare-earth surface is the same; the grid here is a plain per-cell mean of the ground returns (class 2) with the holes filled by
normalised convolution, like lidar_pc.py does for the European COPC tiles.

An EPT dataset is a cube split into an octree (ept.json, ept-hierarchy/<D-X-Y-Z>.json: how many points each node holds, -1 = the
subtree has its own hierarchy file, ept-data/<D-X-Y-Z>.laz: the node's points). Points are already in EPSG:3857, the same plane as
the site grids; Z stays in the survey's own units (metres for NAVD88 5703, US survey feet for 6360; WESM's vert_crs says which).
A node of depth D is thinned to a span x span grid, so spacing = cube side / 2^D / span; depth 11-12 is about 1 m on the ground.

usage: python3 pipeline/ept.py <lon> <lat> [width_m]     which work units hold the point, their depth for 1 m spacing, and the node count
"""
import concurrent.futures as cf
import io
import json
import math
import os
import sys

import numpy as np
from scipy.ndimage import gaussian_filter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aw  # noqa: E402
import s3  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw", "ept")
BUCKET = "usgs-lidar-public"
FILL_M = 6.0
# WESM vert_crs -> metres per Z unit (EPSG 5703 NAVD88 m, 6360 NAVD88 ftUS, 8228 NAVD88 ft); other codes are not trusted
UNITS = {"5703": 1.0, "6360": 1200.0 / 3937.0, "8228": 0.3048}
MAX_NODES = 1500


def _json(project, rel):
    path = os.path.join(RAW, project, rel)
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(s3.get(s3.url(BUCKET, f"{project}/{rel}")))
    return json.load(open(path))


def meta(project):
    return _json(project, "ept.json")


def select(project, bbox, spacing_m=1.0, ept=None):
    """Keys of the nodes that hold points inside the Mercator bbox, from the root down to the depth whose grid spacing is `spacing_m`
    (ground metres at the box centre). Returns (keys, depth)."""
    ept = ept or meta(project)
    b, span = ept["bounds"], ept["span"]
    side0 = b[3] - b[0]
    lat = aw.to_lonlat((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)[1]
    want = spacing_m / math.cos(math.radians(lat))  # spacing in Mercator metres
    depth = max(0, math.ceil(math.log2(side0 / span / want)))
    hier = {}
    loaded = set()

    def load(key):
        if key in loaded:
            return
        loaded.add(key)
        hier.update(_json(project, f"ept-hierarchy/{key}.json"))

    load("0-0-0-0")
    keys = []

    def visit(d, x, y, z):
        side = side0 / 2 ** d
        x0, y0 = b[0] + x * side, b[1] + y * side
        if x0 >= bbox[2] or x0 + side <= bbox[0] or y0 >= bbox[3] or y0 + side <= bbox[1]:
            return
        key = f"{d}-{x}-{y}-{z}"
        n = hier.get(key)
        if n == -1:
            load(key)
            n = hier.get(key)
        if not n or n < 0:
            return
        keys.append(key)
        if d < depth:
            for dx in (0, 1):
                for dy in (0, 1):
                    for dz in (0, 1):
                        visit(d + 1, 2 * x + dx, 2 * y + dy, 2 * z + dz)

    visit(0, 0, 0, 0)
    return keys, depth


def _read_node(project, key, scale, tries=4):
    import laspy
    for i in range(tries):  # a body cut short decodes as "failed to fill whole buffer": fetch it again
        try:
            body = s3.get(s3.url(BUCKET, f"{project}/ept-data/{key}.laz"))
            las = laspy.read(io.BytesIO(body))
            break
        except Exception:
            if i == tries - 1:
                raise
    c = np.asarray(las.classification)
    g = c == 2
    return np.asarray(las.x)[g], np.asarray(las.y)[g], np.asarray(las.z)[g] * scale, int(len(c)), int(g.sum())


def ground_grid(project, bbox, w, h, region=None, spacing_m=1.0, log=print):
    """Ground DEM of one work unit on the w x h Mercator grid of `bbox` (metres, NaN where no ground return is within reach).
    region: optional (x0, y0, x1, y1) Mercator rectangle to read instead of the whole box. Returns (z, observed share of cells with a return)."""
    from usgs import wesm_row
    row = wesm_row(project)
    scale = UNITS.get(str(row.get("vert_crs")))
    if scale is None:
        raise RuntimeError(f"{project}: vertical CRS {row.get('vert_crs')!r} is not one this code trusts")
    rb = region or bbox
    ept = meta(project)
    keys, depth = select(project, rb, spacing_m, ept)
    if len(keys) > MAX_NODES:
        raise RuntimeError(f"{project}: {len(keys)} nodes for this region (limit {MAX_NODES})")
    log(f"  3DEP point cloud {project}: {len(keys)} nodes to depth {depth}")
    sums, cnts = np.zeros(w * h), np.zeros(w * h)
    sx, sy = w / (bbox[2] - bbox[0]), h / (bbox[3] - bbox[1])
    total = ground = 0
    with cf.ThreadPoolExecutor(12) as ex:
        for x, y, z, n, g in ex.map(lambda k: _read_node(project, k, scale), keys):
            total, ground = total + n, ground + g
            ix, iy = ((x - bbox[0]) * sx).astype(np.int64), ((bbox[3] - y) * sy).astype(np.int64)
            ok = (ix >= 0) & (ix < w) & (iy >= 0) & (iy < h)
            flat = iy[ok] * w + ix[ok]
            sums += np.bincount(flat, weights=z[ok], minlength=w * h)
            cnts += np.bincount(flat, minlength=w * h)
    log(f"    {total} points read, {ground} ground")
    sums, cnts = sums.reshape(h, w), cnts.reshape(h, w)
    z = np.where(cnts > 0, sums / np.maximum(cnts, 1), np.nan)
    have = (cnts > 0).astype(float)
    observed = float(have.mean())
    filled = z.copy()
    for sigma in (1.5, 4.0, 12.0):  # cells
        num, den = gaussian_filter(np.where(have > 0, z, 0.0), sigma), gaussian_filter(have, sigma)
        fill = np.isnan(filled) & (den > 1e-3)
        filled[fill] = (num / np.maximum(den, 1e-9))[fill]
    px = (bbox[2] - bbox[0]) / w
    reach = gaussian_filter(have, max(1.0, FILL_M / px / 2)) > 1e-3
    filled[~reach] = np.nan
    return filled, observed


if __name__ == "__main__":
    import usgs
    lon, lat = float(sys.argv[1]), float(sys.argv[2])
    wm = float(sys.argv[3]) if len(sys.argv) > 3 else 1000.0
    bbox = aw.site_bbox(lon, lat, wm, wm)
    for p in usgs.lidar_projects(lon, lat):
        try:
            keys, depth = select(p["workunit"], bbox)
            print(f"{p['workunit']:<34} {p['collect_end']}  {p['ql']}  vert {usgs.wesm_row(p['workunit']).get('vert_crs')}  depth {depth}  {len(keys)} nodes")
        except Exception as e:
            print(p["workunit"], "ERR", type(e).__name__, str(e)[:100])
