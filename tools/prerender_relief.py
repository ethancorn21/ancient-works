"""Pre-render the LiDAR relief tiles around every site for the public copy (which has no live tile server).

usage: .venv/bin/python tools/prerender_relief.py plan            (count tiles and chunks)
       .venv/bin/python tools/prerender_relief.py sample N        (render N uncached chunks, report timing)
       .venv/bin/python tools/prerender_relief.py render SOURCE   (ea, usgs, ign, ahn: one process per provider)
       .venv/bin/python tools/prerender_relief.py pack OUTDIR [CAP_MB]   (sharded PMTiles + index, for R2)

Same renderer as the LAN copy (server/relief_tiles.py: same DEMs, same look, same WebP), so a pre-rendered tile is
byte-identical to the live one. Coverage per site and zoom (z12-17): the site box plus one box width each side, and
at least a 10 x 6 tile view centred on the site (a normal screen when zoomed out from the site). Tiles are cut from
6 x 6 chunks (one DEM download each), cached under data/tilecache like the live server's, so render resumes.
"""
import json
import math
import os
import random
import sys
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "server"))
import relief_tiles as rt  # noqa: E402
import dem_sources  # noqa: E402

PAD_BOX = 1.0
CAP_MB = 250            # per archive: wrangler r2 object put uploads up to ~300 MB in one request
INDEX_LEVELS = (8, 9, 10)  # an area cell is a z8 tile, split to z9/z10 where one cell alone is over the cap
MIN_VIEW = (10, 6)


