"""Export a finished scan for the page: the strongest candidates with a relief crop each.

usage: export_scan.py <name> <label> [max_n]
reads data/scan/<name>/candidates.json (+ specs/known_<name>.json if present)
writes web/data/scan/<name>/{candidates.json, c/<id>.jpg} and the entry in web/data/scans.json
"""
import json
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aw  # noqa: E402
from build_site import duotone  # noqa: E402
from scan_view import Scan, dist_m, matches  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CROP_PX = 360


def main(name, label, max_n=150):
    sc = Scan(name)
    out = os.path.join(ROOT, "web", "data", "scan", name)
    os.makedirs(os.path.join(out, "c"), exist_ok=True)
    for f in os.listdir(os.path.join(out, "c")):
        os.remove(os.path.join(out, "c", f))
    kp = os.path.join(ROOT, "specs", f"known_{name}.json")
    known = json.load(open(kp)) if os.path.exists(kp) else []
    picked = sc.cands[:max_n]
    hit = {c["id"]: k["name"] for k in known for c in matches(sc, k)}
    rows = []
    for i, c in enumerate(picked):
        half = max(150.0, 3.0 * c["r_m"])
        z, mask, bbox = sc.crop(c["lon"], c["lat"], half)
        g, clip = aw.render_relief(z, sc.px_m, ignore=mask)
        im = Image.fromarray(duotone(g).astype(np.uint8))
        im.thumbnail((CROP_PX, CROP_PX), Image.LANCZOS)
        im.save(os.path.join(out, "c", f"{c['id']}.jpg"), quality=84, optimize=True)
        rows.append({**{k: c[k] for k in ("id", "lon", "lat", "r_m", "score_m", "snr", "rough_m", "sectors")},
                     "rank": i + 1, "known": hit.get(c["id"]), "crop": f"c/{c['id']}.jpg",
                     "corners": [[round(v, 6) for v in p] for p in aw.corners(bbox)], "clip_m": round(float(clip), 2)})
    lon0, lat0, lon1, lat1 = sc.meta["area"]
    w_km = dist_m(sc, (lon0, lat0), (lon1, lat0)) / 1000
    h_km = dist_m(sc, (lon0, lat0), (lon0, lat1)) / 1000
    entry = {"name": name, "label": label, "area": sc.meta["area"], "size_km": [round(w_km, 1), round(h_km, 1)],
             "px_m": sc.px_m, "radii_m": sc.meta["radii_m"], "n_total": len(sc.cands), "n_shown": len(rows),
             "known": [{"name": k["name"], "lon": k["lon"], "lat": k["lat"], "r_m": k.get("r_m", 0),
                        "expected": bool(k.get("expected")), "note": k.get("note", "")} for k in known]}
    aw.save_json(os.path.join(out, "candidates.json"), {**entry, "candidates": rows})
    sp = os.path.join(ROOT, "web", "data", "scans.json")
    scans = json.load(open(sp))["scans"] if os.path.exists(sp) else []
    scans = [s for s in scans if s["name"] != name] + [entry]
    aw.save_json(sp, {"scans": scans})
    kb = sum(os.path.getsize(os.path.join(out, "c", f)) for f in os.listdir(os.path.join(out, "c"))) // 1024
    print(f"{name}: {len(rows)} of {len(sc.cands)} candidates exported, crops {kb} KB")


if __name__ == "__main__":
    a = sys.argv
    main(a[1], a[2], *(int(v) for v in a[3:4]))
