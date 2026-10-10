"""Wide LiDAR relief previews with a labelled metre grid, for finding an earthwork whose coordinates are only roughly known.

usage: preview.py <catalog.json> <out_dir> [--ids a,b,c] [--tier B,C] [--sheet N]
For each site: relief over its preview_box_m (coarse: about 4-8 m per pixel), a grid every 500 m labelled in metres east/north of the
catalogue coordinate (the cross), saved as <out_dir>/<id>.jpg. --sheet N also tiles N previews per contact sheet (sheet_<k>.jpg),
so a batch can be looked at in one go and the earthwork's offset read straight off the grid.
Re-centring a site: add the east/north offset to the coordinate in the catalogue (111 320 m per degree of latitude,
111 320 * cos(lat) per degree of longitude) and check again with a tighter box.
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("AW_DEM", "s3")
import aw  # noqa: E402
import harvest  # noqa: E402
from build_site import duotone  # noqa: E402


def dem(site, box, n):
    bbox = aw.site_bbox(site["lon"], site["lat"], box, box)
    reg = harvest.region(site["lon"], site["lat"])
    if reg == "US":
        import usgs
        iso = site.get("iso") or ""
        return usgs.read_dem(bbox, n, n, site["lon"], site["lat"], coarse=True, states=[iso[3:]] if iso.startswith("US-") else ())[0]
    s = dict(site, width_m=box, height_m=box)
    return harvest.dem_for(s, bbox, n, n)[0]


def preview(site, out_dir, n=1000):
    box = int(site.get("preview_box_m") or site.get("box_m") or 2000)
    z = dem(site, box, n)
    px = box / n
    img, _ = aw.render_relief(z, px, ignore=aw.water_mask(z, px), radius_m=max(24.0, 6 * px))
    im = Image.fromarray(duotone(img).astype(np.uint8)).convert("RGB")
    d = ImageDraw.Draw(im)
    half = box / 2
    for m in range(-int(half // 500) * 500, int(half) + 1, 500):  # grid lines every 500 m
        c = n / 2 + m / px
        d.line([(c, 0), (c, n)], fill=(206, 46, 78) if m == 0 else (206, 120, 130), width=1)
        d.line([(0, n - c), (n, n - c)], fill=(206, 46, 78) if m == 0 else (206, 120, 130), width=1)
        d.text((c + 2, 2), f"{m:+d}E" if m else "E0", fill=(120, 20, 40))
        d.text((2, n - c + 2), f"{m:+d}N" if m else "N0", fill=(120, 20, 40))
    d.rectangle([0, 0, n - 1, n - 1], outline=(90, 80, 70))
    d.text((8, n - 14), f"{site['id']}  box {box} m  (grid 500 m)", fill=(20, 20, 20))
    os.makedirs(out_dir, exist_ok=True)
    im.save(os.path.join(out_dir, f"{site['id']}.jpg"), quality=84)
    return im


def main(argv):
    cat = json.load(open(argv[0]))
    out = argv[1]
    ids = argv[argv.index("--ids") + 1].split(",") if "--ids" in argv else None
    tiers = argv[argv.index("--tier") + 1].split(",") if "--tier" in argv else None
    sheet = int(argv[argv.index("--sheet") + 1]) if "--sheet" in argv else 0
    todo = [s for s in cat if (not ids or s["id"] in ids) and (not tiers or s.get("tier") in tiers)]
    done = []
    for s in todo:
        try:
            done.append((s["id"], preview(s, out)))
            print(s["id"], "ok", flush=True)
        except Exception as e:
            print(s["id"], "FAILED:", type(e).__name__, str(e)[:120], flush=True)
    if sheet:
        for k in range(0, len(done), sheet):
            chunk = done[k:k + sheet]
            cols = 3 if sheet > 4 else 2
            rows = math.ceil(len(chunk) / cols)
            S = Image.new("RGB", (cols * 640, rows * 640), "white")
            for i, (sid, im) in enumerate(chunk):
                S.paste(im.resize((634, 634)), ((i % cols) * 640, (i // cols) * 640))
            S.save(os.path.join(out, f"sheet_{k // sheet}.jpg"), quality=84)


if __name__ == "__main__":
    main(sys.argv[1:])
