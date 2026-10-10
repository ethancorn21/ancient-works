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


def affine_to_ground(uv, u0, v0, M, t):
    """Plate px -> ground metres with a general 2x2 matrix M and shift t (v axis flipped, centred on u0, v0)."""
    d = np.stack([uv[:, 0] - u0, -(uv[:, 1] - v0)], 1)
    return d @ np.asarray(M).T + np.asarray(t)


def sim_matrix(s, rot):
    c, sn = math.cos(rot), math.sin(rot)
    return np.array([[s * c, -s * sn], [s * sn, s * c]])


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
    # steep ground (hill rims) needs a tighter relief filter, or the slope swamps a 1 m wall
    lrm = aw.local_relief(z, px_m, radius_m=plate.get("lrm_radius_m", 24.0))
    clip = plate.get("clip_m", 1.0)
    lrm = np.clip(lrm, -clip, clip)  # quarry pits and banks would dominate the score otherwise
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
    if plate.get("control"):
        # control pairs [u, v, col, row]: plate crop px -> relief image px; solve z = a*w + b (complex least squares)
        c = np.array(plate["control"], float)
        wv = (c[:, 0] - u0) - 1j * (c[:, 1] - v0)
        zv = (c[:, 2] * px_m - site["width_m"] / 2) + 1j * (site["height_m"] / 2 - c[:, 3] * px_m)
        A = np.stack([wv, np.ones_like(wv)], 1)
        (a, b), *_ = np.linalg.lstsq(A, zv, rcond=None)
        s0, rot0, tx0, ty0 = abs(a), float(np.angle(a)), b.real, b.imag
        resid = np.abs(A @ np.array([a, b]) - zv)
        plate["_resid"] = np.round(resid, 1).tolist()
        print("  control seed: m/px %.3f rot %.1f shift %.0f %.0f, residuals m %s" % (
            s0, math.degrees(rot0), tx0, ty0, np.round(resid, 1).tolist()))

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
    if plate.get("model") == "control":
        # too little wall survives to search on (towns): trust the hand-picked control points
        plate["_skip_search"] = True
    # Plates are drawn north-up from compass surveys, so keep rotation near the drawing's own (+-rot_max).
    # Free rotation lets the walls snap onto section-line roads and field edges instead.
    rot_max = math.radians(plate.get("rot_max_deg", 3.0))
    span = dict(s=0.08 * s0, rot=rot_max, t=plate.get("search_m", 120.0))
    for _ in range(0 if plate.pop("_skip_search", False) else 5):  # coarse-to-fine grid search around the current best
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
    M, t = sim_matrix(s, rot), np.array([tx, ty])
    M_global, t_global = M.copy(), t.copy()

    def score_affine(M, t, P, N):
        en = affine_to_ground(P, u0, v0, M, t)
        n = np.stack([N[:, 0], -N[:, 1]], 1) @ np.linalg.inv(M)  # normals transform by M^-T
        n /= np.linalg.norm(n, axis=1, keepdims=True)
        on, a, b = relief_at(en), relief_at(en + n * side_m), relief_at(en - n * side_m)
        contrast = on - np.maximum(a, b)
        good = np.isfinite(contrast)
        return float(np.median(contrast[good])) if good.mean() >= 0.5 else -9

    warp_ctrl = None
    if plate.get("model") == "warp":
        # Rubber-sheet: fit each feature with its own similarity transform (they are surveyed well
        # individually, but distances and bearings between them drift), then warp the plate image
        # through all of them with a thin-plate spline.
        fs = plate.get("feature_search_m", 120.0)
        src_pts, dst_pts, feats = [], [], []
        for fi, line in enumerate(plate["walls"]):
            P, N = sample_walls([line], normals=True)
            cen = np.array([P[:, 0].mean() - u0, -(P[:, 1].mean() - v0)])
            # 1) translation only, at the global scale/rotation, fine grid (walls are ~10 m wide)
            bd, bsc = np.zeros(2), score_affine(M, t, P, N)
            span, n = fs, int(2 * fs / 6) + 1
            for _ in range(3):
                c0 = bd.copy()
                for dx in np.linspace(-span, span, n):
                    for dy in np.linspace(-span, span, n):
                        v = score_affine(M, t + c0 + [dx, dy], P, N)
                        if v > bsc:
                            bsc, bd = v, c0 + [dx, dy]
                span, n = 2 * span / (n - 1), 9
            # 2) scale and rotation about the feature's own centre, with small shifts
            fm_s, fm_r, fm_d = 1.0, 0.0, bd
            gcen = M @ cen + t
            for sspan, rspan, dspan in [(0.12, math.radians(5), 12.0), (0.04, math.radians(1.5), 4.0), (0.012, math.radians(0.5), 1.5)]:
                b0 = (fm_s, fm_r, fm_d.copy())
                for ks in np.linspace(b0[0] * (1 - sspan), b0[0] * (1 + sspan), 7):
                    for kr in np.linspace(b0[1] - rspan, b0[1] + rspan, 7):
                        Mi = sim_matrix(ks, kr) @ M
                        for dx in np.linspace(-dspan, dspan, 5):
                            for dy in np.linspace(-dspan, dspan, 5):
                                d = b0[2] + [dx, dy]
                                ti = gcen + d - Mi @ cen
                                v = score_affine(Mi, ti, P, N)
                                if v > bsc:
                                    bsc, fm_s, fm_r, fm_d = v, ks, kr, d
            Mi = sim_matrix(fm_s, fm_r) @ M
            ti = gcen + fm_d - Mi @ cen
            ok = bsc > plate.get("feature_min_m", 0.05)
            feats.append({"moved_m": round(float(np.hypot(*fm_d)), 1), "scale": round(fm_s, 3),
                          "rot_deg": round(math.degrees(fm_r), 2), "contrast_m": round(bsc, 3), "used": bool(ok)})
            print("  feature %d: moved %.0f m, scale %.3f, rot %+.1f deg, contrast %.3f m%s" % (
                fi, np.hypot(*fm_d), fm_s, math.degrees(fm_r), bsc, "" if ok else "  (not found, ignored)"))
            if ok:
                idx = np.linspace(0, len(P) - 1, min(40, len(P))).astype(int)
                src_pts.append(P[idx])
                dst_pts.append(affine_to_ground(P[idx], u0, v0, Mi, ti))
        if src_pts:
            warp_ctrl = (np.concatenate(src_pts), np.concatenate(dst_pts))
            plate["features"] = feats
            sc = float(np.median([f["contrast_m"] for f in feats if f["used"]]))

    if plate.get("model") == "features" and len(plate["walls"]) >= 2:
        # Long plates drift: each feature is surveyed well on its own, but bearings between distant
        # features can be off by several degrees. Locate every feature separately, then solve one
        # affine (3+ features) or similarity (2) transform through the located centres.
        src, dst, fs = [], [], plate.get("feature_search_m", 60.0)
        for line in plate["walls"]:
            P, N = sample_walls([line], normals=True)
            bd, bsc = np.zeros(2), score_affine(M, t, P, N)
            # walls are ~10 m wide, so the first pass must step finer than that or it jumps over them
            span, n = fs, int(2 * fs / 6) + 1
            for _ in range(3):
                c0 = bd.copy()
                for dx in np.linspace(-span, span, n):
                    for dy in np.linspace(-span, span, n):
                        v = score_affine(M, t + c0 + [dx, dy], P, N)
                        if v > bsc:
                            bsc, bd = v, c0 + [dx, dy]
                span, n = 2 * span / (n - 1), 9
            cen = np.array([P[:, 0].mean() - u0, -(P[:, 1].mean() - v0)])
            src.append(cen)
            dst.append(M @ cen + t + bd)
            print("  feature moved %.0f m, contrast %.3f m" % (np.hypot(*bd), bsc))
        src, dst = np.array(src), np.array(dst)
        if len(src) >= 3:
            A = np.hstack([src, np.ones((len(src), 1))])
            sol, *_ = np.linalg.lstsq(A, dst, rcond=None)
            M, t = sol[:2].T, sol[2]
        else:
            wv, zv = src[:, 0] + 1j * src[:, 1], dst[:, 0] + 1j * dst[:, 1]
            a = (zv[1] - zv[0]) / (wv[1] - wv[0])
            b = zv[0] - a * wv[0]
            M, t = sim_matrix(abs(a), float(np.angle(a))), np.array([b.real, b.imag])
        sc = score_affine(M, t, pts, nrm)
        print("  per-feature transform: contrast %.3f m" % sc)
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
        e, n = affine_to_ground(np.array([[u, v]], float), u0, v0, M, t)[0]
        corners.append(list(aw.to_lonlat(cx + e * k, cy + n * k)))
    plate["corners"] = corners
    plate.pop("warp", None)
    if warp_ctrl is not None:
        # anchors: the plate's frame follows the global fit, so the sheet stays sane away from features
        fr = np.array([[x, y] for x in np.linspace(0, W, 5) for y in np.linspace(0, H, 5)
                       if x in (0, W) or y in (0, H)], float)
        src = np.concatenate([warp_ctrl[0], fr])
        dst = np.concatenate([warp_ctrl[1], affine_to_ground(fr, u0, v0, M_global, t_global)])
        plate["warp"] = {"src_px": np.round(src, 1).tolist(), "dst_m": np.round(dst, 2).tolist()}
    plate["fit"] = {"m_per_px": round(float(math.sqrt(abs(np.linalg.det(M)))), 4),
                    "rot_deg": round(math.degrees(math.atan2(M[1, 0], M[0, 0])), 2),
                    "affine": [round(float(v), 5) for v in (*M.ravel(), *t)], "u0v0": [round(u0, 2), round(v0, 2)],
                    "ridge_contrast_m": round(sc, 3), "model": plate.get("model", "similarity"),
                    "control_resid_m": plate.pop("_resid", None),
                    "null_mean_m": round(float(null.mean()), 3), "null_p99_m": round(float(np.percentile(null, 99)), 3)}
    print("fit", plate["fit"])
    json.dump(site, open(path, "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
