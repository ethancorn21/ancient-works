"""Hand-fitted plans from the old books -> overlays on a site (kind "plan" in its depictions.json).

usage: plan_fit.py            sync every fit in data/db/platefits/ (serve.py runs this after each save or delete)
       plan_fit.py <doc id>   just that one

A fit is saved by the page's plate-fitting tool as data/db/platefits/<site id>.<plan id>.json:
  {"site", "plan", "ia", "file", "crop": [x0, y0, x1, y1] (page px), "pairs": [[u, v, lon, lat], ...] (page px ->
   ground), "label", "title", "book", "cite", "at"}
The fit is a similarity transform (shift, rotation, one scale) by least squares over the pairs, solved in Web
Mercator metres (conformal, so a similarity there is a similarity on the ground). The page solves the same thing
for its preview; this file is the one that decides. Pairs are never moved or snapped here.

Also here, next to the fit math it guards: fabrication_pattern, the one-site line's check for the batch
model's fabricated anchor patterns (tools/site_done.py runs it on every doc before it syncs).
"""
import glob
import io
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aw  # noqa: E402
import depict  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "db", "platefits")
RAW = os.path.join(ROOT, "data", "raw", "books")
WEB = os.path.join(ROOT, "web", "data", "sites")
MAX_PX = 2400
Image.MAX_IMAGE_PIXELS = 200_000_000  # fold-out plates are big scans, not decompression bombs

PACE_S = 1.0  # commons.get paces Wikimedia calls this way: a burst of bare urllib calls gets 429'd
_last = 0.0


def _root(root=None):
    """The project root for this call: an explicit root (a one-site run against a copy of the
    site's files, tools/site_done.py) or this checkout (the module constants keep working)."""
    return os.path.abspath(str(root)) if root else ROOT


def _fetch(url, tries=4, timeout=300):
    """The bytes of a Wikimedia URL, paced like commons.get: PACE_S apart, honours Retry-After on
    429/5xx. An automatic fit downloads one API answer plus one big picture per doc, back to back."""
    global _last
    for k in range(tries):
        time.sleep(max(0.0, _last + PACE_S - time.time()))
        _last = time.time()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=aw.UA), timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504) or k == tries - 1:
                raise
            wait = int(e.headers.get("Retry-After") or 30 * (k + 1))
            print(f"  {e.code} on {url.split('?')[0][:70]}: waiting {wait} s", flush=True)
            time.sleep(wait)
        except Exception as e:
            if k == tries - 1:
                raise
            print(f"  retry {k + 1}: {str(e)[:100]}", flush=True)
            time.sleep(3 * (k + 1))


def similarity(pairs):
    """pairs [[u, v, lon, lat]] -> (a, b) complex with merc = a * (u - i v) + b, residuals (ground m), lat0."""
    p = np.asarray(pairs, float)
    w = p[:, 0] - 1j * p[:, 1]
    xy = np.array([aw.to_merc(lon, lat) for lon, lat in p[:, 2:4]])
    z = xy[:, 0] + 1j * xy[:, 1]
    wm, zm = w.mean(), z.mean()
    a = np.sum((z - zm) * np.conj(w - wm)) / np.sum(np.abs(w - wm) ** 2)
    b = zm - a * wm
    k = aw.ground_scale(float(p[:, 3].mean()))  # ground metres per Mercator metre
    return a, b, np.abs(a * w + b - z) * k, k


