"""Turn catalog entries (data/catalog/sites.jsonl) into sites on the globe: LiDAR relief + block, old maps, summary.

usage: build_catalog.py [--ids a,b,c] [--region US] [--top N] [--min-p 0.5] [--force]
For each entry: data/sites/<id>/site.json -> build_site (relief, block) -> topo.py (US) / depict.py (Europe, Iowa).
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
SITES = os.path.join(ROOT, "data", "sites")
WEB = os.path.join(ROOT, "web", "data")

# site box (ground metres) by kind of work; a box is square
BOX = [("hillfort", 1600), ("enclosure", 1600), ("fort", 1600), ("camp", 1600), ("oppidum", 2400), ("henge", 1000),
       ("group", 1600), ("complex", 2000), ("dyke", 2000), ("linear", 2000), ("field", 1600), ("motte", 800),
       ("platform", 1000), ("effigy", 1200), ("mound", 800), ("barrow", 800), ("tumul", 800)]


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
        if entry.get(k):
            urls.append(entry[k])
    w = entry.get("wikipedia_urls") or entry.get("wiki") or {}
    if isinstance(w, dict):
        urls += [w[k] for k in ("en", "fr", "nl", "de") if w.get(k)]
    elif isinstance(w, list):
        urls += w
    for url in urls:
        m = re.match(r"https?://(\w+)\.wikipedia\.org/wiki/(.+)", url)
        if not m:
            continue
        api = f"https://{m.group(1)}.wikipedia.org/api/rest_v1/page/summary/{m.group(2)}"
        try:
            with urllib.request.urlopen(urllib.request.Request(api, headers=aw.UA), timeout=30) as r:
                d = json.load(r)
            text = (d.get("extract") or "").strip()
            if text:
                return text, url
        except Exception as e:
            print("   wikipedia", e)
    return None, None


def place_of(entry):
    parts = [entry.get(k) for k in ("admin", "admin_area", "county", "state", "region_name")]
    parts = [p for p in parts if p]
    country = {"US": None, "EN": "England", "GB": "England", "NL": "Netherlands", "FR": "France", "WA": "Wales",
               "DK": "Denmark", "BE": "Belgium"}.get(str(entry.get("region", "")).upper(), entry.get("region"))
    if country and country not in parts:
        parts.append(country)
    return ", ".join(str(p) for p in parts) or None


def make_site(entry):
    sid = re.sub(r"[^a-z0-9_-]+", "-", str(entry["id"]).lower()).strip("-")
    m = box_m(entry)
    text, url = wiki_summary(entry)
    site = {"id": sid, "name": entry["name"], "place": place_of(entry), "lon": float(entry["lon"]), "lat": float(entry["lat"]),
            "width_m": m, "height_m": m, "px_m": 1.0, "region": entry.get("region"), "kind": entry.get("kind"),
            "qid": entry.get("qid"), "summary": text, "wiki": url,
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
    import topo
    rows = [json.loads(l) for l in open(CAT)]
    if a.ids:
        want = set(a.ids.split(","))
        rows = [r for r in rows if r["id"] in want]
    if a.region:
        rows = [r for r in rows if str(r.get("region", "")).upper() == a.region.upper()]
    rows.sort(key=lambda r: -(r.get("sitelinks") or r.get("sitelink_count") or 0))
    if a.min_p is not None:
        tp = os.path.join(ROOT, "data", "catalog", "triage_scores.jsonl")
        scores = {}
        for l in open(tp):
            d = json.loads(l)
            if d.get("id") is not None and d.get("clef_p") is not None:
                scores[d["id"]] = d["clef_p"]
        rows = [r for r in rows if scores.get(r["id"], 0) >= a.min_p]
    if a.top:
        rows = rows[:a.top]
    done, skipped, failed = [], [], []
    for i, entry in enumerate(rows):
        site = make_site(entry)
        sid = site["id"]
        sdir = os.path.join(SITES, sid)
        if os.path.exists(os.path.join(WEB, "sites", sid, "relief.jpg")) and not a.force:
            continue
        bbox = aw.site_bbox(site["lon"], site["lat"], site["width_m"], site["height_m"])
        src = dem_sources.source_for_bbox(bbox)
        if src is None:
            skipped.append((sid, "no LiDAR source"))
            continue
        print(f"[{i + 1}/{len(rows)}] {sid} ({src}, {site['width_m']} m)", flush=True)
        t = time.time()
        try:
            os.makedirs(sdir, exist_ok=True)
            path = os.path.join(sdir, "site.json")
            json.dump(site, open(path, "w"), indent=1)
            build_site.main(path)
            if src == "usgs":
                topo.main(path)
            depict.build(site)
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
