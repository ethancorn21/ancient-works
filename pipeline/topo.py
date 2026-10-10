"""USGS historical topographic maps for a site: the oldest large-scale edition, reprojected onto the site box.

usage: topo.py data/sites/<id>/site.json [--max-scale 62500] [--all-editions]
Writes web/data/sites/<id>/topo_<year>.webp and lists it in web/data/sites/<id>/depictions.json.

Old quads are mostly NAD27 polyconic GeoTIFFs with the sheet margin (collar) included; the collar is cut
off with the quad's own extent from the TNM catalogue. Most quads do not draw the earthworks: they are
context (roads, fields and towns of 1900), not depictions of the works.
"""
import json
import math
import os
import sys
import urllib.parse
import urllib.request

import numpy as np
import pyproj
import tifffile
from PIL import Image
from scipy.ndimage import map_coordinates

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aw  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw", "topo")
WEB = os.path.join(ROOT, "web", "data", "sites")
TNM = "https://tnmaccess.nationalmap.gov/api/v1/products"
pyproj.network.set_network_enabled(True)  # NADCON grids for NAD27 -> WGS84 come from cdn.proj.org


def find_quads(lon0, lat0, lon1, lat1):
    q = {"datasets": "Historical Topographic Maps", "bbox": f"{lon0},{lat0},{lon1},{lat1}",
         "prodFormats": "GeoTIFF", "max": 200}
    with urllib.request.urlopen(urllib.request.Request(TNM + "?" + urllib.parse.urlencode(q), headers=aw.UA), timeout=120) as r:
        items = json.load(r)["items"]
    out = []
    for it in items:
        url = (it.get("urls") or {}).get("GeoTIFF")
        title = it["title"]
        if not url or "-scale" not in title:
            continue
        scale = int(title.split("1:")[1].split("-")[0])
        bb = it["boundingBox"]
        out.append({"title": title, "year": int(it["publicationDate"][:4]), "scale": scale, "url": url,
                    "extent": [bb["minX"], bb["minY"], bb["maxX"], bb["maxY"]], "size": it.get("sizeInBytes")})
    return out


def fetch(url):
    os.makedirs(RAW, exist_ok=True)
    path = os.path.join(RAW, urllib.parse.unquote(url.rsplit("/", 1)[1]))
    if not os.path.exists(path):
        print("  downloading", os.path.basename(path))
        tmp = path + ".part"
        with urllib.request.urlopen(urllib.request.Request(url, headers=aw.UA), timeout=600) as r, open(tmp, "wb") as f:
            f.write(r.read())
        os.replace(tmp, path)
    return path


def geotiff_crs(g):
    """pyproj CRS from GeoTIFF keys (user-defined projections as used by the USGS historical quads)."""
    datum = {4267: "NAD27", 4269: "NAD83", 4326: "WGS84"}.get(g.get("GeographicTypeGeoKey"), None)
    if datum is None:
        raise ValueError(f"unhandled datum {g.get('GeographicTypeGeoKey')}")
    pcs = g.get("ProjectedCSTypeGeoKey")
    if pcs and pcs != 32767:
        return pyproj.CRS.from_epsg(int(pcs))
    ct = g.get("ProjCoordTransGeoKey")
    lon0 = g.get("ProjNatOriginLongGeoKey", g.get("ProjCenterLongGeoKey"))
    lat0 = g.get("ProjNatOriginLatGeoKey", g.get("ProjCenterLatGeoKey", 0))
    fe, fn = g.get("ProjFalseEastingGeoKey", 0), g.get("ProjFalseNorthingGeoKey", 0)
    if ct == 22:
        proj = f"+proj=poly +lat_0={lat0} +lon_0={lon0}"
    elif ct == 1:
        proj = f"+proj=tmerc +lat_0={lat0} +lon_0={lon0} +k={g.get('ProjScaleAtNatOriginGeoKey', 1)}"
    else:
        raise ValueError(f"unhandled projection transform {ct}")
    return pyproj.CRS.from_proj4(f"{proj} +x_0={fe} +y_0={fn} +datum={datum} +units=m +no_defs")


