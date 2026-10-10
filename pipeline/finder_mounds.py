"""Mound detector: multi-scale, slope-proof, ridge-proof local relief maxima, then per-peak measurements.

For each basal diameter D (8-64 m) and every pixel as a centre:
  top     = mean height of a disc of radius 0.3 D/2 (the mound top)
  annulus = ring from 1.1 to 1.6 x D/2 (ground just outside the foot), split into 8 sectors
A plane is fitted to the annulus (closed form: the ring is symmetric) and removed, so a leftover slope cancels.
score_D = (top - plane at centre) - (2nd highest sector residual): the top must stand above the ground in every
direction but one, so ridges, terrace edges and hill shoulders (which are high in some directions) score ~0.
All sums are FFT correlations over the tile. Masked ground (roads, buildings, water) is filled with a smooth
background first and its share is tracked; peaks need >= 80% valid top and >= 60% valid ring.

measure() then reads radial profiles in 16 directions around each peak on the 2 m DEM:
  h_m          height of the top above the fitted ring plane
  diam_m       2 x median radius where the profile falls to half height
  round        min / max of those 16 radii (1 = circle)
  elong        major / minor axis from second moments of the above-half-height blob
  flat_top     area above 80% height / area above 50% height (cylinders ~1, domes and cones lower)
  base_slope   slope of the ring plane, degrees
  rough_m      robust spread of the ring residuals
  snr          h_m / rough_m
  modern_m     distance to the nearest masked (OSM modern) pixel
"""
import math

import numpy as np
from scipy import fft as sfft
from scipy.ndimage import gaussian_filter, maximum_filter, distance_transform_edt

DIAMS_FINE = [8.0, 11.0, 15.0, 20.0, 27.0]  # run at the tile's pixel size
DIAMS_COARSE = [36.0, 48.0, 64.0]           # run at twice the pixel size
MIN_SCORE_M = 0.12


def _kernels(r_px):
    """Top disc, ring, ring*x, ring*y and 8 ring sectors, plus the sectors' centroid offsets (px, x east, y north)."""
    ri, ra0, ra1 = max(1.0, 0.3 * r_px), 1.1 * r_px, max(1.6 * r_px, 1.1 * r_px + 2.0)
    R = int(math.ceil(ra1))
    yy, xx = np.mgrid[-R:R + 1, -R:R + 1].astype(np.float64)
    d = np.hypot(yy, xx)
    north = -yy
    top = (d <= ri).astype(np.float32)
    ring = ((d >= ra0) & (d <= ra1)).astype(np.float32)
    ang = np.degrees(np.arctan2(north, xx)) % 360
    secs, cent = [], []
    for s in range(8):
        m = ring * ((((ang - s * 45 + 22.5) % 360) < 45).astype(np.float32))
        secs.append(m)
        cent.append(((xx * m).sum() / m.sum(), (north * m).sum() / m.sum()))
    return top, ring, (ring * xx).astype(np.float32), (ring * north).astype(np.float32), secs, cent, \
        float((ring * xx * xx).sum()), float((ring * north * north).sum())


class FFTCorr:
    """Correlation of one image with many small kernels, sharing the image's FFT."""

    def __init__(self, img, kmax):
        self.H, self.W = img.shape
        self.P = (sfft.next_fast_len(self.H + kmax), sfft.next_fast_len(self.W + kmax))
        self.F = sfft.rfft2(img.astype(np.float32), self.P, workers=-1)

    def __call__(self, K, F=None):
        h = K.shape[0] // 2
        Fk = sfft.rfft2(K[::-1, ::-1], self.P, workers=-1)
        out = sfft.irfft2((self.F if F is None else F) * Fk, self.P, workers=-1)
        return out[h:h + self.H, h:h + self.W]


