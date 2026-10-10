"""Finder test set: known earthworks with mapped coordinates (positives) and terrain-matched random ground.

usage:
  finder_testset.py build            sources -> data/finder/positives_raw.jsonl (all of Ohio, area tagged)
  finder_testset.py sheet <area|all> relief contact sheets at 1 m for labelling by eye -> data/finder/label_sheets/
  finder_testset.py freeze           positives_raw + data/finder/positive_labels.json -> positives.jsonl (+ sha256)
  finder_testset.py randoms <area> [n]  terrain-stratified random points -> data/finder/randoms_<area>.jsonl

Sources (see docs/finder.md section 1): specs/known_ross.json, OSM archaeological sites (local Geofabrik extract,
finder_osm.py), GNIS mound summits, Wikidata items already fetched by the catalog agent, data/catalog/sites.jsonl
(+ triage_scores.jsonl) if present. Positives are labelled visible / faint / none / coord_off BEFORE any
detector output for their area is looked at.
"""
import csv
import json
import math
import os
import re
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aw  # noqa: E402
import finder_osm  # noqa: E402
from finder_common import AREAS, FD, ROOT, area_of, dem_crop, hav_m, load_jsonl, save_jsonl, sha256  # noqa: E402

RAW = os.path.join(FD, "positives_raw.jsonl")
LABELS = os.path.join(FD, "positive_labels.json")
FROZEN = os.path.join(FD, "positives.jsonl")
OHIO = (-84.9, 38.3, -80.5, 42.0)

SKIP_NAME = re.compile(r"park|memorial|village|preserve|ruin|inscription|petroglyph|woodhenge|county|^granville$|"
                       r"ceremonial earthworks|newark earth(works)?$|\bsite$", re.I)
ENCL_NAME = re.compile(r"circle|square|octagon|wall|fort\b|earthworks?\b|enclosure|works\b", re.I)
QUALITY = {"known": 0, "osm_way": 1, "osm_relation": 1, "osm_node": 2, "gnis": 3, "catalog": 4, "wikidata": 5}


def _centre(geom):
    """Centroid (vertex mean, closing vertex dropped) and mean / max radius in metres."""
    g = geom[:-1] if len(geom) > 3 and geom[0] == geom[-1] else geom
    lon = sum(p[0] for p in g) / len(g)
    lat = sum(p[1] for p in g) / len(g)
    d = [hav_m(lon, lat, p[0], p[1]) for p in g]
    return lon, lat, (sum(d) / len(d) if d else 0.0), (max(d) if d else 0.0)


def from_osm():
    out = []
    for e in finder_osm.arch():
        t = e["tags"]
        name = t.get("name", "")
        st = t.get("archaeological_site") or t.get("site_type") or ""
        if st in ("settlement", "petroglyph", "fortification", "burial") or (name and SKIP_NAME.search(name)):
            continue
        lon, lat, rmean, rmax = _centre(e["geom"])
        if not (OHIO[0] < lon < OHIO[2] and OHIO[1] < lat < OHIO[3]):
            continue
        if e["type"] == "relation" and rmax > 1000 and "wall" not in name.lower():
            continue
        if not name and rmax > 300:
            continue
        kind = "enclosure" if (ENCL_NAME.search(name) and "mound" not in name.lower()) or rmax > 70 else "mound"
        if kind == "mound" and re.search(r"mounds\b", name, re.I) and e["type"] == "node":
            kind = "mound"  # a node for a mound group: the point is somewhere in the group
        out.append({"name": name or f"(unnamed {st or 'earthwork'})", "lon": round(lon, 6), "lat": round(lat, 6),
                    "kind": kind, "r_m": round(rmean if kind == "enclosure" else max(rmean, 0), 1),
                    "src": f"osm_{e['type']}", "ref": f"osm:{e['type']}/{e['id']}"})
    return out


def from_known():
    out = []
    for k in json.load(open(os.path.join(ROOT, "specs", "known_ross.json"))):
        kind = "mound" if k["name"] == "Story Mound" else "enclosure"
        out.append({"name": k["name"], "lon": k["lon"], "lat": k["lat"], "kind": kind, "r_m": k.get("r_m") or 0,
                    "src": "known", "ref": "specs/known_ross.json"})
    return out


