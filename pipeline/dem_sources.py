"""Bare-earth DEMs by area, all returned as metres on an exact EPSG:3857 grid (row 0 = north edge).

  usgs  USGS 3DEP ImageServer            US; 1 m where 1 m lidar exists, else 1/3 arc-second (~10 m)
  ea    Environment Agency composite DTM  England (+ some old EA flights in Wales); 1 m; WCS 2.0.1, EPSG:27700
  ahn   AHN dtm_05m (PDOK)                Netherlands; 0.5 m; WCS 2.0.1, EPSG:28992; holes under buildings,
                                          water and dense trees are filled here (fill_gaps)
  ign   IGN LiDAR HD MNT (Geoplateforme)  France where delivered; 0.5 m grid; WMS-R raw float, EPSG:2154. In
                                          Oct 2026 whole 50-100 km blocks are still missing (e.g. the Morvan
                                          around Bibracte, central Brittany around Huelgoat)

Checked 2026-10-10 against each service's own EPSG:3857 output: features agree within 0.02 px.

The three European sources are fetched in their native CRS on their native grid (scaled server-side only
when the target is much coarser) and reprojected here with pyproj + one bilinear pass, so every source
lands on exactly the requested Mercator pixels. OSTN15 (England) is downloaded once into
data/tilecache/proj; without it pyproj falls back to a Helmert fit good to ~2 m.

Coverage: source_for(lon, lat) / source_for_bbox(bbox) use rough polygons (generous along borders and
coasts: the services return nodata outside their area, and callers treat all-NaN as "not covered").
probe=True also fetches a tiny DEM and returns None when it is all nodata.
"""
import io
import math
import os
import threading
import time
import urllib.parse
import urllib.request

import logging

import numpy as np
import tifffile

import aw

logging.getLogger("tifffile").setLevel(logging.ERROR)  # EA's GDAL_NODATA (-3.4e38 as text) makes it complain
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRID_DIR = os.path.join(ROOT, "data", "tilecache", "proj")
UA = {"User-Agent": "ancient-works/0.2 (personal research)"}
GRIDS = ["uk_os_OSTN15_NTv2_OSGBtoETRS.tif"]

EA_URL = "https://environment.data.gov.uk/spatialdata/lidar-composite-digital-terrain-model-dtm-1m/wcs"
EA_COVERAGE = "13787b9a-26a4-4775-8523-806d13af58fc__Lidar_Composite_Elevation_DTM_1m"
AHN_URL = "https://service.pdok.nl/rws/ahn/wcs/v1_0"
IGN_URL = "https://data.geopf.fr/wms-r/wms"
IGN_LAYER = "IGNF_LIDAR-HD_MNT_ELEVATION.ELEVATIONGRIDCOVERAGE.LAMB93"
LINEAR = "http://www.opengis.net/def/interpolation/OGC/1/linear"

