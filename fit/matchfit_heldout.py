"""Held-out measurement of the pretrained matcher (fit/matchfit.py) against the 21 hand fits.

usage: .venv/bin/python fit/matchfit_heldout.py run      # one pass, checkpointed per document
       .venv/bin/python fit/matchfit_heldout.py table    # the table from the checkpoint
       .venv/bin/python fit/matchfit_heldout.py rules    # accept-rule sweep (inlier threshold x ground)

Same truth set and metric as fit/inkfit_heldout.py (302b): the 20 golden hand-fit documents plus the
lead's Maiden Castle fit; corner error = RMS over the four full-image corners mapped by the method's
similarity and by the hand similarity, in ground metres. The method never reads the hand pairs; only
the evaluator does, after the method has answered.

Unlike matchfit.fit_row (which keeps only the best candidate), this records EVERY candidate the
matcher produced (each ground image x each window) with its inlier count, rotation and corner error,
so an accept rule can be chosen afterwards on the whole table. The owner's bar (2026-10-11): a fit
within 100 m is good enough; the question is which rule accepts only those.
"""
import json
import math
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))
sys.path.insert(0, os.path.join(ROOT, "fit"))
import plan_fit  # noqa: E402
import propose  # noqa: E402
import inkfit_heldout as ih  # noqa: E402
import matchfit as mf  # noqa: E402

VARIANT = os.environ.get("MF_VARIANT", "")      # "" = matchfit's centred windows; "located" = fit/matchfit2.py
TAG = os.environ.get("MF_TAG", "")              # e.g. "roma" when MATCHER_URL points at another model
HOLDOUT = os.path.join(ROOT, "data", "matchfit", "heldout" + ("_" + VARIANT if VARIANT else "") + ("_" + TAG if TAG else ""))
RESULTS = os.path.join(HOLDOUT, "results.json")
if VARIANT == "located":
    import matchfit2
    candidates_fn = lambda root, site, row, url=None: matchfit2.candidates(root, site, row, url)  # noqa: E731
else:
    candidates_fn = None


def load():
    if os.path.exists(RESULTS):
        return json.load(open(RESULTS))
    return {"at": datetime.now(timezone.utc).isoformat(), "docs": {}}


def save(res):
    os.makedirs(HOLDOUT, exist_ok=True)
    tmp = RESULTS + ".tmp"
    json.dump(res, open(tmp, "w"), indent=1, default=lambda o: float(o))
    os.replace(tmp, RESULTS)


def candidates(root, site, row, url=None):
    """Every (ground, window) candidate: matches, inliers, rot, pairs (row size frame -> lon/lat)."""
    pic = mf.plan_image(root, row)
    if pic is None:
        return None
    plan, (x0, y0, _, _), fx, fy = pic
    out = []
    for name, path, corners in mf.grounds(root, site):
        img = Image.open(path)
        W, H = img.size
        (lo0, la0), (lo1, _), (_, la1) = corners[0], corners[1], corners[2]
        X0, Y0 = mf._merc(lo0, la0)
        X1, Y1 = mf._merc(lo1, la1)
        for f in mf.WINDOWS:
            cw, ch = W * f, H * f
            ox, oy = (W - cw) / 2, (H - ch) / 2
            win = img.crop((round(ox), round(oy), round(ox + cw), round(oy + ch)))
            k = cw / win.width
            t0 = time.time()
            try:
                a, b = mf.match(plan, win, url)
            except Exception as e:
                out.append({"ground": name, "window": f, "error": repr(e)})
                continue
            c = {"ground": name, "window": f, "matches": int(len(a)), "seconds": round(time.time() - t0, 1)}
            if len(a) < 3:
                c["inliers"] = 0
                out.append(c)
                continue
            b = b * k + [ox, oy]
            res = mf.ransac(a, b, 0.01 * max(W, H) * f)
            if res is None:
                c["inliers"] = 0
                out.append(c)
                continue
            m, s, t = res
            A = a[m]
            Bm = s * (A[:, 0] + 1j * A[:, 1]) + t
            ll = [mf._unmerc(X0 + z.real / W * (X1 - X0), Y0 + z.imag / H * (Y1 - Y0)) for z in Bm]
            resid = np.abs(Bm - (b[m][:, 0] + 1j * b[m][:, 1])) * abs(X1 - X0) / W * math.cos(math.radians(la0))
            pairs = [[x0 + A[i, 0] / fx, y0 + A[i, 1] / fy, ll[i][0], ll[i][1]] for i in range(len(A))]
            c.update({"inliers": int(m.sum()), "rot": round(math.degrees(np.angle(s)), 2),
                      "resid_m": round(float(np.median(resid)), 1), "pairs": pairs})
            out.append(c)
    return out


