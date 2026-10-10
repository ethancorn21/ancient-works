"""OpenStreetMap from a local Geofabrik extract, so the Finder does not depend on Overpass (busy, 504s).

One pass over the .pbf writes:
  data/finder/osm/arch.json        archaeological sites / tumuli (nodes, ways, relations) with geometry
  data/finder/osm/cells/<i>_<j>.pkl modern features (roads, rails, buildings, water, waterways, quarries),
                                   in 0.05 degree cells, in the same (kind, [(lon, lat), ...]) form as aw.osm_ways
ways(bbox) then gives aw.modern_mask exactly what aw.osm_ways would have fetched (same tag filter).

usage: finder_osm.py build data/raw/finder/osm/ohio-261009.osm.pbf
"""
import json
import os
import pickle
import re
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aw  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "finder", "osm")
CELL = 0.05
HIGHWAY = re.compile(r"^(motorway|trunk|primary|secondary|tertiary|unclassified|residential|service|living_street|road)(_link)?$")


def is_arch(t):
    return (t.get("historic") in ("archaeological_site", "tumulus") or t.get("archaeological_site") == "tumulus"
            or t.get("site_type") == "tumulus")


def modern_kind(t):
    if "highway" in t:
        return "road" if HIGHWAY.match(t["highway"]) else None
    if "railway" in t:
        return "rail"
    if "building" in t:
        return "building"
    if "waterway" in t:
        return "waterway"
    if t.get("natural") == "water" or t.get("landuse") in ("quarry", "reservoir"):
        return "area"
    return None


