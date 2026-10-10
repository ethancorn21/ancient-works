"""National Library of Scotland map tiles for a site: Roy's Military Survey and the Ordnance Survey 1st editions of Britain
and Ireland, mosaicked onto the site box.

Only surveys at least 150 years old (Ethan 2026-10-10: "if the surveys are less than 150 years old, don't include them";
age is the point, the works unchanged for a couple hundred years). The NLS also serves the OS 2nd editions (1888-1913), the
1973 1:10,000, the 1944-50 air photos and LiDAR hillshades; those were dropped when this came over from the cloud branch, and
so were the "25-inch 1st edition" sets, whose edition was only inferred (the Wiltshire set has coloured roads: a later edition).

usage: nls.py data/sites/<id>/site.json [--px 1.5] [--layers six-inch,25-inch,...] [--list]
Writes web/data/sites/<id>/<layer>.webp and lists each in web/data/sites/<id>/depictions.json (kind "map").

The tiles are plain XYZ PNGs in Web Mercator on S3 (https://mapseries-tilesets.s3.amazonaws.com/<set>/{z}/{x}/{y}.png,
no key, no CORS headers, so the server or this script has to fetch them). Sets are per county, so every set that has a tile at the
site is used. NLS says the tiles are free for personal and research use with credit (CC-BY on many layers: check a layer's
licence in their Georeferenced Maps viewer before any public use). Ordnance Survey maps: Crown copyright, out of copyright or
open-licensed through the NLS.
"""
import concurrent.futures as cf
import io
import json
import math
import os
import sys
import time
import urllib.error
import urllib.request

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aw  # noqa: E402
import s3  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw", "nls")
WEB = os.path.join(ROOT, "web", "data", "sites")
BUCKET = "mapseries-tilesets"
CREDIT = "Maps: National Library of Scotland (maps.nls.uk), Ordnance Survey"

# family -> how its sets are named on S3 and how they are labelled. The dates are the NLS/OS ranges for the edition, not per sheet.
# Which edition a set holds was read off the maps (side-by-side tiles at Amesbury, Newgrange): "inferred" labels are marked so.
FAMILIES = {
    # surveyed county by county, northern counties in the 1840s-60s, southern ones as late as the 1880s (Wiltshire's Silbury sheet
    # is c. 1880: about 145 years old); NLS's sheet dates were not reachable, so the edition range is what the label says
    "six-inch-1st": dict(kind="map", scale="1:10,560", years="surveyed 1840s-1880s by county", year=1842, maxz=17, inferred=True,
                         label="Ordnance Survey six-inch map, England and Wales, 1st edition"),
    "scotland-6-first": dict(kind="map", scale="1:10,560", years="1st edition, 1843-1882", year=1843, maxz=17, sets=["os/6inchfirst"],
                             label="Ordnance Survey six-inch map, Scotland, 1st edition"),
    "ireland-6-first": dict(kind="map", scale="1:10,560", years="1st edition, surveyed 1829-1842", year=1829, maxz=17,
                            label="Ordnance Survey six-inch map of Ireland, 1st edition"),
    "ireland-6-first-b": dict(kind="map", scale="1:10,560", years="1st edition, later printing c. 1860", year=1860, maxz=17,
                              label="Ordnance Survey six-inch map of Ireland, 1st edition (c. 1860 printing)"),
    "roy": dict(kind="map", scale="c. 1:36,000", years="1747-1755", year=1750, maxz=14, sets=["roy/lowlands", "roy/highlands"],
                label="Roy's Military Survey of Scotland"),
}
MIN_AGE_YEARS = 150  # a family whose edition starts later than this many years ago is not built
IRISH = ("antrim armagh carlow cavan clare cork donegal down dublin fermanagh galway kerry kildare kilkenny kings leitrim limerick "
         "londonderry longford louth mayo meath monaghan queens roscommon sligo tipperary tyrone waterford westmeath wexford wicklow").split()
SKIP_25 = ("key", "parishes", "holes", "blue", "govan", "edinburgh_1914", "additions", "addition", "correction", "Shrop", "wales")


