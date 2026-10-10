"""Look at a finished scan: relief crops from the cached tiles with the candidate rings drawn on.

usage:
  scan_view.py <name> known <known.json> <out.png>      contact sheet of known sites, nearest candidate marked
  scan_view.py <name> top <n> <out.png>                 contact sheet of the n strongest candidates
crop() is also used by export_scan.py.
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aw  # noqa: E402
from scan import PAD_M, TILE_M  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Scan:
    def __init__(self, name):
        self.d = os.path.join(ROOT, "data", "scan", name)
        self.meta = json.load(open(os.path.join(self.d, "candidates.json")))
        lon0, lat0, lon1, lat1 = self.meta["area"]
        self.px_m = self.meta["px_m"]
        self.x0, _ = aw.to_merc(lon0, lat0)
        _, self.y1 = aw.to_merc(lon1, lat1)
        self.k = 1 / aw.ground_scale((lat0 + lat1) / 2)
        self.tile, self.pad = TILE_M * self.k, PAD_M * self.k
        self.cands = self.meta["candidates"]
        self._cache = {}

    def _tile(self, ty, tx):
        if (ty, tx) not in self._cache:
            f = np.load(os.path.join(self.d, "tiles", f"{ty}_{tx}.npz"))
            self._cache = {(ty, tx): (f["z"], f["mask"])}  # one tile in memory is enough for sorted access
        return self._cache[(ty, tx)]

    def crop(self, lon, lat, half_m):
        """DEM and mask around a point, from the tile whose core holds it. Returns z, mask, merc bbox."""
        gx, gy = aw.to_merc(lon, lat)
        tx, ty = int((gx - self.x0) // self.tile), int((self.y1 - gy) // self.tile)
        z, mask = self._tile(ty, tx)
        bx0, by1 = self.x0 + tx * self.tile - self.pad, self.y1 - ty * self.tile + self.pad
        mp = self.px_m * self.k
        c, r, h = (gx - bx0) / mp, (by1 - gy) / mp, half_m / self.px_m
        c0, r0 = int(max(0, c - h)), int(max(0, r - h))
        c1, r1 = int(min(z.shape[1], c + h)), int(min(z.shape[0], r + h))
        bbox = (bx0 + c0 * mp, by1 - r1 * mp, bx0 + c1 * mp, by1 - r0 * mp)
        return z[r0:r1, c0:c1], mask[r0:r1, c0:c1], bbox

    def to_px(self, bbox, shape, lon, lat):
        gx, gy = aw.to_merc(lon, lat)
        return (gx - bbox[0]) / (bbox[2] - bbox[0]) * shape[1], (bbox[3] - gy) / (bbox[3] - bbox[1]) * shape[0]


def panel(sc, lon, lat, half_m, title, mark=None, size=420):
    z, mask, bbox = sc.crop(lon, lat, half_m)
    g, _ = aw.render_relief(z, sc.px_m, ignore=mask)
    im = Image.fromarray(g).convert("RGB")
    s = size / max(im.size)
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    for c in sc.cands:
        x, y = sc.to_px(bbox, z.shape, c["lon"], c["lat"])
        if not (-50 < x < z.shape[1] + 50 and -50 < y < z.shape[0] + 50):
            continue
        rr = c["r_m"] / sc.px_m * s
        x, y = x * s, y * s
        col = (206, 46, 78) if c is mark else (40, 110, 200)
        d.ellipse((x - rr, y - rr, x + rr, y + rr), outline=col, width=2)
        d.text((x + rr + 2, y - 6), c["id"].split("-")[-1].lstrip("0") or "0", fill=col)
    d.rectangle((0, 0, im.width, 14), fill=(255, 255, 255))
    d.text((3, 1), title, fill=(0, 0, 0))
    return im


def sheet(panels, cols, out):
    w, h = max(p.width for p in panels), max(p.height for p in panels)
    rows = math.ceil(len(panels) / cols)
    S = Image.new("RGB", (cols * (w + 6), rows * (h + 6)), (255, 255, 255))
    for i, p in enumerate(panels):
        S.paste(p, ((i % cols) * (w + 6), (i // cols) * (h + 6)))
    S.save(out)
    print("wrote", out, S.size)


def dist_m(sc, a, b):
    ax, ay = aw.to_merc(*a)
    bx, by = aw.to_merc(*b)
    return math.hypot(ax - bx, ay - by) / sc.k


def matches(sc, kn):
    """Candidates that are this known ring: centre within half its radius (30 m at least), radius within 25%."""
    if not kn.get("expected") or not kn.get("r_m"):
        return []
    return [c for c in sc.cands if dist_m(sc, (c["lon"], c["lat"]), (kn["lon"], kn["lat"])) <= max(30, 0.5 * kn["r_m"])
            and abs(c["r_m"] / kn["r_m"] - 1) <= 0.25]


def main():
    name, mode = sys.argv[1], sys.argv[2]
    sc = Scan(name)
    rank = {c["id"]: i + 1 for i, c in enumerate(sc.cands)}
    print(f"{len(sc.cands)} candidates")
    if mode == "known":
        known, out = json.load(open(sys.argv[3])), sys.argv[4]
        panels = []
        for kn in known:
            hits = matches(sc, kn)
            best = min(hits, key=lambda c: rank[c["id"]]) if hits else None
            near = sum(dist_m(sc, (c["lon"], c["lat"]), (kn["lon"], kn["lat"])) < 400 for c in sc.cands)
            if not kn.get("expected"):
                msg = f"{kn['name']} (control): {near} candidates within 400 m"
            else:
                msg = f"{kn['name']}: " + (f"#{rank[best['id']]} of {len(sc.cands)}, r{best['r_m']} score {best["score_m"]} snr {best["snr"]}" if best else "MISSED")
            print(" ", msg)
            panels.append(panel(sc, kn["lon"], kn["lat"], max(400, 2.5 * kn.get("r_m", 0)), msg, best))
        sheet(panels, 3, out)
    else:
        n, out = int(sys.argv[3]), sys.argv[4]
        panels = [panel(sc, c["lon"], c["lat"], max(150, c["r_m"] * 2.5),
                        f"#{i + 1} r{c['r_m']} score {c['score_m']} snr {c['snr']}", c, size=300)
                  for i, c in enumerate(sc.cands[:n])]
        sheet(panels, 6, out)


if __name__ == "__main__":
    main()
