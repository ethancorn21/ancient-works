"""Bare-earth model of one EBA LiDAR strip (Brazilian Amazon), in the strip's own frame.

usage: amazon_dtm.py <strip.laz> [out_dir]    -> <out_dir>/<name>.npz  (z float32, 2 m cells; frame + CRS to map back)

The strips are 12.5 km x ~0.5 km and run at any angle, so the points are rotated onto the strip's long axis
first (a north-up raster of a diagonal strip would be ~95% empty). EBA's class 2 is not ground: every class-2 point is
simply a last return, and under closed forest most last returns stop in the canopy (2026-10-10: relief noise
+-15 m in forest on strip 0414). Ground is therefore found here: the lowest return per 2 m cell, isolated low
outliers dropped, then a progressive morphological filter (openings of growing window, each cell kept if it is
within dh + slope * window of the opened surface; a simplified SMRF). An opening removes raised clutter narrower than
the window but keeps ditches exactly, which is what the enclosure detector looks for. Kept cells are interpolated
(nearest, then smoothed where filled).
Frame: u along the strip, v across it, both in metres of the strip's UTM CRS; cell (row i, col j) is at
u = u0 + (j + 0.5), v = v0 + (i + 0.5); x = cx + u*cos(a) - v*sin(a), y = cy + u*sin(a) + v*cos(a).
"""
import json
import os
import sys

import laspy
import numpy as np
from scipy import ndimage

PX = 2.0
WINDOWS = [3, 5, 9, 15, 25]  # opening sizes in cells (6-50 m)
# metres, and metres per metre of half-window. 2026-10-10 on strip 0414: 0.4 / 0.25 let understory through (9% of
# the swath >1 m above a 30 m opening, canopy blobs ranking as ring ditches); 0.25 / 0.06 leaves 2%, with the
# geoglyph's ditch unchanged and its bank shaved under 0.5 m.
DH, SLOPE = 0.25, 0.06


def ground_cells(zmin):
    """Boolean mask of cells whose lowest return is ground (progressive morphological filter)."""
    big = np.nanmax(zmin) + 100
    z = np.where(np.isfinite(zmin), zmin, big)
    # isolated low outliers (multipath, birds below ground): more than 2 m under the 2nd-lowest of the 8 neighbours
    fp = np.ones((3, 3), bool); fp[1, 1] = False
    second = ndimage.rank_filter(z, 1, footprint=fp)
    z = np.where(z < second - 2.0, big, z)
    ok = z < big
    surf = z.copy()
    for w in WINDOWS:
        op = ndimage.grey_opening(surf, size=(w, w))
        thr = DH + SLOPE * (w * PX / 2)
        ok &= (z - op) <= thr
        surf = np.where(ok, z, op)
    return ok


def build(path, out_dir):
    f = laspy.read(path)
    crs = f.header.parse_crs()
    x, y, z = np.asarray(f.x), np.asarray(f.y), np.asarray(f.z, np.float32)
    cl = np.asarray(f.classification)
    keep = cl != 7  # LAS class 7 = low noise, if a strip has it
    x, y, z = x[keep], y[keep], z[keep]
    cx, cy = float(x.mean()), float(y.mean())
    sub = np.stack([x[::50] - cx, y[::50] - cy])
    w, vecs = np.linalg.eigh(np.cov(sub))
    a = float(np.arctan2(vecs[1, -1], vecs[0, -1]))
    ca, sa = np.cos(a), np.sin(a)
    u = (x - cx) * ca + (y - cy) * sa
    v = -(x - cx) * sa + (y - cy) * ca
    u0, v0 = float(np.floor(u.min())), float(np.floor(v.min()))
    W, H = int(np.ceil((u.max() - u0) / PX)) + 1, int(np.ceil((v.max() - v0) / PX)) + 1
    k = ((v - v0) / PX).astype(np.int64) * W + ((u - u0) / PX).astype(np.int64)
    zmin = np.full(W * H, np.inf, np.float32)
    np.minimum.at(zmin, k, z)
    zmin = zmin.reshape(H, W)
    zmin[~np.isfinite(zmin)] = np.nan
    seen = np.isfinite(zmin)
    swath = ndimage.binary_closing(ndimage.binary_dilation(seen, iterations=3), iterations=10)
    have = ground_cells(zmin)
    idx = ndimage.distance_transform_edt(~have, return_distances=False, return_indices=True)
    zf = zmin[tuple(idx)]
    sm = ndimage.gaussian_filter(zf, 1.0)
    zf = np.where(have, zf, sm).astype(np.float32)
    zf[~swath] = np.nan
    name = os.path.splitext(os.path.basename(path))[0]
    os.makedirs(out_dir, exist_ok=True)
    meta = {"name": name, "crs": crs.to_string() if crs else None, "epsg": crs.to_epsg() if crs else None,
            "cx": cx, "cy": cy, "angle_rad": a, "u0": u0, "v0": v0, "px_m": PX, "shape": [H, W],
            "points": int(len(z)), "ground_cell_share": round(float(have.sum() / max(1, swath.sum())), 3)}
    np.savez_compressed(os.path.join(out_dir, name + ".npz"), z=zf, have=have, meta=json.dumps(meta))
    print(name, meta["shape"], "ground cells", meta["ground_cell_share"], flush=True)
    return os.path.join(out_dir, name + ".npz")


def load(npz):
    d = np.load(npz)
    return d["z"], d["have"], json.loads(str(d["meta"]))


def to_frame(meta, x, y):
    """UTM x, y -> (row, col) in the strip raster."""
    ca, sa = np.cos(meta["angle_rad"]), np.sin(meta["angle_rad"])
    u = (x - meta["cx"]) * ca + (y - meta["cy"]) * sa
    v = -(x - meta["cx"]) * sa + (y - meta["cy"]) * ca
    return (v - meta["v0"]) / meta["px_m"] - 0.5, (u - meta["u0"]) / meta["px_m"] - 0.5


def to_xy(meta, row, col):
    ca, sa = np.cos(meta["angle_rad"]), np.sin(meta["angle_rad"])
    u = meta["u0"] + (np.asarray(col) + 0.5) * meta["px_m"]
    v = meta["v0"] + (np.asarray(row) + 0.5) * meta["px_m"]
    return meta["cx"] + u * ca - v * sa, meta["cy"] + u * sa + v * ca


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(sys.argv[1]), "..", "dtm"))
