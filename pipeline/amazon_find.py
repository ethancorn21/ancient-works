"""Find geometric earthworks (ditched enclosures, ring ditches, geoglyphs) in an Amazon ground model.

usage: amazon_find.py <dtm.npz | dtm.tif> [out.json]

Two detectors on one ground model (EBA strip npz from amazon_dtm.py, or an SFB concession dtm.tif):

A. Ring ditches. scan.py's ring stage turned over: four oriented trench maps (how far each point lies BELOW the mean
   of the two points 12 m away along one axis), each ring radius split into 8 sectors, each sector reading the map
   whose axis runs across the ring line there. Score = second-lowest sector mean, so a ditch has to run most of the
   way round; a stream crossing part of a ring scores nothing.
B. Closed enclosures of any shape (squares, D-shapes, ovals). Ditch mask = black top-hat (closing minus ground,
   window 25 m) above 0.35 m; gaps up to ~10 m bridged (entrances, eroded stretches); the holes the mask encloses are
   the candidates. Kept if 0.12-20 ha, solid (area / convex hull >= 0.85) and with the ditch running round at least
   75% of the outline. Stream networks seldom enclose a solid, convex area; braided channels and logging-road
   loops can, which is what the eye check is for.

Ring candidates then get a second look (verify): the radial profile around the centre must dip into a ditch near the
ring and come back up on BOTH sides; inside and outside within 1.5 m of each other. A pit or sink (low inside), a
valley head or a hill shoulder fails. Score = the shallower of the two ditch walls (m) x the share of 32 spokes that
show the dip.
Before both detectors, raised specks under 6 m (vegetation left in the ground model) are opened away; ditches stay.

Output: candidates with centre (CRS x, y), size, scores and the detector that found them, strongest first.
"""
import json
import math
import os
import sys
import warnings

import numpy as np
from scipy import fft as sfft
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aw  # noqa: E402

SIDE_M = 12.0
AXES = [(0, 1), (-1, 1), (1, 0), (1, 1)]
# bridge 20 m: entrances / causeways of Acre geoglyphs run 10-20 m; at 10 m the 0414 geoglyph leaked out through
# a 28 m stretch where it meets a valley side, at 30 m the closing swallowed every hole (2026-10-10, tuning areas)
TOPHAT_M, DITCH_MIN_M, BRIDGE_M = 25.0, 0.35, 20.0
AREA_HA = (0.12, 20.0)
DITCH_HALF_M, SHOULDER_M = 6.0, 12.0  # verify: ditch edge this far from its floor, shoulder read over the next 12 m


def ring_width(r):
    return max(8.0, 0.08 * r)


def radii(r0=25.0, r1=200.0):
    out, r = [], r0
    while r <= r1:
        out.append(round(r, 1))
        r += 0.8 * ring_width(r)
    return out


RADII = radii()


def load(path):
    """(z, valid, px_m, meta) for an EBA npz or a GeoTIFF dtm (SFB)."""
    if path.endswith(".npz"):
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import amazon_dtm
        z, have, meta = amazon_dtm.load(path)
        meta["kind"] = "strip"
        return z, np.isfinite(z), meta["px_m"], meta
    import tifffile
    t = tifffile.TiffFile(path)
    z = t.pages[0].asarray().astype(np.float32)
    g = t.geotiff_metadata
    sx, sy = g["ModelPixelScale"][:2]
    tp = g["ModelTiepoint"]
    meta = {"kind": "grid", "epsg": int(g.get("ProjectedCSTypeGeoKey")), "x0": tp[3], "y0": tp[4], "px_m": float(sx),
            "name": os.path.splitext(os.path.basename(path))[0], "shape": list(z.shape)}
    return z, np.isfinite(z), float(sx), meta


def to_xy(meta, row, col):
    if meta["kind"] == "strip":
        import amazon_dtm
        return amazon_dtm.to_xy(meta, row, col)
    return meta["x0"] + (np.asarray(col) + 0.5) * meta["px_m"], meta["y0"] - (np.asarray(row) + 0.5) * meta["px_m"]


def trench_maps(lrm, px_m):
    k = SIDE_M / px_m
    out = []
    for dr, dc in AXES:
        n = math.hypot(dr, dc)
        sr, sc = int(round(dr / n * k)), int(round(dc / n * k))
        a = np.roll(lrm, (sr, sc), (0, 1))
        b = np.roll(lrm, (-sr, -sc), (0, 1))
        out.append(np.clip(0.5 * (a + b) - lrm, -0.6, 1.5).astype(np.float32))
    return out


def sector_kernels(r_px, w_px):
    R = int(math.ceil(r_px + w_px / 2))
    yy, xx = np.mgrid[-R:R + 1, -R:R + 1]
    d = np.hypot(yy, xx)
    ang = np.degrees(np.arctan2(-yy, xx)) % 360
    on = np.abs(d - r_px) <= w_px / 2
    return [(on & (((ang - s * 45 + 22.5) % 360) < 45))[::-1, ::-1].astype(np.float32) for s in range(8)]


