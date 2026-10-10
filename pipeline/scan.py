"""Scan an area of LiDAR for circular earthworks.

For every tile: DEM -> local relief -> four oriented ridge maps (how far each point stands above the mean of
the two points 20 m away along one axis; the mean, not the higher, so a leftover slope cancels instead of
burying a low wall), with roads, buildings and water masked. Each ring radius is split
into 8 sectors, and each sector reads the ridge map whose axis runs across the wall there (radially), so only
walls running round the ring count. Stage 1 score is the second-lowest sector mean, in metres:
a wall must go most of the way round, so a river bank or gully crossing part of a ring scores nothing.
Large rings run at half resolution. Stage 2 (verify) re-scores each stage-1 ring on the full-resolution relief
with a local plane removed, needing the crest above BOTH its inner and outer band in 6 of 8 sectors, which drops
hill shoulders and terrace edges. Candidates are ranked by that score over the roughness of the ground around.

usage: scan.py <name> <lon0> <lat0> <lon1> <lat1> [px_m]     (ONLY=ty_tx,ty_tx limits the run to those tiles)
writes data/scan/<name>/{tiles/*.npz, candidates.json, ridge_preview.png}
"""
import json
import math
import os
import sys
import time

import numpy as np
from PIL import Image
from scipy import fft as sfft
from scipy.ndimage import maximum_filter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aw  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIDE_M = 20.0
TILE_M, PAD_M = 4000.0, 560.0
AXES = [(0, 1), (-1, 1), (1, 0), (1, 1)]  # (drow, dcol): wall normals at 0, 45, 90, 135 degrees from east
MIN_SCORE_M = 0.05
COARSE_FROM_M = 90.0  # rings this big run at twice the pixel size


def ring_width(r):
    return max(10.0, 0.09 * r)


def radii(r0=30.0, r1=270.0):
    out, r = [], r0
    while r <= r1:
        out.append(round(r, 1))
        r += 0.8 * ring_width(r)
    return out


RADII = radii()


def ridge_maps(z, px_m):
    lrm = aw.local_relief(aw.fill_nan(z), px_m)
    k = SIDE_M / px_m
    out = []
    for dr, dc in AXES:
        n = math.hypot(dr, dc)
        sr, sc = int(round(dr / n * k)), int(round(dc / n * k))
        a = np.roll(lrm, (sr, sc), (0, 1))
        b = np.roll(lrm, (-sr, -sc), (0, 1))
        out.append(np.clip(lrm - 0.5 * (a + b), -0.4, 0.6).astype(np.float32))
    return out


def sector_kernels(r_px, w_px):
    R = int(math.ceil(r_px + w_px / 2))
    yy, xx = np.mgrid[-R:R + 1, -R:R + 1]
    d = np.hypot(yy, xx)
    ang = np.degrees(np.arctan2(-yy, xx)) % 360  # counterclockwise from east, rows point south
    on = np.abs(d - r_px) <= w_px / 2
    ks = []
    for s in range(8):
        sec = on & (((ang - s * 45 + 22.5) % 360) < 45)
        ks.append(sec[::-1, ::-1].astype(np.float32))  # flipped: convolution with a flipped kernel = correlation
    return ks


def ring_scores(rids, valid, px_m, rads):
    """Second-lowest sector mean of the oriented ridge, for every pixel as a ring centre, per radius."""
    H, W = valid.shape
    Kmax = max(2 * int(math.ceil(r / px_m + ring_width(r) / px_m / 2)) + 1 for r in rads)
    P = (sfft.next_fast_len(H + Kmax), sfft.next_fast_len(W + Kmax))
    v = valid.astype(np.float32)
    Fv = sfft.rfft2(v, P, workers=-1)
    Fr = [sfft.rfft2(r * v, P, workers=-1) for r in rids]
    out = []
    for r in rads:
        ks = sector_kernels(r / px_m, ring_width(r) / px_m)
        h = ks[0].shape[0] // 2
        means = np.empty((8, H, W), np.float32)
        cover = np.empty((8, H, W), np.float32)
        for s, K in enumerate(ks):
            Fk = sfft.rfft2(K, P, workers=-1)
            num = sfft.irfft2(Fr[s % 4] * Fk, P, workers=-1)[h:h + H, h:h + W]
            den = sfft.irfft2(Fv * Fk, P, workers=-1)[h:h + H, h:h + W]
            cover[s] = den / K.sum()
            means[s] = np.where(cover[s] > 0.5, num / np.maximum(den, 1e-3), np.nan)
        n_ok = np.isfinite(means).sum(0)
        srt = np.sort(means, 0)  # NaN sorts last
        score = np.where(n_ok >= 6, srt[1], np.nan)
        out.append((r, score, np.nanmean(means, 0), cover.mean(0)))
    return out


