"""Finder evaluation: recall@k per 100 km2, precision_known@k, terrain-matched random baseline (docs/finder.md s.1).

usage:
  finder_eval.py tune [ranker]          tune area (ross) only; prints everything
  finder_eval.py final [ranker]         held-out areas, once: writes data/finder/eval/final_<stamp>.json
Held-out areas print only aggregate numbers, and only in `final` mode.
"""
import datetime
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from finder_common import AREAS, FD, area_km2, load_jsonl, local_xy, wilson  # noqa: E402

KS = (5, 10, 20, 50)
MOUND_TOL = 40.0


def positives(area):
    return [p for p in load_jsonl(os.path.join(FD, "positives.jsonl")) if p["area"] == area]


def counted(p):
    return p["vis"] in ("visible", "faint") and p["kind"] in ("mound", "enclosure")


def hits(points, cands, kinds_for_encl=("ring", "enclosure")):
    """For each point, the best (lowest) rank of a candidate that hits it under the gate tolerance; inf if none.
    points: dicts with lon, lat, kind, r_m. cands: ranked list (index = rank) with lon, lat, kind."""
    if not cands:
        return np.full(len(points), np.inf)
    lon0, lat0 = points[0]["lon"], points[0]["lat"]
    cx, cy = local_xy([c["lon"] for c in cands], [c["lat"] for c in cands], lon0, lat0)
    kinds = np.array([c["kind"] for c in cands])
    is_ring = np.isin(kinds, kinds_for_encl)
    ranks = np.arange(len(cands))
    out = []
    for p in points:
        px, py = local_xy([p["lon"]], [p["lat"]], lon0, lat0)
        d = np.hypot(cx - px[0], cy - py[0])
        if p["kind"] == "enclosure":
            m = (d <= max(60.0, 0.5 * (p.get("r_m") or 0))) & is_ring
        else:
            m = d <= MOUND_TOL
        out.append(ranks[m].min() if m.any() else np.inf)
    return np.array(out, float)


def baseline(area, cands, weights_by_terrain, n_max=3000):
    """Share of terrain-matched random points that a top-K list hits (mound tolerance), for each k."""
    rs = load_jsonl(os.path.join(FD, f"randoms_{area}.jsonl"))[:n_max]
    if not rs:
        return None
    pts = [{"lon": r["lon"], "lat": r["lat"], "kind": "mound"} for r in rs]
    h = hits(pts, cands)
    w = np.array([weights_by_terrain.get(r["terrain"], 0.0) for r in rs])
    w = w / w.sum()
    km2 = area_km2(AREAS[area])
    return {k: float((w * (h < round(k * km2 / 100))).sum()) for k in KS}


def terrain_weights(area, pts):
    """Weights that make the random points' valley / upland mix match the positives'."""
    from finder_scan import AreaScan
    sc = AreaScan(area)
    t = [sc.terrain_at(p["lon"], p["lat"]) for p in pts]
    t = [x[0] for x in t if x]
    rs = load_jsonl(os.path.join(FD, f"randoms_{area}.jsonl"))
    if not t or not rs:
        return {"valley": 1.0, "upland": 1.0}
    pv = sum(x == "valley" for x in t) / len(t)
    rv = sum(r["terrain"] == "valley" for r in rs) / len(rs)
    return {"valley": pv / max(rv, 1e-6), "upland": (1 - pv) / max(1 - rv, 1e-6)}, pv