# Rough areas as (lon, lat) rings. Order matters only where rings would overlap (they do not).
US = [[(-124.9, 48.5), (-123.2, 48.25), (-123.0, 49.05), (-95.15, 49.05), (-94.6, 48.7), (-89.6, 48.0),
       (-88.0, 48.3), (-84.6, 46.5), (-83.5, 46.1), (-82.4, 45.3), (-82.5, 42.7), (-83.1, 41.9), (-80.5, 42.2),
       (-79.0, 42.9), (-79.2, 43.5), (-76.5, 43.7), (-76.2, 44.3), (-74.8, 45.0), (-71.5, 45.0), (-70.8, 45.4),
       (-69.2, 47.45), (-67.8, 47.1), (-67.8, 45.6), (-66.9, 44.8), (-69.0, 43.8), (-70.6, 42.6), (-69.9, 41.6),
       (-71.9, 41.0), (-74.0, 40.3), (-75.0, 38.5), (-75.5, 37.0), (-75.4, 35.2), (-77.0, 34.4), (-78.6, 33.7),
       (-80.6, 32.1), (-81.3, 30.5), (-80.0, 26.8), (-80.1, 25.2), (-81.1, 24.5), (-82.2, 24.5), (-81.6, 25.8),
       (-82.9, 27.6), (-82.6, 28.8), (-84.0, 29.9), (-85.4, 29.6), (-88.0, 30.2), (-89.1, 30.0), (-89.2, 29.0),
       (-90.5, 29.0), (-93.5, 29.6), (-94.9, 29.2), (-97.2, 27.6), (-97.1, 25.9), (-99.1, 26.4), (-100.3, 28.0),
       (-101.4, 29.7), (-102.7, 29.7), (-103.2, 28.9), (-104.6, 29.6), (-106.5, 31.7), (-108.2, 31.7),
       (-108.2, 31.3), (-111.1, 31.3), (-114.8, 32.4), (-114.7, 32.7), (-117.2, 32.5), (-118.6, 33.6),
       (-120.0, 33.9), (-120.7, 34.5), (-121.9, 36.3), (-122.6, 37.3), (-123.1, 38.2), (-123.9, 39.7),
       (-124.5, 40.4), (-124.4, 42.8), (-124.1, 44.6), (-124.1, 46.4), (-124.9, 48.5)],   # lower 48, along the coast
      [(-179.9, 50.5), (-129.5, 54.3), (-129.5, 56.2), (-141.0, 60.4), (-141.0, 70.5), (-156.8, 71.8),
       (-169.0, 69.0), (-179.9, 65.0)],                                         # Alaska (rough)
      [(-160.6, 18.8), (-154.6, 18.8), (-154.6, 22.4), (-160.6, 22.4)],         # Hawaii
      [(-67.5, 17.8), (-65.2, 17.8), (-65.2, 18.6), (-67.5, 18.6)]]             # Puerto Rico
ENGLAND = [[(-6.5, 49.85), (-5.0, 49.9), (-3.5, 50.15), (-1.0, 50.55), (0.9, 50.8), (1.45, 51.15),
            (1.9, 51.45), (1.95, 52.95), (0.5, 53.1), (0.3, 53.75), (-0.5, 54.6), (-1.3, 55.2),
            (-1.75, 55.85), (-2.1, 55.85), (-2.6, 55.2), (-3.1, 55.05), (-3.6, 54.9), (-3.75, 54.5),
            (-3.3, 54.0), (-3.25, 53.45), (-3.05, 53.2), (-2.75, 52.95), (-3.2, 52.5), (-3.15, 52.0),
            (-2.7, 51.62), (-3.3, 51.35), (-4.7, 51.25), (-6.5, 50.4)]]
NETHERLANDS = [[(3.0, 51.2), (3.9, 51.15), (4.5, 51.4), (5.1, 51.25), (5.55, 51.1), (5.6, 50.72),
                (6.15, 50.72), (6.25, 51.0), (6.1, 51.2), (6.25, 51.55), (6.2, 51.85), (6.85, 51.8),
                (7.1, 52.2), (7.1, 52.65), (7.25, 53.0), (7.3, 53.35), (6.9, 53.65), (5.8, 53.6),
                (4.6, 53.3), (4.4, 52.6), (3.9, 52.0), (3.2, 51.6)]]
FRANCE = [[(2.6, 51.15), (4.2, 50.2), (4.8, 50.2), (4.9, 49.8), (5.8, 49.55), (6.4, 49.5), (8.25, 49.0),
           (7.6, 47.6), (6.9, 47.45), (6.0, 46.4), (6.0, 46.15), (6.8, 46.4), (7.05, 45.9), (6.6, 45.1),
           (7.1, 44.7), (7.0, 44.2), (7.7, 43.8), (7.6, 43.4), (6.0, 42.9), (4.0, 43.3), (3.2, 42.4),
           (1.8, 42.3), (0.7, 42.65), (-0.3, 42.75), (-1.4, 43.1), (-1.9, 43.35), (-1.6, 44.5),
           (-1.4, 46.0), (-2.4, 46.6), (-2.7, 47.2), (-4.9, 47.8), (-4.9, 48.6), (-3.0, 49.0),
           (-2.0, 48.75), (-1.95, 49.75), (-1.0, 49.75), (0.1, 49.55), (1.4, 50.2), (1.5, 50.9)],
          [(8.5, 41.3), (9.65, 41.3), (9.65, 43.05), (8.5, 43.05)]]                # Corsica

