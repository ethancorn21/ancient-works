"""Compact catalog for the page: web/data/catalog.json (every catalog entry as a pin; built sites are the full pages).

usage: tools/export_catalog.py
Reads data/catalog/sites.jsonl + specs/catalog_manual.jsonl; drops entries within 400 m of a hand-fitted site.
"""
import json
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGION = {"us": "US", "england": "England", "wales": "Wales", "netherlands": "Netherlands", "france": "France"}


def dist_m(a, b):
    k = math.cos(math.radians(a[1]))
    return math.hypot((a[0] - b[0]) * k, a[1] - b[1]) * 111320


def main():
    rows = [json.loads(l) for l in open(os.path.join(ROOT, "data", "catalog", "sites.jsonl"))]
    rows += [json.loads(l) for l in open(os.path.join(ROOT, "specs", "catalog_manual.jsonl"))]
    fitted = []
    for sid in os.listdir(os.path.join(ROOT, "data", "sites")):
        p = os.path.join(ROOT, "data", "sites", sid, "site.json")
        if os.path.exists(p):
            s = json.load(open(p))
            if "plate" in s:
                fitted.append((s["lon"], s["lat"]))
    out = []
    for r in rows:
        if any(dist_m((r["lon"], r["lat"]), f) < 400 for f in fitted):
            continue
        a = r.get("admin") or {}
        place = [a.get(k) for k in ("parish", "municipality", "commune", "county", "departement", "province", "state")] if isinstance(a, dict) else [a]
        place = [p for i, p in enumerate(place) if p and p not in place[:i]][-2:]
        w = r.get("wikipedia") or {}
        wiki = w.get("en") or next(iter(w.values()), None) if isinstance(w, dict) else None
        period = r.get("period") or []
        out.append([r["id"], r["name"], round(r["lon"], 6), round(r["lat"], 6), REGION.get(r.get("region"), r.get("region")),
                    r.get("kind") or "earthwork", ", ".join(place), wiki or "", r.get("qid") or "",
                    period[0] if isinstance(period, list) and period else (period or ""), r.get("wiki_links") or 0])
    out.sort(key=lambda x: -x[10])
    doc = {"cols": ["id", "name", "lon", "lat", "region", "kind", "place", "wiki", "qid", "period", "notability"], "rows": out,
           "source": "Wikidata (CC0) via pipeline/catalog.py; manual additions in specs/catalog_manual.jsonl"}
    path = os.path.join(ROOT, "web", "data", "catalog.json")
    json.dump(doc, open(path, "w"), separators=(",", ":"))
    print(len(out), "entries,", os.path.getsize(path) // 1024, "KB")


if __name__ == "__main__":
    main()
