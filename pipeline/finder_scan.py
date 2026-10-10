"""Finder area scan: 2 m DEM tiles (cached), OSM modern mask from the local extract, mound + ring detectors.

Tiles follow scan.py (4 km core + 560 m pad, Web Mercator, 2 m/px), so the existing data/scan/ross tiles are reused.
Each tile's detections go to data/scan/<name>/det/<ty>_<tx>.json; a killed run resumes where it stopped.

usage:
  finder_scan.py run <name> [lon0 lat0 lon1 lat1]   (box defaults to finder_common.AREAS[name]; RINGS=0 skips rings)
  finder_scan.py point <lon> <lat>                  detections around one point (1 km crop), for tuning on known sites
Python: AreaScan(name).candidates() -> all detections of the area (mounds + rings), with lon/lat.
"""
import json
import math
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aw  # noqa: E402
import finder_mounds as fm  # noqa: E402
import finder_osm  # noqa: E402
from finder_common import AREAS, ROOT, terrain_class  # noqa: E402

TILE_M, PAD_M, PX_M = 4000.0, 560.0, 2.0
RING_MIN_SNR = 1.5  # small rings below this are not kept on disk (the old scan kept everything: 25 MB of noise);
# big rings (r >= 60 m) are kept down to snr 0.3: the known great circles score 0.85-1.0


def boxes_path(name):
    return os.path.join(ROOT, "data", "scan", name, "area.json")


