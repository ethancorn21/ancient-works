"""Finder re-ranker: Cloudflare Clef-flash (decision model on the AI box, 127.0.0.1:18083) scores relief crops.

Every crop, positive or negative, is centred on a DETECTOR position (never on a published coordinate), drawn by the
same renderer at 1 m/px with a fixed stretch, so framing cannot leak the label.

Configs (chosen on the tune set only):
  view    relief_s (5 m local relief, clip 0.4 m) | relief_m (15 m, clip 0.6 m)
  half    crop half-width in metres for mounds (rings: max(half, 1.6 r))
  meas    True: the detector's measurements go into the state as JSON
One batch of 6 in flight at a time (the server is one process on a 16 GB card).

usage:
  finder_rerank.py tune                 build the tune set (ross + extras) and score it under each config -> AUCs
  finder_rerank.py area <area> <config> score the top RERANK_PER100 per 100 km2 of an area -> data/finder/rerank/<area>.json
"""
import io
import json
import math
import os
import sys
import time

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import clef  # noqa: E402
from finder_common import AREAS, FD, area_km2, dem_crop, hav_m, load_jsonl  # noqa: E402

RD = os.path.join(FD, "rerank")
CONFIGS = {
    "s150": {"view": "relief_s", "half": 150, "meas": False},
    "m150": {"view": "relief_m", "half": 150, "meas": False},
    "m300": {"view": "relief_m", "half": 300, "meas": False},
    "s150j": {"view": "relief_s", "half": 150, "meas": True},
}
CLIP = {"relief_s": (5.0, 0.4), "relief_m": (15.0, 0.6)}
STATE = ("A LiDAR bare-earth elevation model of farmland and woods in southern Ohio, drawn as local relief: ground "
         "higher than its surroundings is light, lower is dark. The image is {w} m across, north up. A detector "
         "flagged the {what} at the centre.")
QUESTION = {"earthwork": {"type": "noul", "instructions":
            "Is the feature at the centre of the image an ancient earthwork built by people (a burial mound, or the "
            "wall or ditch of an enclosure such as a circle or square), rather than a natural landform (knoll, river "
            "terrace, meander scar, sinkhole, tree throw) or a modern feature (building pad, farm pond, road, spoil "
            "heap, silo base)?"}}


def render(lon, lat, view, half):
    from scipy.ndimage import gaussian_filter
    import aw
    z, _ = dem_crop(lon, lat, half)
    z = aw.fill_nan(z.astype(np.float64))
    r, clip = CLIP[view]
    rel = z - gaussian_filter(z, r)
    g = ((np.clip(rel / clip, -1, 1) * 0.5 + 0.5) * 255).astype(np.uint8)
    return Image.fromarray(g).convert("RGB")


def describe(c):
    if c["kind"] == "mound":
        return "rounded rise"
    return f"ring about {2 * c['r_m']:.0f} m across"


def meas_json(c):
    keys = ("h_m", "diam_m", "round", "elong", "flat_top", "snr", "base_slope") if c["kind"] == "mound" else \
        ("r_m", "score_m", "snr", "sectors", "band_slope")
    return json.dumps({k: c[k] for k in keys if k in c})


def half_for(c, half):
    return half if c["kind"] == "mound" else max(half, 1.6 * c["r_m"])


