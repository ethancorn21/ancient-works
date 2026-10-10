"""US LiDAR coverage check for every US catalog entry (USGS 3DEP).

Two probes per entry, both cached in data/raw/catalog/coverage.jsonl (append-only; a re-run skips entries
already done, so a killed run resumes):
  1. ImageServer `identify` at the point: the 3DEP catalog items under it. The finest item's pixel size and
     title say which source the DEM there comes from ('USGS 1 Meter ...' = 1 m LiDAR DEM; '1/9 arc-second'
     ~3 m, older LiDAR; '1/3 arc-second' ~10 m, mostly not LiDAR).
  2. aw.fetch_dem for 200 x 200 px at 1 m around the point: does real data come back (share of valid
     pixels) and how much 1-3 m detail it holds (hf_std_cm: std of DEM minus a 1.5 px gaussian). Coarse
     data resampled to 1 m has almost none, so this cross-checks probe 1.

The export service resamples whatever it has to the requested 1 m everywhere in the lower 48, so 'data came
back' alone says nothing about LiDAR; best_res_m is the field that does.

usage: catalog_cover.py [--limit N]     # then writes data/catalog/us_coverage.jsonl (compact copy)
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

import numpy as np
from scipy.ndimage import gaussian_filter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw", "catalog", "coverage.jsonl")
OUT = os.path.join(ROOT, "data", "catalog", "us_coverage.jsonl")
SITES = os.path.join(ROOT, "data", "catalog", "sites.jsonl")
IDENTIFY = "https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/identify"
UA = {"User-Agent": "ancient-works/0.2 (personal research)"}


def identify(lon, lat, tries=4):
    import aw
    x, y = aw.to_merc(lon, lat)
    q = IDENTIFY + "?" + urllib.parse.urlencode({
        "geometry": f"{x},{y}", "geometryType": "esriGeometryPoint", "sr": 3857,
        "returnCatalogItems": "true", "returnGeometry": "false", "returnPixelValues": "false", "f": "json"})
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(q, headers=UA), timeout=90) as r:
                d = json.load(r)
            if "error" in d:
                raise RuntimeError(str(d["error"])[:200])
            items = [f["attributes"] for f in d.get("catalogItems", {}).get("features", [])
                     if f["attributes"].get("Category") == 1]
            if not items:
                return {"best_res_m": None, "best_title": None, "has_1m": False}
            best = min(items, key=lambda a: a.get("LowPS") or 1e9)
            return {"best_res_m": round(best["LowPS"], 2), "best_title": best.get("title"),
                    "has_1m": any("1 Meter" in (a.get("title") or "") for a in items),
                    "acquired": time.strftime("%Y-%m-%d", time.gmtime(best["AcquisitionDate"] / 1000))
                    if best.get("AcquisitionDate") else None}
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep(5 * (i + 1))


def dem_probe(lon, lat, size=200):
    import aw
    bbox = aw.site_bbox(lon, lat, size, size)
    z = aw.fetch_dem(bbox, size, size)
    valid = np.isfinite(z)
    out = {"valid_frac": round(float(valid.mean()), 3)}
    if valid.mean() > 0.5:
        zf = np.where(valid, z, np.nanmedian(z))
        hf = (zf - gaussian_filter(zf, 1.5))[valid]
        out["hf_std_cm"] = round(float(hf.std() * 100), 2)
        out["relief_m"] = round(float(np.nanpercentile(z, 99) - np.nanpercentile(z, 1)), 1)
    return out


def check(lon, lat):
    rec = {}
    try:
        rec.update(identify(lon, lat))
    except Exception as e:
        rec["identify_error"] = str(e)[:200]
    try:
        rec.update(dem_probe(lon, lat))
    except Exception as e:
        rec["dem_error"] = str(e)[:200]
    rec["ok"] = rec.get("valid_frac", 0) > 0.9
    rec["lidar_1m"] = bool(rec.get("best_res_m") is not None and rec["best_res_m"] <= 1.5)
    return rec


def load_done():
    done = {}
    if os.path.exists(RAW):
        for line in open(RAW):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if "identify_error" not in r and "dem_error" not in r:
                done[r["id"]] = r
    return done


def main(limit=None):
    sites = [json.loads(l) for l in open(SITES)]
    us = [s for s in sites if s["region"] == "us"]
    done = load_done()
    todo = [s for s in us if s["id"] not in done][:limit]
    print(f"{len(us)} US entries, {len(done)} done, {len(todo)} to check", flush=True)
    os.makedirs(os.path.dirname(RAW), exist_ok=True)
    t0 = time.time()
    with open(RAW, "a") as f:
        for i, s in enumerate(todo):
            rec = {"id": s["id"], "lon": s["lon"], "lat": s["lat"], **check(s["lon"], s["lat"]),
                   "checked": time.strftime("%Y-%m-%d %H:%M")}
            f.write(json.dumps(rec) + "\n")
            f.flush()
            done[s["id"]] = rec
            if i % 25 == 0:
                print(f"  {i + 1}/{len(todo)} {s['id']} res={rec.get('best_res_m')} valid={rec.get('valid_frac')} "
                      f"hf={rec.get('hf_std_cm')} {time.time() - t0:.0f}s", flush=True)
            time.sleep(0.5)  # throttle: one entry at a time, half a second between
    keep = ("id", "ok", "lidar_1m", "best_res_m", "best_title", "acquired", "valid_frac", "hf_std_cm", "relief_m")
    with open(OUT, "w") as f:
        for s in us:
            r = done.get(s["id"])
            if r:
                f.write(json.dumps({k: r[k] for k in keep if k in r}) + "\n")
    n = [done[s["id"]] for s in us if s["id"] in done]
    print(f"checked {len(n)}/{len(us)}: data back {sum(r['ok'] for r in n)}, "
          f"1 m LiDAR source {sum(r['lidar_1m'] for r in n)}")


if __name__ == "__main__":
    lim = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    main(lim)
