"""Automatic plan fitting with a pretrained image matcher (the lead, 2026-10-11).

usage: .venv/bin/python fit/matchfit.py <site id> ... [--all-queue] [--dry] [--root DIR] [--matcher URL]

Two automatic fits failed before this one: the batch's vision model invented its points (301), and
ink against relief by hand-built features landed 231-2204 m off on the owner's 21 hand fits (302b).
This one asks a pretrained cross-modality matcher - MatchAnything-ELoFTR (Hugging Face
zju-community/matchanything_eloftr, Apache-2.0), served on the AI box's 5060 Ti at port 8091
(Local-AI-Lab server/matcher) - for matching points between the old plan and an image of the
ground whose position is known:

  grounds   the site's LiDAR relief (relief.jpg) and aerial photograph (imagery.jpg), both on the
            site's own box (web/data/sites.json corners), and its survey sheets (kind "map" in
            depictions.json: OS six-inch / one-inch, Cassini, Etat-major), each on its own corners.
  windows   the site box is often 3-4x the plan's extent and the matcher fails past a ~2-3x scale
            gap (Serpent Mound: the serpent is a squiggle in a 1.2 km relief), so each ground is
            matched whole and as centred windows of 0.7, 0.5, 0.35 and 0.25 of its size.
  fit       RANSAC similarity (plan px -> ground px, tolerance 1% of the window), refit on the
            inliers, carried to lon/lat through the ground's corners (Web Mercator).
  trust     the inlier count. On the owner's hand fits (a look by the lead, not a held-out test):
            every result with >= 10 inliers landed 26-76 m from the hand fit; results with 2-7
            inliers were 100-2000 m off. A fit is written only with >= MIN_INLIERS inliers and a
            rotation within MAX_ROT_DEG of north-up (old plans are drawn north-up or by their arrow;
            a large rotation was always a wrong match). Anything else is left for the owner's
            Ready-to-fit queue.
  RoMa      a picture ELoFTR is not sure of goes to MatchAnything-RoMa (port 8092), judged by the fraction
            of its matches that agree (>= 0.4) instead of a count, at any rotation (judge; docs/matchfit.md
            sections 7-8).

A written fit is an ordinary platefit document (fit/batch_us.write_doc: by "agent", auto true) with
"fitter": "matcher" and its inlier count; its pairs are up to 8 of the real matched points, spread
over the plan, so the line's fabrication check sees real, irregular points. tools/site_done.py then
syncs it to the map like any other automatic fit. Existing documents (hand or automatic) are never
touched.
"""
import argparse
import base64
import io
import json
import math
import os
import sys
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "fit"))
import batch_us  # noqa: E402
import review  # noqa: E402

Image.MAX_IMAGE_PIXELS = None
MATCHER_URL = os.environ.get("MATCHER_URL", "http://127.0.0.1:8091")
ROMA_URL = os.environ.get("ROMA_URL", "http://127.0.0.1:8092")
WINDOWS = (1.0, 0.7, 0.5, 0.35, 0.25)
MIN_INLIERS = 10
MAX_ROT_DEG = 30.0
ROMA_MIN_FRAC = 0.4
MODELS = {"eloftr": "zju-community/matchanything_eloftr", "roma": "zju-community/matchanything_roma"}
N_PAIRS = 8
SPREAD_MIN_RATIO = 0.1
SPREAD_MIN_SD_PX = 20.0


def spread(pts):
    """How two-dimensional the consistent points are on the plan: (ratio, minor sd in px). ratio =
    sqrt(minor/major eigenvalue) of their covariance (1 = round cloud, 0 = a line). Why (2026-10-11):
    Aesica's bath-house plan had 13 consistent points all along one column (0.054, 15.6 px); a near-line
    leaves the similarity's scale free, and it was placed 8x too big. Every right fit on the owner's hand
    fits had >= 0.138 and >= 30 px (projects-00's measurement, docs/matchfit.md section 6)."""
    p = np.array([q[:2] for q in pts], float)
    if len(p) < 3:
        return 0.0, 0.0
    c = p - p.mean(0)
    ev = np.clip(np.linalg.eigvalsh(c.T @ c / len(p)), 0, None)
    return (float(np.sqrt(ev[0] / ev[1])) if ev[1] > 0 else 0.0), float(np.sqrt(ev[0]))