def _block2(a):
    H, W = (a.shape[0] // 2) * 2, (a.shape[1] // 2) * 2
    return a[:H, :W].reshape(H // 2, 2, W // 2, 2).mean((1, 3))


def scores(z, valid, px_m, diams):
    """score_D, height_D and valid shares for each D (list of dicts of arrays at this pixel size)."""
    zf = np.where(valid, z, np.nan)
    v = valid.astype(np.float32)
    g = gaussian_filter(np.nan_to_num(zf), 6) / np.maximum(gaussian_filter(v, 6), 1e-3)
    zf = np.where(valid, z, g).astype(np.float32)
    zf = zf - np.float32(np.mean(zf))  # numerical headroom for float32 FFTs
    kmax = 2 * int(math.ceil(1.6 * max(diams) / 2 / px_m + 2)) + 1
    cz = FFTCorr(zf, kmax)
    Fv = sfft.rfft2(v, cz.P, workers=-1)
    out = []
    for D in diams:
        r_px = D / 2 / px_m
        top, ring, rx, ry, secs, cent, sxx, syy = _kernels(r_px)
        n_top, n_ring = top.sum(), ring.sum()
        t = cz(top) / n_top
        a = cz(ring) / n_ring
        b = cz(rx) / sxx
        c = cz(ry) / syy
        res = []
        for m, (cx, cy) in zip(secs, cent):
            res.append(cz(m) / m.sum() - (a + b * cx + c * cy))
        res = np.sort(np.stack(res), 0)
        h = t - a
        out.append({"D": D, "score": h - res[-2], "h": h, "slope": np.hypot(b, c) / px_m,
                    "vtop": cz(top, Fv) / n_top, "vring": cz(ring, Fv) / n_ring})
    return out


def detect(z, valid, px_m, core=None, min_score=MIN_SCORE_M):
    """Peaks over space and scale. Returns list of dicts with row, col (full-res px), D, score, h."""
    peaks = []
    for fct, diams in ((1, DIAMS_FINE), (2, DIAMS_COARSE)):
        if fct == 1:
            zz, vv = z, valid
        else:
            zz = _block2(np.where(valid, z, 0)) / np.maximum(_block2(valid.astype(np.float32)), 1e-3)
            vv = _block2(valid.astype(np.float32)) > 0.5
            zz = np.where(vv, zz, np.nanmedian(z))
        for s in scores(zz, vv, px_m * fct, diams):
            sc = np.where((s["vtop"] > 0.8) & (s["vring"] > 0.6), s["score"], -9)
            size = max(3, int(round(s["D"] / (px_m * fct))) | 1)
            pk = (sc == maximum_filter(sc, size=size)) & (sc >= min_score)
            for r, c in zip(*np.nonzero(pk)):
                R0, C0 = (r + 0.5) * fct - 0.5, (c + 0.5) * fct - 0.5
                if core is not None and not (core[0] <= R0 < core[1] and core[0] <= C0 < core[1]):
                    continue
                peaks.append({"row": float(R0), "col": float(C0), "D": s["D"], "score": float(sc[r, c]),
                              "h_scale": float(s["h"][r, c]), "slope_scale": float(s["slope"][r, c])})
    # one peak per mound: strongest first, suppress weaker peaks within half the stronger one's diameter
    peaks.sort(key=lambda p: -p["score"])
    kept, cell = [], 40.0 / px_m
    grid = {}
    for p in peaks:
        gx, gy = int(p["col"] // cell), int(p["row"] // cell)
        clash = False
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                for o in grid.get((gx + i, gy + j), ()):
                    if math.hypot(p["col"] - o["col"], p["row"] - o["row"]) * px_m < 0.5 * max(p["D"], o["D"]):
                        clash = True
                        break
                if clash:
                    break
            if clash:
                break
        if not clash:
            kept.append(p)
            grid.setdefault((gx, gy), []).append(p)
    return kept


N_DIR = 16


def measure(z, valid, px_m, peaks, dist_modern=None):
    """Radial-profile measurements for each peak (see module doc). Adds keys in place; returns peaks."""
    H, W = z.shape
    th = np.arange(N_DIR) * 2 * np.pi / N_DIR
    if dist_modern is None:
        dist_modern = distance_transform_edt(valid) * px_m
    for p in peaks:
        r0, c0 = p["row"], p["col"]
        rmax = max(1.6 * p["D"], 20.0)
        steps = np.arange(0, rmax + px_m, px_m / 2)  # metres
        rr = r0 - np.outer(np.sin(th), steps) / px_m
        cc = c0 + np.outer(np.cos(th), steps) / px_m
        ri, ci = np.clip(np.rint(rr).astype(int), 0, H - 1), np.clip(np.rint(cc).astype(int), 0, W - 1)
        prof = z[ri, ci].astype(np.float64)
        ok = valid[ri, ci]
        # base ring: 1.1-1.6 x D/2 (the detector's ring), plane fit by least squares
        bmask = (steps >= 0.55 * p["D"]) & (steps <= 0.8 * p["D"])
        X = np.cos(th)[:, None] * steps[None, :]
        Y = np.sin(th)[:, None] * steps[None, :]
        sel = bmask[None, :] & ok
        if sel.sum() < 12:
            p["skip"] = "no ring"
            continue
        A = np.stack([np.ones(sel.sum()), X[sel], Y[sel]], 1)
        coef, *_ = np.linalg.lstsq(A, prof[sel], rcond=None)
        base = coef[0] + coef[1] * X + coef[2] * Y
        rel = prof - base
        resid = rel[sel]
        rough = float(np.median(np.abs(resid - np.median(resid))) * 1.4826)
        ctr = rel[:, :3][ok[:, :3]]
        h = float(np.mean(ctr)) if ctr.size else float("nan")
        p["h_m"] = round(h, 3)
        p["rough_m"] = round(max(rough, 0.02), 3)
        p["snr"] = round(h / max(rough, 0.02), 2)
        p["base_slope"] = round(math.degrees(math.atan(math.hypot(coef[1], coef[2]))), 2)
        if not h > 0:
            p["skip"] = "not raised"
            continue
        # half-height radius per direction: first step where the profile falls below h/2
        below = rel < h / 2
        below[:, 0] = False
        first = np.where(below.any(1), below.argmax(1), len(steps) - 1)
        rad = steps[first]
        p["diam_m"] = round(float(2 * np.median(rad)), 1)
        p["round"] = round(float(rad.min() / max(rad.max(), px_m)), 2)
        # blob moments and flatness on the grid, inside 1.6 x median radius
        R = int(math.ceil(1.6 * max(np.median(rad), px_m) / px_m)) + 1
        r_lo, r_hi = int(max(0, round(r0) - R)), int(min(H, round(r0) + R + 1))
        c_lo, c_hi = int(max(0, round(c0) - R)), int(min(W, round(c0) + R + 1))
        sub = z[r_lo:r_hi, c_lo:c_hi].astype(np.float64)
        yy, xx = np.mgrid[r_lo:r_hi, c_lo:c_hi]
        dx, dy = (xx - c0) * px_m, (r0 - yy) * px_m
        relg = sub - (coef[0] + coef[1] * dx + coef[2] * dy)
        half = relg > h / 2
        if half.sum() >= 3:
            w = half.astype(float)
            mx, my = (dx * w).sum() / w.sum(), (dy * w).sum() / w.sum()
            cov = np.cov(np.stack([dx[half] - mx, dy[half] - my]))
            ev = np.sort(np.linalg.eigvalsh(cov))
            p["elong"] = round(float(math.sqrt(max(ev[1], 1e-6) / max(ev[0], 1e-6))), 2)
            p["flat_top"] = round(float((relg > 0.8 * h).sum() / half.sum()), 2)
        else:
            p["elong"], p["flat_top"] = 1.0, 0.0
        p["modern_m"] = round(float(dist_modern[int(round(r0)), int(round(c0))]), 1)
    return peaks


def keep(p):
    """Plausibility limits for a mound (before ranking)."""
    return ("skip" not in p and 0.15 <= p["h_m"] <= 15 and 6 <= p["diam_m"] <= 70 and p["round"] >= 0.35
            and p["elong"] <= 3.0)
