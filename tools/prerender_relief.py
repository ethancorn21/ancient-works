"""Pre-render the LiDAR relief tiles around every site for the public copy (which has no live tile server).

usage: .venv/bin/python tools/prerender_relief.py plan            (count tiles and chunks)
       .venv/bin/python tools/prerender_relief.py sample N        (render N uncached chunks, report timing)
       .venv/bin/python tools/prerender_relief.py render SOURCE   (ea, usgs, ign, ahn: one process per provider)
       .venv/bin/python tools/prerender_relief.py pack OUT.pmtiles

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
        # one PMTiles archive (the standard single-file tile format for static hosting: the page reads tiles by HTTP
        # range request, pmtiles JS). Only planned tiles that rendered with data; a missing tile shows as no relief,
        # exactly as the live server's transparent BLANK does.
        from pmtiles.tile import Compression, TileType, zxy_to_tileid
        from pmtiles.writer import Writer
        out = argv[1]
        tiles = sorted((zxy_to_tileid(c[0], x, y), c[0], x, y) for c, ts in want.items() for x, y in ts)
        n = missing = 0
        lon0 = lat0 = 180.0
        lon1 = lat1 = -180.0
        with open(out + ".tmp", "wb") as f:
            w = Writer(f)
            for tid, z, x, y in tiles:
                path = os.path.join(rt.PNG_DIR, str(z), str(x), f"{y}.webp")
                if not os.path.exists(path):
                    missing += 1
                    continue
                with open(path, "rb") as t:
                    w.write_tile(tid, t.read())
                n += 1
                if z == rt.ZMIN:
                    ts = 2 ** z
                    lon0, lon1 = min(lon0, x / ts * 360 - 180), max(lon1, (x + 1) / ts * 360 - 180)
                    lat = lambda yy: math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * yy / ts))))
                    lat0, lat1 = min(lat0, lat(y + 1)), max(lat1, lat(y))
            e7 = lambda v: int(v * 1e7)
            w.finalize({"tile_type": TileType.WEBP, "tile_compression": Compression.NONE,
                        "min_zoom": rt.ZMIN, "max_zoom": rt.ZMAX,
                        "min_lon_e7": e7(lon0), "min_lat_e7": e7(lat0), "max_lon_e7": e7(lon1), "max_lat_e7": e7(lat1),
                        "center_zoom": rt.ZMIN, "center_lon_e7": e7((lon0 + lon1) / 2), "center_lat_e7": e7((lat0 + lat1) / 2)},
                       {"name": "Resurface LiDAR relief", "style": rt.STYLE,
                        "attribution": "LiDAR: USGS 3DEP; Environment Agency (OGL v3.0); AHN; IGN LiDAR HD (Licence Ouverte 2.0)"})
        os.replace(out + ".tmp", out)
        print(f"{out}: {n} tiles, {missing} planned tiles not rendered (or blank), {os.path.getsize(out) / 1e6:.0f} MB")


if __name__ == "__main__":
    main(sys.argv[1:])
