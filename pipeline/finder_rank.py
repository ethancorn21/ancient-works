"""Finder ranking: per-kind scores, fusion of mounds and rings into one list, optional re-ranker on top.

ranked(area, ranker) -> final ordered candidate list for an area (dicts with lon, lat, kind, score, measurements)
  ranker = "raw"       mounds by detector score (m), rings by snr; fused by quota
           "detector"  tuned scores (mound_score, ring_score below; chosen on the tune area); fused by quota
           "clef"      "detector" list, top RERANK_PER100 per 100 km2 re-ordered by the mean of the detector rank
                       and the Clef-flash rank (config s150j; data/finder/rerank/<area>.json, finder_rerank.py)
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from finder_common import AREAS, FD, area_km2  # noqa: E402

RING_SHARE = 0.2      # share of each top-K given to ring candidates (tuned on ross; see docs/finder.md)
RING_MIN_R = 60.0     # rings smaller than this are not ranked (small natural rings flood the list)
RERANK_PER100 = 50    # candidates per 100 km2 sent to the re-ranker


def mound_score_raw(m):
    return m["score"]


_MODEL = None


def mound_score(m):
    """Logistic model fitted on the tune area (finder_tune.py mound_model): log height prominence, log snr,
    log base slope, elongation, roundness, top flatness, log diameter. Falls back to mound_score_v1."""
    global _MODEL
    if _MODEL is None:
        p = os.path.join(FD, "tune", "mound_model.json")
        _MODEL = json.load(open(p)) if os.path.exists(p) else {}
    if not _MODEL:
        return mound_score_v1(m)
    from finder_tune import feats
    z = [(f - mu) / sd for f, mu, sd in zip(feats(m, _MODEL["feats"]), _MODEL["mu"], _MODEL["sd"])]
    return _MODEL["coef"][0] + sum(c * v for c, v in zip(_MODEL["coef"][1:], z))


def mound_score_v1(m):
    """Height prominence, damped above 3 m (natural knolls are often taller than mounds), times shape and
    setting terms: round outlines, low base slope (mounds sit on level ground far more often than knolls do)."""
    s = 3.0 * math.tanh(m["score"] / 3.0)
    s *= min(1.0, m["round"] / 0.6) ** 1.0
    s *= math.exp(-max(m["base_slope"], 0.0) / 4.0)
    s *= min(1.0, m["snr"] / 4.0) ** 0.5
    return s


def ring_score_raw(r):
    return r["snr"]


def ring_score(r):
    """snr, damped on tilted ground (geometric works sit on level terraces); rings under RING_MIN_R dropped."""
    return r["snr"] * math.exp(-max(r.get("band_slope", 0.0), 0.0) / 2.0) if r["r_m"] >= RING_MIN_R else -1.0


def fuse(ms, rs, ring_share=RING_SHARE):
    """Interleave the two sorted lists so that each prefix holds about ring_share rings."""
    out, i, j = [], 0, 0
    while i < len(ms) or j < len(rs):
        take_ring = j < len(rs) and (i >= len(ms) or j < ring_share * (len(out) + 1))
        if take_ring:
            out.append(rs[j])
            j += 1
        else:
            out.append(ms[i])
            i += 1
    return out


def detections(area):
    from finder_scan import AreaScan
    return AreaScan(area).candidates()


def ranked(area, ranker="detector", ring_share=RING_SHARE, mfun=None, rfun=None):
    ms, rs = detections(area)
    if ranker == "raw":
        mf, rf = mound_score_raw, ring_score_raw
    else:
        mf, rf = mound_score, ring_score
    mf, rf = mfun or mf, rfun or rf
    M = [dict(m, kind="mound", rank_score=round(mf(m), 4)) for m in ms]
    R = [dict(r, kind="ring", rank_score=round(rf(r), 4)) for r in rs]
    R = [r for r in R if r["rank_score"] > 0]
    M.sort(key=lambda c: -c["rank_score"])
    R.sort(key=lambda c: -c["rank_score"])
    out = fuse(M, R, ring_share)
    if ranker == "clef":
        p = os.path.join(FD, "rerank", f"{area}.json")
        probs = json.load(open(p))["p"] if os.path.exists(p) else {}
        N = round(RERANK_PER100 * scanned_km2(area) / 100)
        head, tail = out[:N], out[N:]
        for i, c in enumerate(head):
            c["p_reranker"] = probs.get(cand_key(c))
            c["det_rank"] = i
        # rank blend (chosen on tune, docs/finder.md): mean of detector rank and Clef rank inside the head
        by_p = sorted(range(len(head)), key=lambda i: -(head[i]["p_reranker"] if head[i]["p_reranker"] is not None else -1))
        crank = {i: r for r, i in enumerate(by_p)}
        order = sorted(range(len(head)), key=lambda i: ((head[i]["det_rank"] + crank[i]) / 2.0, head[i]["det_rank"]))
        head = [head[i] for i in order]
        out = head + tail
    return out


def scanned_km2(area):
    if area in AREAS:
        return area_km2(AREAS[area])
    from finder_scan import AreaScan
    return AreaScan(area).km2()


def cand_key(c):
    return f"{c['kind'][0]}{c['lon']:.6f},{c['lat']:.6f}"