class AreaScan:
    def __init__(self, name, box=None):
        self.name = name
        self.d = os.path.join(ROOT, "data", "scan", name)
        os.makedirs(os.path.join(self.d, "tiles"), exist_ok=True)
        os.makedirs(os.path.join(self.d, "det"), exist_ok=True)
        if box is None:
            if name in AREAS:
                box = AREAS[name][:4]
            else:
                box = json.load(open(boxes_path(name)))["area"]
        self.box = tuple(box)
        aw.save_json(boxes_path(name), {"area": list(self.box), "px_m": PX_M, "tile_m": TILE_M, "pad_m": PAD_M})
        lon0, lat0, lon1, lat1 = self.box
        self.x0, y0 = aw.to_merc(lon0, lat0)
        x1, self.y1 = aw.to_merc(lon1, lat1)
        self.k = 1 / aw.ground_scale((lat0 + lat1) / 2)
        self.tile, self.pad = TILE_M * self.k, PAD_M * self.k
        self.nx, self.ny = int(math.ceil((x1 - self.x0) / self.tile)), int(math.ceil((self.y1 - y0) / self.tile))
        self.pw = int((TILE_M + 2 * PAD_M) / PX_M)
        self.core = (int(PAD_M / PX_M), int((PAD_M + TILE_M) / PX_M))
        self._cache = {}

    def bbox(self, ty, tx):
        bx0, by1 = self.x0 + tx * self.tile - self.pad, self.y1 - ty * self.tile + self.pad
        return (bx0, by1 - self.tile - 2 * self.pad, bx0 + self.tile + 2 * self.pad, by1)

    def tile_of(self, lon, lat):
        gx, gy = aw.to_merc(lon, lat)
        return int((self.y1 - gy) // self.tile), int((gx - self.x0) // self.tile)

    def load(self, ty, tx):
        """z (float32), modern mask, valid mask for a tile; fetched and cached on first use."""
        if (ty, tx) in self._cache:
            return self._cache[(ty, tx)]
        path = os.path.join(self.d, "tiles", f"{ty}_{tx}.npz")
        bbox = self.bbox(ty, tx)
        if os.path.exists(path):
            f = np.load(path)
            z, mask = f["z"].astype(np.float32), f["mask"]
        else:
            z = aw.fetch_dem(bbox, self.pw, self.pw).astype(np.float32)
            mask = aw.modern_mask(bbox, self.pw, self.pw, PX_M, ways=finder_osm.ways(bbox))
            np.savez_compressed(path, z=z, mask=mask)
        if np.isnan(z).mean() > 0.5:
            out = (None, None, None)
        else:
            valid = ~mask & ~aw.water_mask(z, PX_M) & np.isfinite(z)
            out = (aw.fill_nan(z).astype(np.float32), mask, valid)
        self._cache = {(ty, tx): out}
        return out

    def px_to_lonlat(self, ty, tx, row, col):
        bx0, by1 = self.x0 + tx * self.tile - self.pad, self.y1 - ty * self.tile + self.pad
        return aw.to_lonlat(bx0 + (col + 0.5) * PX_M * self.k, by1 - (row + 0.5) * PX_M * self.k)

    def lonlat_to_px(self, ty, tx, lon, lat):
        gx, gy = aw.to_merc(lon, lat)
        bx0, by1 = self.x0 + tx * self.tile - self.pad, self.y1 - ty * self.tile + self.pad
        return (by1 - gy) / (PX_M * self.k) - 0.5, (gx - bx0) / (PX_M * self.k) - 0.5

    def terrain_at(self, lon, lat):
        ty, tx = self.tile_of(lon, lat)
        if not (0 <= ty < self.ny and 0 <= tx < self.nx):
            return None
        z, mask, valid = self.load(ty, tx)
        if z is None:
            return None
        r, c = (int(round(v)) for v in self.lonlat_to_px(ty, tx, lon, lat))
        if not valid[r, c] and not mask[r, c]:  # water or no data (masked modern ground is kept)
            return None
        return terrain_class(z, PX_M, r, c)

    # ------------------------------------------------------------------ detection

    def detect_tile(self, ty, tx, rings=True):
        out_p = os.path.join(self.d, "det", f"{ty}_{tx}.json")
        if os.path.exists(out_p):
            return json.load(open(out_p))
        t0 = time.time()
        z, mask, valid = self.load(ty, tx)
        res = {"tile": [ty, tx], "mounds": [], "rings": []}
        if z is None:
            aw.save_json(out_p, res)
            return res
        pk = fm.detect(z, valid, PX_M, core=self.core)
        fm.measure(z, valid, PX_M, pk)
        for p in pk:
            if not fm.keep(p):
                continue
            lon, lat = self.px_to_lonlat(ty, tx, p["row"], p["col"])
            res["mounds"].append({"lon": round(lon, 6), "lat": round(lat, 6), "D": p["D"], "score": round(p["score"], 3),
                                  **{k: p[k] for k in ("h_m", "diam_m", "round", "elong", "flat_top", "snr", "rough_m",
                                                       "base_slope", "modern_m")}})
        t1 = time.time()
        if rings:
            res["rings"] = self.ring_tile(z, valid, ty, tx)
            res["rings_v"] = 2
        res["seconds"] = [round(t1 - t0, 1), round(time.time() - t1, 1)]
        aw.save_json(out_p, res)
        return res

    def ring_tile(self, z, valid, ty, tx):
        """The old ring scanner (scan.py stage 1 + verify), unchanged, plus the ring band's plane slope."""
        import scan
        from scipy.ndimage import maximum_filter
        rid, maps = scan.scan_tile(z, valid, PX_M)
        raw = []
        for r, sc, mn, cv, fct in maps:
            pm = PX_M * fct
            c0, c1 = int(PAD_M / pm), int((PAD_M + TILE_M) / pm)
            s0 = np.where(np.isfinite(sc), sc, -9.0)
            peak = (s0 == maximum_filter(s0, size=max(3, int(r / pm)))) & (s0 >= scan.MIN_SCORE_M)
            peak[:c0], peak[c1:], peak[:, :c0], peak[:, c1:] = False, False, False, False
            for row, col in zip(*np.nonzero(peak)):
                R0, C0 = (row + 0.5) * fct - 0.5, (col + 0.5) * fct - 0.5
                raw.append({"row": R0, "col": C0, "x": C0 * PX_M, "y": -R0 * PX_M, "r_m": r,
                            "stage1_m": round(float(sc[row, col]), 3)})
        one = scan.merge(raw, "stage1_m")
        lrm = aw.local_relief(z, PX_M)
        lrm[~valid] = np.nan
        out = []
        for c in scan.verify(lrm, one, PX_M):
            if c["score_m"] <= 0.02 or c["snr"] < (0.3 if c["r_m"] >= 60 else RING_MIN_SNR):
                continue
            lon, lat = self.px_to_lonlat(ty, tx, c["row"], c["col"])
            out.append({"lon": round(lon, 6), "lat": round(lat, 6), "r_m": c["r_m"], "score_m": c["score_m"],
                        "snr": c["snr"], "rough_m": c["rough_m"], "sectors": c["sectors"], "stage1_m": c["stage1_m"],
                        "band_slope": round(self._band_slope(z, c), 2)})
        return out

    @staticmethod
    def _band_slope(z, c, n=48):
        """Slope (degrees) of a plane through the ground on the ring line: geometric works sit on level terraces."""
        th = np.arange(n) * 2 * np.pi / n
        rr = c["row"] - np.sin(th) * c["r_m"] / PX_M
        cc = c["col"] + np.cos(th) * c["r_m"] / PX_M
        ri, ci = np.clip(np.rint(rr).astype(int), 0, z.shape[0] - 1), np.clip(np.rint(cc).astype(int), 0, z.shape[1] - 1)
        v = z[ri, ci].astype(float)
        X = np.stack([np.ones(n), np.cos(th) * c["r_m"], np.sin(th) * c["r_m"]], 1)
        coef, *_ = np.linalg.lstsq(X, v, rcond=None)
        return math.degrees(math.atan(math.hypot(coef[1], coef[2])))

    def tiles_in(self, poly_path=None):
        """Tiles whose core touches a polygon (GeoJSON features, lon/lat); all tiles if no polygon."""
        if not poly_path:
            return [(ty, tx) for ty in range(self.ny) for tx in range(self.nx)]
        from PIL import Image, ImageDraw
        d = json.load(open(poly_path))
        S = 8  # raster cells per tile
        im = Image.new("L", (self.nx * S, self.ny * S), 0)
        dr = ImageDraw.Draw(im)
        for f in d["features"]:
            g = f["geometry"]
            polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
            for poly in polys:
                xy = []
                for lon, lat in poly[0]:
                    gx, gy = aw.to_merc(lon, lat)
                    xy.append(((gx - self.x0) / self.tile * S, (self.y1 - gy) / self.tile * S))
                dr.polygon(xy, fill=255)
        a = np.asarray(im).reshape(self.ny, S, self.nx, S).max((1, 3))
        return [(ty, tx) for ty in range(self.ny) for tx in range(self.nx) if a[ty, tx]]

    def run(self, rings=True, poly=None):
        tiles = self.tiles_in(poly)
        mod = os.environ.get("TILE_MOD")  # "n,i": only tiles whose row % n == i (parallel runs)
        if mod:
            n, i = map(int, mod.split(","))
            tiles = [t for t in tiles if t[0] % n == i]
        print(f"{self.name}: {len(tiles)} of {self.nx} x {self.ny} tiles at {PX_M} m/px, box {self.box}", flush=True)
        for ty, tx in tiles:
            if True:
                done = os.path.exists(os.path.join(self.d, "det", f"{ty}_{tx}.json"))
                t0 = time.time()
                r = self.detect_tile(ty, tx, rings)
                if not done:
                    print(f"  tile {ty},{tx}: {len(r['mounds'])} mounds, {len(r['rings'])} rings, "
                          f"{time.time() - t0:.0f}s {r.get('seconds')}", flush=True)

    def km2(self):
        """Scanned ground: tile cores that have detections, clipped to the box (km2)."""
        lon0, lat0, lon1, lat1 = self.box
        bx0, by0 = aw.to_merc(lon0, lat0)
        bx1, by1 = aw.to_merc(lon1, lat1)
        tot = 0.0
        for ty in range(self.ny):
            for tx in range(self.nx):
                if not os.path.exists(os.path.join(self.d, "det", f"{ty}_{tx}.json")):
                    continue
                cx0, cy1 = self.x0 + tx * self.tile, self.y1 - ty * self.tile
                cx1, cy0 = cx0 + self.tile, cy1 - self.tile
                w = max(0.0, min(cx1, bx1) - max(cx0, bx0))
                h = max(0.0, min(cy1, by1) - max(cy0, by0))
                tot += w * h / self.k ** 2 / 1e6
        return tot

    def candidates(self):
        """All detections in the area (inside the box), mounds and rings, from the per-tile files."""
        lon0, lat0, lon1, lat1 = self.box
        ms, rs = [], []
        for ty in range(self.ny):
            for tx in range(self.nx):
                p = os.path.join(self.d, "det", f"{ty}_{tx}.json")
                if not os.path.exists(p):
                    continue
                for _ in range(5):  # a ring re-run may be rewriting the file
                    try:
                        r = json.load(open(p))
                        break
                    except json.JSONDecodeError:
                        time.sleep(1)
                ms += [m for m in r["mounds"] if lon0 <= m["lon"] <= lon1 and lat0 <= m["lat"] <= lat1]
                rs += [m for m in r["rings"] if lon0 <= m["lon"] <= lon1 and lat0 <= m["lat"] <= lat1]
        return ms, rs


def point_detect(lon, lat, half_m=500.0):
    """Mound detections in a crop around one point (same detector and mask as the tiles)."""
    bbox = aw.site_bbox(lon, lat, 2 * half_m, 2 * half_m)
    n = int(2 * half_m / PX_M)
    cache = os.path.join(ROOT, "data", "finder", "dem2m")
    os.makedirs(cache, exist_ok=True)
    p = os.path.join(cache, f"{lon:.5f}_{lat:.5f}_{int(half_m)}.npz")
    if os.path.exists(p):
        f = np.load(p)
        z, mask = f["z"], f["mask"]
    else:
        z = aw.fetch_dem(bbox, n, n).astype(np.float32)
        mask = aw.modern_mask(bbox, n, n, PX_M, ways=finder_osm.ways(bbox))
        np.savez_compressed(p, z=z, mask=mask)
    valid = ~mask & ~aw.water_mask(z, PX_M) & np.isfinite(z)
    z = aw.fill_nan(z).astype(np.float32)
    pk = fm.detect(z, valid, PX_M)
    fm.measure(z, valid, PX_M, pk)
    k = 1 / aw.ground_scale(lat)
    out = []
    for q in pk:
        if not fm.keep(q):
            continue
        qlon, qlat = aw.to_lonlat(bbox[0] + (q["col"] + 0.5) * PX_M * k, bbox[3] - (q["row"] + 0.5) * PX_M * k)
        out.append({"lon": qlon, "lat": qlat, "D": q["D"], "score": q["score"],
                    **{kk: q[kk] for kk in ("h_m", "diam_m", "round", "elong", "flat_top", "snr", "rough_m",
                                            "base_slope", "modern_m")}})
    return out


if __name__ == "__main__":
    a = sys.argv
    if a[1] == "run":
        box = tuple(map(float, a[3:7])) if len(a) >= 7 else None
        AreaScan(a[2], box).run(rings=os.environ.get("RINGS", "1") != "0", poly=os.environ.get("POLY"))
    elif a[1] == "rings":  # recompute the ring stage only, keeping the mound detections
        sc = AreaScan(a[2])
        for ty, tx in sc.tiles_in(os.environ.get("POLY")):
            p = os.path.join(sc.d, "det", f"{ty}_{tx}.json")
            if not os.path.exists(p):
                continue
            r = json.load(open(p))
            if r.get("rings_v") == 2:
                continue
            z, mask, valid = sc.load(ty, tx)
            t0 = time.time()
            r["rings"] = sc.ring_tile(z, valid, ty, tx) if z is not None else []
            r["rings_v"] = 2
            aw.save_json(p, r)
            print(f"  rings {ty},{tx}: {len(r['rings'])} in {time.time() - t0:.0f}s", flush=True)
    elif a[1] == "fetch":  # DEM + mask tiles only (no detection): lets held-out areas be prepared unseen
        sc = AreaScan(a[2], tuple(map(float, a[3:7])) if len(a) >= 7 else None)
        for ty, tx in sc.tiles_in(os.environ.get("POLY")):
            if True:
                t0 = time.time()
                sc.load(ty, tx)
                print(f"  {a[2]} tile {ty},{tx} ready {time.time() - t0:.0f}s", flush=True)
    elif a[1] == "point":
        for q in sorted(point_detect(float(a[2]), float(a[3])), key=lambda q: -q["score"])[:20]:
            print(q)