def homography(pairs):
    """pairs [[u, v, lon, lat]] -> (H 3x3 page px -> Mercator, residuals in ground m, k). Same normalised least
    squares as the page (h33 = 1)."""
    p = np.asarray(pairs, float)
    Z = np.array([aw.to_merc(lon, lat) for lon, lat in p[:, 2:4]])
    U = p[:, :2]
    def norm(P):
        m = P.mean(0)
        sc = np.sqrt(((P - m) ** 2).sum(1).mean()) or 1.0
        return m, sc
    (um, us), (zm, zs) = norm(U), norm(Z)
    u, z = (U - um) / us, (Z - zm) / zs
    A, b = [], []
    for (x, y), (X, Y) in zip(u, z):
        A += [[x, y, 1, 0, 0, 0, -x * X, -y * X], [0, 0, 0, x, y, 1, -x * Y, -y * Y]]
        b += [X, Y]
    h, *_ = np.linalg.lstsq(np.array(A), np.array(b), rcond=None)
    Hn = np.append(h, 1).reshape(3, 3)
    Tu = np.array([[1 / us, 0, -um[0] / us], [0, 1 / us, -um[1] / us], [0, 0, 1]])
    Tzi = np.array([[zs, 0, zm[0]], [0, zs, zm[1]], [0, 0, 1]])
    H = Tzi @ Hn @ Tu
    q = (H @ np.c_[U, np.ones(len(U))].T).T
    k = aw.ground_scale(float(p[:, 3].mean()))
    return H, np.hypot(*(q[:, :2] / q[:, 2:3] - Z).T) * k, k


def _gap_ratios(axis):
    """Consecutive gaps between the distinct sorted values -> (max/median, min/median), or None.
    Near-arithmetic spacing is small ratios in both directions (exact arithmetic: 1.0, 1.0)."""
    d = np.unique(np.asarray(axis, float))
    if d.size < 2:
        return None
    g = np.diff(d)
    med = float(np.median(g))
    if med <= 0:
        return None
    return float(g.max() / med), float(g.min() / med)


def fabrication_pattern(pairs):
    """The line's check for the batch model's documented fabrication class (fit/batch_us.py
    llm_model, docs/gate.md section 7): internally perfect regular patterns on the fit sheet's
    page grid, which the batch's pre-gate checks and the gate all pass by construction (the gate
    scores the least-squares fit against the same points the model invented), so the one-site
    line re-checks the pattern before it syncs a doc to the map. Any one clause fires:
      (a) 2D lattice - >=4 anchors, >=3 distinct u AND >=3 distinct v, near-arithmetic spacing
          between distinct values on BOTH axes (max/median <= 1.3 and min/median >= 0.67);
      (b) 1D ladder - >=3 anchors sharing one coordinate (spread <= 2 px) with near-arithmetic
          spacing on the other (max/median <= 1.5 and min/median >= 0.9);
      (c) grid-round page coordinates - >=4 anchors and >=90% of the distinct anchor coordinates
          (per axis) within 0.5 px of a multiple of 10 px: the fit sheet's grid is labelled every
          100-1000 source px (fit/batch_us.py _step), so a model that reads labels lands on
          multiples of 10, while the page tool records a human's drag with one decimal (the 20
          hand fits in the repo are <=43% round).
    Calibrated on this repo (301): fires on all 15 stonehenge + argentoratum batch docs and on
    every other batch doc, and on none of the 20 hand fits (tests/golden/hand_fit_docs.sha256);
    nearest hand margins: (a) max/median 1.307-1.429 vs 1.3, (b) min/median 0.801 vs 0.9,
    (c) 0.43 vs 0.9. Pairs are the doc's [[u, v, lon, lat], ...] in the picture's size frame;
    no download, no network. -> None, or a reason string naming the clause(s) that fired.
    """
    p = np.asarray(pairs, float)
    if p.size == 0 or p.shape[1] < 2:
        return None
    u, v = p[:, 0], p[:, 1]
    clauses = []
    if len(p) >= 4 and np.unique(u).size >= 3 and np.unique(v).size >= 3:
        gu, gv = _gap_ratios(u), _gap_ratios(v)
        if gu and gv and gu[0] <= 1.3 and gu[1] >= 0.67 and gv[0] <= 1.3 and gv[1] >= 0.67:
            clauses.append("2D lattice (regular ladders on both page axes)")
    if len(p) >= 3:
        for shared in (1, 0):  # v-shared and u-shared orientations
            s = p[np.argsort(p[:, shared])]
            i = 0
            for j in range(s.shape[0]):
                while s[j, shared] - s[i, shared] > 2:
                    i += 1
                if j - i + 1 >= 3:
                    g = _gap_ratios(s[i:j + 1, 1 - shared])
                    if g and g[0] <= 1.5 and g[1] >= 0.9:
                        clauses.append("1D ladder (%d anchors share one coordinate, regular spacing on the other)"
                                       % (j - i + 1))
                        break
            if len(clauses) > 1:
                break
    if len(p) >= 4:
        def round_counts(axis):
            d = np.unique(axis)
            return int(sum(abs(x / 10.0 - round(x / 10.0)) <= 0.05 + 1e-9 for x in d)), int(d.size)
        (ru, nu), (rv, nv) = round_counts(u), round_counts(v)
        if nu + nv and (ru + rv) / (nu + nv) >= 0.9:
            clauses.append("grid-round page coordinates (%d of %d distinct values on a 10-px grid)" % (ru + rv, nu + nv))
    if not clauses:
        return None
    return "fabricated anchor pattern: " + "; ".join(clauses)