def from_gnis():
    p = os.path.join(ROOT, "data", "raw", "finder", "gnis", "Text", "DomesticNames_OH.txt")
    out = []
    for r in csv.DictReader(open(p, encoding="utf-8-sig"), delimiter="|"):
        n = r["feature_name"]
        if r["feature_class"] == "Summit" and re.search(r"\bmounds?\b", n, re.I) and not re.search(r"\bhill\b", n, re.I):
            out.append({"name": n, "lon": float(r["prim_long_dec"]), "lat": float(r["prim_lat_dec"]),
                        "kind": "mound", "r_m": 0, "src": "gnis", "ref": f"gnis:{r['feature_id']}"})
    return out


def from_wikidata():
    """Items already in the catalog agent's raw entity store (read only), Ohio, earthwork-like names."""
    p = os.path.join(ROOT, "data", "raw", "catalog", "entities.jsonl")
    out = []
    for line in open(p):
        e = json.loads(line)
        c = (e.get("P625") or [None])[0]
        if not c or not (OHIO[0] < c[0] < OHIO[2] and OHIO[1] < c[1] < OHIO[3]):
            continue
        name = e["labels"].get("en") or ""
        desc = (e["desc"].get("en") or "")
        bad = SKIP_NAME.search(name) and not re.search(r"mound", name, re.I)
        if bad or re.search(r"woodhenge", desc, re.I) or ("Q839954" not in e.get("P31", []) and not re.search(r"mound|earthwork", name + " " + desc, re.I)):
            continue
        if not re.search(r"mound|earthwork|fort|circle|works|enclosure", name, re.I):
            continue
        prec = c[2]
        kind = "mound" if re.search(r"mound", name, re.I) else "enclosure"
        out.append({"name": name, "lon": c[0], "lat": c[1], "kind": kind, "r_m": 0, "src": "wikidata",
                    "ref": f"wd:{e['id']}", "coord_prec_deg": prec})
    return out


def from_catalog():
    p = os.path.join(ROOT, "data", "catalog", "sites.jsonl")
    if not os.path.exists(p):
        return []
    tri = {}
    tp = os.path.join(ROOT, "data", "catalog", "triage_scores.jsonl")
    for r in load_jsonl(tp):
        tri[r.get("qid") or r.get("id")] = r
    out = []
    for s in load_jsonl(p):
        if not (OHIO[0] < s["lon"] < OHIO[2] and OHIO[1] < s["lat"] < OHIO[3]):
            continue
        name = s.get("name", "")
        bad = SKIP_NAME.search(name) and not re.search(r"mound", name, re.I)
        if bad or re.search(r"woodhenge", s.get("description") or "", re.I) or (s.get("coord_precision_deg") or 0) >= 0.01:
            continue
        kind = "mound" if re.search(r"mound|tumul|barrow", name, re.I) else "enclosure"
        t = tri.get(s.get("qid"))
        out.append({"name": s.get("name", ""), "lon": s["lon"], "lat": s["lat"], "kind": kind, "r_m": 0,
                    "src": "catalog", "ref": f"wd:{s.get('qid')}", "coord_prec_deg": s.get("coord_precision_deg"),
                    "triage": (t or {}).get("label")})
    return out


def patch_radii():
    """Apply the merge fix (max r_m, carried coordinate precision) to the existing positives_raw.jsonl by ref,
    without rebuilding it: pids (and the labels keyed on them) stay as they are; positives.jsonl is untouched."""
    rows = from_known() + from_osm() + from_gnis() + from_wikidata() + from_catalog()
    by_ref = {r["ref"]: r for r in rows}
    cur = load_jsonl(RAW)
    n = 0
    for r in cur:
        refs = [r["ref"]] + r.get("also", [])
        rm = max([by_ref[x].get("r_m") or 0 for x in refs if x in by_ref] + [r.get("r_m") or 0])
        if rm != (r.get("r_m") or 0):
            r["r_m"] = round(rm, 1)
            n += 1
        if not r.get("coord_prec_deg"):
            pr = [by_ref[x].get("coord_prec_deg") for x in refs if x in by_ref and by_ref[x].get("coord_prec_deg")]
            if pr:
                r["coord_prec_deg"] = pr[0]
    save_jsonl(RAW, cur)
    print(n, "radii patched")


