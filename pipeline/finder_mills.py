"""Mills 1914, Archeological Atlas of Ohio: georeference a county map and extract its red site symbols.

Georeferencing: Census TIGER county-subdivision (township) boundaries are matched to the map's own line work.
  1. Four county corners read off the scan by eye give a first affine fit (data/finder/mills/<county>_seed.json).
  2. Dark (non-red) pixels -> distance transform; TIGER township and county lines, sampled every 100 m, are
     projected onto the scan and the mean truncated distance to the nearest dark pixel is minimised, first over
     an affine, then a second-order polynomial. Township lines that moved since 1914, roads and streams near
     them are outliers; the 12 px truncation keeps them from pulling the fit.
  3. Residual: per boundary sample, distance to the nearest dark pixel after the fit (median, 90th pct).
The independent check is the known sites (evaluate()): distance from each known work to the 1914 symbol drawn for it.

Symbols: red = high saturation, hue near 0. Connected components are classed by shape (legend p. IV):
  mound = small solid triangle; enclosure = hollow outline (circle, square, crescent) or a plan of one;
  burial = thin arc; other = anything else red (village, cemetery, quarry symbols). Merged blobs of triangles
  (dense groups) are counted by area / median single-triangle area.

usage:
  finder_mills.py georef <county>       fit, write data/finder/mills/<county>_georef.json + overlay jpg
  finder_mills.py extract <county>      symbols -> data/finder/mills_1914_<county>.jsonl (+ symbol overlay)
  finder_mills.py evaluate <county>     georeferencing error on known sites (data/finder/mills/<county>_known.json)
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from scipy.optimize import minimize

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aw  # noqa: E402
from finder_common import FD, ROOT, hav_m, save_jsonl  # noqa: E402

MD = os.path.join(FD, "mills")
TIGER = os.path.join(ROOT, "data", "raw", "finder", "tiger")
COUNTY_FIPS = {"ross": "141", "pike": "131"}


def page(county):
    for line in open(os.path.join(ROOT, "data", "books", "mills_county_maps.jsonl")):
        r = json.loads(line)
        if (r.get("county") or "").lower() == county:
            return os.path.join(ROOT, r["full_local"]), r
    raise SystemExit(f"no Mills page for {county}")


def tiger_lines(county):
    """Township polygons -> list of boundary polylines (lon, lat), interior and county outline, deduplicated."""
    d = json.load(open(os.path.join(TIGER, f"cousub_{county}.geojson")))
    edges = {}
    for f in d["features"]:
        g = f["geometry"]
        rings = g["coordinates"] if g["type"] == "Polygon" else [r for p in g["coordinates"] for r in p]
        for ring in rings:
            for a, b in zip(ring, ring[1:]):
                A, B = (round(a[0], 6), round(a[1], 6)), (round(b[0], 6), round(b[1], 6))
                key = (A, B) if A < B else (B, A)
                edges[key] = edges.get(key, 0) + 1
    return [(k, n) for k, n in edges.items()]  # n = 1: county outline, 2: between townships


def sample_lines(edges, step_m=100.0):
    pts, outer = [], []
    carry = 0.0
    for (A, B), n in edges:
        L = hav_m(A[0], A[1], B[0], B[1])
        t = carry
        while t < L:
            f = t / L
            pts.append((A[0] + f * (B[0] - A[0]), A[1] + f * (B[1] - A[1])))
            outer.append(n == 1)
            t += step_m
        carry = t - L
    return np.array(pts), np.array(outer)


class Frame:
    """Local metric frame (km east, km north) around a county centre."""

    def __init__(self, lon0, lat0):
        self.lon0, self.lat0 = lon0, lat0
        self.kx = 111.320 * math.cos(math.radians(lat0))
        self.ky = 110.950

    def fwd(self, lon, lat):
        return (np.asarray(lon) - self.lon0) * self.kx, (np.asarray(lat) - self.lat0) * self.ky

    def inv(self, x, y):
        return np.asarray(x) / self.kx + self.lon0, np.asarray(y) / self.ky + self.lat0


def design(x, y, order):
    cols = [np.ones_like(x), x, y]
    if order >= 2:
        cols += [x * x, x * y, y * y]
    if order >= 3:
        cols += [x ** 3, x * x * y, x * y * y, y ** 3]
    return np.stack(cols, -1)


def dark_mask(img):
    a = np.asarray(img.convert("RGB")).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    lum = 0.3 * r + 0.59 * g + 0.11 * b
    red = (r - g > 60) & (r > 120)
    return (lum < 135) & ~red


def red_mask(img):
    a = np.asarray(img.convert("RGB")).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return (r > 150) & (r - g > 70) & (r - b > 60)


def georef(county):
    os.makedirs(MD, exist_ok=True)
    path, meta = page(county)
    img = Image.open(path)
    W, H = img.size
    seed = json.load(open(os.path.join(MD, f"{county}_seed.json")))
    edges = tiger_lines(county)
    P, outer = sample_lines(edges)
    fr = Frame(P[:, 0].mean(), P[:, 1].mean())
    X, Y = fr.fwd(P[:, 0], P[:, 1])
    # corners of the TIGER outline for the seed (extremes along the diagonals in the local frame)
    o = outer
    corner = {"nw": np.argmax(Y[o] - X[o]), "ne": np.argmax(Y[o] + X[o]), "se": np.argmax(-Y[o] + X[o]),
              "sw": np.argmax(-Y[o] - X[o])}
    cx = {k: (X[o][i], Y[o][i]) for k, i in corner.items()}
    src = np.array([cx[k] for k in ("nw", "ne", "se", "sw")])
    dst = np.array([seed[k] for k in ("nw", "ne", "se", "sw")], float)
    A1 = design(src[:, 0], src[:, 1], 1)
    cu, *_ = np.linalg.lstsq(A1, dst[:, 0], rcond=None)
    cv, *_ = np.linalg.lstsq(A1, dst[:, 1], rcond=None)
    seed_res = np.hypot(A1 @ cu - dst[:, 0], A1 @ cv - dst[:, 1])
    print("seed affine residuals at the 4 corners (px):", seed_res.round(1))
    dark = dark_mask(img)
    dist = ndi.distance_transform_edt(~dark)
    TR = 12.0

    def cost(params, order):
        n = design(np.zeros(1), np.zeros(1), order).shape[1]
        pu, pv = params[:n], params[n:]
        D = design(X, Y, order)
        u, v = D @ pu, D @ pv
        ok = (u >= 0) & (u < W - 1) & (v >= 0) & (v < H - 1)
        d = np.full(len(u), TR)
        d[ok] = np.minimum(ndi.map_coordinates(dist, [v[ok], u[ok]], order=1), TR)
        return d.mean()

    p = np.concatenate([cu, cv])
    c0 = cost(p, 1)
    for _ in range(3):
        r = minimize(cost, p, args=(1,), method="Powell", options={"maxiter": 20000, "xtol": 1e-4, "ftol": 1e-5})
        p = r.x
    c1 = cost(p, 1)
    p2 = np.concatenate([p[:3], np.zeros(3), p[3:], np.zeros(3)])
    for _ in range(3):
        r = minimize(cost, p2, args=(2,), method="Powell", options={"maxiter": 40000, "xtol": 1e-5, "ftol": 1e-6})
        p2 = r.x
    c2 = cost(p2, 2)
    print(f"mean truncated distance (px): seed {c0:.2f}, affine {c1:.2f}, poly2 {c2:.2f}")
    D = design(X, Y, 2)
    u, v = D @ p2[:6], D @ p2[6:]
    ok = (u >= 0) & (u < W - 1) & (v >= 0) & (v < H - 1)
    dd = ndi.map_coordinates(dist, [v[ok], u[ok]], order=1)
    # map scale: metres per pixel from the affine part
    J = np.array([[p2[1], p2[2]], [p2[7], p2[8]]])  # px per km
    m_per_px = 1000 / math.sqrt(abs(np.linalg.det(J)))
    res = {"county": county, "page": os.path.relpath(path, ROOT), "frame": [fr.lon0, fr.lat0], "order": 2,
           "pu": p2[:6].tolist(), "pv": p2[6:].tolist(), "m_per_px": round(m_per_px, 1),
           "cost_px": {"seed": round(c0, 2), "affine": round(c1, 2), "poly2": round(c2, 2)},
           "line_residual_px": {"median": round(float(np.median(dd)), 2), "p75": round(float(np.percentile(dd, 75)), 2),
                                "p90": round(float(np.percentile(dd, 90)), 2), "share_within_3px": round(float((dd <= 3).mean()), 3),
                                "n": int(ok.sum())},
           "seed": seed, "tiger": "TIGERweb County Subdivisions (current), STATE 39 COUNTY " + COUNTY_FIPS[county]}
    aw.save_json(os.path.join(MD, f"{county}_georef.json"), res)
    print(json.dumps({k: res[k] for k in ("m_per_px", "cost_px", "line_residual_px")}))
    ov = img.convert("RGB").copy()
    dr = ImageDraw.Draw(ov)
    for (A, B), n in edges:
        ax, ay = fr.fwd(*A)
        bx, by = fr.fwd(*B)
        a = design(np.array([ax, bx]), np.array([ay, by]), 2)
        dr.line([(float((a @ p2[:6])[0]), float((a @ p2[6:])[0])), (float((a @ p2[:6])[1]), float((a @ p2[6:])[1]))],
                fill=(0, 120, 255) if n == 2 else (0, 200, 80), width=2)
    ov.save(os.path.join(MD, f"{county}_georef_overlay.jpg"), quality=85)
    return res


class Georef:
    def __init__(self, county):
        g = json.load(open(os.path.join(MD, f"{county}_georef.json")))
        self.g = g
        self.fr = Frame(*g["frame"])
        self.pu, self.pv = np.array(g["pu"]), np.array(g["pv"])
        # inverse: fit px -> km with a 3rd-order polynomial on a dense grid of the forward model
        gx, gy = np.meshgrid(np.linspace(-45, 45, 91), np.linspace(-35, 35, 71))
        gx, gy = gx.ravel(), gy.ravel()
        D = design(gx, gy, 2)
        u, v = D @ self.pu, D @ self.pv
        Di = design(u / 1000, v / 1000, 3)
        self.qx, *_ = np.linalg.lstsq(Di, gx, rcond=None)
        self.qy, *_ = np.linalg.lstsq(Di, gy, rcond=None)
        self.inv_err_m = float(np.sqrt(np.mean((Di @ self.qx - gx) ** 2 + (Di @ self.qy - gy) ** 2)) * 1000)

    def to_px(self, lon, lat):
        x, y = self.fr.fwd(lon, lat)
        D = design(np.atleast_1d(x).astype(float), np.atleast_1d(y).astype(float), 2)
        return D @ self.pu, D @ self.pv

    def to_lonlat(self, u, v):
        Di = design(np.atleast_1d(u).astype(float) / 1000, np.atleast_1d(v).astype(float) / 1000, 3)
        return self.fr.inv(Di @ self.qx, Di @ self.qy)


def components(county):
    path, _ = page(county)
    img = Image.open(path)
    red = red_mask(img)
    red = ndi.binary_closing(red, iterations=1)
    lab, n = ndi.label(red)
    objs = ndi.find_objects(lab)
    out = []
    for i, sl in enumerate(objs, 1):
        m = lab[sl] == i
        area = int(m.sum())
        if area < 12:
            continue
        h, w = m.shape
        fill = area / (h * w)
        filled = ndi.binary_fill_holes(m)
        hole = (filled.sum() - area) / max(filled.sum(), 1)
        rows, cols = np.nonzero(m)
        # triangle test: width grows from top to bottom (apex up)
        top, bot = m[: max(1, h // 3)].sum(1).mean(), m[-max(1, h // 3):].sum(1).mean()
        out.append({"id": i, "x": float(sl[1].start + cols.mean()), "y": float(sl[0].start + rows.mean()),
                    "w": w, "h": h, "area": area, "fill": round(fill, 2), "hole": round(float(hole), 2),
                    "taper": round(float(bot / max(top, 0.5)), 2), "bbox": [sl[1].start, sl[0].start, sl[1].stop, sl[0].stop]})
    return out, img.size


def classify(cs):
    tri = [c for c in cs if 0.35 <= c["fill"] <= 0.75 and c["hole"] < 0.1 and c["taper"] >= 1.6 and 6 <= c["h"] <= 22]
    a1 = float(np.median([c["area"] for c in tri])) if tri else 60.0
    hmed = float(np.median([c["h"] for c in tri])) if tri else 12
    for c in cs:
        if c in tri:
            c["type"], c["n"] = "mound", 1
        elif c["hole"] >= 0.15 and max(c["w"], c["h"]) >= 10:
            c["type"], c["n"] = "enclosure", 1
        elif c["fill"] >= 0.35 and c["area"] >= 1.6 * a1 and c["hole"] < 0.15 and max(c["w"], c["h"]) <= 6 * hmed:
            c["type"], c["n"] = "mound_group", int(round(c["area"] / a1))
        elif c["fill"] < 0.35 and c["w"] >= 1.5 * c["h"] and c["h"] <= 0.8 * hmed:
            c["type"], c["n"] = "burial", 1
        elif max(c["w"], c["h"]) >= 3 * hmed:
            c["type"], c["n"] = "enclosure", 1  # big red plan of a work (outline with merged lines)
        else:
            c["type"], c["n"] = "other", 1
    return cs, a1


def extract(county):
    gr = Georef(county)
    cs, (W, H) = components(county)
    cs, a1 = classify(cs)
    m_px = gr.g["m_per_px"]
    ev = os.path.join(MD, f"{county}_known_eval.json")
    # error radius per symbol type, from the known-site check (evaluate): enclosure plans are drawn enlarged and
    # pushed aside (max error seen), triangles are placed closer (only two checked, so a wide margin)
    summ = json.load(open(ev))["summary"] if os.path.exists(ev) else {"enclosure_max_m": 1600, "mound_symbols_m": [500]}
    r_encl = int(math.ceil(summ["enclosure_max_m"] / 100.0) * 100)
    r_mound = max(750, int(math.ceil(1.5 * max(summ["mound_symbols_m"]) / 50.0) * 50))
    rows = []
    for c in cs:
        lon, lat = gr.to_lonlat(c["x"], c["y"])
        err = r_encl if c["type"] == "enclosure" else r_mound + int(0.5 * max(c["w"], c["h"]) * m_px)
        rows.append({"lon": round(float(lon[0]), 6), "lat": round(float(lat[0]), 6), "type": c["type"], "n": c["n"],
                     "err_m": err,
                     "px": [round(c["x"], 1), round(c["y"], 1)], "size_px": [c["w"], c["h"]],
                     "fill": c["fill"], "hole": c["hole"], "taper": c["taper"]})
    from collections import Counter
    cnt = Counter(r["type"] for r in rows)
    nm = sum(r["n"] for r in rows if r["type"] in ("mound", "mound_group"))
    print(f"{len(rows)} red components: {dict(cnt)}; mounds counted (groups split by area): {nm}; "
          f"single triangle area {a1:.0f} px; map scale {m_px} m/px; inverse fit error {gr.inv_err_m:.1f} m")
    out = os.path.join(FD, f"mills_1914_{county}.jsonl")
    save_jsonl(out, rows)
    path, _ = page(county)
    ov = Image.open(path).convert("RGB")
    dr = ImageDraw.Draw(ov)
    col = {"mound": (0, 90, 255), "mound_group": (0, 200, 255), "enclosure": (0, 170, 0), "burial": (200, 0, 200),
           "other": (90, 90, 90)}
    for c in cs:
        x0, y0, x1, y1 = c["bbox"]
        dr.rectangle((x0 - 2, y0 - 2, x1 + 2, y1 + 2), outline=col[c["type"]], width=2)
    ov.save(os.path.join(MD, f"{county}_symbols_overlay.jpg"), quality=85)
    return rows


def evaluate(county):
    """Distance from each known work to the symbol Mills drew for it, after georeferencing."""
    gr = Georef(county)
    cs, _ = components(county)
    byid = {c["id"]: c for c in cs}
    spec = json.load(open(os.path.join(MD, f"{county}_known.json")))
    out = []
    for s in spec["sites"]:
        if "symbol" in s:
            c = byid[s["symbol"]]
            u, v = c["x"], c["y"]
        else:
            u, v = s["symbol_px"]
        lon, lat = gr.to_lonlat(u, v)
        d = hav_m(s["lon"], s["lat"], float(lon[0]), float(lat[0]))
        out.append({**{k: s[k] for k in ("name", "kind", "conf")}, "err_m": round(d)})
        print(f"  {s['name']:30s} {s['kind']:9s} {s['conf']:6s} {d:6.0f} m")
    e = np.array([o["err_m"] for o in out])
    em = np.array([o["err_m"] for o in out if o["kind"] == "mound"])
    ee = np.array([o["err_m"] for o in out if o["kind"] == "enclosure"])
    summ = {"n": len(e), "median_m": int(np.median(e)), "max_m": int(e.max()),
            "mound_symbols_m": em.tolist(), "enclosure_median_m": int(np.median(ee)), "enclosure_max_m": int(ee.max()),
            "line_residual_px": gr.g["line_residual_px"], "m_per_px": gr.g["m_per_px"]}
    aw.save_json(os.path.join(MD, f"{county}_known_eval.json"), {"sites": out, "summary": summ})
    print(json.dumps(summ))
    return out


if __name__ == "__main__":
    cmd, county = sys.argv[1], sys.argv[2]
    {"georef": georef, "extract": extract, "evaluate": evaluate}[cmd](county)