def centre_error(a_h, b_h, a_m, b_m, w, h, lat0):
    """Ground distance between the plan centre mapped by the method and by the hand fit (m)."""
    import aw
    wc = (w / 2) - 1j * (h / 2)
    d = (a_m - a_h) * wc + (b_m - b_h)
    return round(abs(d) * aw.ground_scale(lat0), 1)


def rescore():
    """Recompute corner/centre metrics for every stored candidate from its pairs (no matcher calls)."""
    res = load()
    for doc, e in res["docs"].items():
        if "candidates" not in e:
            continue
        site, plan = doc.split(".", 1)
        row = propose._plans_row(plan, site)
        a_h, b_h, w, h, lat0 = ih.hand_similarity(ROOT, doc, row)
        for c in e["candidates"]:
            if c.get("inliers", 0) >= 3 and "pairs" in c:
                a_m, b_m, _r, _k = plan_fit.similarity(c["pairs"])
                c["corner_m"], c["drot_deg"], c["scale_ratio"] = ih.corner_metrics(a_h, b_h, a_m, b_m, w, h, lat0)
                c["centre_m"] = centre_error(a_h, b_h, a_m, b_m, w, h, lat0)
    save(res)


def measure(root, doc, url=None):
    site, plan = doc.split(".", 1)
    se = propose._site(site)
    row = propose._plans_row(plan, site)
    t0 = time.time()
    cands = (candidates_fn or candidates)(root, se, row, url)
    entry = {"doc": doc, "site": site, "plan": plan, "seconds": round(time.time() - t0, 1)}
    if cands is None:
        entry["error"] = "picture not on this machine"
        return entry
    a_h, b_h, w, h, lat0 = ih.hand_similarity(root, doc, row)
    for c in cands:
        if c.get("inliers", 0) >= 3:
            a_m, b_m, _r, _k = plan_fit.similarity(c["pairs"])
            c["corner_m"], c["drot_deg"], c["scale_ratio"] = ih.corner_metrics(a_h, b_h, a_m, b_m, w, h, lat0)
            c["centre_m"] = centre_error(a_h, b_h, a_m, b_m, w, h, lat0)
    entry["candidates"] = cands
    return entry


def doc_ids():
    """Every platefit document pinned in the golden file plus the lead's Maiden Castle fit, sorted."""
    ids = set()
    for line in open(ih.GOLDEN):
        line = line.strip()
        if line and "platefits/" in line:
            ids.add(line.split()[-1].split("platefits/")[-1][:-len(".json")])
    ids.add(ih.MAIDEN)
    return sorted(ids)


def run(url=None):
    ids = doc_ids()
    print(len(ids), "held-out documents", flush=True)
    ih.precheck(ids)
    if not mf.reachable(url):
        raise SystemExit("matcher not reachable at " + (url or mf.MATCHER_URL))
    res = load()
    for doc in ids:
        if doc in res["docs"] and "error" not in res["docs"][doc]:
            continue
        print(doc, flush=True)
        e = measure(ROOT, doc, url)
        res["docs"][doc] = e
        save(res)
        if "error" in e:
            print("   ", e["error"], flush=True)
            continue
        best = max((c for c in e["candidates"] if "corner_m" in c), key=lambda c: c["inliers"], default=None)
        if best:
            print(f"    best-by-inliers: {best['ground']} {best.get('stage', '')} x{best['window']}  inl {best['inliers']}/{best['matches']}"
                  f"  rot {best['rot']}  corner {best['corner_m']} m  centre {best.get('centre_m')} m", flush=True)
        else:
            print("    no candidate with >= 3 inliers", flush=True)
    print("done:", len(res["docs"]), "documents")