def ring_detector(lrm, valid, px_m, top=400):
    """Detector A: best ring per centre over radii, local maxima, strongest first."""
    tr = trench_maps(lrm, px_m)
    H, W = valid.shape
    Kmax = max(2 * int(math.ceil(r / px_m + ring_width(r) / px_m / 2)) + 1 for r in RADII)
    P = (sfft.next_fast_len(H + Kmax), sfft.next_fast_len(W + Kmax))
    v = valid.astype(np.float32)
    Fv = sfft.rfft2(v, P, workers=-1)
    Ft = [sfft.rfft2(t * v, P, workers=-1) for t in tr]
    best = np.full((H, W), -np.inf, np.float32)
    best_r = np.zeros((H, W), np.float32)
    for r in RADII:
        ks = sector_kernels(r / px_m, ring_width(r) / px_m)
        h = ks[0].shape[0] // 2
        means = np.empty((8, H, W), np.float32)
        for s, K in enumerate(ks):
            Fk = sfft.rfft2(K, P, workers=-1)
            num = sfft.irfft2(Ft[s % 4] * Fk, P, workers=-1)[h:h + H, h:h + W]
            den = sfft.irfft2(Fv * Fk, P, workers=-1)[h:h + H, h:h + W]
            means[s] = np.where(den / K.sum() > 0.6, num / np.maximum(den, 1e-3), np.nan)
        n_ok = np.isfinite(means).sum(0)
        sc = np.where(n_ok >= 7, np.sort(means, 0)[1], -np.inf)
        upd = sc > best
        best[upd], best_r[upd] = sc[upd], r
    peak = (best == ndimage.maximum_filter(best, size=int(2 * 20 / px_m) + 1)) & (best > 0.15)
    rows, cols = np.nonzero(peak)
    order = np.argsort(-best[rows, cols])[:top]
    return [{"row": int(rows[i]), "col": int(cols[i]), "r_m": float(best_r[rows[i], cols[i]]),
             "score": round(float(best[rows[i], cols[i]]), 3), "det": "ring"} for i in order]


def enclosure_detector(z, valid, px_m):
    """Detector B: holes enclosed by a ditch mask."""
    zf = aw.fill_nan(z)
    w = int(round(TOPHAT_M / px_m)) | 1
    th = ndimage.grey_closing(zf, size=(w, w)) - zf
    ditch = (th > DITCH_MIN_M) & valid
    b = int(round(BRIDGE_M / px_m / 2))
    closed = ndimage.binary_closing(ditch, structure=np.ones((3, 3)), iterations=max(1, b))
    holes = ndimage.binary_fill_holes(closed) & ~closed & valid
    lab, n = ndimage.label(holes)
    out = []
    if not n:
        return out
    sl = ndimage.find_objects(lab)
    cell_ha = px_m * px_m / 1e4
    for i, s in enumerate(sl, 1):
        m = lab[s] == i
        area = m.sum() * cell_ha
        if not (AREA_HA[0] <= area <= AREA_HA[1]):
            continue
        # touching the swath edge = not enclosed, just cut off
        pad = tuple(slice(max(0, q.start - 2), q.stop + 2) for q in s)
        if (~valid[pad]).any() and ndimage.binary_dilation(lab[pad] == i, iterations=2)[~valid[pad]].any():
            continue
        rr, cc = np.nonzero(m)
        pts = np.stack([rr, cc], 1).astype(float)
        try:
            from scipy.spatial import ConvexHull
            hull = ConvexHull(pts).volume + 0.5 * len(pts) ** 0.5
        except Exception:
            continue
        solidity = min(1.0, m.sum() / hull)
        if solidity < 0.85:
            continue
        mm = lab[pad] == i
        ring = ndimage.binary_dilation(mm, iterations=int(round(4 / px_m)) + 1) & ~mm
        closure = float(ditch[pad][ring].mean())
        if closure < 0.75:
            continue
        depth = float(np.median(th[pad][ring & ditch[pad]]))
        perim = (m & ~ndimage.binary_erosion(m)).sum() * px_m
        circ = 4 * math.pi * area * 1e4 / max(perim, 1) ** 2
        out.append({"row": float(rr.mean() + s[0].start), "col": float(cc.mean() + s[1].start),
                    "r_m": round(math.sqrt(area * 1e4 / math.pi), 1), "area_ha": round(area, 2),
                    "solidity": round(solidity, 3), "closure": round(closure, 3), "depth_m": round(depth, 2),
                    "circularity": round(min(1.0, circ), 3), "score": round(depth * closure * solidity, 3),
                    "det": "enclosure"})
    return sorted(out, key=lambda c: -c["score"])


