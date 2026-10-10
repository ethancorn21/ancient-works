"""Debug picture: relief + modern mask (blue) + fitted plate walls (amber). usage: show_fit.py site.json out.png"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aw
from fit_plate import sample_walls, affine_to_ground
site = json.load(open(sys.argv[1])); d0 = os.path.dirname(sys.argv[1]); px_m = site.get("px_m", 1.0)
z = np.load(os.path.join(d0, "dem.npy")); mask = np.load(os.path.join(d0, "modern_mask.npy"))
img, _ = aw.render_relief(z, px_m)
rgb = np.stack([img] * 3, -1).astype(float)
rgb[mask] = rgb[mask] * 0.6 + np.array([40, 80, 200]) * 0.4
im = Image.fromarray(rgb.astype(np.uint8)); dr = ImageDraw.Draw(im)
p = site["plate"]; f = p["fit"]; pts = sample_walls(p["walls"]); u0, v0 = pts.mean(0)
for line in p["walls"]:
    a = f["affine"]
    en = affine_to_ground(np.array(line, float), u0, v0, [[a[0], a[1]], [a[2], a[3]]], a[4:6])
    dr.line([((e + site["width_m"] / 2) / px_m, (site["height_m"] / 2 - n) / px_m) for e, n in en], fill=(255, 190, 60), width=3)
im.save(sys.argv[2]); print(im.size)