def set_names():
    """{family: [S3 tileset paths]} from the bucket listing (cached)."""
    path = os.path.join(RAW, "sets.json")
    if not os.path.exists(path):
        os.makedirs(RAW, exist_ok=True)
        os_sets = {p.rstrip("/").split("/")[-1] for p in s3.ls(BUCKET, "os/")[0]}
        inch25 = [p.rstrip("/") for p in s3.ls(BUCKET, "25_inch/")[0]]
        inch25 = [p for p in inch25 if "/" in p and not any(w in p for w in SKIP_25)]
        second = lambda p: p.endswith(("2nd", "_2", "_2_new"))
        out = {
            "six-inch-1st": sorted("os/" + n for n in os_sets if n.startswith("six-inch-") and not n.endswith("V")),
            "25-inch-1st": sorted(p for p in inch25 if not second(p) and not p.endswith("3rd")),
            "25-inch-2nd": sorted(p for p in inch25 if second(p)),
            "ireland-6-first": sorted("os/" + n for n in IRISH if n in os_sets),
            "ireland-6-first-b": sorted("os/" + n + "1" for n in IRISH if n + "1" in os_sets),
            "ireland-6-second": sorted("os/" + n + "_2nd" for n in IRISH if n + "_2nd" in os_sets),
        }
        json.dump(out, open(path, "w"), indent=1)
    out = json.load(open(path))
    for k, f in FAMILIES.items():
        if "sets" in f:
            out[k] = f["sets"]
    return out


def world_px(mx, my, z):
    """Web Mercator metres -> pixel position in the z-level world raster (origin top-left)."""
    n = 256 * 2 ** z
    half = math.pi * aw.R
    return (mx + half) / (2 * half) * n, (half - my) / (2 * half) * n