def score(cands, cfg_name, cache_name=None, batch=6):
    """p(earthwork) for each candidate (dicts with lon, lat, kind, ...). Cached per config."""
    cfg = CONFIGS[cfg_name]
    os.makedirs(RD, exist_ok=True)
    cp = os.path.join(RD, f"cache_{cache_name or cfg_name}.jsonl")
    cache = {}
    for r in load_jsonl(cp):
        cache[r["key"]] = r["p"]
    todo = [c for c in cands if key(c) not in cache]
    t0 = time.time()
    with open(cp, "a") as f:
        for i in range(0, len(todo), batch):
            chunk = todo[i:i + batch]
            items = []
            for c in chunk:
                h = half_for(c, cfg["half"])
                im = render(c["lon"], c["lat"], cfg["view"], h)
                st = STATE.format(w=int(2 * h), what=describe(c))
                if cfg["meas"]:
                    st += " Detector measurements: " + meas_json(c)
                items.append((st, QUESTION, [im]))
            for tries in range(4):
                try:
                    ans = clef.decide_batch(items)
                    break
                except Exception as e:  # server busy or restarting; back off, never pile up requests
                    if tries == 3:
                        raise
                    print("  clef retry", e, flush=True)
                    time.sleep(15 * (tries + 1))
            for c, a in zip(chunk, ans):
                p = float(a["earthwork"]["noul"])
                cache[key(c)] = p
                f.write(json.dumps({"key": key(c), "p": p}) + "\n")
            f.flush()
            if (i // batch) % 10 == 0:
                print(f"  {cfg_name}: {i + len(chunk)}/{len(todo)} in {time.time() - t0:.0f}s", flush=True)
    return [cache[key(c)] for c in cands]


def key(c):
    return f"{c['kind'][0]}{c['lon']:.6f},{c['lat']:.6f}"


def auc(pos, neg):
    pos, neg = np.asarray(pos), np.asarray(neg)
    if not len(pos) or not len(neg):
        return float("nan")
    gt = (pos[:, None] > neg[None]).mean()
    eq = (pos[:, None] == neg[None]).mean()
    return float(gt + 0.5 * eq)


def tune_set():
    """Positives: detections that hit tune positives (ross area + extras). Hard negatives: the detector's top
    candidates in ross (top 50 per 100 km2) that hit no known positive."""
    import finder_rank as fr
    from finder_eval import MOUND_TOL, counted, hits, positives
    from finder_tune import TD
    cands = fr.ranked("ross", "detector", ring_share=float(os.environ.get("RING_SHARE", fr.RING_SHARE)))
    km2 = area_km2(AREAS["ross"])
    N = round(fr.RERANK_PER100 * km2 / 100)
    pos_pts = [p for p in positives("ross") if counted(p)]
    h = hits(pos_pts, cands)
    P, used = [], set()
    for p, r in zip(pos_pts, h):
        if np.isfinite(r):
            c = cands[int(r)]
            P.append(dict(c, src=p["name"]))
            used.add(int(r))
        else:  # not in the list at all: take the nearest detection of the right kind, if within tolerance x 2
            pool = [c for c in cands if (c["kind"] == "mound") == (p["kind"] == "mound")]
            near = min(pool, key=lambda c: hav_m(c["lon"], c["lat"], p["lon"], p["lat"]), default=None)
            if near and hav_m(near["lon"], near["lat"], p["lon"], p["lat"]) <= 2 * max(MOUND_TOL, p.get("r_m") or 0):
                P.append(dict(near, src=p["name"]))
    ex = json.load(open(os.path.join(TD, "extras_det.json")))
    for e in ex:
        if e["kind"] != "mound" or not e["dets"]:
            continue
        d = e["dets"][0]
        if d["dist_m"] <= MOUND_TOL:
            P.append(dict(d, kind="mound", src=e["name"]))
    # hard negatives: top-N that fall within no known record's tolerance (enclosure records cover their extent)
    from finder_export import record_tol, records
    recs = records()
    lon0, lat0 = cands[0]["lon"], cands[0]["lat"]
    from finder_common import local_xy
    rx, ry = local_xy([r["lon"] for r in recs], [r["lat"] for r in recs], lon0, lat0)
    rt = np.array([max(150.0, record_tol(r)) for r in recs])
    Nn = []
    for i, c in enumerate(cands[:N]):
        if i in used:
            continue
        cx, cy = local_xy([c["lon"]], [c["lat"]], lon0, lat0)
        if (np.hypot(rx - cx[0], ry - cy[0]) <= rt).any():
            continue
        Nn.append(c)
    kinds = os.environ.get("TUNE_KINDS")
    if kinds:
        P = [p for p in P if p["kind"] in kinds.split(",")]
        Nn = [n for n in Nn if n["kind"] in kinds.split(",")]
    return P, Nn


def tune(configs=None):
    P, N = tune_set()
    print(f"tune set: {len(P)} positives ({sum(p['kind'] == 'mound' for p in P)} mounds), {len(N)} hard negatives "
          f"({sum(n['kind'] == 'mound' for n in N)} mounds)")
    out = {"n_pos": len(P), "n_neg": len(N), "configs": {}}
    for name in (configs or CONFIGS):
        t = time.time()
        sp = score(P, name)
        sn = score(N, name)
        mp = [s for s, p in zip(sp, P) if p["kind"] == "mound"]
        mn = [s for s, n in zip(sn, N) if n["kind"] == "mound"]
        rp = [s for s, p in zip(sp, P) if p["kind"] != "mound"]
        rn = [s for s, n in zip(sn, N) if n["kind"] != "mound"]
        res = {"auc_all": round(auc(sp, sn), 3), "auc_mounds": round(auc(mp, mn), 3), "auc_rings": round(auc(rp, rn), 3),
               "n": [len(mp), len(mn), len(rp), len(rn)], "seconds": round(time.time() - t)}
        out["configs"][name] = res
        print(name, res, flush=True)
    json.dump({"P": P, "N": N, **out}, open(os.path.join(RD, "tune_result.json"), "w"))
    return out


def score_area(area, cfg_name):
    import finder_rank as fr
    cands = fr.ranked(area, "detector")
    N = round(fr.RERANK_PER100 * fr.scanned_km2(area) / 100)
    head = cands[:N]
    ps = score(head, cfg_name)
    json.dump({"area": area, "config": cfg_name, "p": {fr.cand_key(c): p for c, p in zip(head, ps)}},
              open(os.path.join(RD, f"{area}.json"), "w"))
    print(f"{area}: {len(head)} candidates scored with {cfg_name}")


def tune_order(cfg_name):
    """Rule step 2: pure Clef vs rank blend over the top RERANK_PER100 per 100 km2, by k-equivalent recall of all tune
    mounds (Ross-area mounds + extras) against the Ross candidate list (mounds only)."""
    import finder_rank as fr
    from finder_tune import tune_positives_and_background
    km2 = area_km2(AREAS["ross"])
    cands = fr.ranked("ross", "detector", ring_share=0.0)
    cands = [c for c in cands if c["kind"] == "mound"]
    N = round(fr.RERANK_PER100 * km2 / 100)
    head = cands[:N]
    P, names, B = tune_positives_and_background()
    # background-only head: drop candidates that are themselves tune positives
    pkeys = {key(dict(p, kind="mound")) for p in P if p}
    hp = score(head, cfg_name)
    hs = np.array([c["rank_score"] for c in head])
    res = {}
    for mode in ("detector", "clef", "blend"):
        ke = []
        for p in P:
            if p is None:
                ke.append(np.inf)
                continue
            pc = dict(p, kind="mound")
            s = fr.mound_score(pc)
            in_bg = [c for c in head if key(c) != key(pc)]
            det_pos = sum(c["rank_score"] > s for c in cands if key(c) != key(pc))
            if mode == "detector" or det_pos >= N:
                ke.append(det_pos * 100 / km2)
                continue
            pp = score([pc], cfg_name)[0]
            ps = np.array([q for c, q in zip(head, hp) if key(c) != key(pc)])
            ds = np.array([c["rank_score"] for c in in_bg])
            if mode == "clef":
                pos = (ps > pp).sum()
            else:
                n = len(ds) + 1
                drank = np.argsort(np.argsort(-np.r_[ds, s]))
                crank = np.argsort(np.argsort(-np.r_[ps, pp]))
                b = (drank + crank) / 2.0
                pos = (b[:-1] < b[-1]).sum()
            ke.append(pos * 100 / km2)
        ke = np.array(ke)
        res[mode] = {k: round(float(np.mean(ke < k)), 3) for k in (5, 10, 20, 50)}
        print(mode, res[mode], flush=True)
    json.dump(res, open(os.path.join(RD, f"tune_order_{cfg_name}.json"), "w"))
    return res


if __name__ == "__main__":
    if sys.argv[1] == "tune":
        tune(sys.argv[2:] or None)
    elif sys.argv[1] == "order":
        tune_order(sys.argv[2])
    elif sys.argv[1] == "area":
        score_area(sys.argv[2], sys.argv[3])

