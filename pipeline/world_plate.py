"""Globe base in the style of a USGS plate: cream land, pale water, ink coastlines, dashed state lines, graticule.

Draws Natural Earth 1:50m layers (public domain) into one square Web Mercator texture.
usage: world_plate.py data/raw/world web/data/world.jpg [size]
"""
import json
import math
import os
import sys

from PIL import Image, ImageDraw

src, out = sys.argv[1], sys.argv[2]
S = int(sys.argv[3]) if len(sys.argv) > 3 else 4096
SS = 2  # supersample, then downscale for clean thin lines
N = S * SS
MAXLAT = 85.0511

PAPER = (243, 237, 220)
WATER = (205, 226, 224)
COAST = (92, 84, 76)
LAKE_EDGE = (120, 150, 150)
RIVER = (128, 166, 170)
STATE = (150, 138, 124)
GRAT = (176, 168, 152)


def xy(lon, lat):
    lat = max(-MAXLAT, min(MAXLAT, lat))
    x = (lon + 180) / 360 * N
    y = (1 - math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)) / math.pi) / 2 * N
    return x, y


def rings(geom):
    t, c = geom["type"], geom["coordinates"]
    if t == "Polygon":
        yield from c
    elif t == "MultiPolygon":
        for poly in c:
            yield from poly
    elif t == "LineString":
        yield c
    elif t == "MultiLineString":
        yield from c


def polys(geom):
    t, c = geom["type"], geom["coordinates"]
    return [c] if t == "Polygon" else c if t == "MultiPolygon" else []


def load(name):
    return json.load(open(os.path.join(src, name)))["features"]


img = Image.new("RGB", (N, N), WATER)
d = ImageDraw.Draw(img)
land, lakes = load("ne_50m_land.geojson"), load("ne_50m_lakes.geojson")
for f in land:
    for poly in polys(f["geometry"]):
        d.polygon([xy(*p[:2]) for p in poly[0]], fill=PAPER)
        for hole in poly[1:]:
            d.polygon([xy(*p[:2]) for p in hole], fill=WATER)
for f in lakes:
    for poly in polys(f["geometry"]):
        d.polygon([xy(*p[:2]) for p in poly[0]], fill=WATER)

# graticule every 10 degrees, under the ink lines
for lon in range(-180, 181, 10):
    d.line([xy(lon, -MAXLAT), xy(lon, MAXLAT)], fill=GRAT, width=SS)
for lat in range(-80, 81, 10):
    d.line([xy(-180, lat), xy(180, lat)], fill=GRAT, width=SS)

for f in load("ne_50m_rivers.geojson"):
    for line in rings(f["geometry"]):
        d.line([xy(*p[:2]) for p in line], fill=RIVER, width=SS)


def dashed(pts, dash=10 * SS, gap=6 * SS, **kw):
    acc, on = 0.0, True
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        pos = 0.0
        while pos < L:
            step = min((dash if on else gap) - acc, L - pos)
            if on:
                a, b = pos / L, (pos + step) / L
                d.line([(x0 + (x1 - x0) * a, y0 + (y1 - y0) * a), (x0 + (x1 - x0) * b, y0 + (y1 - y0) * b)], **kw)
            pos += step
            acc += step
            if acc >= (dash if on else gap) - 1e-9:
                acc, on = 0.0, not on


for f in load("ne_50m_admin1_lines.geojson"):
    if f["properties"].get("ADM0_A3") not in ("USA", "CAN"):
        continue
    for line in rings(f["geometry"]):
        dashed([xy(*p[:2]) for p in line], fill=STATE, width=SS)

for f in lakes:
    for line in rings(f["geometry"]):
        d.line([xy(*p[:2]) for p in line], fill=LAKE_EDGE, width=SS)
for f in land:
    for line in rings(f["geometry"]):
        d.line([xy(*p[:2]) for p in line], fill=COAST, width=2 * SS)

img = img.resize((S, S), Image.LANCZOS)
img.save(out, quality=88, optimize=True)
print("wrote", out, img.size, os.path.getsize(out) // 1024, "KB")
