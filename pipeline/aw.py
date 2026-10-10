"""Shared helpers: Web Mercator math, bare-earth DEMs (USGS 3DEP; Europe via dem_sources.py) + USGS imagery exports,
local relief model rendering.

All exports are requested in EPSG:3857 so a MapLibre `image` source with the bbox corners lines up exactly.
"""
import io
import json
import math
import os
import time
import urllib.parse
import urllib.request

import numpy as np
import tifffile
from PIL import Image
from scipy.ndimage import gaussian_filter

R = 6378137.0
DEM_URL = "https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/exportImage"
IMG_URL = "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/export"
class NoLidar(RuntimeError):
    """No LiDAR source has data for the box (as opposed to a source that failed to answer)."""


UA = {"User-Agent": "ancient-works/0.2 (personal research; https://github.com/ethancorn21/ancient-works)"}


def to_merc(lon, lat):
    x = math.radians(lon) * R
    y = math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)) * R
    return x, y


def to_lonlat(x, y):
    return math.degrees(x / R), math.degrees(2 * math.atan(math.exp(y / R)) - math.pi / 2)


def ground_scale(lat):
    """Metres on the ground per Mercator metre at this latitude."""
    return math.cos(math.radians(lat))


def site_bbox(lon, lat, width_m, height_m):
    """Mercator bbox (xmin, ymin, xmax, ymax) centred on lon/lat covering width x height ground metres."""
    x, y = to_merc(lon, lat)
    k = 1 / ground_scale(lat)
    hw, hh = width_m / 2 * k, height_m / 2 * k
    return (x - hw, y - hh, x + hw, y + hh)


def corners(bbox):
    """MapLibre image-source corners (TL, TR, BR, BL) as [lon, lat]."""
    x0, y0, x1, y1 = bbox
    return [list(to_lonlat(x0, y1)), list(to_lonlat(x1, y1)), list(to_lonlat(x1, y0)), list(to_lonlat(x0, y0))]


def _get(url, params, tries=4):
    q = url + "?" + urllib.parse.urlencode(params)
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(q, headers=UA), timeout=180) as r:
                body = r.read()
                if r.headers.get("Content-Type", "").startswith("text"):
                    raise RuntimeError(body[:300])
                return body
        except Exception as e:  # service is slow and sometimes 5xx; back off and retry
            if i == tries - 1:
                raise
            print("  retry", i + 1, e)
            time.sleep(5 * (i + 1))


def fetch_dem(bbox, w, h, tile=2000):
    """Bare-earth DEM (metres, NaN = no data) for a Mercator bbox at w x h pixels.

    England, the Netherlands and France come from their national LiDAR DTMs; Scotland and the countries on the
    open-lidar-data mirror from public S3 (dem_sources.py). The US goes to USGS 3DEP: the ImageServer, and when
    that fails (it is slow and 5xx-prone, and some networks block it) the same DEMs read from the S3 tiles by
    usgs.py; AW_DEM=s3 skips the ImageServer."""
    import dem_sources  # imported here so that `import aw` stays as light as it was
    src = dem_sources.source_for_bbox(bbox)
    if src in ("ea", "ahn", "ign"):
        # the live outlines are generous along borders (Burnswark, in Scotland, falls inside England's): a service that
        # errors or answers mostly nodata hands over to the S3 sources when one covers the box
        static = dem_sources.static_source_for_bbox(bbox)
        try:
            z = dem_sources.fetch(src, bbox, w, h)
            # EA answers outside England with zeros, not nodata (Burnswark 2026-10-10: a 1.9 km box of 0.0 m)
            if not static or (np.isfinite(z) & (z != 0)).mean() > 0.5:
                return z
        except Exception:
            if not static:
                raise
        print(f"  {src} has no data here; reading {static}")
        return dem_sources.fetch_static(static, bbox, w, h)
    if src is None:
        static = dem_sources.static_source_for_bbox(bbox)
        if static:
            return dem_sources.fetch_static(static, bbox, w, h)
    if os.environ.get("AW_DEM") != "s3":
        try:
            return _fetch_3dep(bbox, w, h, tile)
        except Exception as e:
            print("  3DEP ImageServer failed (%s); reading the S3 tiles" % str(e)[:80])
    import usgs  # needs rasterio, so imported only when the S3 path is taken
    z, info = usgs.read_dem(bbox, w, h)
    for i in info:
        print("  DEM from %s (%.0f%%, collected to %s)" % (i["source"], 100 * i["share"], i["collect_end"]))
    return z