def _xy(lon, lat, z):
    n = 2 ** z
    return ((lon + 180) / 360 * n,
            (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n)


def plan():
    """{(z, cx, cy): set of (x, y) tiles wanted in that chunk}, only chunks with LiDAR coverage."""
    with open(os.path.join(ROOT, "web", "data", "sites.json")) as f:
        sites = [s for s in json.load(f)["sites"] if s.get("lidar") is not False]
    want = {}
    for s in sites:
        xs = [c[0] for c in s["corners"]]
        ys = [c[1] for c in s["corners"]]
        for z in range(rt.ZMIN, rt.ZMAX + 1):
            ax, ay = _xy(min(xs), max(ys), z)
            bx, by = _xy(max(xs), min(ys), z)
            cx, cy = (ax + bx) / 2, (ay + by) / 2
            hw = max((bx - ax) * (0.5 + PAD_BOX), MIN_VIEW[0] / 2)
            hh = max((by - ay) * (0.5 + PAD_BOX), MIN_VIEW[1] / 2)
            for x in range(int(cx - hw), int(cx + hw) + 1):
                for y in range(int(cy - hh), int(cy + hh) + 1):
                    want.setdefault((z, x // rt.CHUNK, y // rt.CHUNK), set()).add((x, y))
    return {c: t for c, t in want.items() if rt.covered(c[0], c[1] * rt.CHUNK, c[2] * rt.CHUNK)}


def render_chunk(c, tiles):
    z = c[0]
    for x, y in sorted(tiles):
        for attempt in range(3):
            try:
                rt.tile(z, x, y)
                break
            except rt.Unavailable:
                if attempt == 2:
                    raise
                rt._failed.pop(c, None)
                time.sleep(20)


def main(argv):
    cmd = argv[0] if argv else "plan"
    want = plan()
    if cmd == "plan":
        cached = sum(1 for c in want if rt._load_dem(*c) is not None)
        print(f"{sum(map(len, want.values()))} tiles in {len(want)} chunks ({cached} DEMs cached)")
    elif cmd == "sample":
        n = int(argv[1]) if len(argv) > 1 else 20
        todo = [c for c in want if rt._load_dem(*c) is None]
        random.seed(1)
        pick = random.sample(todo, min(n, len(todo)))
        t0 = time.time()
        for i, c in enumerate(pick):
            t = time.time()
            render_chunk(c, want[c])
            print(f"{i + 1}/{len(pick)} z{c[0]} chunk {c[1]},{c[2]}: {len(want[c])} tiles in {time.time() - t:.1f}s",
                  flush=True)
        per = (time.time() - t0) / len(pick)
        print(f"mean {per:.1f}s/chunk -> {len(todo)} uncached chunks ~{len(todo) * per / 3600:.1f} h (one at a time)")

    elif cmd == "render":
        # one provider per process: relief_tiles allows 2 DEM downloads at once per process (as on the LAN server),
        # so no provider gets more than 2 at a time; 2 threads keep both slots busy. Resumes from the caches.
        src = argv[1]
        todo = [c for c in sorted(want) if dem_sources.sources_for_bbox(rt._tile_bbox(c[0], c[1] * rt.CHUNK,
                                                                                       c[2] * rt.CHUNK, rt.CHUNK))[0] == src]
        todo = [c for c in todo if not all(os.path.exists(os.path.join(rt.PNG_DIR, str(c[0]), str(x), f"{y}.webp"))
                                           for x, y in want[c])]
        print(f"{src}: {len(todo)} chunks to render", flush=True)
        lock, done, failed, t0 = threading.Lock(), [0], [], time.time()

        def work():
            while True:
                with lock:
                    if not todo:
                        return
                    c = todo.pop(0)
                try:
                    render_chunk(c, want[c])
                except Exception as e:
                    with lock:
                        failed.append(c)
                    print(f"FAILED z{c[0]} {c[1]},{c[2]}: {type(e).__name__}: {str(e)[:150]}", flush=True)
                with lock:
                    done[0] += 1
                    if done[0] % 50 == 0:
                        el = time.time() - t0
                        print(f"{src}: {done[0]} done, {len(todo)} left, {len(failed)} failed, "
                              f"~{len(todo) * el / done[0] / 3600:.1f} h to go", flush=True)

        ths = [threading.Thread(target=work) for _ in range(2)]
        [t.start() for t in ths]
        [t.join() for t in ths]
        print(f"{src}: finished, {done[0]} chunks, {len(failed)} failed: {failed[:20]}", flush=True)

    elif cmd == "pack":
        pack(want, argv[1], int(argv[2]) if len(argv) > 2 else CAP_MB)


def pack(want, outdir, cap_mb):
    """Sharded PMTiles: the tiles grouped by area cell (a z8 tile, split finer only when one cell is over the cap) into
    archives of at most cap_mb, plus an index {cell: archive} the page looks each tile up in (web/index.html
    RELIEF_PM). Archive and index names carry a content hash, so a re-pack never serves a stale mix from caches.
    Only planned tiles that rendered with data; a missing tile shows as no relief, as the live server's BLANK does."""
    import hashlib
    from pmtiles.tile import Compression, TileType, zxy_to_tileid
    from pmtiles.writer import Writer
    cap = cap_mb * 1e6
    tiles = []
    for c, ts in want.items():
        for x, y in ts:
            path = os.path.join(rt.PNG_DIR, str(c[0]), str(x), f"{y}.webp")
            if os.path.exists(path):
                tiles.append((c[0], x, y, path, os.path.getsize(path)))
    missing = sum(map(len, want.values())) - len(tiles)

    def cell(t, level):
        z, x, y = t[:3]
        return (level, x >> (z - level), y >> (z - level))

    cells = {}
    for t in tiles:
        cells.setdefault(cell(t, INDEX_LEVELS[0]), []).append(t)
    for level in INDEX_LEVELS[1:]:  # split any cell over the cap one level finer
        for k in [k for k, ts in cells.items() if sum(t[4] for t in ts) > cap and k[0] < level]:
            for t in cells.pop(k):
                cells.setdefault(cell(t, level), []).append(t)
    shards, cur, size = [], [], 0
    for k in sorted(cells, key=lambda k: (k[1] << (INDEX_LEVELS[-1] - k[0]), k[2] << (INDEX_LEVELS[-1] - k[0]))):
        n = sum(t[4] for t in cells[k])
        if cur and size + n > cap:
            shards.append(cur)
            cur, size = [], 0
        cur.append(k)
        size += n
    if cur:
        shards.append(cur)

    os.makedirs(outdir, exist_ok=True)
    for f in os.listdir(outdir):
        if f.startswith("relief-"):
            os.remove(os.path.join(outdir, f))
    index = {"style": rt.STYLE, "minzoom": rt.ZMIN, "maxzoom": rt.ZMAX, "levels": list(INDEX_LEVELS), "cells": {}}
    e7 = lambda v: int(v * 1e7)
    for i, keys in enumerate(shards):
        ts = sorted((zxy_to_tileid(z, x, y), z, x, y, p) for k in keys for z, x, y, p, _ in cells[k])
        lon = [v for k in keys for v in (k[1] / 2 ** k[0] * 360 - 180, (k[1] + 1) / 2 ** k[0] * 360 - 180)]
        lat = [math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * v / 2 ** k[0])))) for k in keys for v in (k[2], k[2] + 1)]
        tmp = os.path.join(outdir, f"relief-{i}.tmp")
        with open(tmp, "wb") as f:
            w = Writer(f)
            for tid, z, x, y, p in ts:
                with open(p, "rb") as t:
                    w.write_tile(tid, t.read())
            w.finalize({"tile_type": TileType.WEBP, "tile_compression": Compression.NONE,
                        "min_zoom": rt.ZMIN, "max_zoom": rt.ZMAX,
                        "min_lon_e7": e7(min(lon)), "min_lat_e7": e7(min(lat)),
                        "max_lon_e7": e7(max(lon)), "max_lat_e7": e7(max(lat)),
                        "center_zoom": rt.ZMIN, "center_lon_e7": e7(sum(lon) / len(lon)),
                        "center_lat_e7": e7(sum(lat) / len(lat))},
                       {"name": "Resurface LiDAR relief", "style": rt.STYLE})
        h = hashlib.sha256()
        with open(tmp, "rb") as f:
            for block in iter(lambda: f.read(1 << 20), b""):
                h.update(block)
        name = f"relief-{h.hexdigest()[:12]}.pmtiles"
        os.replace(tmp, os.path.join(outdir, name))
        for k in keys:
            index["cells"]["/".join(map(str, k))] = name
        print(f"  {name}: {len(ts)} tiles, {len(keys)} cells, {os.path.getsize(os.path.join(outdir, name)) / 1e6:.0f} MB")
    body = json.dumps(index, separators=(",", ":"), sort_keys=True).encode()
    iname = f"relief-index-{hashlib.sha256(body).hexdigest()[:12]}.json"
    with open(os.path.join(outdir, iname), "wb") as f:
        f.write(body)
    print(f"{outdir}/{iname}: {len(shards)} archives, {len(tiles)} tiles, {missing} planned tiles not rendered (or blank)")
    return iname


if __name__ == "__main__":
    main(sys.argv[1:])