def judge(best, kind="eloftr"):
    """Why the best candidate is not to be trusted, or None. ELoFTR (sparse, ~100s of matches): the inlier count and
    a rotation within MAX_ROT_DEG of north. RoMa (dense, ~5000 matches per call, so a count means nothing): the
    inlier FRACTION >= 0.4 and no rotation gate (projects-00, docs/matchfit.md sections 7-8): on the 21 hand fits
    every rotation rule accepts the same 11 at 0 wrong at >= 0.3, because the wrong big-rotation matches all sit
    below 0.25; on the queue the gate threw away 13 right-looking plans (Strasbourg drawn along the Rhine axis at
    32-39 deg), and the only wrong or doubtful accepts sat in 0.3-0.4 (Eaton Socon / Lewes Down 0.32, Norwich
    museum guide 0.30). Both: the spread guard."""
    if kind == "roma":
        frac = best["inliers"] / max(best["matches"], 1)
        if frac < ROMA_MIN_FRAC:
            return f"not sure: {frac:.2f} of the matches agree (need {ROMA_MIN_FRAC})"
    elif best["inliers"] < MIN_INLIERS:
        return f"not sure: {best['inliers']} consistent points (need {MIN_INLIERS})"
    if kind == "eloftr" and abs(best["rot"]) > MAX_ROT_DEG:
        return f"not sure: rotated {best['rot']:.0f} deg from north"
    if best["spread"][0] < SPREAD_MIN_RATIO or best["spread"][1] < SPREAD_MIN_SD_PX:
        return (f"not sure: the consistent points lie nearly on a line (spread {best['spread'][0]:.2f}, "
                f"{best['spread'][1]:.0f} px across): the scale is not pinned")
    return None


def reachable(url=None):
    """True when the matcher answers /health (a run without it leaves everything to the queue)."""
    try:
        urllib.request.urlopen((url or MATCHER_URL) + "/health", timeout=5).read()
        return True
    except Exception:
        return False


def _merc(lon, lat):
    return lon * 20037508.34 / 180, math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)) * 6378137


def _unmerc(x, y):
    return x * 180 / 20037508.34, math.degrees(2 * math.atan(math.exp(y / 6378137)) - math.pi / 2)


def _b64(im):
    buf = io.BytesIO()
    im.convert("RGB").save(buf, "PNG")
    return base64.b64encode(buf.getvalue()).decode()


def match(a, b, url=None):
    """MatchAnything on the 5060 Ti: (keypoints in a, keypoints in b), original pixel frames."""
    req = json.dumps({"image0": _b64(a), "image1": _b64(b), "threshold": 0.2, "max_side": 1024}).encode()
    r = json.load(urllib.request.urlopen(urllib.request.Request(
        (url or MATCHER_URL) + "/match", req, {"Content-Type": "application/json"}), timeout=180))
    if "error" in r:
        raise RuntimeError(r["error"])
    return np.array(r["keypoints0"]).reshape(-1, 2), np.array(r["keypoints1"]).reshape(-1, 2)


def _sim(p, q):
    P = p[:, 0] + 1j * p[:, 1]
    Q = q[:, 0] + 1j * q[:, 1]
    s, t = np.linalg.lstsq(np.c_[P, np.ones_like(P)], Q, rcond=None)[0]
    return s, t


def ransac(a, b, tol, iters=3000, seed=0):
    """(inlier mask, s, t) of the best similarity a -> b, or None."""
    if len(a) < 3:
        return None
    rng = np.random.default_rng(seed)
    A = a[:, 0] + 1j * a[:, 1]
    B = b[:, 0] + 1j * b[:, 1]
    best = None
    for _ in range(iters):
        i = rng.choice(len(a), 2, replace=False)
        if abs(A[i[0]] - A[i[1]]) < 1e-6:
            continue
        s, t = _sim(a[i], b[i])
        m = np.abs(s * A + t - B) < tol
        if best is None or m.sum() > best.sum():
            best = m
    if best is None or best.sum() < 3:
        return None
    s, t = _sim(a[best], b[best])
    return best, s, t


def _spread(pts, k):
    """Up to k indices of pts, spread out (farthest-point order from the centroid's nearest)."""
    if len(pts) <= k:
        return list(range(len(pts)))
    c = pts.mean(axis=0)
    idx = [int(np.argmin(((pts - c) ** 2).sum(1)))]
    d = ((pts - pts[idx[0]]) ** 2).sum(1)
    while len(idx) < k:
        j = int(np.argmax(d))
        idx.append(j)
        d = np.minimum(d, ((pts - pts[j]) ** 2).sum(1))
    return idx