def _fetch_3dep(bbox, w, h, tile=2000):
    """USGS 3DEP DEM; big requests are fetched in tiles because the service answers 500 on very large exports."""
    if w > tile or h > tile:
        out = np.full((h, w), np.nan)
        x0, y0, x1, y1 = bbox
        sx, sy = (x1 - x0) / w, (y1 - y0) / h
        for r0 in range(0, h, tile):
            for c0 in range(0, w, tile):
                r1, c1 = min(h, r0 + tile), min(w, c0 + tile)
                sub = (x0 + c0 * sx, y1 - r1 * sy, x0 + c1 * sx, y1 - r0 * sy)
                out[r0:r1, c0:c1] = _fetch_3dep(sub, c1 - c0, r1 - r0, tile)
        return out
    body = _get(DEM_URL, {
        "bbox": ",".join(f"{v:.3f}" for v in bbox), "bboxSR": 3857, "imageSR": 3857,
        "size": f"{w},{h}", "format": "tiff", "pixelType": "F32",
        "interpolation": "RSP_BilinearInterpolation", "f": "image",
    })
    z = tifffile.imread(io.BytesIO(body)).astype(np.float64)
    z[(z < -1000) | ~np.isfinite(z)] = np.nan
    return z


def fetch_imagery(bbox, w, h):
    body = _get(IMG_URL, {
        "bbox": ",".join(f"{v:.3f}" for v in bbox), "bboxSR": 3857, "imageSR": 3857,
        "size": f"{w},{h}", "format": "jpg", "f": "image",
    })
    return Image.open(io.BytesIO(body)).convert("RGB")


def fill_nan(z):
    if np.isnan(z).all():
        raise NoLidar("no elevation data in this bbox")
    return np.where(np.isnan(z), np.nanmedian(z), z)


def local_relief(z, px_m, radius_m=24.0):
    """DEM minus a smoothed copy: removes natural slope, keeps features smaller than ~radius."""
    return z - gaussian_filter(z, radius_m / px_m)


def hillshade(z, px_m, az=315, alt=35, exag=3.0):
    gy, gx = np.gradient(z * exag, px_m)
    slope = np.arctan(np.hypot(gx, gy))
    aspect = np.arctan2(-gx, gy)
    a, b = math.radians(az), math.radians(alt)
    hs = np.sin(b) * np.cos(slope) + np.cos(b) * np.sin(slope) * np.cos(a - aspect)
    return np.clip(hs, 0, 1)


def render_relief(z, px_m, clip_m=None, ignore=None, radius_m=24.0):
    """Grayscale relief picture: raised = light, sunken = dark, plus a soft hillshade for texture.

    The contrast stretch comes from open ground only (`ignore` masks roads, quarries, water), so highway
    embankments do not wash out half-metre walls. Returns (uint8 image array, clip used in metres).
    """
    z = fill_nan(z)
    lrm = local_relief(z, px_m, radius_m)
    if clip_m is None:
        sample = lrm if ignore is None or ignore.all() else lrm[~ignore]
        lo, hi = np.percentile(sample, [2, 98])
        clip_m = float(min(max(abs(lo), abs(hi), 0.15), 1.2))  # bluffs may clip; walls need the contrast
    rel = np.clip(lrm / clip_m, -1, 1) * 0.5 + 0.5
    hs = hillshade(z, px_m)
    mix = 0.78 * rel + 0.22 * hs
    return (np.clip(mix, 0, 1) * 255).astype(np.uint8), clip_m


