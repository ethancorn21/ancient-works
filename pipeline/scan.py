"""Scan an area of LiDAR for circular earthworks.

For every tile: DEM -> local relief -> direction-free ridge map (how far each point stands above the higher
of the two points 20 m away, in the best of 8 directions) with roads, buildings and water masked. Ring
templates of several radii are run over the ridge map; a candidate is a ring whose mean ridge height, and
the share of its length that is raised, stand far above the tile's background.

usage: scan.py <name> <lon0> <lat0> <lon1> <lat1> [px_m]
writes data/scan/<name>/{tiles/*.npz, candidates.json, ridge_preview.png}
"""
import json
import math
import os
import sys
import time

import numpy as np
from PIL import Image
from scipy.ndimage import maximum_filter
from scipy.signal import fftconvolve

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aw  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RADII = [30, 45, 60, 80, 105, 135, 170, 210, 260]  # metres
SIDE_M = 20.0
TILE_M, PAD_M = 4000.0, 560.0


def ridge_map(z, px_m):
    lrm = np.clip(aw.local_relief(aw.fill_nan(z), px_m), -1.5, 1.5)
    k = max(1, int(round(SIDE_M / px_m)))
    best = np.full(lrm.shape, -9.0)
    for dy, dx in [(0, 1), (1, 0), (1, 1), (1, -1), (1, 2), (2, 1), (1, -2), (2, -1)]:
        n = math.hypot(dx, dy)
        sy, sx = int(round(dy / n * k)), int(round(dx / n * k))
        a = np.roll(lrm, (sy, sx), (0, 1))
        b = np.roll(lrm, (-sy, -sx), (0, 1))
        best = np.maximum(best, lrm - np.maximum(a, b))
    return best


def ring(r_px, width_px):
    R = int(math.ceil(r_px + width_px))
    yy, xx = np.mgrid[-R:R + 1, -R:R + 1]
    d = np.hypot(yy, xx)
    return (np.abs(d - r_px) <= width_px / 2).astype(np.float32)


def scan_tile(z, valid, px_m):
    rid = ridge_map(z, px_m)
    rid = np.clip(rid, -0.5, 1.0)
    rid[~valid] = 0
    raised = ((rid > 0.08) & valid).astype(np.float32)
    v = valid.astype(np.float32)
    out = []
    for r in RADII:
        K = ring(r / px_m, max(2.0, 8.0 / px_m))
        n = K.sum()
        vs = fftconvolve(v, K, mode="same") / n                 # share of the ring on open ground
        s = fftconvolve(rid, K, mode="same") / np.maximum(vs * n, 1)  # mean ridge on the open part
        f = fftconvolve(raised, K, mode="same") / np.maximum(vs * n, 1)  # share of the ring that is raised
        out.append((r, s, f, vs))
    return rid, out


def main(name, lon0, lat0, lon1, lat1, px_m=2.0):
    d = os.path.join(ROOT, "data", "scan", name)
    os.makedirs(os.path.join(d, "tiles"), exist_ok=True)
    x0, y0 = aw.to_merc(lon0, lat0)
    x1, y1 = aw.to_merc(lon1, lat1)
    k = 1 / aw.ground_scale((lat0 + lat1) / 2)  # ground m -> mercator m
    tile, pad = TILE_M * k, PAD_M * k
    nx, ny = int(math.ceil((x1 - x0) / tile)), int(math.ceil((y1 - y0) / tile))
    print(f"{name}: {nx} x {ny} tiles of {TILE_M / 1000:.0f} km at {px_m} m/px")
    cands, previews = [], {}
    pw = int((TILE_M + 2 * PAD_M) / px_m)
    core = slice(int(PAD_M / px_m), int((PAD_M + TILE_M) / px_m))
    for ty in range(ny):
        for tx in range(nx):
            t0 = time.time()
            bx0, by1 = x0 + tx * tile - pad, y1 - ty * tile + pad
            bbox = (bx0, by1 - tile - 2 * pad, bx0 + tile + 2 * pad, by1)
            path = os.path.join(d, "tiles", f"{ty}_{tx}.npz")
            if os.path.exists(path):
                f = np.load(path)
                z, mask = f["z"], f["mask"]
            else:
                z = aw.fetch_dem(bbox, pw, pw).astype(np.float32)
                try:
                    mask = aw.modern_mask(bbox, pw, pw, px_m)
                except Exception as e:  # Overpass can fail; scan without the mask rather than stop
                    print("  no OSM mask:", e)
                    mask = np.zeros_like(z, bool)
                np.savez_compressed(path, z=z, mask=mask)
            if np.isnan(z).mean() > 0.5:
                print(f"  tile {ty},{tx}: no data")
                continue
            valid = ~mask & ~aw.water_mask(z, px_m) & np.isfinite(z)
            rid, maps = scan_tile(z, valid, px_m)
            previews[(ty, tx)] = rid[core, core]
            for r, s, f, vs in maps:
                sc, fc, vc = s[core, core], f[core, core], vs[core, core]
                ok = vc > 0.6
                if ok.sum() < 1000:
                    continue
                med = np.median(sc[ok])
                mad = np.median(np.abs(sc[ok] - med)) * 1.4826 + 1e-6
                zs = np.where(ok, (sc - med) / mad, -9)
                peak = (zs == maximum_filter(zs, size=max(3, int(r / px_m)))) & (zs > 5) & (sc > 0.06) & (fc > 0.4)
                for row, col in zip(*np.nonzero(peak)):
                    gx = bx0 + pad + (col + 0.5) * px_m * k
                    gy = by1 - pad - (row + 0.5) * px_m * k
                    lon, lat = aw.to_lonlat(gx, gy)
                    cands.append({"lon": round(lon, 6), "lat": round(lat, 6), "r_m": r, "z": round(float(zs[row, col]), 1),
                                  "ridge_m": round(float(sc[row, col]), 3), "raised": round(float(fc[row, col]), 2),
                                  "open": round(float(vc[row, col]), 2), "tile": [ty, tx]})
            print(f"  tile {ty},{tx} done in {time.time() - t0:.0f}s, {len(cands)} raw candidates so far")
    # one candidate per place: keep the strongest radius within the larger radius of any two
    cands.sort(key=lambda c: -c["z"])
    kept = []
    for c in cands:
        cx, cy = aw.to_merc(c["lon"], c["lat"])
        if all(math.hypot(cx - kx, cy - ky) / k > max(c["r_m"], kc["r_m"]) for kx, ky, kc in kept):
            kept.append((cx, cy, c))
    out = [c for _, _, c in kept]
    for i, c in enumerate(out):
        c["id"] = f"{name}-{i:04d}"
    aw.save_json(os.path.join(d, "candidates.json"), {"area": [lon0, lat0, lon1, lat1], "px_m": px_m,
                                                      "radii_m": RADII, "candidates": out})
    # preview mosaic of the ridge map at 4x reduction
    step = 4
    ct = int(TILE_M / px_m) // step
    mos = np.zeros((ny * ct, nx * ct), np.float32)
    for (ty, tx), r in previews.items():
        mos[ty * ct:(ty + 1) * ct, tx * ct:(tx + 1) * ct] = r[::step, ::step][:ct, :ct]
    Image.fromarray((np.clip(mos / 0.5, 0, 1) * 255).astype(np.uint8)).save(os.path.join(d, "ridge_preview.png"))
    print(f"{len(out)} candidates after merging; wrote {d}/candidates.json")


if __name__ == "__main__":
    a = sys.argv
    main(a[1], *map(float, a[2:6]), *(map(float, a[6:7])))
