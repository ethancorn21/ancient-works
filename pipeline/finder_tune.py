"""Tuning data for the Finder (tune positives only; never the held-out areas).

usage:
  finder_tune.py extras     detector output around every labelled extra positive -> data/finder/tune/extras_det.json
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from finder_common import FD, hav_m  # noqa: E402
import finder_testset as ts  # noqa: E402

TD = os.path.join(FD, "tune")


def extra_labels():
    lab = {k: v for k, v in json.load(open(os.path.join(FD, "extra_labels.json"))).items() if not k.startswith("_")}
    out = []
    for r in ts.extras():
        l = lab[r["pid"]]
        l = l if isinstance(l, dict) else {"vis": l}
        out.append({**r, **l})
    return out


def extras_det():
    from finder_scan import point_detect
    os.makedirs(TD, exist_ok=True)
    out = []
    for r in extra_labels():
        if r["vis"] not in ("visible", "faint"):
            continue
        dets = point_detect(r["lon"], r["lat"])
        near = [dict(d, dist_m=round(hav_m(r["lon"], r["lat"], d["lon"], d["lat"]), 1)) for d in dets]
        near = [d for d in near if d["dist_m"] <= 150]
        out.append({**r, "dets": sorted(near, key=lambda d: d["dist_m"])})
        best = min(near, key=lambda d: d["dist_m"]) if near else None
        print(f"{r['pid']} {r['kind']:9s} {r['vis']:7s} {r['name'][:30]:30s} "
              + (f"nearest det {best['dist_m']:.0f} m score {best['score']:.2f} h {best['h_m']} d {best['diam_m']} "
                 f"round {best['round']} slope {best['base_slope']}" if best else "no det within 150 m"), flush=True)
    json.dump(out, open(os.path.join(TD, "extras_det.json"), "w"))




# ---------------------------------------------------------------- mound ranking model (tune data only)

FEATS_ALL = ("log_score", "log_snr", "log_slope", "elong", "round", "flat_top", "log_diam")
FEATS = tuple(os.environ.get("MOUND_FEATS", ",".join(FEATS_ALL)).split(","))


def feats(m, names=None):
    v = {"log_score": math.log(max(m["score"], 0.05)), "log_snr": math.log(max(m["snr"], 0.1)),
         "log_slope": math.log(0.5 + max(m["base_slope"], 0)), "elong": m["elong"], "round": m["round"],
         "flat_top": m["flat_top"], "log_diam": math.log(max(m["diam_m"], 4))}
    return [v[k] for k in (names or FEATS)]


def logreg(X, y, w, lam=1.0, iters=50):
    """L2-regularised logistic regression by Newton steps (intercept not penalised)."""
    import numpy as np
    n, d = X.shape
    A = np.hstack([np.ones((n, 1)), X])
    b = np.zeros(d + 1)
    R = lam * np.eye(d + 1)
    R[0, 0] = 0
    for _ in range(iters):
        p = 1 / (1 + np.exp(-A @ b))
        g = A.T @ (w * (p - y)) + R @ b
        H = (A * (w * p * (1 - p))[:, None]).T @ A + R
        step = np.linalg.solve(H, g)
        b -= step
        if np.abs(step).max() < 1e-6:
            break
    return b


def tune_positives_and_background():
    from finder_eval import MOUND_TOL, counted, positives
    from finder_rank import detections
    ms, _ = detections("ross")
    pos = [p for p in positives("ross") if counted(p) and p["kind"] == "mound"]
    P, names = [], []
    for p in pos:
        near = [m for m in ms if hav_m(m["lon"], m["lat"], p["lon"], p["lat"]) <= MOUND_TOL]
        P.append(max(near, key=lambda m: m["score"]) if near else None)
        names.append(p["name"])
    for e in json.load(open(os.path.join(TD, "extras_det.json"))):
        if e["kind"] != "mound":
            continue
        near = [d for d in e["dets"] if d["dist_m"] <= MOUND_TOL]
        P.append(max(near, key=lambda d: d["score"]) if near else None)
        names.append(e["name"])
    allp = positives("ross")
    B = [m for m in ms if not any(hav_m(m["lon"], m["lat"], p["lon"], p["lat"]) < 150 for p in allp)]
    return P, names, B


def fit_mound_model(lam=None, out_name="mound_model.json"):
    lam = float(os.environ.get("LAM", 3.0)) if lam is None else lam
    import numpy as np
    from finder_common import AREAS, area_km2
    P, names, B = tune_positives_and_background()
    Pv = [p for p in P if p is not None]
    Xp, Xb = np.array([feats(p) for p in Pv]), np.array([feats(m) for m in B])
    X = np.vstack([Xp, Xb])
    mu, sd = X.mean(0), X.std(0) + 1e-9
    Z = (X - mu) / sd
    y = np.r_[np.ones(len(Xp)), np.zeros(len(Xb))]
    w = np.r_[np.full(len(Xp), len(Xb) / len(Xp)), np.ones(len(Xb))]
    km2 = area_km2(AREAS["ross"])

    def kequiv(b, zi):
        sb = np.sort(np.hstack([np.ones((len(Xb), 1)), (Xb - mu) / sd]) @ b)[::-1]
        s = np.r_[1, zi] @ b
        return (sb > s).sum() * 100 / km2

    full = logreg(Z, y, w, lam)
    loo = []
    for i in range(len(Xp)):
        keep = np.ones(len(y), bool)
        keep[i] = False
        b = logreg(Z[keep], y[keep], w[keep], lam)
        loo.append(kequiv(b, Z[i]))
    loo = np.array(loo + [np.inf] * (len(P) - len(Pv)))
    res = {"feats": FEATS, "mu": mu.tolist(), "sd": sd.tolist(), "coef": full.tolist(), "lam": lam,
           "n_pos": len(Pv), "n_pos_total": len(P), "n_bg": len(Xb),
           "loo_recall": {k: round(float(np.mean(loo < k)), 3) for k in (5, 10, 20, 50)},
           "loo_kequiv": {n: (None if not np.isfinite(v) else round(float(v), 1)) for n, v in zip([n for n, p in zip(names, P) if p is not None] + [n for n, p in zip(names, P) if p is None], loo)}}
    json.dump(res, open(os.path.join(TD, os.environ.get("OUT", out_name)), "w"), indent=1)
    print("coef (standardised):", dict(zip(("intercept",) + FEATS, np.round(full, 2))))
    print("LOO recall (k per 100 km2, all", len(P), "tune mounds):", res["loo_recall"])
    return res


if __name__ == "__main__":
    {"extras": extras_det, "mound_model": fit_mound_model}[sys.argv[1]]()