def plan_image(root, row):
    """The plan's picture cropped to its map box, and the factor from the row's size frame to it.
    Returns (crop image, crop box in the size frame, fx, fy) or None when the picture is not here."""
    r = Path(root)
    if row.get("ia"):
        p = r / "data" / "raw" / "books" / row["ia"] / "full" / row["file"]
    elif row.get("url"):
        p = r / row["url"].replace("media/commons", "data/raw/commons")
    else:
        return None
    if not p.is_file():
        return None
    page = Image.open(p)
    w0, h0 = row.get("size") or page.size
    fx, fy = page.width / w0, page.height / h0
    x0, y0, x1, y1 = batch_us._crop_px(dict(row, size=[w0, h0]))
    crop = page.crop((round(x0 * fx), round(y0 * fy), round(x1 * fx), round(y1 * fy)))
    return crop, (x0, y0, x1, y1), fx, fy


def grounds(root, site):
    """(name, image path, corners) for every ground of the site that exists."""
    r = Path(root) / "web" / "data" / "sites" / site["id"]
    out = [(g, r / g, site["corners"]) for g in ("relief.jpg", "imagery.jpg") if (r / g).is_file()]
    dep = r / "depictions.json"
    if dep.is_file():
        for d in json.loads(dep.read_text()).get("depictions", []):
            if d.get("kind") == "map" and d.get("corners") and (r / d["file"]).is_file():
                out.append((d["file"], r / d["file"], d["corners"]))
    return out


def fit_row(root, site, row, url=None, kind="eloftr"):
    """Best matcher fit of one plan row on one site: a dict (inliers, rot, ground, window, pairs_ll,
    resid_m) or a dict with 'why' when there is nothing to trust. kind picks the accept rule (judge)."""
    pic = plan_image(root, row)
    if pic is None:
        return {"why": "picture not on this machine"}
    plan, (x0, y0, _, _), fx, fy = pic
    best = None
    for name, path, corners in grounds(root, site):
        img = Image.open(path)
        W, H = img.size
        (lo0, la0), (lo1, _), (_, la1) = corners[0], corners[1], corners[2]
        X0, Y0 = _merc(lo0, la0)
        X1, Y1 = _merc(lo1, la1)
        for f in WINDOWS:
            cw, ch = W * f, H * f
            ox, oy = (W - cw) / 2, (H - ch) / 2
            win = img.crop((round(ox), round(oy), round(ox + cw), round(oy + ch)))
            k = cw / win.width
            try:
                a, b = match(plan, win, url)
            except Exception as e:  # one bad request must not end the site
                print(f"  matcher error on {name} x{f}: {e}", file=sys.stderr)
                continue
            if len(a) < 3:
                continue
            b = b * k + [ox, oy]
            res = ransac(a, b, 0.01 * max(W, H) * f)
            if res is None:
                continue
            m, s, t = res
            n = int(m.sum())
            if best is not None and n <= best["inliers"]:
                continue
            # plan crop px -> row size frame px; ground px -> lon/lat
            A = a[m]
            Bm = s * (A[:, 0] + 1j * A[:, 1]) + t
            ll = [_unmerc(X0 + z.real / W * (X1 - X0), Y0 + z.imag / H * (Y1 - Y0)) for z in Bm]
            mpp = abs(s) * abs(X1 - X0) / W * math.cos(math.radians((la0 + la1) / 2))
            resid = np.abs(Bm - (b[m][:, 0] + 1j * b[m][:, 1])) * abs(X1 - X0) / W * math.cos(math.radians(la0))
            sel = _spread(A, N_PAIRS)
            sp = spread([[x0 + u / fx, y0 + v / fy] for u, v in A])   # in the pairs' frame, all inliers
            pairs = [[x0 + A[i, 0] / fx, y0 + A[i, 1] / fy, ll[i][0], ll[i][1]] for i in sel]
            best = {"inliers": n, "matches": len(a), "rot": math.degrees(np.angle(s)), "ground": name,
                    "window": f, "pairs": pairs, "resid_m": float(np.median(resid)), "m_per_px": mpp, "spread": sp}
    if best is None:
        return {"why": "the matcher found nothing consistent"}
    why = judge(best, kind)
    if why:
        best["why"] = why
    return best


def _sites(root):
    d = json.loads((Path(root) / "web" / "data" / "sites.json").read_text())
    return {s["id"]: s for s in (d["sites"] if isinstance(d, dict) else d)}


