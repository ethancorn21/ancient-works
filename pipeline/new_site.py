"""Create data/sites/<id>/site.json + plate_scan.jpg from a traced spec.

usage: new_site.py spec.json
spec: {id, name, aka, place, lon, lat, width_m, height_m, status, summary, notes,
       plate: {leaf: "data/plates/sd_n129.jpg", crop: [x0,y0,x1,y1], label, source, m_per_px,
               guess: {rot_deg, tx, ty}, rot_max_deg, search_m,
               walls: [ [[x,y],...] | {"circle": [cx, cy, r]} | {"arc": [cx, cy, r, deg0, deg1]} ]}}
Wall coordinates are in leaf (full scan) pixels; they are shifted into crop pixels here.
"""
import json
import math
import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def to_lines(walls, ox, oy):
    out = []
    for w in walls:
        if isinstance(w, dict) and ("circle" in w or "arc" in w):
            cx, cy, r, a0, a1 = (w["circle"] + [0, 360]) if "circle" in w else w["arc"]
            n = max(8, int(abs(a1 - a0) / 5))
            out.append([[round(cx - ox + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), 1),
                         round(cy - oy - r * math.sin(math.radians(a0 + (a1 - a0) * i / n)), 1)] for i in range(n + 1)])
        else:
            out.append([[x - ox, y - oy] for x, y in w])
    return out


def main(spec_path):
    spec = json.load(open(spec_path))
    sdir = os.path.join(ROOT, "data", "sites", spec["id"])
    os.makedirs(sdir, exist_ok=True)
    p = spec["plate"]
    x0, y0, x1, y1 = p["crop"]
    im = Image.open(os.path.join(ROOT, p["leaf"])).convert("RGB")
    if p.get("blank"):  # paint over parts of the plate that are not map (sections, titles), in paper colour
        from PIL import ImageDraw, ImageStat
        paper = tuple(int(v) for v in ImageStat.Stat(im.crop((x0, y0, x1, y1))).median)
        d = ImageDraw.Draw(im)
        for bx0, by0, bx1, by1 in p["blank"]:
            d.rectangle((bx0, by0, bx1, by1), fill=paper)
    im.crop((x0, y0, x1, y1)).save(os.path.join(sdir, "plate_scan.jpg"), quality=92)
    site = {k: v for k, v in spec.items() if k != "plate"}
    site["plate"] = {k: v for k, v in p.items() if k not in ("leaf", "crop", "walls", "control", "blank")}
    site["plate"]["image"] = "plate_scan.jpg"
    site["plate"]["walls"] = to_lines(p["walls"], x0, y0)
    if p.get("control"):  # [u_leaf, v_leaf, col, row] -> crop px
        site["plate"]["control"] = [[u - x0, v - y0, c, r] for u, v, c, r in p["control"]]
    site["plate"]["leaf_crop"] = [p["leaf"], p["crop"]]
    # keep a previous fit's dem/mask caches valid only if the bbox is unchanged
    old = os.path.join(sdir, "site.json")
    if os.path.exists(old):
        o = json.load(open(old))
        if [o.get(k) for k in ("lon", "lat", "width_m", "height_m")] != [site.get(k) for k in ("lon", "lat", "width_m", "height_m")]:
            for f in ("dem.npy", "modern_mask.npy"):
                if os.path.exists(os.path.join(sdir, f)):
                    os.remove(os.path.join(sdir, f))
    json.dump(site, open(old, "w"), indent=1)
    print("wrote", old)


if __name__ == "__main__":
    main(sys.argv[1])