SOURCES = {
    "usgs": {"label": "USGS 3DEP", "native_m": 1.0, "areas": US,
             "attribution": "LiDAR: USGS 3DEP"},
    "ea": {"label": "Environment Agency LiDAR composite DTM", "native_m": 1.0, "areas": ENGLAND, "epsg": 27700,
           "attribution": "LiDAR: Environment Agency, Crown copyright, Open Government Licence v3.0"},
    "ahn": {"label": "AHN dtm_05m", "native_m": 0.5, "areas": NETHERLANDS, "epsg": 28992,
            "attribution": "LiDAR: AHN (Rijkswaterstaat)"},
    "ign": {"label": "IGN LiDAR HD MNT", "native_m": 0.5, "areas": FRANCE, "epsg": 2154,
            "attribution": "LiDAR: IGN, LiDAR HD (Licence Ouverte 2.0)"},
}
ORDER = ["usgs", "ea", "ahn", "ign"]
MAX_PX = 2500  # largest side of one upstream request; bigger areas are fetched in blocks
# EA's GeoServer drops whole rectangles from big scaled requests (a 38 km z12 chunk came back 10% empty, its
# halves complete), so its requests are also capped by ground extent
MAX_EXTENT_M = {"ea": 15000}


# ---------------------------------------------------------------- coverage
def _in_ring(lon, lat, ring):
    inside, j = False, len(ring) - 1
    for i in range(len(ring)):
        (xi, yi), (xj, yj) = ring[i], ring[j]
        if (yi > lat) != (yj > lat) and lon < (xj - xi) * (lat - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def _near_ring(lon, lat, ring, km):
    """Within km of the ring's outline (equirectangular, fine at this scale)."""
    k = math.cos(math.radians(lat))
    for (x0, y0), (x1, y1) in zip(ring, ring[1:] + ring[:1]):
        dx, dy = (x1 - x0) * k, y1 - y0
        t = max(0.0, min(1.0, (((lon - x0) * k) * dx + (lat - y0) * dy) / (dx * dx + dy * dy or 1)))
        if math.hypot((lon - x0) * k - t * dx, lat - y0 - t * dy) * 111.2 < km:
            return True
    return False


def _area_of(lon, lat, buffer_km=12.0):
    """Area holding lon/lat; failing that, an area whose outline is within buffer_km (coasts, islands, borders)."""
    for name in ORDER:
        if any(_in_ring(lon, lat, r) for r in SOURCES[name]["areas"]):
            return name
    for name in ORDER:
        if any(_near_ring(lon, lat, r, buffer_km) for r in SOURCES[name]["areas"]):
            return name
    return None


def _probe(name, bbox):
    try:
        z = fetch(name, bbox, 24, 24, tries=2)
    except Exception:
        return None
    return name if np.isfinite(z).any() else None


def source_for(lon, lat, probe=False):
    """Name of the DEM source covering lon/lat, or None. probe=True also checks the service has data there."""
    name = _area_of(lon, lat)
    if name and probe:
        return _probe(name, aw.site_bbox(lon, lat, 60, 60))
    return name


def sources_for_bbox(bbox):
    """Every source whose area holds the centre, a corner or an edge midpoint of a Mercator bbox, centre first."""
    x0, y0, x1, y1 = bbox
    xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
    out = []
    for x, y in [(xm, ym), (x0, y0), (x1, y0), (x1, y1), (x0, y1), (xm, y0), (xm, y1), (x0, ym), (x1, ym)]:
        name = _area_of(*aw.to_lonlat(x, y))
        if name and name not in out:
            out.append(name)
    return out


def source_for_bbox(bbox, probe=False):
    """Source for a Mercator bbox: the area holding its centre, else the first area holding a corner."""
    x0, y0, x1, y1 = bbox
    pts = [((x0 + x1) / 2, (y0 + y1) / 2), (x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    for x, y in pts:
        name = _area_of(*aw.to_lonlat(x, y))
        if name:
            return _probe(name, bbox) if probe else name
    return None


# ---------------------------------------------------------------- http + geotiff
def _get(url, params, tries=3):
    return _get_raw(url + "?" + urllib.parse.urlencode(params), tries)


def _read_geotiff(body):
    """-> (float64 array, x0, y0, sx, sy): top-left corner and pixel size (sy > 0 means rows go south)."""
    with tifffile.TiffFile(io.BytesIO(body)) as t:
        a = t.pages[0].asarray().astype(np.float64)
        g = t.geotiff_metadata or {}
    if "ModelTransformation" in g:
        m = g["ModelTransformation"]
        x0, y0, sx, sy = m[0][3], m[1][3], m[0][0], -m[1][1]
    else:
        s, tp = g["ModelPixelScale"], g["ModelTiepoint"]
        sx, sy = s[0], s[1]
        x0, y0 = tp[3] - tp[0] * sx, tp[4] + tp[1] * sy
    if g.get("GTRasterTypeGeoKey") == 2:  # PixelIsPoint: tiepoint is a pixel centre
        x0, y0 = x0 - sx / 2, y0 + sy / 2
    return a, x0, y0, sx, sy


# ---------------------------------------------------------------- reprojection
_tf_lock = threading.Lock()
_tf = {}


def _ensure_grids():
    os.makedirs(GRID_DIR, exist_ok=True)
    for f in GRIDS:
        p = os.path.join(GRID_DIR, f)
        if os.path.exists(p):
            continue
        try:
            with urllib.request.urlopen(urllib.request.Request("https://cdn.proj.org/" + f, headers=UA), timeout=60) as r:
                data = r.read()
            with open(p + ".tmp", "wb") as fh:
                fh.write(data)
            os.replace(p + ".tmp", p)
        except Exception as e:  # not fatal: pyproj falls back to a Helmert transformation (~2 m)
            print("  could not fetch PROJ grid", f, e, flush=True)


def _transformer(epsg):
    """3857 -> native CRS (pyproj >= 3.1 Transformers are thread-safe, so one per CRS)."""
    with _tf_lock:
        if epsg not in _tf:
            import pyproj
            if not _tf:  # grids must be on the data path before the first Transformer is built
                _ensure_grids()
                pyproj.datadir.append_data_dir(GRID_DIR)
            _tf[epsg] = pyproj.Transformer.from_crs(3857, epsg, always_xy=True)
        return _tf[epsg]


def _native_coords(epsg, bbox, w, h, step=16):
    """Native-CRS coordinates of every target pixel centre, from a coarse control grid expanded bilinearly."""
    from scipy.ndimage import map_coordinates
    x0, y0, x1, y1 = bbox
    sx, sy = (x1 - x0) / w, (y1 - y0) / h
    rows = np.arange(0, h + step, step, dtype=float)
    cols = np.arange(0, w + step, step, dtype=float)
    X, Y = np.meshgrid(x0 + (cols + 0.5) * sx, y1 - (rows + 0.5) * sy)
    E, N = _transformer(epsg).transform(X, Y)
    rr, cc = np.meshgrid(np.arange(h) / step, np.arange(w) / step, indexing="ij")
    return (map_coordinates(np.asarray(E), [rr, cc], order=1, mode="nearest"),
            map_coordinates(np.asarray(N), [rr, cc], order=1, mode="nearest"))


def _reproject(name, fetch_native, bbox, w, h, tries):
    """Fetch the native-CRS block covering bbox and resample it bilinearly onto the w x h Mercator grid."""
    from scipy.ndimage import map_coordinates
    src = SOURCES[name]
    E, N = _native_coords(src["epsg"], bbox, w, h)
    lat = aw.to_lonlat(0, (bbox[1] + bbox[3]) / 2)[1]
    target_m = (bbox[2] - bbox[0]) / w * aw.ground_scale(lat)
    # native pixels unless the target is much coarser; then let the server scale (one resample either way)
    res = src["native_m"] if target_m < 2 * src["native_m"] else target_m
    pad = 3 * res
    e0, e1 = math.floor((E.min() - pad) / res) * res, math.ceil((E.max() + pad) / res) * res
    n0, n1 = math.floor((N.min() - pad) / res) * res, math.ceil((N.max() + pad) / res) * res
    nw, nh = int(round((e1 - e0) / res)), int(round((n1 - n0) / res))
    out = np.full(E.shape, np.nan)
    # blocks keep each upstream request under MAX_PX a side
    side = min(MAX_PX, int(MAX_EXTENT_M.get(name, 1e12) / res))
    bw, bh = math.ceil(nw / math.ceil(nw / side)), math.ceil(nh / math.ceil(nh / side))
    for r0 in range(0, nh, bh):
        for c0 in range(0, nw, bw):
            cw, ch = min(bw, nw - c0), min(bh, nh - r0)
            sub = (e0 + c0 * res, n1 - (r0 + ch) * res, e0 + (c0 + cw) * res, n1 - r0 * res)
            a, ax0, ay0, asx, asy = _read_geotiff(fetch_native(sub, cw, ch, res, tries))
            a[~src["valid"](a)] = np.nan
            if name == "ign":  # the server blends -9999 into edge pixels before we see them
                from scipy.ndimage import binary_dilation
                a[binary_dilation(np.isnan(a), iterations=2)] = np.nan
            col = (E - ax0) / asx - 0.5
            row = (ay0 - N) / asy - 0.5
            inside = (col >= -0.5) & (col <= a.shape[1] - 0.5) & (row >= -0.5) & (row <= a.shape[0] - 0.5)
            if not inside.any():
                continue
            v = map_coordinates(a, [np.clip(row[inside], 0, a.shape[0] - 1), np.clip(col[inside], 0, a.shape[1] - 1)],
                                order=1, mode="nearest")
            out[inside] = np.where(np.isnan(out[inside]), v, out[inside])
    return out


# ---------------------------------------------------------------- per-service requests (native CRS)
def _ea_native(b, w, h, res, tries):
    q = (f"service=WCS&version=2.0.1&request=GetCoverage&coverageId={EA_COVERAGE}&format=image/tiff"
         f"&subset=E({b[0]:.2f},{b[2]:.2f})&subset=N({b[1]:.2f},{b[3]:.2f})")
    if res > SOURCES["ea"]["native_m"] * 1.01:
        q += f"&scalesize=i({w}),j({h})&interpolation={urllib.parse.quote(LINEAR, safe='')}"
    return _get_raw(EA_URL + "?" + q, tries)


def _ahn_native(b, w, h, res, tries):
    q = (f"SERVICE=WCS&VERSION=2.0.1&REQUEST=GetCoverage&COVERAGEID=dtm_05m&FORMAT=image/tiff"
         f"&SUBSET=x({b[0]:.2f},{b[2]:.2f})&SUBSET=y({b[1]:.2f},{b[3]:.2f})")
    if res > SOURCES["ahn"]["native_m"] * 1.01:
        q += f"&SCALESIZE=x({w}),y({h})&INTERPOLATION=BILINEAR"
    return _get_raw(AHN_URL + "?" + q, tries)


def _ign_native(b, w, h, res, tries):
    q = urllib.parse.urlencode({
        "SERVICE": "WMS", "VERSION": "1.3.0", "REQUEST": "GetMap", "LAYERS": IGN_LAYER, "STYLES": "normal",
        "CRS": "EPSG:2154", "BBOX": f"{b[0]:.2f},{b[1]:.2f},{b[2]:.2f},{b[3]:.2f}", "WIDTH": w, "HEIGHT": h,
        "FORMAT": "image/geotiff"})
    return _get_raw(IGN_URL + "?" + q, tries)


def _get_raw(q, tries):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(q, headers=UA), timeout=150) as r:
                body = r.read()
            if body[:4] not in (b"II*\x00", b"MM\x00*"):
                raise RuntimeError("not a GeoTIFF: " + body[:300].decode("utf-8", "replace"))
            return body
        except Exception as e:
            if i == tries - 1:
                raise
            print("  dem retry", i + 1, type(e).__name__, str(e)[:120], flush=True)
            time.sleep(3 * (i + 1))


SOURCES["ea"]["valid"] = lambda a: np.isfinite(a) & (a > -100) & (a < 2000)    # nodata -3.4e38
SOURCES["ahn"]["valid"] = lambda a: np.isfinite(a) & (a > -100) & (a < 1000)   # nodata +3.4e38
SOURCES["ign"]["valid"] = lambda a: np.isfinite(a) & (a > -500) & (a < 5000)   # nodata -9999


def _usgs(bbox, w, h, tries):
    """3DEP export with the same request as aw.fetch_dem, but short retries (for the tile server)."""
    body = _get(aw.DEM_URL, {
        "bbox": ",".join(f"{v:.3f}" for v in bbox), "bboxSR": 3857, "imageSR": 3857,
        "size": f"{w},{h}", "format": "tiff", "pixelType": "F32",
        "interpolation": "RSP_BilinearInterpolation", "f": "image",
    }, tries=tries)
    z = tifffile.imread(io.BytesIO(body)).astype(np.float64)
    z[(z < -1000) | (z > 1e30) | ~np.isfinite(z)] = np.nan
    return z


NATIVE = {"ea": _ea_native, "ahn": _ahn_native, "ign": _ign_native}


def fill_gaps(z, px_m, max_m=100.0):
    """Fill holes (AHN leaves buildings, water and dense trees empty) with a smooth surface pulled in from the
    surrounding ground; pixels more than max_m from any data stay NaN (sea, outside the country)."""
    from scipy.ndimage import distance_transform_edt, zoom
    nan = np.isnan(z)
    if not nan.any() or nan.all():
        return z

    def pushpull(v, ok):
        if ok.all() or min(v.shape) < 4:
            return np.where(ok, v, v[ok].mean() if ok.any() else 0.0)
        h, w = v.shape
        hp, wp = h + h % 2, w + w % 2
        vv = np.zeros((hp, wp)); oo = np.zeros((hp, wp))
        vv[:h, :w] = np.where(ok, v, 0.0); oo[:h, :w] = ok
        num = vv.reshape(hp // 2, 2, wp // 2, 2).sum((1, 3))
        den = oo.reshape(hp // 2, 2, wp // 2, 2).sum((1, 3))
        coarse = pushpull(np.where(den > 0, num / np.maximum(den, 1), 0.0), den > 0)
        up = zoom(coarse, 2, order=1, mode="nearest", grid_mode=True)[:h, :w]
        return np.where(ok, v, up)

    out = pushpull(z, ~nan)
    hole = nan.copy()
    for _ in range(12):  # relax the holes a little so their edges meet the ground without a step
        p = np.pad(out, 1, mode="edge")
        avg = (p[:-2, 1:-1] + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:]) / 4
        out[hole] = avg[hole]
    out[distance_transform_edt(nan) * px_m > max_m] = np.nan
    return out


def fetch(name, bbox, w, h, tries=3):
    """DEM (float64 metres, NaN = no data) from source `name` for a Mercator bbox at w x h pixels."""
    if name == "usgs":
        if w > 2000 or h > 2000:
            out = np.full((h, w), np.nan)
            x0, y0, x1, y1 = bbox
            sx, sy = (x1 - x0) / w, (y1 - y0) / h
            for r0 in range(0, h, 2000):
                for c0 in range(0, w, 2000):
                    r1, c1 = min(h, r0 + 2000), min(w, c0 + 2000)
                    out[r0:r1, c0:c1] = _usgs((x0 + c0 * sx, y1 - r1 * sy, x0 + c1 * sx, y1 - r0 * sy), c1 - c0, r1 - r0, tries)
            return out
        return _usgs(bbox, w, h, tries)
    z = _reproject(name, NATIVE[name], bbox, w, h, tries)
    if name != "ahn":  # EA and IGN deliver interpolated DTMs; their NaN is real "no data"
        return z
    lat = aw.to_lonlat(0, (bbox[1] + bbox[3]) / 2)[1]
    return fill_gaps(z, (bbox[2] - bbox[0]) / w * aw.ground_scale(lat))


if __name__ == "__main__":
    import sys
    lon, lat = float(sys.argv[1]), float(sys.argv[2])
    print(source_for(lon, lat), source_for(lon, lat, probe=True))
