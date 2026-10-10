"""Hand-fitted plans from the old books -> overlays on a site (kind "plan" in its depictions.json).

usage: plan_fit.py            sync every fit in data/db/platefits/ (serve.py runs this after each save or delete)
       plan_fit.py <doc id>   just that one

A fit is saved by the page's plate-fitting tool as data/db/platefits/<site id>.<plan id>.json:
  {"site", "plan", "ia", "file", "crop": [x0, y0, x1, y1] (page px), "pairs": [[u, v, lon, lat], ...] (page px ->
   ground), "label", "title", "book", "cite", "at"}
The fit is a similarity transform (shift, rotation, one scale) by least squares over the pairs, solved in Web
Mercator metres (conformal, so a similarity there is a similarity on the ground). The page solves the same thing
for its preview; this file is the one that decides. Pairs are never moved or snapped here.
"""
import glob
import json
import math
import os
import sys

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


def build(doc):
    sid, plan = doc["site"], doc["plan"]
    out_dir = os.path.join(WEB, sid)
    if not os.path.isdir(out_dir):
        raise SystemExit(f"{sid}: site not built")
    if len(doc["pairs"]) < 2:
        raise SystemExit(f"{sid} {plan}: needs at least 2 point pairs")
    a, b, resid, k = similarity(doc["pairs"])
    x0, y0, x1, y1 = [int(round(v)) for v in doc["crop"]]
    page = Image.open(os.path.join(RAW, doc["ia"], "full", doc["file"])).convert("RGB")
    crop = page.crop((x0, y0, x1, y1))
    f = min(1.0, MAX_PX / max(crop.size))
    if f < 1:
        crop = crop.resize((round(crop.width * f), round(crop.height * f)), Image.LANCZOS)
    corners = []
    for u, v in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]:
        z = a * (u - 1j * v) + b
        corners.append([round(c, 7) for c in aw.to_lonlat(z.real, z.imag)])
    name = f"plan_{plan}.webp"
    crop.save(os.path.join(out_dir, name), quality=80, method=6)
    ink = depict.make_ink(crop.convert("RGBA"))
    ink_name = f"plan_{plan}_ink.webp"
    ink.save(os.path.join(out_dir, ink_name), quality=85, method=6)
    m_px = abs(a) * k
    year = next((int(t) for t in doc.get("book", "").split() if t.isdigit() and len(t) == 4), None)
    entry = {"kind": "plan", "file": name, "ink": ink_name, "year": year,
             "label": f"{doc.get('book', '')}: {doc.get('title') or doc.get('label') or 'site plan'}",
             "scale": doc.get("label") or None, "corners": corners, "coverage": 1.0,
             "source": f"{doc.get('cite') or doc.get('book')}. {doc.get('label') or ''}. Scan: Internet Archive "
                       f"{doc['ia']} leaf {doc['file'][1:-4].lstrip('0') or '0'}. Placed by hand on {len(doc['pairs'])} "
                       f"matching points; one rotation and scale fits them within {math.ceil(resid.max())} m.",
             "fit": {"pairs": len(doc["pairs"]), "resid_m": [round(float(r), 1) for r in resid],
                     "m_per_px": round(float(m_px), 4), "rot_deg": round(math.degrees(np.angle(a)), 2),
                     "at": doc.get("at"), "doc": f"{sid}.{plan}"}}
    dep_path = os.path.join(out_dir, "depictions.json")
    deps = json.load(open(dep_path)) if os.path.exists(dep_path) else {"depictions": []}
    deps["depictions"] = [d for d in deps["depictions"] if d.get("file") != name] + [entry]
    deps["depictions"].sort(key=lambda d: d.get("year") or 0)
    tmp = dep_path + ".tmp"
    aw.save_json(tmp, deps)
    os.replace(tmp, dep_path)
    print(f"{sid} {plan}: {len(doc['pairs'])} pairs, {m_px:.3f} m/px, rot {math.degrees(np.angle(a)):.1f} deg, "
          f"residuals m {entry['fit']['resid_m']}", flush=True)


def prune():
    """Drop plan overlays whose fit was deleted."""
    have = {os.path.basename(p)[:-5] for p in glob.glob(os.path.join(DB, "*.json"))}
    for dep_path in glob.glob(os.path.join(WEB, "*", "depictions.json")):
        deps = json.load(open(dep_path))
        keep = [d for d in deps["depictions"] if d.get("kind") != "plan" or (d.get("fit") or {}).get("doc") in have]
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


def main(args):
    paths = [os.path.join(DB, a + ".json") for a in args] or sorted(glob.glob(os.path.join(DB, "*.json")))
    for p in paths:
        if not os.path.exists(p):
            continue
        doc = json.load(open(p))
        dep = os.path.join(WEB, doc.get("site", ""), "depictions.json")
        done = os.path.exists(dep) and any((d.get("fit") or {}).get("at") == doc.get("at") and d.get("kind") == "plan"
                                           and (d.get("fit") or {}).get("doc") == os.path.basename(p)[:-5]
                                           for d in json.load(open(dep))["depictions"])
        if not done or args:
            try:
                build(doc)
            except SystemExit as e:
                print(e, flush=True)
    if not args:
        prune()


if __name__ == "__main__":
    main(sys.argv[1:])
