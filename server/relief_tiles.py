"""Live LiDAR relief tiles for serve.py: /tiles/relief/{z}/{x}/{y}.png, z 12-17.

Never one upstream request per tile: tiles are grouped in chunks of CHUNK x CHUNK. A chunk's DEM is fetched
once (plus a margin for the gaussian, so chunk edges match), cached under data/tilecache/dem/, rendered once,
and tiles are cut from it; PNGs are cached under data/tilecache/relief/<style>/. Concurrent requests for tiles
of one chunk wait on one fetch. A 6 x 6 chunk plus margin stays under 2000 px, so a 3DEP chunk is one export.

Look: aw.render_relief (local relief + a little hillshade) with a FIXED clip, then build_site.duotone, so tiles
match each other and the per-site relief images. From z14 up the relief radius is RADIUS_M; at z12-13 a
pixel is 15-30 m on the ground, so the radius grows to 3 px and the clip with it: those zooms show the same
kind of picture for larger landforms, not earthworks.
"""
import io
import math
import os
import sys
import threading
import time
from collections import OrderedDict

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "pipeline"))
import aw  # noqa: E402
import build_site  # noqa: E402
import dem_sources  # noqa: E402

ZMIN, ZMAX = 12, 17
TILE, CHUNK = 256, 6
RADIUS_M, CLIP_M = 22.0, 1.2
STYLE = f"v1-r{RADIUS_M:g}-c{CLIP_M:g}"
CACHE = os.path.join(ROOT, "data", "tilecache")
DEM_DIR = os.path.join(CACHE, "dem")
PNG_DIR = os.path.join(CACHE, "relief", STYLE)
WORLD = 2 * math.pi * aw.R
RETRY_AFTER_S = 60  # a chunk whose fetch failed is not retried upstream for this long
KEEP_CHUNKS = 8     # rendered chunks kept in memory (about 12 MB each)


class Unavailable(Exception):
    """Upstream DEM service failed; the tile should be retried later (HTTP 503)."""


class Cancelled(Exception):
    """The browser dropped the request (the map moved on) before its chunk was fetched."""


class _Newest:
    """At most n upstream fetches at once; a free slot goes to the NEWEST waiter, and waiters whose browser has
    gone away leave the queue. Flying across the map asks for tiles at every zoom on the way; without this the
    stale ones would be fetched first and the view you stop at would wait behind them."""

    def __init__(self, n):
        self.free, self.cv, self.waiting, self.seq = n, threading.Condition(), set(), 0

    def acquire(self, alive):
        with self.cv:
            self.seq += 1
            me = self.seq
            self.waiting.add(me)
            try:
                while not (self.free > 0 and me == max(self.waiting)):
                    self.cv.wait(0.25)
                    if not alive():
                        raise Cancelled()
                self.free -= 1
            finally:
                self.waiting.discard(me)
                self.cv.notify_all()

    def release(self):
        with self.cv:
            self.free += 1
            self.cv.notify_all()


def _blank():
    buf = io.BytesIO()
    Image.new("RGBA", (TILE, TILE), (0, 0, 0, 0)).save(buf, "PNG", optimize=True)
    return buf.getvalue()


BLANK = _blank()
_lock = threading.Lock()
_chunk_locks = {}
_rendered = OrderedDict()   # (z, cx, cy) -> RGBA array, or None for "no data"
_failed = {}                # (z, cx, cy) -> (time, message)
_upstream = _Newest(2)  # polite: at most two DEM fetches at once


def _tile_bbox(z, x, y, n=1):
    ts = WORLD / 2 ** z
    x0, y1 = -WORLD / 2 + x * ts, WORLD / 2 - y * ts
    return (x0, y1 - n * ts, x0 + n * ts, y1)


def _geometry(z, cx, cy):
    """Chunk core bbox, Mercator px, ground px, relief radius/clip and margin (px) at this zoom."""
    core = _tile_bbox(z, cx * CHUNK, cy * CHUNK, CHUNK)
    mpx = (WORLD / 2 ** z) / TILE
    lat = aw.to_lonlat(0, (core[1] + core[3]) / 2)[1]
    gpx = mpx * aw.ground_scale(lat)
    radius = max(RADIUS_M, 3 * gpx)
    clip = CLIP_M * radius / RADIUS_M
    margin = int(math.ceil(3 * radius / gpx)) + 2
    return core, mpx, gpx, radius, clip, margin


def _dem_path(z, cx, cy):
    return os.path.join(DEM_DIR, str(z), f"{cx}_{cy}")


def _load_dem(z, cx, cy):
    p = _dem_path(z, cx, cy)
    if os.path.exists(p + ".empty"):
        return "empty"
    if os.path.exists(p + ".npz"):
        with np.load(p + ".npz") as f:
            if "cm" in f:  # centimetres above the chunk minimum (lossless to 1 cm, half the size of float32)
                cm = f["cm"].astype(np.float32)
                return np.where(cm == 65535, np.nan, cm / 100 + float(f["base"])).astype(np.float32)
            return f["z"]
    return None


