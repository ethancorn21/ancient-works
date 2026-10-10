"""Gridded preview of an image (or a crop of it) for reading off pixel coordinates.
usage: grid.py in.jpg out.jpg [x0 y0 x1 y1] [width]   coordinates printed on the grid are in ORIGINAL pixels"""
import sys
from PIL import Image, ImageDraw
im = Image.open(sys.argv[1]).convert("RGB")
box = tuple(map(int, sys.argv[3:7])) if len(sys.argv) >= 7 else (0, 0, im.width, im.height)
W = int(sys.argv[7]) if len(sys.argv) >= 8 else 1000
c = im.crop(box); k = W / c.width
s = c.resize((W, int(c.height * k))); d = ImageDraw.Draw(s)
span = box[2] - box[0]
step = next(v for v in (25, 50, 100, 200, 250, 500, 1000) if span / v <= 14)
x = (box[0] // step + 1) * step
while x < box[2]:
    X = (x - box[0]) * k; d.line([(X, 0), (X, s.height)], fill=(220, 0, 0), width=1); d.text((X + 2, 2), str(x), fill=(220, 0, 0)); x += step
y = (box[1] // step + 1) * step
while y < box[3]:
    Y = (y - box[1]) * k; d.line([(0, Y), (W, Y)], fill=(0, 0, 220), width=1); d.text((2, Y + 2), str(y), fill=(0, 0, 220)); y += step
s.save(sys.argv[2], quality=88); print(s.size, "step", step)