def ink_mask(rgb, have):
    """Covered pixels that differ from the sheet's paper colour (median) by 40+ levels: lines, lettering, tints."""
    out = np.zeros(have.shape, bool)
    px = rgb[have].astype(np.int16)
    if len(px):
        out[have] = np.abs(px - np.median(px, axis=0)).max(axis=1) > 40
    return out


def ink_share(rgb, have):
    """Share of the covered pixels that are ink (ink_mask). A map panel with almost none (< 0.5%) is blank paper: the
    sheet's extent reaches into the box but nothing was printed there."""
    return float(ink_mask(rgb, have)[have].mean()) if have.any() else 0.0


MIN_INK = 0.005


def save_json(path, obj):
    """Write JSON atomically, so a reader (or a second build running in parallel) never sees a half-written file."""
    tmp = f"{path}.{os.getpid()}.tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1)
    os.replace(tmp, path)


OVERPASS = "https://overpass-api.de/api/interpreter"


def osm_ways(bbox):
    """Roads, rails, buildings and water from OpenStreetMap for a Mercator bbox, as lists of (lon, lat) lines.

    Footways, paths and tracks are left out on purpose: at park sites they are mowed along the walls themselves.
    """
    lon0, lat0 = to_lonlat(bbox[0], bbox[1])
    lon1, lat1 = to_lonlat(bbox[2], bbox[3])
    b = f"{lat0:.6f},{lon0:.6f},{lat1:.6f},{lon1:.6f}"
    q = f"""[out:json][timeout:90];
(way["highway"~"^(motorway|trunk|primary|secondary|tertiary|unclassified|residential|service|living_street|road)(_link)?$"]({b});
 way["railway"]({b});way["building"]({b});way["natural"="water"]({b});
 way["waterway"]({b});way["landuse"~"quarry|reservoir"]({b}););
out geom;"""
    req = urllib.request.Request(OVERPASS, data=urllib.parse.urlencode({"data": q}).encode(), headers=UA)
    for i in range(4):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                els = json.load(r)["elements"]
            break
        except Exception as e:
            if i == 3:
                raise
            print("  overpass retry", e)
            time.sleep(10 * (i + 1))
    out = []
    for el in els:
        tags = el.get("tags", {})
        kind = ("road" if "highway" in tags else "rail" if "railway" in tags else
                "building" if "building" in tags else "waterway" if "waterway" in tags else "area")
        out.append((kind, [(p["lon"], p["lat"]) for p in el.get("geometry", [])]))
    return out


def modern_mask(bbox, w, h, px_m, ways=None):
    """Boolean mask of pixels on or next to modern features (roads, rails, buildings, water, quarries)."""
    from PIL import ImageDraw
    ways = osm_ways(bbox) if ways is None else ways
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    sx, sy = w / (bbox[2] - bbox[0]), h / (bbox[3] - bbox[1])
    widths = {"road": 30, "rail": 30, "building": 10, "waterway": 14, "area": 10}
    for kind, pts in ways:
        if len(pts) < 2:
            continue
        xy = []
        for lon, lat in pts:
            x, y = to_merc(lon, lat)
            xy.append(((x - bbox[0]) * sx, (bbox[3] - y) * sy))
        width = max(1, int(widths[kind] / px_m))
        if kind in ("building", "area") and xy[0] == xy[-1]:
            d.polygon(xy, fill=255)
        d.line(xy, fill=255, width=width, joint="curve")
    return np.asarray(m) > 0


def water_mask(z, px_m, win_m=9.0, grow_m=12.0):
    """Hydro-flattened water: 3DEP DEMs set lakes and wide rivers to one flat height, so slope is ~0."""
    from scipy.ndimage import binary_dilation, maximum_filter
    gy, gx = np.gradient(fill_nan(z), px_m)
    flat = maximum_filter(np.hypot(gx, gy), size=max(3, int(win_m / px_m))) < 0.002
    return binary_dilation(flat, iterations=max(1, int(grow_m / px_m)))