def evaluate_area(area, cands):
    """cands: final ranked list for the area. Returns per-kind recall@k etc."""
    km2 = area_km2(AREAS[area])
    pos = [p for p in positives(area) if counted(p)]
    res = {"area": area, "km2": round(km2, 1), "n_cands": len(cands)}
    h_all = hits(pos, cands) if pos else np.array([])
    for kind in ("mound", "enclosure"):
        idx = [i for i, p in enumerate(pos) if p["kind"] == kind]
        hk = h_all[idx] if idx else np.array([])
        res[kind] = {"n": len(idx), "ranks_per100km2": [None if not np.isfinite(r) else round(r * 100 / km2, 1) for r in hk]}
        for k in KS:
            K = round(k * km2 / 100)
            res[kind][f"hit@{k}"] = int((hk < K).sum())
    # precision_known: share of the top K that hit any known positive (all labels, kinds 'other' too; lower bound)
    allpos = [p for p in positives(area) if p["vis"] in ("visible", "faint")]
    res["precision_known"] = {}
    if allpos:
        lon0, lat0 = allpos[0]["lon"], allpos[0]["lat"]
        px, py = local_xy([p["lon"] for p in allpos], [p["lat"] for p in allpos], lon0, lat0)
        tol = np.array([MOUND_TOL if p["kind"] != "enclosure" else max(60.0, 0.5 * (p.get("r_m") or 0)) for p in allpos])
        for k in KS:
            K = round(k * km2 / 100)
            top = cands[:K]
            if not top:
                continue
            cx, cy = local_xy([c["lon"] for c in top], [c["lat"] for c in top], lon0, lat0)
            d = np.hypot(cx[:, None] - px[None], cy[:, None] - py[None])
            res["precision_known"][k] = round(float((d <= tol[None]).any(1).mean()), 3)
    if pos:
        tw = terrain_weights(area, pos)
        if isinstance(tw, tuple):
            w, pv = tw
            res["valley_share_of_positives"] = round(pv, 2)
            res["baseline_hit"] = baseline(area, cands, w)
    return res


def pool(results):
    out = {}
    for kind in ("mound", "enclosure"):
        n = sum(r[kind]["n"] for r in results)
        d = {"n": n}
        for k in KS:
            h = sum(r[kind][f"hit@{k}"] for r in results)
            d[f"recall@{k}"] = round(h / n, 3) if n else None
            d[f"ci@{k}"] = wilson(h, n)
        out[kind] = d
    # baseline pooled by area size
    bs = [(r["km2"], r.get("baseline_hit")) for r in results if r.get("baseline_hit")]
    if bs:
        tot = sum(a for a, _ in bs)
        out["baseline_hit"] = {k: round(sum(a * b[k] for a, b in bs) / tot, 4) for k in KS}
        for kind in ("mound", "enclosure"):
            for k in KS:
                rc, b = out[kind][f"recall@{k}"], out["baseline_hit"][k]
                out[kind][f"enrich@{k}"] = round(rc / b, 1) if rc is not None and b > 0 else None
    return out


def gate(pooled):
    m, e = pooled["mound"], pooled["enclosure"]
    g1 = ("not measurable" if m["n"] < 15 else
          "pass" if (m["recall@20"] >= 0.60 and (m.get("enrich@20") or 0) >= 10) else "fail")
    g2 = "not measurable" if e["n"] < 15 else ("pass" if e["recall@20"] >= 0.50 else "fail")
    return {"G1_mounds": g1, "G2_enclosures": g2}


def heldout_auc(areas, cfg="s150j"):
    """G3: Clef p for detections that hit held-out mound positives vs hard negatives (top RERANK_PER100 per 100 km2
    that hit no known record). Positives are taken from the full detector list (any rank), nearest hit."""
    import finder_rank as fr
    import finder_rerank as rr
    from finder_export import record_tol, records
    recs = records()
    P, N = [], []
    for a in areas:
        cands = fr.ranked(a, "detector")
        km2 = area_km2(AREAS[a])
        K = round(fr.RERANK_PER100 * km2 / 100)
        pos = [p for p in positives(a) if counted(p) and p["kind"] == "mound"]
        h = hits(pos, cands)
        used = set()
        for r in h:
            if np.isfinite(r):
                P.append(cands[int(r)])
                used.add(int(r))
        lon0, lat0 = cands[0]["lon"], cands[0]["lat"]
        rx, ry = local_xy([r["lon"] for r in recs], [r["lat"] for r in recs], lon0, lat0)
        rt = np.array([max(150.0, record_tol(r)) for r in recs])
        for i, c in enumerate(cands[:K]):
            if i in used or c["kind"] != "mound":
                continue
            cx, cy = local_xy([c["lon"]], [c["lat"]], lon0, lat0)
            if not (np.hypot(rx - cx[0], ry - cy[0]) <= rt).any():
                N.append(c)
    sp, sn = rr.score(P, cfg), rr.score(N, cfg)
    return {"auc": round(rr.auc(sp, sn), 3), "n_pos": len(P), "n_neg": len(N)}


