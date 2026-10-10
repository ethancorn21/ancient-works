"""Preview: site relief with the exported plate ink on top. usage: composite.py <site_id> out.png [crop x0 y0 x1 y1 in relief px] [width]"""
import sys
from PIL import Image
sid, out = sys.argv[1], sys.argv[2]
d = f"web/data/sites/{sid}/"
rel = Image.open(d + "relief.jpg").convert("RGBA")
import json, os
e = next(s for s in json.load(open("web/data/sites.json"))["sites"] if s["id"] == sid)
if e.get("plate", {}).get("warped"):
    ink = Image.open(d + e["plate"]["ink"]).convert("RGBA").resize(rel.size)
    rel = Image.alpha_composite(rel, ink)
if len(sys.argv) >= 7:
    rel = rel.crop(tuple(map(int, sys.argv[3:7])))
W = int(sys.argv[7]) if len(sys.argv) >= 8 else 1200
rel = rel.resize((W, int(rel.height * W / rel.width)))
rel.convert("RGB").save(out); print(rel.size)