def warp_quad(path, extent, bbox, ow, oh):
    """Sample the quad onto a w x h grid over a Mercator bbox. Returns (rgb uint8, inside-neatline mask)."""
    t = tifffile.TiffFile(path)
    g = t.geotiff_metadata
    img = t.pages[0].asarray()
    if img.ndim == 2:
        img = np.dstack([img] * 3)
    sx, sy = g["ModelPixelScale"][:2]
    tx, ty = g["ModelTiepoint"][3:5]
    crs = geotiff_crs(g)
    to_src = pyproj.Transformer.from_crs("EPSG:3857", crs, always_xy=True)
    to_geo = pyproj.Transformer.from_crs("EPSG:3857", crs.geodetic_crs, always_xy=True)
    x0, y0, x1, y1 = bbox
    step = 8  # transform a coarse grid, interpolate between (the projections are smooth over a few km)
    cols, rows = np.arange(0, ow + step, step), np.arange(0, oh + step, step)
    X, Y = np.meshgrid(x0 + (cols + 0.5) * (x1 - x0) / ow, y1 - (rows + 0.5) * (y1 - y0) / oh)
    E, N = to_src.transform(X, Y)
    LON, LAT = to_geo.transform(X, Y)
    from scipy.ndimage import zoom
    up = lambda a: zoom(a, step, order=1)[:oh, :ow]
    C, R = up((E - tx) / sx - 0.5), up((ty - N) / sy - 0.5)
    lon_, lat_ = up(LON), up(LAT)
    ex0, ey0, ex1, ey1 = extent
    inside = (lon_ >= ex0) & (lon_ <= ex1) & (lat_ >= ey0) & (lat_ <= ey1)
    inside &= (C >= 0) & (C < img.shape[1] - 1) & (R >= 0) & (R < img.shape[0] - 1)
    out = np.zeros((oh, ow, 3), np.uint8)
    for c in range(3):
        out[..., c] = np.clip(map_coordinates(img[..., c].astype(np.float32), [R, C], order=1, cval=255), 0, 255)
    return out, inside


def main(path, max_scale=62500, all_editions=False):
    site = json.load(open(path))
    sid = site["id"]
    bbox = aw.site_bbox(site["lon"], site["lat"], site["width_m"], site["height_m"])
    (lon0, lat0), (lon1, lat1) = aw.to_lonlat(bbox[0], bbox[1]), aw.to_lonlat(bbox[2], bbox[3])
    quads = [q for q in find_quads(lon0, lat0, lon1, lat1) if q["scale"] <= max_scale]
    if not quads:
        print(sid, "no historical quads at 1:%d or larger" % max_scale)
        return
    # group sheets of one edition (same year + scale); a site on a sheet edge needs both neighbours
    editions = {}
    for q in quads:
        editions.setdefault((q["year"], q["scale"]), []).append(q)
    keys = sorted(editions) if all_editions else [min(editions)]
    px = max(2.0, max(site["width_m"], site["height_m"]) / 2000)  # quads are ~5 m/px; no point going finer
    ow, oh = int(site["width_m"] / px), int(site["height_m"] / px)
    out_dir = os.path.join(WEB, sid)
    os.makedirs(out_dir, exist_ok=True)
    dep_path = os.path.join(out_dir, "depictions.json")
    deps = json.load(open(dep_path)) if os.path.exists(dep_path) else {"depictions": []}
    for year, scale in keys:
        rgb = np.full((oh, ow, 3), 255, np.uint8)
        have = np.zeros((oh, ow), bool)
        titles = []
        # several scans of one sheet often exist (reprints); one per extent is enough
        seen = set()
        for q in editions[(year, scale)]:
            ext = tuple(round(v, 4) for v in q["extent"])
            if ext in seen:
                continue
            seen.add(ext)
            img, inside = warp_quad(fetch(q["url"]), q["extent"], bbox, ow, oh)
            take = inside & ~have
            rgb[take] = img[take]
            have |= inside
            titles.append(q["title"])
        if have.mean() < 0.05:
            print(sid, year, scale, "sheet does not reach the site box")
            continue
        alpha = (have * 255).astype(np.uint8)
        name = f"topo_{year}_{scale}.webp"
        Image.fromarray(np.dstack([rgb, alpha]), "RGBA").save(os.path.join(out_dir, name), quality=82, method=6)
        entry = {"kind": "topo", "file": name, "year": year, "label": f"USGS topographic map, {year}",
                 "scale": f"1:{scale:,}", "corners": aw.corners(bbox), "coverage": round(float(have.mean()), 3),
                 "source": "U.S. Geological Survey Historical Topographic Map Collection: " + "; ".join(titles)}
        deps["depictions"] = [d for d in deps["depictions"] if d.get("file") != name] + [entry]
        print(sid, entry["label"], entry["scale"], f"coverage {entry['coverage']:.0%}",
              os.path.getsize(os.path.join(out_dir, name)) // 1024, "KB")
    deps["depictions"].sort(key=lambda d: d.get("year", 0))
    aw.save_json(dep_path, deps)


if __name__ == "__main__":
    a = sys.argv[1:]
    ms = int(a[a.index("--max-scale") + 1]) if "--max-scale" in a else 62500
    main(a[0], ms, "--all-editions" in a)