def table():
    res = load()
    print("| doc | best ground | window | inliers/matches | rot deg | corner m | centre m | drot | scale | best-corner cand (ground, inl, m) |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for doc in sorted(res["docs"]):
        e = res["docs"][doc]
        if "error" in e:
            print(f"| {doc} | error: {e['error']} |||||||||")
            continue
        cs = [c for c in e["candidates"] if "corner_m" in c]
        if not cs:
            print(f"| {doc} | none |||||||||")
            continue
        b = max(cs, key=lambda c: c["inliers"])
        bc = min(cs, key=lambda c: c["corner_m"])
        print(f"| {doc} | {b['ground']} | {b['window']} | {b['inliers']}/{b['matches']} | {b['rot']} | {b['corner_m']} "
              f"| {b.get('centre_m')} | {b['drot_deg']} | {b['scale_ratio']} | {bc['ground']} x{bc['window']}, {bc['inliers']}, {bc['corner_m']} |")


def rules_frac(good_m=100.0, metric="centre_m", max_rot=30.0):
    """Accept-rule sweep on inlier FRACTION (inliers / matches) and a minimum count, for dense matchers
    (RoMa returns ~5000 matches per call, so a count threshold set for ELoFTR means nothing)."""
    res = load()
    docs = [e for e in res["docs"].values() if "candidates" in e]
    print(f"docs measured: {len(docs)}; good = {metric} <= {good_m:.0f} m; best candidate by inlier fraction; |rot| <= {max_rot}")
    print("| min frac | min inliers | accepted | good | wrong | worst accepted m |")
    print("|---|---|---|---|---|---|")
    for fr in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9):
        for k in (10, 100, 500):
            acc = good = 0
            worst = 0.0
            for e in docs:
                cs = [c for c in e["candidates"] if "corner_m" in c and c.get("matches")]
                if not cs:
                    continue
                b = max(cs, key=lambda c: c["inliers"] / c["matches"])
                if b["inliers"] / b["matches"] >= fr and b["inliers"] >= k and abs(b["rot"]) <= max_rot:
                    acc += 1
                    if b[metric] <= good_m:
                        good += 1
                    worst = max(worst, b[metric])
            if acc:
                print(f"| {fr} | {k} | {acc} | {good} | {acc - good} | {worst:.0f} |")


def rules(good_m=100.0, metric="corner_m"):
    """Sweep accept rules: pick the best-by-inliers candidate (optionally per ground family), accept if
    inliers >= k and |rot| <= r. Report accepted / within good_m / worst accepted error."""
    res = load()
    docs = [e for e in res["docs"].values() if "candidates" in e]
    fams = {"any": lambda g: True, "relief": lambda g: g == "relief.jpg", "aerial": lambda g: g == "imagery.jpg",
            "sheet": lambda g: g not in ("relief.jpg", "imagery.jpg")}
    print(f"docs measured: {len(docs)}; good = {metric} <= {good_m:.0f} m")
    print("| family | min inliers | max rot | accepted | good | wrong | worst accepted m |")
    print("|---|---|---|---|---|---|---|")
    for fam, keep in fams.items():
        for k in (5, 8, 10, 15, 20, 30):
            for r in (30, 180):
                acc = good = 0
                worst = 0.0
                for e in docs:
                    cs = [c for c in e["candidates"] if "corner_m" in c and keep(c["ground"])]
                    if not cs:
                        continue
                    b = max(cs, key=lambda c: c["inliers"])
                    if b["inliers"] >= k and abs(b["rot"]) <= r:
                        acc += 1
                        if b[metric] <= good_m:
                            good += 1
                        worst = max(worst, b[metric])
                if acc:
                    print(f"| {fam} | {k} | {r} | {acc} | {good} | {acc - good} | {worst:.0f} |")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    url = os.environ.get("MATCHER_URL")
    {"run": lambda: run(url), "table": table, "rescore": rescore,
     "frac": lambda: rules_frac(metric=sys.argv[2] if len(sys.argv) > 2 else "centre_m"),
     "rules": lambda: rules(metric=sys.argv[2] if len(sys.argv) > 2 else "corner_m")}[cmd]()
