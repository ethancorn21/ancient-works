"""Turn catalog entries (data/catalog/sites.jsonl) into sites on the globe: LiDAR relief + block, old maps, summary.

usage: build_catalog.py [--ids a,b,c] [--region US] [--top N] [--min-p 0.5] [--force]
For each entry: data/sites/<id>/site.json -> build_site (relief, block) -> depict.py (Europe; no USGS topos) -> nls.py (Britain
and Ireland: Roy's Military Survey and the Ordnance Survey 1st editions).
Entries come from data/catalog/sites.jsonl (Wikidata) and data/catalog/extras.jsonl (sites outside Wikidata's reach, coordinates
checked in LiDAR relief: data/catalog/location_checks.json). LiDAR: the live national services (dem_sources.SOURCES) or, for
pre-built sites only, Scotland's DTM tiles and the open-lidar-data point clouds (dem_sources.STATIC).
Skips sites already built unless --force. Sites without LiDAR coverage are skipped and listed.
The summary is the lead paragraph of the site's Wikipedia article (CC BY-SA, linked), never model text.
"""
import argparse
import json
import os
import re
import sys
import time
import traceback
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aw  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT = os.path.join(ROOT, "data", "catalog", "sites.jsonl")
EXTRAS = os.path.join(ROOT, "data", "catalog", "extras.jsonl")
SITES = os.path.join(ROOT, "data", "sites")
WEB = os.path.join(ROOT, "web", "data")

# site box (ground metres) by kind of work; a box is square
BOX = [("hillfort", 1600), ("enclosure", 1600), ("fort", 1600), ("camp", 1600), ("oppidum", 2400), ("henge", 1000),
       ("group", 1600), ("complex", 2000), ("dyke", 2000), ("linear", 2000), ("field", 1600), ("motte", 800),
       ("platform", 1000), ("effigy", 1200), ("mound", 800), ("barrow", 800), ("tumul", 800),
       ("castle", 800), ("town", 2000), ("garden", 1600)]  # walled towns as Van Deventer drew them; Kip's houses with their avenues


def box_m(entry):
    kind = " ".join(str(entry.get(k, "")) for k in ("kind", "name")).lower()
    for key, m in BOX:
        if key in kind:
            return m
    return 1200


def wiki_summary(entry):
    """Lead paragraph of the site's Wikipedia article: (text, url) or (None, None)."""
    urls = []
    for k in ("wikipedia_en", "enwiki", "wikipedia"):
        if isinstance(entry.get(k), str):
            urls.append(entry[k])
    w = entry.get("wikipedia") or entry.get("wikipedia_urls") or entry.get("wiki") or {}
    if isinstance(w, dict):
        urls += [w[k] for k in ("en", "fr", "nl", "de") if w.get(k)]
    elif isinstance(w, list):
        urls += w
    for url in urls:
        m = re.match(r"https?://(\w+)\.wikipedia\.org/wiki/(.+)", url)
        if not m:
            continue
        # quote what is not already %-escaped: a raw é in the title made urllib fail ("'ascii' codec can't encode", Kervédan)
        api = f"https://{m.group(1)}.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(m.group(2), safe='%/:()_,')}"
        try:
            with urllib.request.urlopen(urllib.request.Request(api, headers=aw.UA), timeout=30) as r:
                d = json.load(r)
            text = (d.get("extract") or "").strip()
            if text:
                return text, url
        except Exception as e:
            print("   wikipedia", e)
    return None, None


REGION_NAME = {"us": None, "england": "England", "wales": "Wales", "netherlands": "Netherlands", "france": "France",
               "scotland": "Scotland", "ireland": "Ireland", "denmark": "Denmark", "spain": "Spain", "switzerland": "Switzerland",
               "poland": "Poland", "lithuania": "Lithuania", "latvia": "Latvia", "belgium": "Belgium"}


def place_of(entry):
    a = entry.get("admin") or {}
    if isinstance(a, dict):  # catalog.py: {parish, county, district, state, departement, province, ...}
        parts = [a.get(k) for k in ("parish", "municipality", "commune", "county", "departement", "province", "state")]
    else:
        parts = [a]
    parts = [p for p in parts if p] or [entry.get("place")]  # extras rows carry their own place ("Watford", "Greenup County, Kentucky")
    parts = [p for p in parts if p]
    seen = []
    for p in parts:
        if p not in seen:
            seen.append(p)
    country = REGION_NAME.get(str(entry.get("region", "")).lower(), entry.get("region"))
    if country and country not in seen:
        seen.append(country)
    return ", ".join(str(p) for p in seen[-3:]) or None