def verify(zo, valid, px, c, n_spokes=32):
    """Radial profiles on n spokes. On each spoke the ditch is the lowest point within 0.75-1.25 r; its shoulders are
    the ground SHOULDER_M beyond its edges on either side (not the far field, which on a ridge-top site is the next
    valley). Wall = the lower shoulder above the ditch floor. Score = the 25th percentile of the walls: a dug ditch
    keeps its depth all the way round, a stream channel fades out at its head. Adds fields; returns score."""
    r_px = c["r_m"] / px
    edge, sh = DITCH_HALF_M / px, SHOULDER_M / px
    best = None
    for dr in (-2, 0, 2):
        for dc in (-2, 0, 2):
            for f in (0.85, 1.0, 1.15):
                rc, cc, R = c["row"] + dr, c["col"] + dc, r_px * f
                t = np.linspace(0, 2 * np.pi, n_spokes, endpoint=False)
                q = np.arange(0, 1.25 * R + edge + sh + 1)
                rr = rc - np.outer(np.sin(t), q)
                cl = cc + np.outer(np.cos(t), q)
                ok = (rr >= 0) & (rr < zo.shape[0] - 1) & (cl >= 0) & (cl < zo.shape[1] - 1)
                if ok.mean() < 0.9:
                    continue
                at = [np.clip(rr, 0, zo.shape[0] - 1), np.clip(cl, 0, zo.shape[1] - 1)]
                v = ndimage.map_coordinates(valid.astype(np.float32), at, order=0) > 0
                prof = np.where(v, ndimage.map_coordinates(zo, at, order=1), np.nan)
                band = (q >= 0.75 * R) & (q <= 1.25 * R)
                bp = np.where(band, prof, np.nan)
                if not np.isfinite(bp).any(1).any():
                    continue
                pos = np.nanargmin(np.where(np.isfinite(bp), bp, np.inf), 1)
                qd = q[pos][:, None]
                win_in = (q >= np.maximum(qd - edge - sh, 0.1 * R)) & (q <= qd - edge)
                win_out = (q >= qd + edge) & (q <= qd + edge + sh)
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", RuntimeWarning)
                    dit = np.nanmin(bp, 1)
                    z_in = np.nanmedian(np.where(win_in, prof, np.nan), 1)
                    z_out = np.nanmedian(np.where(win_out, prof, np.nan), 1)
                wall = np.minimum(z_in, z_out) - dit
                # a spoke that leaves the swath is no evidence: at strip edges sparse returns read as a ditch
                # (2026-10-10: 9 of the 0414 top 20 sat on the swath edge)
                good = np.isfinite(wall) & v.all(1)
                if good.mean() < 0.9:
                    continue
                w = wall[good]
                sc = max(0.0, float(np.percentile(w, 25)))
                level = abs(float(np.nanmedian(z_in - z_out)))
                if level > 1.5:
                    sc = 0.0
                if best is None or sc > best[0]:
                    floor_rng = float(np.nanpercentile(dit, 90) - np.nanpercentile(dit, 10))
                    sh_rng = float(np.nanpercentile(z_out, 90) - np.nanpercentile(z_out, 10))
                    best = (sc, rc, cc, R, float(np.median(w)), float((w > 0.25).mean()), level, floor_rng, sh_rng)
    if best is None:
        c.update(vscore=0.0)
        return 0.0
    sc, rc, cc, R, wmed, share, level, floor_rng, sh_rng = best
    c.update(row=rc, col=cc, r_m=round(R * px, 1), vscore=round(sc, 3), wall_med_m=round(wmed, 2),
             spokes=round(share, 2), level_m=round(level, 2), floor_range_m=round(floor_rng, 2),
             shoulder_range_m=round(sh_rng, 2))
    return sc


def find(path):
    z, valid, px, meta = load(path)
    zo = ndimage.grey_opening(aw.fill_nan(z), size=(3, 3)) if px <= 2 else aw.fill_nan(z)
    lrm = aw.local_relief(zo, px, 30.0)
    rings = ring_detector(lrm, valid, px)
    for c in rings:
        verify(zo, valid, px, c)
    rings = [c for c in rings if c["vscore"] > 0]
    for c in rings:
        c["rank_score"] = c["vscore"]
    encl = enclosure_detector(np.where(valid, zo, np.nan), valid, px)
    for c in encl:
        c["rank_score"] = c["score"]
    # one list: both scores are ditch depths in metres; a ring and an enclosure on the same spot count once (the
    # stronger stays, the other detector is noted)
    cands = []
    for c in sorted(rings + encl, key=lambda c: -c["rank_score"]):
        dup = next((k for k in cands if math.hypot(k["row"] - c["row"], k["col"] - c["col"]) * px
                    <= max(60.0, 0.5 * max(k["r_m"], c["r_m"]))), None)
        if dup:
            dup.setdefault("also", []).append(c["det"])
        else:
            cands.append(c)
    for c in cands:
        x, y = to_xy(meta, c["row"], c["col"])
        c["x"], c["y"] = round(float(x), 1), round(float(y), 1)
    area_km2 = float(valid.sum()) * px * px / 1e6
    return {"source": os.path.basename(path), "meta": meta, "area_km2": round(area_km2, 3), "candidates": cands}


if __name__ == "__main__":
    res = find(sys.argv[1])
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(sys.argv[1])[0] + ".cands.json"
    json.dump(res, open(out, "w"), indent=0)
    n = {d: sum(1 for c in res["candidates"] if c["det"] == d) for d in ("ring", "enclosure")}
    print(res["source"], res["area_km2"], "km2", n, "->", out)
