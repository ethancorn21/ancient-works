"""Two-stage matcher fit: coarse hit on the whole ground, then windows CENTRED ON THE HIT and SIZED to the
plan's coarse scale (the recall lever named in docs/matchfit.md section 4, item 2).

fit/matchfit.py matches the plan against windows that are always centred on the site box. When the plan
covers a corner of the box, or is much smaller than the box, those windows miss it or hold it too small
for the matcher (it fails past a ~2-3x scale gap). Here every ground is matched whole first; the coarse
similarity (even one with only 3-7 inliers) says roughly where the plan lands and how big it is in ground
pixels; then windows of 1.3x, 1.8x and 2.5x the plan's coarse footprint, centred on the coarse centre, are
matched again. The accept rule is matchfit's, unchanged (>= MIN_INLIERS inliers, |rot| <= MAX_ROT_DEG).

Measured by fit/matchfit_heldout.py with MF_VARIANT=located (results in data/matchfit/heldout_located/).
Candidates carry "stage": "coarse" | "located" so the table can say which stage produced the accepted fit.
"""
import math
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import matchfit as mf  # noqa: E402

COARSE_WINDOWS = (1.0, 0.5)           # stage 1: whole ground, and the centred half (matchfit's best two)
LOCATED_FACTORS = (1.3, 1.8, 2.5)     # stage 2: window side = factor x plan footprint (ground px)
MAX_SIDE = 1024


def _match_window(plan, img, box, W, H, url):
    """Match the plan against img cropped to box=(x0,y0,x1,y1) (clipped to the image); returns
    (a, b_in_full_ground_px) or None."""
    x0, y0, x1, y1 = (max(0, box[0]), max(0, box[1]), min(W, box[2]), min(H, box[3]))
    if x1 - x0 < 32 or y1 - y0 < 32:
        return None
    win = img.crop((round(x0), round(y0), round(x1), round(y1)))
    a, b = mf.match(plan, win, url)
    if len(a) < 3:
        return None
    return a, b + [round(x0), round(y0)]


def _candidate(name, f, stage, a, b, W, H, corners, plan_box, fx, fy, tol):
    res = mf.ransac(a, b, tol)
    c = {"ground": name, "window": f, "stage": stage, "matches": int(len(a))}
    if res is None:
        c["inliers"] = 0
        return c, None
    m, s, t = res
    (lo0, la0), (lo1, _), (_, la1) = corners[0], corners[1], corners[2]
    X0, Y0 = mf._merc(lo0, la0)
    X1, Y1 = mf._merc(lo1, la1)
    A = a[m]
    Bm = s * (A[:, 0] + 1j * A[:, 1]) + t
    ll = [mf._unmerc(X0 + z.real / W * (X1 - X0), Y0 + z.imag / H * (Y1 - Y0)) for z in Bm]
    resid = np.abs(Bm - (b[m][:, 0] + 1j * b[m][:, 1])) * abs(X1 - X0) / W * math.cos(math.radians(la0))
    x0, y0 = plan_box[0], plan_box[1]
    pairs = [[x0 + A[i, 0] / fx, y0 + A[i, 1] / fy, ll[i][0], ll[i][1]] for i in range(len(A))]
    c.update({"inliers": int(m.sum()), "rot": round(math.degrees(np.angle(s)), 2),
              "resid_m": round(float(np.median(resid)), 1), "pairs": pairs})
    return c, (s, t)


def candidates(root, site, row, url=None):
    pic = mf.plan_image(root, row)
    if pic is None:
        return None
    plan, plan_box, fx, fy = pic
    pw, ph = plan.size
    out = []
    for name, path, corners in mf.grounds(root, site):
        img = Image.open(path)
        W, H = img.size
        tol = 0.01 * max(W, H)
        hits = []
        for f in COARSE_WINDOWS:
            cw, ch = W * f, H * f
            ox, oy = (W - cw) / 2, (H - ch) / 2
            t0 = time.time()
            try:
                r = _match_window(plan, img, (ox, oy, ox + cw, oy + ch), W, H, url)
            except Exception as e:
                out.append({"ground": name, "window": f, "stage": "coarse", "error": repr(e)})
                continue
            if r is None:
                out.append({"ground": name, "window": f, "stage": "coarse", "matches": 0, "inliers": 0})
                continue
            a, b = r
            c, st = _candidate(name, f, "coarse", a, b, W, H, corners, plan_box, fx, fy, tol * f)
            c["seconds"] = round(time.time() - t0, 1)
            out.append(c)
            if st is not None:
                hits.append((c["inliers"], st))
        if not hits:
            continue
        # stage 2 from the best coarse hit: plan centre and footprint in ground px
        hits.sort(key=lambda h: -h[0])
        s, t = hits[0][1]
        zc = s * complex(pw / 2, ph / 2) + t
        foot = abs(s) * max(pw, ph)
        for k in LOCATED_FACTORS:
            side = foot * k
            box = (zc.real - side / 2, zc.imag - side / 2, zc.real + side / 2, zc.imag + side / 2)
            t0 = time.time()
            try:
                r = _match_window(plan, img, box, W, H, url)
            except Exception as e:
                out.append({"ground": name, "window": k, "stage": "located", "error": repr(e)})
                continue
            if r is None:
                out.append({"ground": name, "window": k, "stage": "located", "matches": 0, "inliers": 0})
                continue
            a, b = r
            c, _ = _candidate(name, k, "located", a, b, W, H, corners, plan_box, fx, fy, tol * min(1.0, side / max(W, H)))
            c["seconds"] = round(time.time() - t0, 1)
            c["coarse_inliers"] = hits[0][0]
            out.append(c)
    return out


def spread(pairs):
    """How two-dimensional a set of inlier points is on the plan: (ratio, minor_sd_px).
    ratio = sqrt(minor / major eigenvalue) of the point covariance (1.0 = round cloud, 0 = a line);
    minor_sd_px = standard deviation along the minor axis in plan pixels.

    Why (2026-10-11, the line lead's Aesica counterexample): a single bath-house plan got 13 inliers on
    the OS six-inch sheet, all along one column of the plan (ratio 0.054, minor sd 15.6 px), and the
    similarity solved from a near-line of points put the building 8x too big over the fields; the page
    check caught it. On the 21 hand fits every accepted fit (>= 10 inliers) has ratio >= 0.138 and
    minor sd >= 30 px. Proposed guard: ratio >= 0.1 and minor_sd_px >= 20, else not sure.
    """
    p = np.array([[u, v] for u, v, *_ in pairs], float)
    if len(p) < 3:
        return 0.0, 0.0
    c = p - p.mean(0)
    ev = np.clip(np.linalg.eigvalsh(c.T @ c / len(p)), 0, None)
    ratio = float(np.sqrt(ev[0] / ev[1])) if ev[1] > 0 else 0.0
    return round(ratio, 3), round(float(np.sqrt(ev[0])), 1)


SPREAD_MIN_RATIO = 0.1
SPREAD_MIN_SD_PX = 20.0