def load_picture(doc, root=None):
    """The full-size picture the pairs refer to, and the factor from the browser's image to it."""
    r = _root(root)
    if doc.get("src") == "commons":
        # the page fits on a 1280 px thumbnail; the overlay is made from a bigger rendering of the same file
        cache = os.path.join(r, "data", "raw", "commons", "big", doc["plan"] + ".jpg")
        if not os.path.exists(cache):
            q = {"action": "query", "titles": doc["ref"], "prop": "imageinfo", "iiprop": "url|size", "iiurlwidth": "3000",
                 "format": "json"}
            data = _fetch("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(q), timeout=60)
            ii = next(iter(json.loads(data)["query"]["pages"].values()))["imageinfo"][0]
            url = ii.get("thumburl") if ii.get("width", 0) > 3000 else ii["url"]
            data = _fetch(url)
            os.makedirs(os.path.dirname(cache), exist_ok=True)
            Image.open(io.BytesIO(data)).convert("RGB").save(cache, quality=92)
        im = Image.open(cache).convert("RGB")
    else:
        im = Image.open(os.path.join(r, "data", "raw", "books", doc["ia"], "full", doc["file"])).convert("RGB")
    size = doc.get("size") or im.size
    return im, im.width / size[0]


def warp_view(pic, crop, H, site_lonlat, max_px=2400, lim_m=3000):
    """Resample a perspective picture onto a north-up Mercator rectangle. Returns RGBA image and its corners."""
    from scipy.ndimage import map_coordinates
    x0, y0, x1, y1 = crop
    cx, cy = aw.to_merc(*site_lonlat)
    k = aw.ground_scale(site_lonlat[1])
    lim = lim_m / k
    cs = (H @ np.array([[x0, y0, 1], [x1, y0, 1], [x1, y1, 1], [x0, y1, 1]], float).T).T
    pts = [c[:2] / c[2] for c in cs if c[2] > 0]
    if len(pts) < 4:  # the horizon is inside the picture
        pts += [np.array([cx - lim, cy - lim]), np.array([cx + lim, cy + lim])]
    pts = np.array(pts)
    X0, X1 = max(pts[:, 0].min(), cx - lim), min(pts[:, 0].max(), cx + lim)
    Y0, Y1 = max(pts[:, 1].min(), cy - lim), min(pts[:, 1].max(), cy + lim)
    sc = max_px / max(X1 - X0, Y1 - Y0)
    W, Hh = max(2, round((X1 - X0) * sc)), max(2, round((Y1 - Y0) * sc))
    X, Y = np.meshgrid(X0 + (np.arange(W) + 0.5) / sc, Y1 - (np.arange(Hh) + 0.5) / sc)
    Hi = np.linalg.inv(H)
    q = np.tensordot(Hi, np.stack([X, Y, np.ones_like(X)]), 1)
    u, v = q[0] / q[2], q[1] / q[2]
    fwd = H[2, 0] * u + H[2, 1] * v + H[2, 2]  # in front of the viewer: same side of the horizon as the ground
    ok = (fwd > 0) & (u >= x0) & (u < x1) & (v >= y0) & (v < y1)
    a = np.asarray(pic, np.float32)
    out = np.zeros((Hh, W, 4), np.uint8)
    for c in range(3):
        out[..., c] = np.clip(map_coordinates(a[..., c], [v, u], order=1, cval=255), 0, 255)
    out[..., 3] = np.where(ok, 255, 0)
    corners = [list(aw.to_lonlat(x, y)) for x, y in [(X0, Y1), (X1, Y1), (X1, Y0), (X0, Y0)]]
    return Image.fromarray(out, "RGBA"), corners


def is_done(doc, name, root=None):
    """The site's depictions.json already carries this doc's overlay, current (same `at`, same doc id)."""
    r = _root(root)
    dep = os.path.join(r, "web", "data", "sites", doc.get("site", ""), "depictions.json")
    if not os.path.exists(dep):
        return False
    return any((d.get("fit") or {}).get("at") == doc.get("at") and d.get("kind") in ("plan", "view")
               and (d.get("fit") or {}).get("doc") == name
               for d in json.load(open(dep))["depictions"])


def build(doc, root=None):
    r = _root(root)
    sid, plan = doc["site"], doc["plan"]
    out_dir = os.path.join(r, "web", "data", "sites", sid)
    if not os.path.isdir(out_dir):
        raise SystemExit(f"{sid}: site not built")
    view = doc.get("model") == "homography"
    if len(doc["pairs"]) < (4 if view else 2):
        raise SystemExit(f"{sid} {plan}: too few point pairs")
    pic, fs = load_picture(doc, root)
    pairs = [[u * fs, v * fs, lon, lat] for u, v, lon, lat in doc["pairs"]]
    x0, y0, x1, y1 = [int(round(v * fs)) for v in doc["crop"]]
    name, ink_name = f"plan_{plan}.webp", f"plan_{plan}_ink.webp"
    if view:
        H, resid, k = homography(pairs)
        site = next(x for x in json.load(open(os.path.join(r, "web", "data", "sites.json")))["sites"] if x["id"] == sid)
        crop, corners = warp_view(pic, (x0, y0, x1, y1), H, (site["lon"], site["lat"]))
        corners = [[round(c, 7) for c in cc] for cc in corners]
        m_px, rot = None, None
    else:
        a, b, resid, k = similarity(pairs)
        crop = pic.crop((x0, y0, x1, y1))
        corners = []
        for u, v in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]:
            z = a * (u - 1j * v) + b
            corners.append([round(c, 7) for c in aw.to_lonlat(z.real, z.imag)])
        m_px, rot = float(abs(a) * k), round(math.degrees(np.angle(a)), 2)
    f = min(1.0, MAX_PX / max(crop.size))
    if f < 1:
        crop = crop.resize((round(crop.width * f), round(crop.height * f)), Image.LANCZOS)
        if m_px:
            m_px /= f
    crop.save(os.path.join(out_dir, name), quality=80, method=6)
    ink = depict.make_ink(crop.convert("RGBA"))
    ink.save(os.path.join(out_dir, ink_name), quality=85, method=6)
    # sort year: first 4-digit year in the book or label ("1575-1635" -> 1575); a century label sorts at its middle
    words = doc.get("book", "") + " " + str(doc.get("label") or "")
    ym, cm = re.search(r"(?<!\d)(1[2-9]\d\d)(?!\d)", words), re.search(r"\b(1[2-9])(?:st|nd|rd|th) century", words)
    year = int(ym.group(1)) if ym else (int(cm.group(1)) - 1) * 100 + 50 if cm else None
    # what the public page's source line says: hand fits were placed by hand; the batch's automatic
    # documents must not claim that (their fit was made by the working run, gate score on the doc)
    if doc.get("auto"):
        how = (f"Fitted automatically by the batch on {len(pairs)} matching points with a perspective fit; all within "
               f"{math.ceil(resid.max())} m (gate score {doc.get('score')} m)" if view else
               f"Fitted automatically by the batch on {len(pairs)} matching points; one rotation and scale fits "
               f"them within {math.ceil(resid.max())} m (gate score {doc.get('score')} m)")
    else:
        how = (f"Placed by hand on {len(pairs)} matching points with a perspective fit; all within {math.ceil(resid.max())} m."
               if view else f"Placed by hand on {len(pairs)} matching points; one rotation and scale fits them within "
                            f"{math.ceil(resid.max())} m.")
    src = (f"{doc.get('cite') or doc.get('book')}. {doc.get('label') or ''}. Scan: Internet Archive {doc['ia']} leaf "
           f"{doc['file'][1:-4].lstrip('0') or '0'}." if doc.get("src") != "commons" else
           f"{doc.get('title')} ({doc.get('label') or 'undated'}), Wikimedia Commons: {doc.get('cite')}.")
    entry = {"kind": "view" if view else "plan", "file": name, "ink": ink_name, "year": year,
             "label": (doc.get("title") if doc.get("src") == "commons" else
                       f"{doc.get('book', '')}: {doc.get('title') or doc.get('label') or 'site plan'}"),
             "scale": doc.get("label") or None, "corners": corners, "coverage": 1.0, "source": f"{src} {how}",
             "fit": {"pairs": len(pairs), "model": doc.get("model", "similarity"),
                     "resid_m": [round(float(r), 1) for r in resid],
                     "m_per_px": round(m_px, 4) if m_px else None, "rot_deg": rot,
                     "at": doc.get("at"), "doc": f"{sid}.{plan}"}}
    dep_path = os.path.join(out_dir, "depictions.json")
    deps = json.load(open(dep_path)) if os.path.exists(dep_path) else {"depictions": []}
    deps["depictions"] = [d for d in deps["depictions"] if d.get("file") != name] + [entry]
    deps["depictions"].sort(key=lambda d: d.get("year") or 0)
    tmp = dep_path + ".tmp"
    aw.save_json(tmp, deps)
    os.replace(tmp, dep_path)
    print(f"{sid} {plan}: {len(pairs)} pairs, {doc.get('model', 'similarity')}, residuals m {entry['fit']['resid_m']}",
          flush=True)
    import build_site
    build_site.set_drawings(sid, r)  # the page's flagship marker follows the count of fitted drawings