def build(pbf):
    import osmium
    os.makedirs(os.path.join(OUT, "cells"), exist_ok=True)

    class Rel(osmium.SimpleHandler):
        def __init__(self):
            super().__init__()
            self.rels, self.members = [], set()

        def relation(self, r):
            t = dict(r.tags)
            if is_arch(t):
                ways = [m.ref for m in r.members if m.type == "w"]
                self.rels.append({"type": "relation", "id": r.id, "tags": t, "ways": ways})
                self.members.update(ways)

    h1 = Rel()
    h1.apply_file(pbf)
    print(len(h1.rels), "archaeological relations")

    class Main(osmium.SimpleHandler):
        def __init__(self, members):
            super().__init__()
            self.members, self.arch, self.wgeom = members, [], {}
            self.cells = defaultdict(list)
            self.n = 0

        def node(self, n):
            t = dict(n.tags)
            if t and is_arch(t):
                self.arch.append({"type": "node", "id": n.id, "tags": t, "geom": [[n.location.lon, n.location.lat]]})

        def way(self, w):
            t = dict(w.tags)
            arch, kind = is_arch(t), modern_kind(t)
            if not (arch or kind or w.id in self.members):
                return
            try:
                pts = [(nd.lon, nd.lat) for nd in w.nodes]
            except osmium.InvalidLocationError:
                pts = [(nd.lon, nd.lat) for nd in w.nodes if nd.location.valid()]
            if len(pts) < 1:
                return
            if arch:
                self.arch.append({"type": "way", "id": w.id, "tags": t, "geom": [list(p) for p in pts]})
            if w.id in self.members:
                self.wgeom[w.id] = pts
            if kind:
                self.n += 1
                lons = [p[0] for p in pts]
                lats = [p[1] for p in pts]
                for i in range(int(min(lons) // CELL), int(max(lons) // CELL) + 1):
                    for j in range(int(min(lats) // CELL), int(max(lats) // CELL) + 1):
                        self.cells[(i, j)].append((kind, pts))

    h2 = Main(h1.members)
    h2.apply_file(pbf, locations=True, idx="flex_mem")
    for r in h1.rels:
        geom = [list(p) for wid in r.pop("ways") for p in h2.wgeom.get(wid, [])]
        if geom:
            h2.arch.append({**r, "geom": geom})
    aw.save_json(os.path.join(OUT, "arch.json"), {"source": os.path.basename(pbf), "elements": h2.arch})
    for (i, j), lst in h2.cells.items():
        with open(os.path.join(OUT, "cells", f"{i}_{j}.pkl"), "wb") as f:
            pickle.dump(lst, f, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"{len(h2.arch)} archaeological elements, {h2.n} modern ways in {len(h2.cells)} cells")


def ways(bbox):
    """Modern features for a Mercator bbox, from the local cells, deduplicated (a way spans several cells)."""
    lon0, lat0 = aw.to_lonlat(bbox[0], bbox[1])
    lon1, lat1 = aw.to_lonlat(bbox[2], bbox[3])
    out, seen = [], set()
    for i in range(int(lon0 // CELL), int(lon1 // CELL) + 1):
        for j in range(int(lat0 // CELL), int(lat1 // CELL) + 1):
            p = os.path.join(OUT, "cells", f"{i}_{j}.pkl")
            if not os.path.exists(p):
                continue
            for kind, pts in pickle.load(open(p, "rb")):
                key = (kind, pts[0], pts[-1], len(pts))
                if key in seen:
                    continue
                xs = [q[0] for q in pts]
                ys = [q[1] for q in pts]
                if max(xs) < lon0 or min(xs) > lon1 or max(ys) < lat0 or min(ys) > lat1:
                    continue
                seen.add(key)
                out.append((kind, pts))
    return out


def arch():
    return json.load(open(os.path.join(OUT, "arch.json")))["elements"]




# ---------------------------------------------------------------- land-use settings (flags for the export, never a mask)

SETTING_LANDUSE = {"residential", "industrial", "commercial", "retail", "cemetery", "landfill", "military",
                   "construction", "brownfield", "railway", "quarry"}


def setting_of(t):
    if t.get("leisure") == "golf_course":
        return "golf_course"
    if t.get("amenity") == "grave_yard":
        return "cemetery"
    lu = t.get("landuse")
    return lu if lu in SETTING_LANDUSE else None


def build_settings(pbf):
    import osmium
    os.makedirs(os.path.join(OUT, "settings"), exist_ok=True)

    class A(osmium.SimpleHandler):
        def __init__(self):
            super().__init__()
            self.cells = defaultdict(list)
            self.n = 0

        def area(self, a):
            kind = setting_of(dict(a.tags))
            if not kind:
                return
            try:
                for outer in a.outer_rings():
                    pts = [(n.lon, n.lat) for n in outer]
                    if len(pts) < 4:
                        continue
                    self.n += 1
                    lons = [p[0] for p in pts]
                    lats = [p[1] for p in pts]
                    bb = (min(lons), min(lats), max(lons), max(lats))
                    for i in range(int(bb[0] // CELL), int(bb[2] // CELL) + 1):
                        for j in range(int(bb[1] // CELL), int(bb[3] // CELL) + 1):
                            self.cells[(i, j)].append((kind, bb, pts))
            except Exception:
                return

    h = A()
    h.apply_file(pbf, locations=True, idx="flex_mem")
    for (i, j), lst in h.cells.items():
        with open(os.path.join(OUT, "settings", f"{i}_{j}.pkl"), "wb") as f:
            pickle.dump(lst, f, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"{h.n} setting polygons in {len(h.cells)} cells")


def _inside(lon, lat, pts):
    inside = False
    n = len(pts)
    for k in range(n - 1):
        (x1, y1), (x2, y2) = pts[k], pts[k + 1]
        if (y1 > lat) != (y2 > lat) and lon < (x2 - x1) * (lat - y1) / (y2 - y1 + 1e-15) + x1:
            inside = not inside
    return inside


_SET_CACHE = {}


def settings_at(lon, lat):
    """Land-use settings (golf_course, residential, cemetery, ...) whose OSM polygon contains the point."""
    key = (int(lon // CELL), int(lat // CELL))
    if key not in _SET_CACHE:
        p = os.path.join(OUT, "settings", f"{key[0]}_{key[1]}.pkl")
        _SET_CACHE[key] = pickle.load(open(p, "rb")) if os.path.exists(p) else []
    out = set()
    for kind, bb, pts in _SET_CACHE[key]:
        if bb[0] <= lon <= bb[2] and bb[1] <= lat <= bb[3] and _inside(lon, lat, pts):
            out.add(kind)
    return sorted(out)


if __name__ == "__main__":
    if sys.argv[1] == "build":
        build(sys.argv[2])
    elif sys.argv[1] == "settings":
        build_settings(sys.argv[2])
