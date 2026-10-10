"""Finder: classify ranked candidates by independent evidence and export them for the page.

class (per candidate):
  known   a modern public record lies within its error: catalog (Wikidata), OSM historic=archaeological_site,
          GNIS, specs/known_<area>.json. Enclosure records cover their whole extent (radius + 60 m).
  lost    no modern record, but inside the error radius of a Mills 1914 symbol (data/finder/mills_1914_<county>.jsonl)
  new     no record anywhere we have
Tolerances: OSM ways / known specs 40 m (mounds); points with uncertain placement (OSM nodes, GNIS, Wikidata,
catalog) max(150 m, 1.5 x coordinate precision).

usage: finder_export.py <area> <label> [n_per100] [ranker] [county]
writes web/data/scan/<area>/{candidates.json, c/<id>.jpg}, the entry in web/data/scans.json,
and data/finder/classified_<area>.json (all exported candidates with evidence).
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aw  # noqa: E402
from finder_common import FD, ROOT, area_km2, dem_crop, hav_m, load_jsonl, local_xy  # noqa: E402

CROP_PX = 360
# product-only post-filter (not part of the gate pipeline): candidates on these OSM land uses go to the end of the
# exported list, flagged, never deleted. Residential land, golf courses and cemeteries stay in place (flagged):
# known mounds sit in all three.
DEMOTE = {"industrial", "commercial", "retail", "military", "landfill", "quarry", "construction", "brownfield", "railway"}
MILLS_FOR = {"mound": ("mound", "mound_group", "other"), "ring": ("enclosure",)}
POINT_SRC = ("osm_node", "gnis", "wikidata", "catalog")


def records():
    """Every known-site record we have for Ohio (positives_raw keeps all sources, before visibility labels)."""
    return load_jsonl(os.path.join(FD, "positives_raw.jsonl"))


def record_tol(r):
    if r["kind"] == "enclosure" and r.get("r_m"):
        return r["r_m"] + 60.0
    if r["src"] in POINT_SRC:
        prec = r.get("coord_prec_deg") or 0
        return max(150.0, 1.5 * prec * 111000)
    return 40.0 if r["kind"] != "enclosure" else 150.0


def evidence(cands, county=None):
    recs = records()
    mills = load_jsonl(os.path.join(FD, f"mills_1914_{county}.jsonl")) if county else []
    lon0, lat0 = cands[0]["lon"], cands[0]["lat"]
    cx, cy = local_xy([c["lon"] for c in cands], [c["lat"] for c in cands], lon0, lat0)
    rx, ry = local_xy([r["lon"] for r in recs], [r["lat"] for r in recs], lon0, lat0)
    rt = np.array([record_tol(r) for r in recs])
    if mills:
        mx, my = local_xy([m["lon"] for m in mills], [m["lat"] for m in mills], lon0, lat0)
        me = np.array([m["err_m"] for m in mills])
    for i, c in enumerate(cands):
        d = np.hypot(rx - cx[i], ry - cy[i])
        j = int(np.argmin(d))
        within = np.nonzero(d <= rt)[0]
        ev = {"records": [{"name": recs[k]["name"], "src": recs[k]["src"], "ref": recs[k]["ref"], "dist_m": round(float(d[k]))}
                          for k in within[np.argsort(d[within])][:3]],
              "nearest_record": {"name": recs[j]["name"], "src": recs[j]["src"], "dist_m": round(float(d[j]))}}
        if mills:
            dm = np.hypot(mx - cx[i], my - cy[i])
            k = int(np.argmin(dm))
            # kind-matched: mounds vs triangles (single, merged groups, and 'other' small red symbols, which include
            # triangles cut by black lines); rings vs enclosure plans
            ok = MILLS_FOR[c["kind"]]
            inside = np.nonzero((dm <= me) & np.array([m["type"] in ok for m in mills]))[0]
            ev["mills1914"] = {"nearest_type": mills[k]["type"], "dist_m": round(float(dm[k])), "err_m": int(me[k]),
                               "nearest_matching_m": (round(float(dm[inside].min())) if len(inside) else None),
                               "n_within_err": int(len(inside)),
                               "types_within_err": sorted({mills[q]["type"] for q in inside})}
        import finder_osm
        ev["setting"] = finder_osm.settings_at(c["lon"], c["lat"])  # flags only (golf course, residential, ...)
        ev["dem_smooth"] = bool(c.get("rough_m", 1) <= 0.021)  # very smooth surround: possible DEM void / TIN facets
        c["evidence"] = ev
        c["class"] = "known" if ev["records"] else ("lost" if mills and ev["mills1914"]["n_within_err"] else "new")
    return cands


def mills_chance(area, county):
    """Chance that a random point (all ground / valley ground) lies within the error radius of some Mills mound-type
    symbol, i.e. the chance that a mound candidate is called 'lost' by coincidence."""
    mills = [m for m in load_jsonl(os.path.join(FD, f"mills_1914_{county}.jsonl")) if m["type"] in MILLS_FOR["mound"]]
    rs = load_jsonl(os.path.join(FD, f"randoms_{area}.jsonl"))
    if not mills or not rs:
        return None
    lon0, lat0 = rs[0]["lon"], rs[0]["lat"]
    mx, my = local_xy([m["lon"] for m in mills], [m["lat"] for m in mills], lon0, lat0)
    me = np.array([m["err_m"] for m in mills])
    px, py = local_xy([r["lon"] for r in rs], [r["lat"] for r in rs], lon0, lat0)
    near = (np.hypot(px[:, None] - mx[None], py[:, None] - my[None]) <= me[None]).any(1)
    val = np.array([r["terrain"] == "valley" for r in rs])
    return {"all": round(float(near.mean()), 3), "valley": round(float(near[val].mean()), 3),
            "upland": round(float(near[~val].mean()), 3), "n": len(rs)}


def as_row(c, i, area):
    m = c["kind"] == "mound"
    r_m = round(c["diam_m"] / 2, 1) if m else c["r_m"]
    meas = ({k: c[k] for k in ("D", "score", "h_m", "diam_m", "round", "elong", "flat_top", "snr", "rough_m", "base_slope",
                               "modern_m")} if m else
            {k: c[k] for k in ("r_m", "score_m", "snr", "rough_m", "sectors", "stage1_m", "band_slope") if k in c})
    return {"id": f"{area}-{c['kind'][0]}{i:04d}", "kind": c["kind"], "lon": round(c["lon"], 6), "lat": round(c["lat"], 6),
            "r_m": r_m, "score_m": round(c["h_m"] if m else c["score_m"], 3), "snr": c["snr"],
            "rough_m": c["rough_m"], "sectors": 8 if m else c["sectors"], "rank": i + 1,
            "rank_score": c.get("rank_score"), "p_reranker": c.get("p_reranker"), "measurements": meas,
            "evidence": c.get("evidence"), "class": c.get("class")}


def export(area, label, n_per100=20, ranker="detector", county=None):
    import finder_rank as fr
    from build_site import duotone
    from finder_scan import AreaScan
    sc = AreaScan(area)
    km2 = fr.scanned_km2(area)
    cands = fr.ranked(area, ranker)
    N = round(n_per100 * km2 / 100)
    import finder_osm
    if os.environ.get("DEMOTE", "1") == "1":
        pool = cands[:3 * N]
        keep_, low = [], []
        for c in pool:
            (low if set(finder_osm.settings_at(c["lon"], c["lat"])) & DEMOTE else keep_).append(c)
        n_dem = sum(1 for c in cands[:N] if set(finder_osm.settings_at(c["lon"], c["lat"])) & DEMOTE)
        cands = keep_ + low + cands[3 * N:]
        print(f"  post-filter: {n_dem} of the top {N} were on {sorted(DEMOTE)} land and moved down")
    top = evidence(cands[:N], county)
    out = os.path.join(ROOT, "web", "data", "scan", area)
    os.makedirs(os.path.join(out, "c"), exist_ok=True)
    for f in os.listdir(os.path.join(out, "c")):
        os.remove(os.path.join(out, "c", f))
    rows = []
    for i, c in enumerate(top):
        row = as_row(c, i, area)
        half = max(150.0, 3.0 * row["r_m"])
        z, bbox = dem_crop(c["lon"], c["lat"], half)
        g, clip = aw.render_relief(z.astype(np.float64), 1.0)
        im = Image.fromarray(duotone(g).astype(np.uint8))
        im.thumbnail((CROP_PX, CROP_PX), Image.LANCZOS)
        im.save(os.path.join(out, "c", f"{row['id']}.jpg"), quality=84, optimize=True)
        recs = (c["evidence"] or {}).get("records") or []
        row.update({"known": recs[0]["name"] if recs else None, "crop": f"c/{row['id']}.jpg",
                    "corners": [[round(v, 6) for v in p] for p in aw.corners(bbox)], "clip_m": round(float(clip), 2)})
        rows.append(row)
    kp = os.path.join(ROOT, "specs", f"known_{area}.json")
    known = json.load(open(kp)) if os.path.exists(kp) else []
    lon0, lat0, lon1, lat1 = sc.box
    from collections import Counter
    cls = Counter(r["class"] for r in rows)
    kinds = Counter(r["kind"] for r in rows)
    entry = {"name": area, "label": label, "area": list(sc.box),
             "size_km": [round(hav_m(lon0, lat0, lon1, lat0) / 1000, 1), round(hav_m(lon0, lat0, lon0, lat1) / 1000, 1)],
             "px_m": 2.0, "radii_m": [4.0, 32.0] if not kinds.get("ring") else [4.0, 270.0],
             "n_total": len(cands), "n_shown": len(rows), "ranker": ranker, "schema": "finder-2",
             "classes": dict(cls), "kinds": dict(kinds), "per100km2": n_per100,
             "demoted_settings": sorted(DEMOTE) if os.environ.get("DEMOTE", "1") == "1" else [],
             "known": [{"name": k["name"], "lon": k["lon"], "lat": k["lat"], "r_m": k.get("r_m", 0),
                        "expected": bool(k.get("expected")), "note": k.get("note", "")} for k in known]}
    if county:
        entry["mills1914_chance"] = mills_chance(area, county) if area in ("ross",) or os.path.exists(
            os.path.join(FD, f"randoms_{area}.jsonl")) else None
    aw.save_json(os.path.join(out, "candidates.json"), {**entry, "candidates": rows})
    sp = os.path.join(ROOT, "web", "data", "scans.json")
    scans = json.load(open(sp))["scans"] if os.path.exists(sp) else []
    scans = [s for s in scans if s["name"] != area] + [entry]
    aw.save_json(sp, {"scans": scans})
    aw.save_json(os.path.join(FD, f"classified_{area}.json"), {**entry, "candidates": rows})
    print(f"{area}: exported {len(rows)} of {len(cands)} ({dict(kinds)}); classes {dict(cls)}; "
          f"Mills chance {entry.get('mills1914_chance')}")
    return entry


if __name__ == "__main__":
    a = sys.argv
    export(a[1], a[2], *(int(v) for v in a[3:4]), *(a[4:6]))