def tile_range(bbox, z):
    (x0, y0), (x1, y1) = world_px(bbox[0], bbox[3], z), world_px(bbox[2], bbox[1], z)
    return int(x0 // 256), int(y0 // 256), int(x1 // 256), int(y1 // 256), (x0, y0, x1, y1)


def tile(path, z, x, y):
    """One tile as RGBA, or None when the set has none there. Cached on disk (an empty file marks a known miss)."""
    cache = os.path.join(RAW, path, str(z), str(x), f"{y}.png")
    if os.path.exists(cache):
        if not os.path.getsize(cache):
            return None
        try:
            return Image.open(cache).convert("RGBA")
        except Exception:  # a download that was cut off: fetch it again
            os.remove(cache)
    os.makedirs(os.path.dirname(cache), exist_ok=True)
    u = s3.url(BUCKET, f"{path}/{z}/{x}/{y}.png")
    try:
        body = s3.get(u)
    except urllib.error.HTTPError as e:
        if e.code in (403, 404):
            open(cache, "wb").close()
            return None
        raise
    img = Image.open(io.BytesIO(body)).convert("RGBA")  # raises on a truncated body, before it is cached
    tmp = f"{cache}.{os.getpid()}.part"
    with open(tmp, "wb") as f:
        f.write(body)
    os.replace(tmp, cache)
    return img


def has_tile(path, lon, lat, z):
    mx, my = aw.to_merc(lon, lat)
    px, py = world_px(mx, my, z)
    t = tile(path, z, int(px // 256), int(py // 256))
    return t is not None and bool((np.asarray(t)[..., 3] > 8).any())  # counties return transparent tiles beyond their edge


def mosaic(path, bbox, z, ow, oh):
    """The tiles of one set covering the box, stitched, cropped to the box and resampled to ow x oh. Returns (RGBA, share of the box with data)."""
    tx0, ty0, tx1, ty1, (x0, y0, x1, y1) = tile_range(bbox, z)
    jobs = [(x, y) for y in range(ty0, ty1 + 1) for x in range(tx0, tx1 + 1)]
    with cf.ThreadPoolExecutor(16) as ex:
        tiles = list(ex.map(lambda j: tile(path, z, *j), jobs))
    if not any(t is not None for t in tiles):
        return None, 0.0
    big = Image.new("RGBA", ((tx1 - tx0 + 1) * 256, (ty1 - ty0 + 1) * 256), (0, 0, 0, 0))
    for (x, y), t in zip(jobs, tiles):
        if t is not None:
            big.paste(t, ((x - tx0) * 256, (y - ty0) * 256))
    box = (x0 - tx0 * 256, y0 - ty0 * 256, x1 - tx0 * 256, y1 - ty0 * 256)
    out = big.resize((ow, oh), Image.LANCZOS, box=box)
    return out, float((np.asarray(out)[..., 3] > 8).mean())


def merge_counties(layers, px_m, window_m=100):
    """One sheet from several counties' sets. Each county's sheet runs on past its border as blank printed paper, and that
    paper is not transparent: stacked, it hid the next county's map over the site (2026-10-10: King Arthur's Round Table,
    Whitley Castle, Pons Aelius, Pen-y-clawdd all showed paper). Each pixel comes from the set with the most ink within
    ~100 m; where none has any, from the first set with data."""
    if len(layers) == 1:
        return layers[0]
    from scipy.ndimage import uniform_filter
    k = max(3, int(window_m / px_m))
    dens = []
    for arr in layers:
        got = arr[..., 3] > 8
        d = uniform_filter(aw.ink_mask(arr[..., :3], got).astype(np.float32), k)
        dens.append(np.where(got, d + 1e-6, -1.0))  # +1e-6: any data beats none; ties go to the first set
    pick = np.argmax(np.stack(dens), axis=0)
    return np.take_along_axis(np.stack(layers), pick[None, ..., None], 0)[0]


def covers(lon, lat):
    return -10.7 <= lon <= 1.9 and 49.8 <= lat <= 61.0  # the NLS sets cover Britain and Ireland only


def build(site_path, px=1.5, families=None, list_only=False):
    site = json.load(open(site_path))
    sid = site["id"]
    if not covers(site["lon"], site["lat"]):
        return
    bbox = aw.site_bbox(site["lon"], site["lat"], site["width_m"], site["height_m"])
    out_dir = os.path.join(WEB, sid)
    os.makedirs(out_dir, exist_ok=True)
    dep_path = os.path.join(out_dir, "depictions.json")
    deps = json.load(open(dep_path)) if os.path.exists(dep_path) else {"depictions": []}
    sets = set_names()
    probe = [(fam, p) for fam in FAMILIES if not families or fam in families for p in sets.get(fam, [])]
    with cf.ThreadPoolExecutor(16) as ex:  # one tile per set says whether the set covers the site (counties are separate sets)
        hit = set(fp for fp, ok in zip(probe, ex.map(lambda fp: has_tile(fp[1], site["lon"], site["lat"], min(15, FAMILIES[fp[0]]["maxz"])), probe)) if ok)
    skip = set(site.get("skip_maps", []))  # layers a person looked at and rejected for this site (data/catalog/candidates.json "skip_maps")
    newest = time.gmtime().tm_year - MIN_AGE_YEARS
    for fam, meta in FAMILIES.items():
        if (families and fam not in families) or fam in skip or meta["year"] > newest:
            continue
        z = meta["maxz"]
        paths = [p for p in sets.get(fam, []) if (fam, p) in hit]
        if not paths:
            continue
        if list_only:
            print(sid, fam, "->", paths)
            continue
        name = f"{fam.replace('scotland-', 'scot-')}.webp"
        fpx = max(min(px, meta.get("px", px)), max(site["width_m"], site["height_m"]) / 3200)  # a family may ask for finer pixels; never more than 3200 a side
        ow, oh = int(site["width_m"] / fpx), int(site["height_m"] / fpx)
        layers, used = [], []
        for p in paths:  # a site near a county line takes both counties' sets
            m, share = mosaic(p, bbox, z, ow, oh)
            if m is None:
                continue
            arr = np.asarray(m)
            got = arr[..., 3] > 8
            if meta["kind"] == "map" and got.any() and aw.ink_share(arr[..., :3], got) < aw.MIN_INK:
                continue  # the neighbouring county's sheet margin: blank paper that would hide the real map
            layers.append(arr)
            used.append(p)
        paths = used
        arr = merge_counties(layers, fpx) if layers else np.zeros((oh, ow, 4), np.uint8)
        img = Image.fromarray(arr, "RGBA")
        have = arr[..., 3] > 8
        cover = float(have.mean())
        if cover < 0.2:
            print(sid, fam, "covers only %.0f%% of the site box: skipped" % (100 * cover))
            continue
        if meta["kind"] == "map" and aw.ink_share(arr[..., :3], have) < aw.MIN_INK:  # e.g. the 1st-edition sheet that stops short of the site
            print(sid, fam, "the part of the sheet inside the box is blank paper: skipped")
            continue
        img.save(os.path.join(out_dir, name), quality=80, method=6)
        credit = meta.get("credit") or CREDIT
        entry = {"kind": meta["kind"], "file": name, "year": meta["year"], "years": meta["years"], "label": meta["label"],
                 "scale": meta["scale"], "corners": aw.corners(bbox), "coverage": round(cover, 3),
                 "source": f"{credit}: {meta['label']}, {meta['years']} (tile set {', '.join(paths)})"}
        if meta.get("inferred"):
            entry["note"] = "Edition read off the maps, not from NLS's layer list; confirm before quoting a date."
        deps["depictions"] = [d for d in deps["depictions"] if d.get("file") != name] + [entry]
        print(sid, entry["label"], entry["years"], f"coverage {cover:.0%}", os.path.getsize(os.path.join(out_dir, name)) // 1024, "KB")
    if not list_only:
        deps["depictions"].sort(key=lambda d: d.get("year", 0))
        aw.save_json(dep_path, deps)
        import depict  # the page's survey-red "ink" version of every old map (aerials are left alone)
        depict.add_ink(sid)


if __name__ == "__main__":
    a = sys.argv[1:]
    px = float(a[a.index("--px") + 1]) if "--px" in a else 1.5
    fams = a[a.index("--layers") + 1].split(",") if "--layers" in a else None
    build(a[0], px, fams, "--list" in a)