def build():
    rows = from_known() + from_osm() + from_gnis() + from_wikidata() + from_catalog()
    rows.sort(key=lambda r: QUALITY[r["src"]])
    kept = []
    for r in rows:
        dup = None
        for k in kept:
            point = r["src"] not in ("osm_way", "osm_relation") or k["src"] not in ("osm_way", "osm_relation")
            tol = (120 if point else 50) if r["kind"] == "mound" else max(60 if not point else 150, 0.5 * max(r["r_m"], k["r_m"]))
            if k["kind"] == r["kind"] and hav_m(k["lon"], k["lat"], r["lon"], r["lat"]) <= tol:
                dup = k
                break
        if dup:
            dup.setdefault("also", []).append(r["ref"])
            dup["r_m"] = max(dup.get("r_m") or 0, r.get("r_m") or 0)  # keep the enclosure extent of merged records
            if r.get("coord_prec_deg") and not dup.get("coord_prec_deg"):
                dup["coord_prec_deg"] = r["coord_prec_deg"]
            continue
        kept.append(r)
    for i, r in enumerate(kept):
        r["pid"] = f"p{i:03d}"
        r["area"] = area_of(r["lon"], r["lat"])
    save_jsonl(RAW, kept)
    by = {}
    for r in kept:
        by.setdefault((r["area"], r["kind"]), 0)
        by[(r["area"], r["kind"])] += 1
    print(f"{len(kept)} positives (Ohio); by area/kind:", {f"{a}/{k}": n for (a, k), n in sorted(by.items(), key=str)})


def relief(z, r_m, clip):
    from scipy.ndimage import gaussian_filter
    z = aw.fill_nan(z)
    return ((np.clip((z - gaussian_filter(z, r_m)) / clip, -1, 1) * 0.5 + 0.5) * 255).astype(np.uint8)


def near_heldout(lon, lat, km=25.0):
    for a, b, c, d, role in AREAS.values():
        if role != "heldout":
            continue
        dx = max(a - lon, 0, lon - c) * 85.0
        dy = max(b - lat, 0, lat - d) * 111.0
        if math.hypot(dx, dy) < km:
            return True
    return False


def extras():
    """Known sites outside the four areas and more than 25 km from the held-out boxes: extra tuning positives."""
    return [r for r in load_jsonl(RAW) if not r["area"] and not near_heldout(r["lon"], r["lat"])]