def block2(a, valid):
    """2x2 block mean over valid pixels (a) and the block's valid share."""
    H, W = (a.shape[0] // 2) * 2, (a.shape[1] // 2) * 2
    av, v = (a * valid)[:H, :W], valid[:H, :W].astype(np.float32)
    s = av.reshape(H // 2, 2, W // 2, 2).sum((1, 3))
    n = v.reshape(H // 2, 2, W // 2, 2).sum((1, 3))
    return s / np.maximum(n, 1), n / 4


def scan_tile(z, valid, px_m):
    rids = ridge_maps(z, px_m)
    fine = [r for r in RADII if r < COARSE_FROM_M]
    coarse = [r for r in RADII if r >= COARSE_FROM_M]
    res = [(r, sc, mn, cv, 1) for r, sc, mn, cv in ring_scores(rids, valid, px_m, fine)]
    if coarse:
        pairs = [block2(r, valid) for r in rids]
        v2 = pairs[0][1] > 0.5
        res += [(r, sc, mn, cv, 2) for r, sc, mn, cv in ring_scores([p[0] for p in pairs], v2, px_m * 2, coarse)]
    return np.max(rids, 0), res


def merge(cands, key):
    """One candidate per ring, strongest first: the same centre at neighbouring radii is one ring; a small ring
    inside a big one is not. Candidates carry ground metres x, y. Spatial hash, so it stays fast at 10^5."""
    cell = 0.5 * max(RADII) + 1
    grid, kept = {}, []
    for c in sorted(cands, key=lambda c: -c[key]):
        gx, gy = int(c["x"] // cell), int(c["y"] // cell)
        clash = False
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                for o in grid.get((gx + i, gy + j), ()):
                    big, small = max(c["r_m"], o["r_m"]), min(c["r_m"], o["r_m"])
                    if math.hypot(c["x"] - o["x"], c["y"] - o["y"]) <= 0.5 * big and big / small <= 1.6:
                        clash = True
                        break
                if clash:
                    break
            if clash:
                break
        if not clash:
            kept.append(c)
            grid.setdefault((gx, gy), []).append(c)
    return kept


N_ANG = 128


def verify(lrm, cands, px_m, chunk=64):
    """Second look at each stage-1 ring on the full-resolution relief, centre and radius refined one step.

    For each trial ring a plane is fitted to two bands 20 m inside and outside it (not the ring itself) and
    removed; each of 8 sectors then scores crest minus the HIGHER of its inner and outer band. A wall beats
    both; a hill shoulder (inside higher) or a terrace edge loses on one side. Score = third-lowest sector,
    so two sectors may fail (gateways, junctions with other walls). snr = score / roughness of the bands.
    """
    H, W = lrm.shape
    th = (np.arange(N_ANG) + 0.5) / N_ANG * 2 * np.pi
    sec = (np.degrees(th) + 22.5) % 360 // 45  # sector of each angle, 0 = east
    sec = sec.astype(int)
    out = []
    by_r = {}
    for c in cands:
        by_r.setdefault(c["r_m"], []).append(c)
    for r, group in by_r.items():
        w = ring_width(r)
        trial = []
        for dr in (-0.8, -0.4, 0.0, 0.4, 0.8):
            rr = r + dr * w
            sub = np.array([-w / 4, 0, w / 4])
            rho = np.stack([rr - SIDE_M + sub, rr + sub, rr + SIDE_M + sub]) / px_m  # (band, sub)
            dx = rho[..., None] * np.cos(th)  # (3, 3, A) px, east
            dy = -rho[..., None] * np.sin(th)  # rows point south
            X = np.stack([np.ones_like(dx), dx, dy], -1)  # plane design, per sample
            Xs = X[[0, 2]].reshape(-1, 3)  # inner + outer bands only
            trial.append((rr, dx, dy, np.linalg.pinv(Xs), X))
        offs = np.array([(a, b) for a in (-0.4, 0, 0.4) for b in (-0.4, 0, 0.4)]) * w / px_m  # (9, 2) row, col
        for k0 in range(0, len(group), chunk):
            g = group[k0:k0 + chunk]
            rc = np.array([[c["row"], c["col"]] for c in g])  # (N, 2)
            best = [None] * len(g)
            for rr, dx, dy, P, X in trial:
                R = rc[:, None, 0, None, None, None] + offs[None, :, 0, None, None, None] + dy[None, None]
                C = rc[:, None, 1, None, None, None] + offs[None, :, 1, None, None, None] + dx[None, None]
                Ri, Ci = np.rint(R).astype(int), np.rint(C).astype(int)
                inb = (Ri >= 0) & (Ri < H) & (Ci >= 0) & (Ci < W)
                v = np.where(inb, lrm[np.clip(Ri, 0, H - 1), np.clip(Ci, 0, W - 1)], np.nan)  # (N, 9, 3, 3, A)
                ok = np.isfinite(v)
                side = v[:, :, [0, 2]].reshape(len(g), 9, -1)
                fill = np.nanmedian(side, -1)
                fill = np.where(np.isfinite(fill), fill, 0)
                sidef = np.where(np.isfinite(side), side, fill[..., None])
                coef = sidef @ P.T  # (N, 9, 3)
                res = v - (X[None, None] @ coef[:, :, None, None, :, None])[..., 0]  # (N, 9, 3, 3, A)
                rsd = res[:, :, [0, 2]].reshape(len(g), 9, -1)
                med = np.nanmedian(rsd, -1)
                rough = np.maximum(np.nanmedian(np.abs(rsd - med[..., None]), -1) * 1.4826, 0.05)
                band = np.nanmean(res, 3)  # (N, 9, 3, A): mean across the band's width
                valid = ok.mean(3)[:, :, 1]  # crest coverage per angle
                smean = np.full(band.shape[:3] + (8,), np.nan)
                scov = np.zeros(band.shape[:2] + (8,))
                for s_ in range(8):
                    m = sec == s_
                    with np.errstate(invalid="ignore"):
                        smean[..., s_] = np.nanmean(band[..., m], -1)
                    scov[..., s_] = valid[..., m].mean(-1)
                con = smean[:, :, 1] - np.maximum(smean[:, :, 0], smean[:, :, 2])  # (N, 9, 8)
                con = np.where(scov > 0.5, con, np.nan)
                n_ok = np.isfinite(con).sum(-1)
                srt = np.sort(con, -1)
                score = np.where(n_ok >= 6, srt[..., 2], np.nan)
                snr = score / rough
                for i in range(len(g)):
                    if not np.isfinite(snr[i]).any():
                        continue
                    j = int(np.nanargmax(snr[i]))
                    if best[i] is None or snr[i, j] > best[i][0]:
                        best[i] = (float(snr[i, j]), float(score[i, j]), float(rough[i, j]), rr, offs[j],
                                   int((con[i, j] > 0).sum()))
            for c, b in zip(g, best):
                if b is None:
                    continue
                snr_, sc_, ro_, rr, (orow, ocol), npos = b
                out.append({**c, "row": c["row"] + orow, "col": c["col"] + ocol, "r_m": round(rr, 1),
                            "score_m": round(sc_, 3), "rough_m": round(ro_, 3), "snr": round(snr_, 2), "sectors": npos})
    return out


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
    only = set(os.environ.get("ONLY", "").split(",")) - {""}
    pw = int((TILE_M + 2 * PAD_M) / px_m)
    core = slice(int(PAD_M / px_m), int((PAD_M + TILE_M) / px_m))
    for ty in range(ny):
        for tx in range(nx):
            if only and f"{ty}_{tx}" not in only:
                continue
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
            raw = []
            for r, sc, mn, cv, fct in maps:
                pm = px_m * fct
                c0, c1 = int(PAD_M / pm), int((PAD_M + TILE_M) / pm)
                s0 = np.where(np.isfinite(sc), sc, -9.0)
                peak = (s0 == maximum_filter(s0, size=max(3, int(r / pm)))) & (s0 >= MIN_SCORE_M)
                peak[:c0], peak[c1:], peak[:, :c0], peak[:, c1:] = False, False, False, False
                for row, col in zip(*np.nonzero(peak)):
                    R0, C0 = (row + 0.5) * fct - 0.5, (col + 0.5) * fct - 0.5  # full-resolution pixel
                    raw.append({"row": R0, "col": C0, "x": C0 * px_m, "y": -R0 * px_m, "r_m": r,
                                "stage1_m": round(float(sc[row, col]), 3)})
            one = merge(raw, "stage1_m")
            lrm = aw.local_relief(aw.fill_nan(z), px_m)
            lrm[~valid] = np.nan
            ver = [c for c in verify(lrm, one, px_m) if c["score_m"] > 0.02]
            for c in ver:
                lon, lat = aw.to_lonlat(bx0 + (c["col"] + 0.5) * px_m * k, by1 - (c["row"] + 0.5) * px_m * k)
                gx, gy = aw.to_merc(lon, lat)
                cands.append({"lon": round(lon, 6), "lat": round(lat, 6), "r_m": c["r_m"], "score_m": c["score_m"],
                              "snr": c["snr"], "rough_m": c["rough_m"], "sectors": c["sectors"], "stage1_m": c["stage1_m"],
                              "tile": [ty, tx], "x": gx / k, "y": gy / k})
            print(f"  tile {ty},{tx} done in {time.time() - t0:.0f}s: {len(raw)} raw, {len(one)} rings, {len(ver)} verified",
                  flush=True)
    out = merge(cands, "snr")  # tiles overlap by their padding
    for i, c in enumerate(out):
        c.pop("x"), c.pop("y")
        c["id"] = f"{name}-{i:04d}"
    aw.save_json(os.path.join(d, "candidates.json"), {"area": [lon0, lat0, lon1, lat1], "px_m": px_m,
                                                      "radii_m": RADII, "min_score_m": MIN_SCORE_M, "candidates": out})
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
