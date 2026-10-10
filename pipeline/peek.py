"""Quick look: relief image for lon lat width_m height_m [px_m] -> out.png"""
import sys
import numpy as np
from PIL import Image
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aw
lon, lat, wm, hm = map(float, sys.argv[1:5]); out = sys.argv[5]; px_m = float(sys.argv[6]) if len(sys.argv) > 6 else 1.0
bbox = aw.site_bbox(lon, lat, wm, hm)
w, h = int(wm / px_m), int(hm / px_m)
z = aw.fetch_dem(bbox, w, h)
img, clip = aw.render_relief(z, px_m)
Image.fromarray(img).save(out)
print("clip m", round(clip, 2), "size", w, h, "corners", aw.corners(bbox))
