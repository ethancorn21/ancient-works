"""Fit a plate onto LiDAR relief from a rough seed, with a hand or automatically extracted wall template.

Test harness for docs/autofit.md (pre-registered criterion). Coordinates follow fit_plate.py:
ground(uv) = M @ [u - u0, -(v - v0)] + t, ground = metres (E, N) from the relief image centre.
Here (u0, v0) is always the plate-image centre, so t is where the plate centre lands.

usage:
  autofit.py check                       # scorer reproduces fit_plate's ridge_contrast_m on the hand fits
  autofit.py run <tag> <auto|auto_noqwen|hand> [site ...]   # seeds x sites, writes data/autofit/results_<tag>.json
"""
import json
import math
import os
import sys
import time

import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates, shift as nd_shift

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aw  # noqa: E402
from fit_plate import sample_walls  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "autofit")
SITES = ["fudge", "hopeton", "newark", "forthill", "highbank"]
RNG_SEED, N_SEEDS = 20261010, 8
WIN_ROT, WIN_LOGS, WIN_T = math.radians(25), (math.log(0.74), math.log(1.36)), 200.0


def sim(s, rot):
    c, sn = math.cos(rot), math.sin(rot)
    return np.array([[s * c, -s * sn], [s * sn, s * c]])


def mat_params(M):
    return math.sqrt(abs(np.linalg.det(M))), math.atan2(M[1, 0], M[0, 0])


class Site:
    """Relief, masks and the hand fit for one site, in the plate-centre convention."""

    def __init__(self, sid):
        self.id = sid
        self.dir = os.path.join(ROOT, "data", "sites", sid)
        self.site = json.load(open(os.path.join(self.dir, "site.json")))
        p = self.site["plate"]
        self.plate = p
        self.px_m = self.site.get("px_m", 1.0)
        self.W_m, self.H_m = self.site["width_m"], self.site["height_m"]
        z = aw.fill_nan(np.load(os.path.join(self.dir, "dem.npy")))
        self.z = z
        self.lrm_radius = p.get("lrm_radius_m", 24.0)
        self.clip = p.get("clip_m", 1.0)
        self.side_m = p.get("side_m", 20.0)
        lrm = np.clip(aw.local_relief(z, self.px_m, radius_m=self.lrm_radius), -self.clip, self.clip)
        self.modern = np.load(os.path.join(self.dir, "modern_mask.npy"))
        self.water = aw.water_mask(z, self.px_m)
        lrm[self.modern] = np.nan
        lrm[self.water] = np.nan
        self.lrm = lrm
        self.h, self.w = lrm.shape
        self.img_size = Image.open(os.path.join(self.dir, "plate_scan.jpg")).size
        Wp, Hp = self.img_size
        self.c0 = np.array([Wp / 2.0, Hp / 2.0])
        # hand fit, re-expressed about the plate-image centre
        a = p["fit"]["affine"]
        M = np.array([[a[0], a[1]], [a[2], a[3]]])
        u0, v0 = p["fit"]["u0v0"]
        t = np.array(a[4:6])
        d = np.array([self.c0[0] - u0, -(self.c0[1] - v0)])
        self.hand_M, self.hand_t = M, M @ d + t
        self.hand_s, self.hand_rot = mat_params(M)
        self.diag_m = math.hypot(Wp, Hp) * self.hand_s
        self.tol_m = max(15.0, 0.02 * self.diag_m)
        self.hand_u0v0 = (u0, v0)

    # plate px -> ground metres
    def to_ground(self, uv, M, t):
        d = np.stack([uv[:, 0] - self.c0[0], -(uv[:, 1] - self.c0[1])], 1)
        return d @ M.T + t

    def corners_ground(self, M, t):
        Wp, Hp = self.img_size
        return self.to_ground(np.array([[0, 0], [Wp, 0], [Wp, Hp], [0, Hp]], float), M, t)

    def corner_rms(self, M, t):
        a, b = self.corners_ground(M, t), self.corners_ground(self.hand_M, self.hand_t)
        return float(np.sqrt(np.mean(np.sum((a - b) ** 2, 1))))

    def relief_at(self, en):
        col = (en[:, 0] + self.W_m / 2) / self.px_m
        row = (self.H_m / 2 - en[:, 1]) / self.px_m
        ok = (col >= 0) & (col < self.w - 1) & (row >= 0) & (row < self.h - 1)
        vals = np.full(len(en), np.nan)
        vals[ok] = map_coordinates(self.lrm, [row[ok], col[ok]], order=0)
        return vals

    def contrast(self, P, N, M, t):
        """Per-point ridge contrast (fit_plate's definition) for plate points P with plate-px normals N."""
        en = self.to_ground(P, M, t)
        n = np.stack([N[:, 0], -N[:, 1]], 1) @ np.linalg.inv(M)  # normals transform by M^-T
        n /= np.linalg.norm(n, axis=1, keepdims=True)
        on = self.relief_at(en)
        a = self.relief_at(en + n * self.side_m)
        b = self.relief_at(en - n * self.side_m)
        return on - np.maximum(a, b)

    def score(self, P, N, M, t, wts=None):
        c = self.contrast(P, N, M, t)
        good = np.isfinite(c)
        if good.mean() < 0.5:
            return -9.0
        if wts is None:
            return float(np.median(c[good]))
        return wmedian(c[good], wts[good])

    def null(self, P, N, s, n=1000, wts=None, seed=0):
        rng = np.random.default_rng(seed)
        out = []
        for _ in range(n):
            M = sim(s, rng.uniform(-math.pi, math.pi))
            t = np.array([rng.uniform(-self.W_m / 3, self.W_m / 3), rng.uniform(-self.H_m / 3, self.H_m / 3)])
            out.append(self.score(P, N, M, t, wts))
        out = np.array([v for v in out if v > -9])
        return out