def _save_dem(z, cx, cy, dem, src):
    p = _dem_path(z, cx, cy)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    if not np.isfinite(dem).any():
        open(p + ".empty", "w").write(",".join(src) + "\n")
        return
    base = float(np.nanmin(dem))
    tmp = p + ".tmp.npz"
    if np.nanmax(dem) - base < 655:
        cm = np.where(np.isnan(dem), 65535, np.round((dem - base) * 100)).astype(np.uint16)
        np.savez_compressed(tmp, cm=cm, base=np.float64(base), src=np.array(",".join(src)))
    else:
        np.savez_compressed(tmp, z=dem.astype(np.float32), src=np.array(",".join(src)))
    os.replace(tmp, p + ".npz")


def _fetch(z, cx, cy, sources, alive):
    core, mpx, gpx, radius, clip, m = _geometry(z, cx, cy)
    bbox = (core[0] - m * mpx, core[1] - m * mpx, core[2] + m * mpx, core[3] + m * mpx)
    n = CHUNK * TILE + 2 * m
    dem = None
    for src in sources:  # a chunk on a border is filled from each source in turn
        _upstream.acquire(alive)
        t = time.time()
        try:
            part = dem_sources.fetch(src, bbox, n, n, tries=2).astype(np.float32)
        finally:
            _upstream.release()
        print(f"  relief z{z} chunk {cx},{cy}: {src} {n}px in {time.time() - t:.1f}s, "
              f"{np.isfinite(part).mean() * 100:.0f}% data", flush=True)
        dem = part if dem is None else np.where(np.isnan(dem), part, dem)
        if np.isfinite(dem).all():
            break
    return dem


def _render(z, cx, cy, dem):
    from scipy.ndimage import distance_transform_edt
    core, mpx, gpx, radius, clip, m = _geometry(z, cx, cy)
    nan = np.isnan(dem)
    if nan.all():
        return None
    if nan.any():  # nearest-value fill keeps the gaussian honest near the edge of coverage; masked after
        idx = distance_transform_edt(nan, return_distances=False, return_indices=True)
        dem = dem[tuple(idx)]
    gray, _ = aw.render_relief(dem, gpx, clip_m=clip, radius_m=radius)
    rgba = np.empty(dem.shape + (4,), np.uint8)
    rgba[..., :3] = build_site.duotone(gray)
    rgba[..., 3] = np.where(nan, 0, 255)
    return rgba[m:-m, m:-m]


def _chunk(z, cx, cy, alive):
    key = (z, cx, cy)
    with _lock:
        if key in _rendered:
            _rendered.move_to_end(key)
            return _rendered[key]
        ck = _chunk_locks.setdefault(key, threading.Lock())
    while not ck.acquire(timeout=0.25):  # the first request for this chunk fetches; the others wait here
        if not alive():
            raise Cancelled()
    try:
        with _lock:
            if key in _rendered:
                return _rendered[key]
            f = _failed.get(key)
            if f and time.time() - f[0] < RETRY_AFTER_S:
                raise Unavailable(f[1])
        dem = _load_dem(z, cx, cy)
        if dem is None:
            core = _geometry(z, cx, cy)[0]
            sources = dem_sources.sources_for_bbox(core)
            try:
                dem = _fetch(z, cx, cy, sources, alive)
            except Cancelled:
                raise
            except Exception as e:
                msg = f"{type(e).__name__}: {str(e)[:200]}"
                print(f"  relief z{z} chunk {cx},{cy}: fetch failed ({msg})", flush=True)
                with _lock:
                    _failed[key] = (time.time(), msg)
                raise Unavailable(msg)
            _save_dem(z, cx, cy, dem, sources)
        rgba = None if isinstance(dem, str) else _render(z, cx, cy, dem)
        with _lock:
            _failed.pop(key, None)
            _rendered[key] = rgba
            while len(_rendered) > KEEP_CHUNKS:
                _rendered.popitem(last=False)
        return rgba
    finally:
        ck.release()


def covered(z, x, y):
    """Cheap check (polygons only) whether a tile can have relief at all."""
    return bool(dem_sources.sources_for_bbox(_tile_bbox(z, x // CHUNK * CHUNK, y // CHUNK * CHUNK, CHUNK)))


def tile(z, x, y, alive=lambda: True):
    """PNG bytes for one tile; BLANK (transparent) outside coverage. Raises Unavailable, Cancelled, ValueError.
    `alive()` says whether the browser still wants the tile; it is polled while the request waits."""
    if not (ZMIN <= z <= ZMAX and 0 <= x < 2 ** z and 0 <= y < 2 ** z):
        raise ValueError("tile out of range")
    path = os.path.join(PNG_DIR, str(z), str(x), f"{y}.png")
    if os.path.exists(path):
        with open(path, "rb") as f:
            return f.read()
    if not covered(z, x, y):
        return BLANK
    rgba = _chunk(z, x // CHUNK, y // CHUNK, alive)
    if rgba is None:
        return BLANK
    r0, c0 = (y % CHUNK) * TILE, (x % CHUNK) * TILE
    t = rgba[r0:r0 + TILE, c0:c0 + TILE]
    if not t[..., 3].any():
        return BLANK
    im = Image.fromarray(t[..., :3], "RGB") if t[..., 3].all() else Image.fromarray(t, "RGBA")
    buf = io.BytesIO()
    im.save(buf, "PNG", compress_level=6)
    body = buf.getvalue()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.{threading.get_ident()}.tmp"
    with open(tmp, "wb") as f:
        f.write(body)
    os.replace(tmp, path)
    return body
