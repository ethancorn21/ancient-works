"""Export one site for the globe: relief + imagery images, plate ink/paper images, and its entry in sites.json.

usage: build_site.py data/sites/<id>/site.json [--refresh-imagery]
Writes web/data/sites/<id>/{relief.jpg,imagery.jpg,plate_ink.png,plate_paper.jpg} and updates web/data/sites.json.
"""
import json
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aw  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, "web", "data")
INK = (255, 196, 92)  # warm gold reads on both grey relief and colour imagery


def plate_ink(scan):
    """Plate scan -> RGBA where alpha follows ink darkness and paper turns transparent."""
    g = np.asarray(scan.convert("L"), dtype=np.float64)
    paper, ink = np.percentile(g, 85), np.percentile(g, 2)
    # paper grain and the engraver's faint ground shading sit just below paper tone; drop them
    a = np.clip((paper - g) / max(paper - ink, 1) * 1.35 - 0.18, 0, 1) ** 0.9
    out = np.zeros(g.shape + (4,), np.uint8)
    out[..., :3] = INK
    out[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def main(path, refresh_imagery=False):
    sdir = os.path.dirname(path)
    site = json.load(open(path))
    sid = site["id"]
    out = os.path.join(WEB, "sites", sid)
    os.makedirs(out, exist_ok=True)
    px_m = site.get("px_m", 1.0)
    bbox = aw.site_bbox(site["lon"], site["lat"], site["width_m"], site["height_m"])
    w, h = int(site["width_m"] / px_m), int(site["height_m"] / px_m)

    dem_cache = os.path.join(sdir, "dem.npy")
    if os.path.exists(dem_cache):
        z = np.load(dem_cache)
    else:
        z = aw.fetch_dem(bbox, w, h)
        np.save(dem_cache, z)
    img, clip = aw.render_relief(z, px_m)
    Image.fromarray(img).save(os.path.join(out, "relief.jpg"), quality=84, optimize=True)

    imagery = os.path.join(out, "imagery.jpg")
    if refresh_imagery or not os.path.exists(imagery):
        aw.fetch_imagery(bbox, min(w, 4096), min(h, 4096)).save(imagery, quality=80, optimize=True)

    entry = {k: site[k] for k in ("id", "name", "aka", "place", "lon", "lat", "status", "summary", "notes")
             if k in site}
    entry["corners"] = aw.corners(bbox)
    entry["relief_clip_m"] = round(clip, 2)
    entry["size_m"] = [site["width_m"], site["height_m"]]
    if "plate" in site and "corners" in site["plate"]:
        p = site["plate"]
        scan = Image.open(os.path.join(sdir, p["image"])).convert("RGB")
        plate_ink(scan).save(os.path.join(out, "plate_ink.png"), optimize=True)
        scan.save(os.path.join(out, "plate_paper.jpg"), quality=82, optimize=True)
        entry["plate"] = {"corners": p["corners"], "source": p["source"], "fit": p.get("fit"),
                          "label": p.get("label", "")}

    index_path = os.path.join(WEB, "sites.json")
    index = json.load(open(index_path)) if os.path.exists(index_path) else {"sites": []}
    index["sites"] = [s for s in index["sites"] if s["id"] != sid] + [entry]
    index["sites"].sort(key=lambda s: s["name"])
    aw.save_json(index_path, index)
    sizes = {f: os.path.getsize(os.path.join(out, f)) // 1024 for f in os.listdir(out)}
    print(sid, "relief clip", round(clip, 2), "m;", sizes, "KB")


if __name__ == "__main__":
    main(sys.argv[1], "--refresh-imagery" in sys.argv)