def _settle(root, sid, row, r, kind, dry, results=None):
    """The per-candidate tail of run(): prints one fitted row's verdict and, when it is a good fit and
    not dry, writes its document (returning the written path, else None). When results is a list, one
    {site, plan, outcome (written|refused|dry), path, why, kind} entry is appended per call: the caller
    (239) records refused candidates from it, including the gate's clause once the gate lands there."""
    title = (row.get("title") or row["id"])[:70]
    if "why" in r:
        extra = f" [{r['ground']} x{r['window']}, rot {r['rot']:.0f}]" if "ground" in r else ""
        print(f"{sid}  {title}: {r['why']}{extra}")
        if results is not None:
            results.append({"site": sid, "plan": row["id"], "outcome": "refused",
                            "path": None, "why": r["why"], "kind": kind})
        return None
    print(f"{sid}  {title}: FIT ({kind}) {r['inliers']}/{r['matches']} points on {r['ground']} x{r['window']}, "
          f"rot {r['rot']:.1f} deg, {r['m_per_px']:.2f} m/px, residual {r['resid_m']:.0f} m")
    if dry:
        if results is not None:
            results.append({"site": sid, "plan": row["id"], "outcome": "dry",
                            "path": None, "why": None, "kind": kind})
        return None
    path = batch_us.write_doc(str(root), sid, row, r["pairs"], round(r["resid_m"], 1))
    if path:
        doc = json.loads(Path(path).read_text())
        doc.update({"fitter": "matcher", "matcher": {
            "model": MODELS[kind], "inliers": r["inliers"], "matches": r["matches"],
            "ground": r["ground"], "window": r["window"], "rot_deg": round(r["rot"], 2),
            "spread": [round(r["spread"][0], 3), round(r["spread"][1], 1)]}})
        batch_us._save_json(path, doc)
    if results is not None:
        results.append({"site": sid, "plan": row["id"],
                        "outcome": "written" if path else "refused",
                        "path": path, "why": None, "kind": kind})
    return path


def run(root, site_ids, dry=False, url=None, roma_url=None, results=None):
    """ELoFTR first (fast, ~1 s a window pair); a picture it is not sure of goes to RoMa (~4 s a pair, placed
    11 of the 21 hand fits against ELoFTR's 7) when that answers. When results is a list, one entry per
    settled candidate is appended to it (see _settle); returns the written paths."""
    roma = roma_url or ROMA_URL
    use_roma = reachable(roma)
    sites = _sites(root)
    rows = batch_us._plans_rows(str(root))
    written = []
    for sid in site_ids:
        site = sites.get(sid)
        if not site:
            print(f"{sid}: not a built site")
            continue
        docs = dict(batch_us.pre_docs(str(root), sid))
        # a picture the lead or the owner dropped (e.g. a modern diagram: historical depictions only)
        # carries "dropped" in the site's review item and is never fitted again
        _, item = review._find_item(str(root), sid)
        dropped = {c.get("plan") for c in ((item or {}).get("candidates") or []) if c.get("dropped")}
        for row in batch_us.candidates(sid, rows):
            if row["id"] in docs or row["id"] in dropped:
                continue
            r, kind = fit_row(root, site, row, url), "eloftr"
            if "why" in r and use_roma and r["why"] != "picture not on this machine":
                rr = fit_row(root, site, row, roma, "roma")
                if "why" not in rr:
                    r, kind = rr, "roma"
                else:
                    r = dict(rr, why=f"{r['why']}; RoMa {rr['why']}")
            path = _settle(root, sid, row, r, kind, dry, results)
            if path:
                written.append(path)
    return written


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("sites", nargs="*")
    ap.add_argument("--all-queue", action="store_true", help="every site in web/data/fit_queue.json")
    ap.add_argument("--dry", action="store_true", help="report only, write no documents")
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--matcher", default=None, help="ELoFTR server (default MATCHER_URL, :8091)")
    ap.add_argument("--roma", default=None, help="RoMa server for the second pass (default ROMA_URL, :8092)")
    a = ap.parse_args(argv)
    ids = list(a.sites)
    if a.all_queue:
        q = json.loads((Path(a.root) / "web" / "data" / "fit_queue.json").read_text())
        ids += [e["site"] for e in q.get("entries", []) if e.get("site") not in ids]
    if not ids:
        ap.error("name sites, or --all-queue")
    w = run(a.root, ids, a.dry, a.matcher, a.roma)
    print(f"{len(w)} fit document(s) written")


if __name__ == "__main__":
    main()