def sheet(which):
    if which == "extra":
        rows = extras()
    else:
        rows = [r for r in load_jsonl(RAW) if r["area"] and (which == "all" or r["area"] == which)]
    od = os.path.join(FD, "label_sheets")
    os.makedirs(od, exist_ok=True)
    panels = []
    for r in rows:
        z, _ = dem_crop(r["lon"], r["lat"], 180)
        a = Image.fromarray(relief(z, 5, 0.4)).convert("RGB")
        b = Image.fromarray(relief(z, 24, 1.0)).convert("RGB")
        im = Image.new("RGB", (a.width * 2 + 4, a.height + 16), (255, 255, 255))
        im.paste(a, (0, 16))
        im.paste(b, (a.width + 4, 16))
        d = ImageDraw.Draw(im)
        for x0 in (0, a.width + 4):
            cx, cy = x0 + a.width / 2, 16 + a.height / 2
            rr = 40 if r["kind"] == "mound" else max(60, r["r_m"])
            d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=(220, 40, 60), width=1)
            d.line((cx - 6, cy, cx + 6, cy), fill=(220, 40, 60))
            d.line((cx, cy - 6, cx, cy + 6), fill=(220, 40, 60))
        d.text((3, 2), f"{r['pid']} {r['kind'][:4]} {r['name'][:34]} [{r['src']}]", fill=(0, 0, 0))
        panels.append(im)
    cols = 3
    for s in range(0, len(panels), 12):
        chunk = panels[s:s + 12]
        w, h = chunk[0].width, chunk[0].height
        S = Image.new("RGB", (cols * (w + 8), math.ceil(len(chunk) / cols) * (h + 8)), (255, 255, 255))
        for i, p in enumerate(chunk):
            S.paste(p, ((i % cols) * (w + 8), (i // cols) * (h + 8)))
        out = os.path.join(od, f"{which}_{s // 12:02d}.jpg")
        S.save(out, quality=88)
        print("wrote", out)


def freeze():
    labels = {k: v for k, v in json.load(open(LABELS)).items() if not k.startswith("_")}
    rows = load_jsonl(RAW)
    out = []
    for r in rows:
        if not r["area"]:
            continue
        lab = labels.get(r["pid"])
        if lab is None:
            raise SystemExit(f"no label for {r['pid']} {r['name']}")
        out.append({**r, **({"vis": lab} if isinstance(lab, str) else lab)})
    save_jsonl(FROZEN, out)
    print(len(out), "positives frozen; sha256", sha256(FROZEN))


def _poly_test(path):
    """Point-in-polygon test for a GeoJSON file (any feature, outer rings only); always True without a file."""
    if not path:
        return lambda lon, lat: True
    rings = []
    for f in json.load(open(path))["features"]:
        g = f["geometry"]
        for poly in ([g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]):
            rings.append(np.array(poly[0], float))

    def inside(lon, lat):
        for r in rings:
            x, y = r[:, 0], r[:, 1]
            x2, y2 = np.roll(x, -1), np.roll(y, -1)
            c = ((y > lat) != (y2 > lat)) & (lon < (x2 - x) * (lat - y) / (y2 - y + 1e-15) + x)
            if c.sum() % 2:
                return True
        return False
    return inside


def randoms(area, n=3000, seed=7):
    """Uniform random land points in an area (water excluded, masked ground kept), > 150 m from any positive, with
    their terrain class. Weighting to the positives' valley/upland mix happens in finder_eval.py."""
    from finder_scan import AreaScan
    sc = AreaScan(area)
    # test areas: their box; other scan areas (e.g. a county): the scan box, optionally clipped to a polygon (env
    # POLY, GeoJSON) and always to tiles that were scanned
    pos = [r for r in load_jsonl(RAW) if r["area"] == area] if area in AREAS else load_jsonl(RAW)
    rng = np.random.default_rng(seed)
    lon0, lat0, lon1, lat1 = AREAS[area][:4] if area in AREAS else sc.box
    inside = _poly_test(os.environ.get("POLY"))
    det = os.path.join(sc.d, "det")
    cand = [(rng.uniform(lon0, lon1), rng.uniform(lat0, lat1)) for _ in range(int(n * 1.6))]
    cand = [(lon, lat) for lon, lat in cand if inside(lon, lat)]
    if area not in AREAS:
        cand = [q for q in cand if os.path.exists(os.path.join(det, "%d_%d.json" % sc.tile_of(*q)))]
    cand = [(lon, lat) for lon, lat in cand if not any(hav_m(lon, lat, p["lon"], p["lat"]) < 150 for p in pos)]
    cand.sort(key=lambda q: sc.tile_of(*q))  # one tile load per tile
    out = []
    for lon, lat in cand:
        t = sc.terrain_at(lon, lat)
        if t is None:  # no data or water
            continue
        out.append({"lon": round(lon, 6), "lat": round(lat, 6), "terrain": t[0], "hand_m": round(t[1], 1)})
    rng.shuffle(out)
    out = out[:n]
    save_jsonl(os.path.join(FD, f"randoms_{area}.jsonl"), out)
    print(area, len(out), "random points;", sum(r["terrain"] == "valley" for r in out), "valley")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "build":
        build()
    elif cmd == "patch_radii":
        patch_radii()
    elif cmd == "sheet":
        sheet(sys.argv[2])
    elif cmd == "freeze":
        freeze()
    elif cmd == "randoms":
        randoms(sys.argv[2], *(int(v) for v in sys.argv[3:4]))
