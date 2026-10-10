"""Fit a survey plate onto LiDAR relief.

Searches a similarity transform (rotation, scale, shift) that puts the plate's drawn walls on the highest
local relief. Walls are polylines in plate-image pixels; the plate is assumed to have north up.

usage: fit_plate.py <site.json>   (reads site["plate"]["walls"], writes site["plate"]["corners"] + fit stats)
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aw  # noqa: E402


def sample_walls(walls, step=2.0, normals=False):
    pts, nrm = [], []
    for line in walls:
        for (u0, v0), (u1, v1) in zip(line, line[1:]):
            L = math.hypot(u1 - u0, v1 - v0)
            n = max(2, int(L / step))
            t = np.linspace(0, 1, n)
            pts.append(np.stack([u0 + (u1 - u0) * t, v0 + (v1 - v0) * t], 1))
            nrm.append(np.tile([-(v1 - v0) / L, (u1 - u0) / L], (n, 1)))
    return (np.concatenate(pts), np.concatenate(nrm)) if normals else np.concatenate(pts)


def plate_to_ground(uv, u0, v0, s, rot, tx, ty):
    """Plate px -> ground metres (E, N) from relief image centre."""
    du, dv = uv[:, 0] - u0, -(uv[:, 1] - v0)
    c, sn = math.cos(rot), math.sin(rot)
    return np.stack([s * (c * du - sn * dv) + tx, s * (sn * du + c * dv) + ty], 1)


def main(path):
    site = json.load(open(path))
    plate = site["plate"]
    px_m = site.get("px_m", 1.0)
    bbox = aw.site_bbox(site["lon"], site["lat"], site["width_m"], site["height_m"])
    w, h = int(site["width_m"] / px_m), int(site["height_m"] / px_m)
    cache = os.path.join(os.path.dirname(path), "dem.npy")
    if os.path.exists(cache):
        z = np.load(cache)
    else:
        z = aw.fetch_dem(bbox, w, h)
        np.save(cache, z)
    z = aw.fill_nan(z)
    lrm = aw.local_relief(z, px_m)
    lrm = np.clip(lrm, -1.0, 1.0)  # quarry pits and banks would dominate the score otherwise
    mask_path = os.path.join(os.path.dirname(path), "modern_mask.npy")
    if os.path.exists(mask_path):
        mask = np.load(mask_path)
    else:
        mask = aw.modern_mask(bbox, w, h, px_m)
        np.save(mask_path, mask)
    lrm[mask] = np.nan  # raised roads and rail beds look exactly like walls; score only open ground
    lrm[aw.water_mask(z, px_m)] = np.nan  # flat water scores neutral and would swallow walls

    pts, nrm = sample_walls(plate["walls"], normals=True)
    u0, v0 = pts.mean(0)
    side_m = plate.get("side_m", 20.0)
    s0 = plate["m_per_px"]
    g = plate.get("guess", {})
    rot0 = math.radians(g.get("rot_deg", 0.0))
    tx0, ty0 = g.get("tx", 0.0), g.get("ty", 0.0)

    def relief_at(en):
        col = (en[:, 0] + site["width_m"] / 2) / px_m
        row = (site["height_m"] / 2 - en[:, 1]) / px_m
        ok = (col >= 0) & (col < w - 1) & (row >= 0) & (row < h - 1)
        vals = np.full(len(en), np.nan)
        vals[ok] = map_coordinates(lrm, [row[ok], col[ok]], order=0)
        return vals

    def score(s, rot, tx, ty):
        """Median ridge contrast: how far the wall line stands above the HIGHER of its two sides (side_m away).

        A plowed-down wall is a broad low ridge, so it beats both sides; a field edge, road shoulder or
        quarry bank is high on one side only and scores near zero or below.
        """
        en = plate_to_ground(pts, u0, v0, s, rot, tx, ty)
        c, sn = math.cos(rot), math.sin(rot)
        # plate normal (du, dv) -> ground direction, same rotation as the points (v axis flipped)
        ne = np.stack([c * nrm[:, 0] + sn * nrm[:, 1], sn * nrm[:, 0] - c * nrm[:, 1]], 1)
        on = relief_at(en)
        a = relief_at(en + ne * side_m)
        b = relief_at(en - ne * side_m)
        contrast = on - np.maximum(a, b)
        good = np.isfinite(contrast)
        if good.mean() < 0.5:
            return -9
        return float(np.median(contrast[good]))

    best = (score(s0, rot0, tx0, ty0), s0, rot0, tx0, ty0)
    # Plates are drawn north-up from compass surveys, so keep rotation near the drawing's own (+-rot_max).
    # Free rotation lets the walls snap onto section-line roads and field edges instead.
    rot_max = math.radians(plate.get("rot_max_deg", 3.0))
    span = dict(s=0.08 * s0, rot=rot_max, t=plate.get("search_m", 120.0))
    for _ in range(5):  # coarse-to-fine grid search around the current best
        _, sb, rb, xb, yb = best
        for s in np.linspace(sb - span["s"], sb + span["s"], 5):
            for rot in np.clip(np.linspace(rb - span["rot"], rb + span["rot"], 9), rot0 - rot_max, rot0 + rot_max):
                for tx in np.linspace(xb - span["t"], xb + span["t"], 13):
                    for ty in np.linspace(yb - span["t"], yb + span["t"], 13):
                        sc = score(s, rot, tx, ty)
                        if sc > best[0]:
                            best = (sc, s, rot, tx, ty)
        span = {k: v / 3 for k, v in span.items()}
        print("  best", round(best[0], 3), "m/px", round(best[1], 3), "rot", round(math.degrees(best[2]), 2),
              "shift", round(best[3], 1), round(best[4], 1))

    sc, s, rot, tx, ty = best
    # null check: how does a random placement of the same wall shape score?
    rng = np.random.default_rng(0)
    null = [score(s, rng.uniform(-math.pi, math.pi), rng.uniform(-site["width_m"] / 3, site["width_m"] / 3),
                  rng.uniform(-site["height_m"] / 3, site["height_m"] / 3)) for _ in range(300)]
    null = np.array([v for v in null if v > -9])
    im = Image.open(os.path.join(os.path.dirname(path), plate["image"]))
    W, H = im.size
    cx, cy = aw.to_merc(site["lon"], site["lat"])
    k = 1 / aw.ground_scale(site["lat"])
    corners = []
    for u, v in [(0, 0), (W, 0), (W, H), (0, H)]:
        e, n = plate_to_ground(np.array([[u, v]], float), u0, v0, s, rot, tx, ty)[0]
        corners.append(list(aw.to_lonlat(cx + e * k, cy + n * k)))
    plate["corners"] = corners
    plate["fit"] = {"m_per_px": round(s, 4), "rot_deg": round(math.degrees(rot), 2), "tx": round(tx, 1),
                    "ty": round(ty, 1), "ridge_contrast_m": round(sc, 3),
                    "null_mean_m": round(float(null.mean()), 3), "null_p99_m": round(float(np.percentile(null, 99)), 3)}
    print("fit", plate["fit"])
    json.dump(site, open(path, "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