def wmedian(x, w):
    o = np.argsort(x)
    cw = np.cumsum(w[o])
    return float(x[o][np.searchsorted(cw, cw[-1] / 2)])


def hand_template(S):
    """The hand-traced walls (plate crop px), sampled every 2 px with normals."""
    P, N = sample_walls(S.plate["walls"], normals=True)
    return P, N, np.ones(len(P))


# ---------------------------------------------------------------- coarse search: FFT over all shifts

K_BINS = 8          # normal-direction bins for the per-direction contrast images (22.5 deg)
CELL_M = 4.0        # coarse grid cell
ROT_STEP = math.radians(2.0)
LOGS_STEP = 0.04
NEG_FLOOR = -0.2    # contrast below this counts as this (junk lines in stream channels must not dominate)


def objective_values(c):
    return np.maximum(c, NEG_FLOOR)


class Coarse:
    """Per-direction contrast images on a coarse grid, padded, with their FFTs."""

    def __init__(self, S, ref, pad_m):
        import scipy.fft as sfft
        self.S, self.ref = S, np.asarray(ref, float)
        f = max(1, int(round(CELL_M / S.px_m)))
        self.f, self.g = f, f * S.px_m
        H, W = S.h // f * f, S.w // f * f
        self.pad = int(math.ceil(pad_m / self.g))
        hg, wg = H // f, W // f
        self.shape = (sfft.next_fast_len(hg + 2 * self.pad), sfft.next_fast_len(wg + 2 * self.pad, real=True))
        off = int(round(S.side_m / S.px_m))
        lrm = S.lrm
        self.FD, self.FV = [], []
        for k in range(K_BINS):
            phi = k * math.pi / K_BINS
            dc, dr = int(round(math.cos(phi) * off)), int(round(-math.sin(phi) * off))
            a, b = shifted(lrm, dr, dc), shifted(lrm, -dr, -dc)
            D = lrm - np.maximum(a, b)
            V = np.isfinite(D)
            D = np.where(V, objective_values(np.where(V, D, 0)), 0.0)
            Dg = D[:H, :W].reshape(hg, f, wg, f).sum((1, 3))
            Vg = V[:H, :W].reshape(hg, f, wg, f).sum((1, 3)).astype(float)
            for img, lst in ((Dg, self.FD), (Vg, self.FV)):
                P = np.zeros(self.shape)
                P[self.pad:self.pad + hg, self.pad:self.pad + wg] = img
                lst.append(sfft.rfft2(P, workers=-1))
        self.hg, self.wg = hg, wg

    def render(self, P, N, w, M):
        """Template under M with the plate centre at self.ref -> K grids of weights (padded frame)."""
        S = self.S
        en = S.to_ground(P, M, self.ref)
        n = np.stack([N[:, 0], -N[:, 1]], 1) @ np.linalg.inv(M)
        phi = np.mod(np.arctan2(n[:, 1], n[:, 0]), math.pi)
        kb = np.round(phi / (math.pi / K_BINS)).astype(int) % K_BINS
        col = np.floor((en[:, 0] + S.W_m / 2) / self.g).astype(int) + self.pad
        row = np.floor((S.H_m / 2 - en[:, 1]) / self.g).astype(int) + self.pad
        ok = (row >= 0) & (row < self.shape[0]) & (col >= 0) & (col < self.shape[1])
        T = np.zeros((K_BINS,) + self.shape)
        np.add.at(T, (kb[ok], row[ok], col[ok]), w[ok])
        return T, float(w.sum())

    def scores(self, P, N, w, M):
        """Mean objective over valid template points for every shift; returns (map, valid-fraction map).
        map[i, j] is the plate centre at ref + (j * g, -i * g) (indices wrap for negative shifts)."""
        import scipy.fft as sfft
        T, wsum = self.render(P, N, w, M)
        cd = np.zeros(self.shape[0] * (self.shape[1] // 2 + 1), complex).reshape(self.shape[0], -1)
        cv = np.zeros_like(cd)
        for k in range(K_BINS):
            FT = np.conj(sfft.rfft2(T[k], workers=-1))
            cd += FT * self.FD[k]
            cv += FT * self.FV[k]
        cD = sfft.irfft2(cd, s=self.shape, workers=-1)
        cV = sfft.irfft2(cv, s=self.shape, workers=-1)
        f2 = self.f * self.f
        frac = cV / f2 / max(wsum, 1e-9)
        with np.errstate(invalid="ignore", divide="ignore"):
            sc = np.where(frac >= 0.5, cD / np.maximum(cV, 1e-9), -9.0)
        return sc, frac


def shifted(img, dr, dc):
    """out[r, c] = img[r + dr, c + dc], NaN outside."""
    out = np.full_like(img, np.nan)
    h, w = img.shape
    r0, r1 = max(0, -dr), min(h, h - dr)
    c0, c1 = max(0, -dc), min(w, w - dc)
    out[r0:r1, c0:c1] = img[r0 + dr:r1 + dr, c0 + dc:c1 + dc]
    return out


def objective(S, P, N, M, t):
    c = S.contrast(P, N, M, t)
    good = np.isfinite(c)
    if good.mean() < 0.5:
        return -9.0
    return float(objective_values(c[good]).mean())


def refine(S, P, N, s, rot, t):
    """Pattern search on (log s, rot, tE, tN) with the exact point-sampled objective."""
    best = (objective(S, P, N, sim(s, rot), t), math.log(s), rot, t[0], t[1])
    for ds, dr, dt in [(0.02, math.radians(1.0), 4.0), (0.01, math.radians(0.5), 2.0), (0.005, math.radians(0.25), 1.0)]:
        for _ in range(8):
            cur = best
            for a in (-ds, 0, ds):
                for b in (-dr, 0, dr):
                    for cx in (-dt, 0, dt):
                        for cy in (-dt, 0, dt):
                            if a == b == cx == cy == 0:
                                continue
                            ls, r, x, y = cur[1] + a, cur[2] + b, cur[3] + cx, cur[4] + cy
                            v = objective(S, P, N, sim(math.exp(ls), r), np.array([x, y]))
                            if v > best[0]:
                                best = (v, ls, r, x, y)
            if best is cur:
                break
    v, ls, r, x, y = best
    return v, math.exp(ls), r, np.array([x, y])


def make_seeds():
    """8 seeds per site, drawn in SITES order: scale factor, rotation offset, disc radius, disc angle."""
    rng = np.random.default_rng(RNG_SEED)
    seeds = {}
    for sid in SITES:
        seeds[sid] = []
        for _ in range(N_SEEDS):
            k = rng.uniform(0.75, 1.25)
            dr = rng.uniform(-20, 20)
            rad = 150 * math.sqrt(rng.uniform())
            ang = rng.uniform(0, 2 * math.pi)
            seeds[sid].append(dict(scale_factor=k, rot_offset_deg=dr, centre_offset_m=[rad * math.cos(ang), rad * math.sin(ang)]))
    return seeds


def fit_site(S, P, N, w, seeds, n_refine=8, log=print):
    """Wide search for every seed of one site. The coarse FFT runs once over the union of the seed windows on
    an absolute (rotation, log-scale) grid; each seed then only looks inside its own window."""
    st = []
    for sd in seeds:
        st.append(dict(s=S.hand_s * sd["scale_factor"], rot=S.hand_rot + math.radians(sd["rot_offset_deg"]),
                       t=S.hand_t + np.array(sd["centre_offset_m"])))
    ref = np.mean([x["t"] for x in st], 0)
    pad = max(np.abs(x["t"] - ref).max() for x in st) + WIN_T + 4 * CELL_M
    C = Coarse(S, ref, pad)
    rots = np.arange(math.floor((min(x["rot"] for x in st) - WIN_ROT) / ROT_STEP),
                     math.ceil((max(x["rot"] for x in st) + WIN_ROT) / ROT_STEP) + 1) * ROT_STEP
    lss = np.arange(math.floor((math.log(min(x["s"] for x in st)) + WIN_LOGS[0]) / LOGS_STEP),
                    math.ceil((math.log(max(x["s"] for x in st)) + WIN_LOGS[1]) / LOGS_STEP) + 1) * LOGS_STEP
    cands = [[] for _ in st]
    H0, W0 = C.shape
    ii = np.arange(H0); ii = np.where(ii > H0 // 2, ii - H0, ii)
    jj = np.arange(W0); jj = np.where(jj > W0 // 2, jj - W0, jj)
    dE = jj * C.g  # plate centre east of ref
    dN = -ii * C.g
    t0 = time.time()
    from scipy.ndimage import maximum_filter
    for rot in rots:
        users_r = [i for i, x in enumerate(st) if abs(rot - x["rot"]) <= WIN_ROT + 1e-9]
        if not users_r:
            continue
        for ls in lss:
            users = [i for i in users_r if WIN_LOGS[0] - 1e-9 <= ls - math.log(st[i]["s"]) <= WIN_LOGS[1] + 1e-9]
            if not users:
                continue
            sc, _ = C.scores(P, N, w, sim(math.exp(ls), rot))
            peak = (sc == maximum_filter(sc, size=5, mode="wrap")) & (sc > -9)
            for i in users:
                okE = np.abs(ref[0] + dE - st[i]["t"][0]) <= WIN_T
                okN = np.abs(ref[1] + dN - st[i]["t"][1]) <= WIN_T
                m = peak & okN[:, None] & okE[None, :]
                vals = np.where(m, sc, -np.inf).ravel()
                top = np.argpartition(vals, -3)[-3:]
                for q in top:
                    if np.isfinite(vals[q]):
                        r_, c_ = divmod(int(q), W0)
                        cands[i].append((float(vals[q]), math.exp(ls), float(rot), ref + np.array([dE[c_], dN[r_]])))
    log("  coarse: %d rotations x %d scales, %.0fs" % (len(rots), len(lss), time.time() - t0))
    out = []
    for i, x in enumerate(st):
        cs = sorted(cands[i], key=lambda c: -c[0])
        keep = []
        for c in cs:
            if all(abs(c[2] - k[2]) > math.radians(4) or abs(math.log(c[1] / k[1])) > 0.08 or
                   np.hypot(*(c[3] - k[3])) > 30 for k in keep):
                keep.append(c)
            if len(keep) >= n_refine:
                break
        best = None
        for c in keep:
            r = refine(S, P, N, c[1], c[2], c[3])
            if best is None or r[0] > best[0]:
                best = r + (c[0],)
        if best is None:  # no valid placement anywhere in the window: record a non-fit at the seed
            best = (-9.0, x["s"], x["rot"], x["t"], -9.0)
        v, s, rot, t, coarse_v = best
        out.append(dict(seed=x, obj=v, coarse_obj=coarse_v, s=s, rot=rot, t=t, top_coarse=[(c[0], c[1], math.degrees(c[2]), c[3].tolist()) for c in keep]))
    return out


def evaluate(S, P, N, r, null_cache):
    M = sim(r["s"], r["rot"])
    rms = S.corner_rms(M, r["t"])
    drot = math.degrees((r["rot"] - S.hand_rot + math.pi) % (2 * math.pi) - math.pi)
    med = S.score(P, N, M, r["t"])
    key = round(r["s"], 4)
    if key not in null_cache:
        null_cache[key] = S.null(P, N, r["s"], n=1000)
    nl = null_cache[key]
    # too few valid random placements (newark: 42% of the box is masked, the plate fills most of it):
    # the null is undefined and criterion 3 cannot pass
    p99 = float(np.percentile(nl, 99)) if len(nl) >= 100 else float("nan")
    ok = (rms <= S.tol_m, abs(drot) <= 2.0, bool(med > p99))
    return dict(corner_rms_m=round(rms, 1), drot_deg=round(drot, 2), scale_ratio=round(r["s"] / S.hand_s, 4),
                median_contrast_m=round(med, 3), null_p99_m=round(p99, 3), null_valid=int(len(nl)), objective=round(r["obj"], 4),
                coarse_objective=round(r["coarse_obj"], 4), pass_rms=ok[0], pass_rot=ok[1], pass_null=ok[2],
                passed=all(ok))


def load_template(S, kind):
    if kind == "hand":
        return hand_template(S)
    z = np.load(os.path.join(OUT, S.id + {"auto": "_template.npz", "auto_noqwen": "_template_noqwen.npz", "auto_qwenpieces": "_template_qwenpieces.npz"}[kind]))
    return z["pts"], z["nrm"], z["w"]


def run(tag, kind, sites):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "results_%s.json" % tag)
    res = json.load(open(path)) if os.path.exists(path) else {"tag": tag, "template": kind, "sites": {}}
    seeds = make_seeds()
    for sid in sites:
        t0 = time.time()
        S = Site(sid)
        P, N, w = load_template(S, kind)
        print("%s: %d template points, tol %.1f m" % (sid, len(P), S.tol_m))
        fits = fit_site(S, P, N, w, seeds[sid])
        null_cache = {}
        rows = []
        for i, r in enumerate(fits):
            e = evaluate(S, P, N, r, null_cache)
            e.update(seed=i, s=r["s"], rot_deg=math.degrees(r["rot"]), t=r["t"].tolist(),
                     seed_s=r["seed"]["s"], seed_rot_deg=math.degrees(r["seed"]["rot"]), seed_t=r["seed"]["t"].tolist(),
                     seed_corner_rms_m=round(S.corner_rms(sim(r["seed"]["s"], r["seed"]["rot"]), r["seed"]["t"]), 1),
                     top_coarse=r["top_coarse"])
            rows.append(e)
            print("  seed %d: seed rms %5.0f m -> rms %6.1f m, drot %+6.2f, scale x%.3f, median %.3f (p99 %.3f) %s" % (
                i, e["seed_corner_rms_m"], e["corner_rms_m"], e["drot_deg"], e["scale_ratio"], e["median_contrast_m"],
                e["null_p99_m"], "PASS" if e["passed"] else "fail"))
        hand_med = S.score(*hand_template(S)[:2], S.hand_M, S.hand_t)
        auto_at_hand = S.score(P, N, S.hand_M, S.hand_t)
        res["sites"][sid] = dict(tol_m=round(S.tol_m, 1), n_points=int(len(P)), seeds=rows,
                                 n_pass=int(sum(r["passed"] for r in rows)),
                                 template_median_at_hand_fit=round(auto_at_hand, 3),
                                 template_objective_at_hand_fit=round(objective(S, P, N, S.hand_M, S.hand_t), 4),
                                 hand_walls_median_at_hand_fit=round(hand_med, 3), seconds=round(time.time() - t0))
        print("  %s: %d/%d seeds pass, %.0fs" % (sid, res["sites"][sid]["n_pass"], len(rows), time.time() - t0))
        json.dump(res, open(path, "w"), indent=1, default=lambda o: bool(o) if isinstance(o, np.bool_) else float(o))
    return res


def check():
    """The scorer must reproduce fit_plate's stored ridge contrast at the hand fit (similarity sites)."""
    for sid in ["fudge", "forthill", "highbank", "hopeton", "newark"]:
        S = Site(sid)
        P, N, _ = hand_template(S)
        sc = S.score(P, N, S.hand_M, S.hand_t)
        print("%-9s scorer %.3f   stored ridge_contrast_m %.3f  (%s)" % (
            sid, sc, S.plate["fit"]["ridge_contrast_m"], S.plate["fit"].get("model", "warp" if S.plate.get("warp") else "similarity")))


if __name__ == "__main__":
    if sys.argv[1] == "check":
        check()
    elif sys.argv[1] == "run":
        run(sys.argv[2], sys.argv[3], sys.argv[4:] or SITES)