def make_site(entry):
    sid = re.sub(r"[^a-z0-9_-]+", "-", str(entry["id"]).lower()).strip("-")
    m = entry.get("box_m") or box_m(entry)
    # hand-set box when the record's point or the kind's default box misses the works (specs/site_boxes.json)
    box = json.load(open(os.path.join(ROOT, "specs", "site_boxes.json"))).get(sid, {})
    m = box.get("m", m)
    text, url = wiki_summary(entry)
    site = {"id": sid, "name": box.get("name", entry["name"]), "place": place_of(entry),
            "lon": float(box.get("lon", entry["lon"])), "lat": float(box.get("lat", entry["lat"])),
            "width_m": m, "height_m": m, "px_m": 1.0, "region": REGION_NAME.get(str(entry.get("region", "")).lower()) or "US",
            "kind": entry.get("kind"), "period": entry.get("period"),
            "qid": entry.get("qid"), "summary": text, "wiki": url, "status": entry.get("status"),
            "lrm_radius_m": box.get("lrm_radius_m", entry.get("lrm_radius_m")), "relief_clip_m": entry.get("relief_clip_m"),
            "skip_maps": entry.get("skip_maps"),
            "aka": ", ".join(entry.get("aliases", [])[:2]) if isinstance(entry.get("aliases"), list) else entry.get("aliases")}
    return {k: v for k, v in site.items() if v not in (None, "", [])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids")
    ap.add_argument("--region")
    ap.add_argument("--top", type=int)
    ap.add_argument("--min-p", type=float, help="minimum relief-triage probability (needs data/catalog/triage_scores.jsonl)")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    import build_site
    import dem_sources
    import depict
    import nls
    rows = [json.loads(l) for l in open(CAT)]
    if os.path.exists(EXTRAS):
        rows += [json.loads(l) for l in open(EXTRAS) if l.strip()]
    if a.ids:
        want = set(a.ids.split(","))
        rows = [r for r in rows if r["id"] in want]
    if a.region:
        rows = [r for r in rows if str(r.get("region", "")).lower() == a.region.lower()]
    rows.sort(key=lambda r: (-(r.get("wiki_links") or 0), -(r.get("sitelinks") or 0)))
    if a.min_p is not None:
        tp = os.path.join(ROOT, "data", "catalog", "triage_scores.jsonl")
        scores = {}
        for l in open(tp):
            d = json.loads(l)
            if d.get("id") is not None and d.get("clef_p") is not None:
                scores[d["id"]] = d["clef_p"]
        rows = [r for r in rows if scores.get(r["id"], 0) >= a.min_p]
    alias = json.load(open(os.path.join(ROOT, "specs", "aliases.json")))
    rows = [r for r in rows if r["id"] not in alias]  # same place as a hand-built site
    if a.top:
        rows = rows[:a.top]
    built = {s["id"] for s in json.load(open(os.path.join(WEB, "sites.json")))["sites"]}
    newest = time.gmtime().tm_year - depict.MIN_AGE_YEARS
    done, skipped, failed = [], [], []
    for i, entry in enumerate(rows):
        site = make_site(entry)
        sid = site["id"]
        sdir = os.path.join(SITES, sid)
        if sid in built and not a.force:
            continue
        if float(entry["lon"]).is_integer() and float(entry["lat"]).is_integer():
            skipped.append((sid, "coordinate rounded to whole degrees: not a place"))  # Bibrax: 3.0, 49.0
            continue
        bbox = aw.site_bbox(site["lon"], site["lat"], site["width_m"], site["height_m"])
        src = dem_sources.source_for_bbox(bbox) or dem_sources.static_source_for_bbox(bbox)
        # no LiDAR: still worth a site when an old map of the place may fit the aerial photograph (Ethan 2026-10-10), or
        # when the record says so ("aerial_ok": a town or garden that comes with its own old plan)
        old_map = (entry.get("aerial_ok") or nls.covers(site["lon"], site["lat"])
                   or any(depict.covers(L, site["lon"], site["lat"]) and L["year"] <= newest for L in depict.LAYERS.values()))
        if src is None and not old_map:
            skipped.append((sid, "no LiDAR source, no old map"))
            continue
        print(f"[{i + 1}/{len(rows)}] {sid} ({src or 'aerial'}, {site['width_m']} m)", flush=True)
        t = time.time()
        try:
            os.makedirs(sdir, exist_ok=True)
            path = os.path.join(sdir, "site.json")
            json.dump(site, open(path, "w"), indent=1)
            ground = build_site.main(path, aerial_ok=old_map)
            # no USGS topographic quads: they show roads and fields, not the works (Ethan 2026-10-10)
            maps = depict.build(site)
            nls.build(path)  # no-op outside Britain and Ireland
            if ground == "aerial" and not entry.get("aerial_ok"):
                dp = os.path.join(WEB, "sites", sid, "depictions.json")
                if not (os.path.exists(dp) and json.load(open(dp))["depictions"]):
                    build_site.drop(sid)
                    skipped.append((sid, "no LiDAR, and no old map came out here"))
                    continue
            done.append(sid)
            print(f"   ok {time.time() - t:.0f}s", flush=True)
        except Exception as e:
            failed.append((sid, f"{type(e).__name__}: {e}"))
            traceback.print_exc(limit=2)
    print(f"built {len(done)}, skipped {len(skipped)}, failed {len(failed)}")
    for sid, why in skipped + failed:
        print("  ", sid, why)


if __name__ == "__main__":
    main()