def run(mode, ranker="detector"):
    import finder_rank as fr
    areas = [a for a, v in AREAS.items() if v[4] == ("tune" if mode == "tune" else "heldout")]
    results = []
    for a in areas:
        cands = fr.ranked(a, ranker)
        results.append(evaluate_area(a, cands))
    pooled = pool(results)
    out = {"mode": mode, "ranker": ranker, "pooled": pooled, "gate": gate(pooled),
           "when": datetime.datetime.now().isoformat(timespec="seconds")}
    if ranker == "clef":
        out["g3_auc"] = heldout_auc(areas)
    if mode == "tune":
        out["areas"] = results
        print(json.dumps(out, indent=1))
    else:
        # aggregate only: per-area counts, no ranks, no coordinates
        out["areas"] = [{"area": r["area"], "km2": r["km2"], "n_cands": r["n_cands"],
                         **{kd: {kk: vv for kk, vv in r[kd].items() if kk != "ranks_per100km2"} for kd in ("mound", "enclosure")},
                         "precision_known": r["precision_known"], "baseline_hit": r.get("baseline_hit")} for r in results]
        os.makedirs(os.path.join(FD, "eval"), exist_ok=True)
        p = os.path.join(FD, "eval", f"final_{ranker}_{datetime.datetime.now():%Y%m%d_%H%M%S}.json")
        json.dump(out, open(p, "w"), indent=1)
        print(json.dumps({"pooled": pooled, "gate": out["gate"]}, indent=1))
        print("wrote", p)
    return out


def mills_enrichment(area, county, cands, ks=KS):
    """Share of the top K candidates inside the error radius of a Mills 1914 symbol, vs the same share for random
    points weighted to the candidates' valley / upland mix. Mound-type symbols (as for the 'lost' class)."""
    from finder_scan import AreaScan
    from finder_export import MILLS_FOR
    mills = [m for m in load_jsonl(os.path.join(FD, f"mills_1914_{county}.jsonl")) if m["type"] in MILLS_FOR["mound"]]
    rs = load_jsonl(os.path.join(FD, f"randoms_{area}.jsonl"))
    import finder_rank as fr
    km2 = area_km2(AREAS[area]) if area in AREAS else fr.scanned_km2(area)
    lon0, lat0 = rs[0]["lon"], rs[0]["lat"]
    mx, my = local_xy([m["lon"] for m in mills], [m["lat"] for m in mills], lon0, lat0)
    me = np.array([m["err_m"] for m in mills])

    def near(pts):
        px, py = local_xy([p["lon"] for p in pts], [p["lat"] for p in pts], lon0, lat0)
        return (np.hypot(px[:, None] - mx[None], py[:, None] - my[None]) <= me[None]).any(1)

    rn = near(rs)
    rv = np.array([r["terrain"] == "valley" for r in rs])
    sc = AreaScan(area)
    out = {}
    for k in ks:
        K = round(k * km2 / 100)
        top = cands[:K]
        cn = near(top)
        t = [sc.terrain_at(c["lon"], c["lat"]) for c in top]
        pv = np.mean([x is not None and x[0] == "valley" for x in t])
        base = pv * rn[rv].mean() + (1 - pv) * rn[~rv].mean()
        out[k] = {"cand_share": round(float(cn.mean()), 3), "random_share": round(float(base), 3),
                  "enrichment": round(float(cn.mean() / base), 2) if base else None, "valley_share": round(float(pv), 2)}
    return out


if __name__ == "__main__":
    run(sys.argv[1], *(sys.argv[2:3]))