def prune(root=None, site=None):
    """Drop plan overlays whose fit was deleted (this site only when `site` is given - the one-site
    line must not write another site's files; the CLI keeps the global sweep)."""
    r = _root(root)
    have = {os.path.basename(p)[:-5] for p in glob.glob(os.path.join(r, "data", "db", "platefits", "*.json"))}
    for dep_path in glob.glob(os.path.join(r, "web", "data", "sites", site or "*", "depictions.json")):
        deps = json.load(open(dep_path))
        keep = [d for d in deps["depictions"] if d.get("kind") not in ("plan", "view") or (d.get("fit") or {}).get("doc") in have]
        if len(keep) != len(deps["depictions"]):
            for d in deps["depictions"]:
                if d not in keep:
                    for f in (d["file"], d.get("ink")):
                        if f and os.path.exists(os.path.join(os.path.dirname(dep_path), f)):
                            os.remove(os.path.join(os.path.dirname(dep_path), f))
            deps["depictions"] = keep
            aw.save_json(dep_path + ".tmp", deps)
            os.replace(dep_path + ".tmp", dep_path)
            print("pruned", dep_path, flush=True)
            import build_site
            build_site.set_drawings(os.path.basename(os.path.dirname(dep_path)), r)


def main(args, root=None):
    r = _root(root)
    paths = [os.path.join(r, "data", "db", "platefits", a + ".json") for a in args] or \
        sorted(glob.glob(os.path.join(r, "data", "db", "platefits", "*.json")))
    for p in paths:
        if not os.path.exists(p):
            continue
        doc = json.load(open(p))
        name = os.path.basename(p)[:-5]
        if not is_done(doc, name, root) or args:  # explicit args always rebuild
            try:
                build(doc, root)
            except SystemExit as e:
                print(e, flush=True)
    if not args:
        prune(root)


if __name__ == "__main__":
    main(sys.argv[1:])
