"""The ink fit: an automatic fit of one candidate picture of one site whose matching points come
from the picture itself (task 302a; the 302 method, docs/autofit.md sections 3-4 and the 10-10 run).

The plate's own ink is extracted with pipeline/autowalls.py's FROZEN config (no hand blank boxes;
the no-model fallback - no blanking boxes, keep every surviving piece - is the deterministic
default and this VM's variant, the AI box is not reachable here), the extracted centre lines are
grouped into 8-connected pieces (a model may blank non-map boxes and keep only wall-labelled
pieces; it is injectable and never gives a coordinate), and the pieces are matched against the
site's bare-earth relief (1 m class, dem_sources) with fit_plate's ridge-contrast objective and
pipeline/autofit.py's coarse-FFT + pattern-search refine, seeded by fit/propose.py's anchor
(scale from bar/ratio/picture size, north from the arrow, centre the site - never a coordinate).

Output: the placement (a Web-Mercator similarity in the platefit convention), N ink-point pairs
(plate px in the doc's size frame -> lon/lat, chosen so plan_fit.fabrication_pattern is silent),
and a confidence score on a search-matched null - the SAME search (identical seed/window/grid) on
a scrambled template and on the DEM shifted half the box north and half east, whichever scores
higher (docs/autofit.md finding 2: random-placement nulls cannot reject false peaks) - ready to
decide sync vs review queue (the threshold is set on 302b's held-out table, 302c applies it).

The method never reads a platefit document, and writes nothing except the relief fetch cache
(data/sites/<id>/dem.npy, working phase); it ACCEPTS a committed offline relief cache
(data/inkfit/relief/<site>.npz: z, px_m, bbox, optional modern mask) so tests can run hermetically
(the seed is built in 302c).

The configuration is FROZEN (pre-registered in DECISIONS.md, 2026-10-11, before a site was fitted):
PX_M, LRM_RADIUS_M, CLIP_M, SIDE_M, the search window/steps (reused by reference from autofit.py),
NEG_FLOOR, NULL_SEED, POINTS_SEED, the quantiles and attempt counts below. Bug fixes may come
later; any parameter change must be labelled exploratory and reported separately.

usage:
  python3 fit/inkfit.py <site> <plan id> [--no-null]   # the result as JSON on stdout
"""

import argparse
import json
import math
import os
import sys
import time
from datetime import datetime, timezone

import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.ndimage import map_coordinates

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))
import aw  # noqa: E402
import autofit  # noqa: E402
import autowalls  # noqa: E402
import fit_gate  # noqa: E402
import plan_fit  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import propose  # noqa: E402

# ---------------------------------------------------------------- the frozen configuration
PX_M = 1.0                     # relief grid: ground metres per px (all target sites have 1 m-class sources)
DEFAULT_SIZE_M = (1000, 1000)  # the site box when the catalog has no size_m
LRM_RADIUS_M = 24.0            # frozen, fit_plate's default: local relief = DEM minus a 24 m-smoothed copy
CLIP_M = 1.0                   # frozen, fit_plate's default: relief clipped to +-1 m
SIDE_M = 20.0                  # frozen, fit_plate's default: the sides of a ridge, 20 m off the line
WIN_ROT = autofit.WIN_ROT      # frozen (10-10 run): rotation window +-25 deg, by reference
WIN_LOGS = autofit.WIN_LOGS    #   scale x0.74..x1.36
WIN_T = autofit.WIN_T          #   centre +-200 m
ROT_STEP = autofit.ROT_STEP    #   coarse grid 2 deg / 0.04 log / 4 m cells (all used inside autofit.fit_site)
LOGS_STEP = autofit.LOGS_STEP
CELL_M = autofit.CELL_M
NEG_FLOOR = autofit.NEG_FLOOR  #   contrast below -0.2 m counts as -0.2 (junk lines must not dominate)
NO_VALID_OBJ = -9.0            # a search that never found a placement with >= 50% of its points valid
NULL_SEED = 20261012           # the scrambled-template draws
POINTS_SEED = 20261012         # the reported-points quantile jitters
MAX_POINTS = 10                # the reported pairs, at most (10-10 discipline: few irregular points)
MIN_POINTS = 4                 # below this the gate's statistics are noise (fit_gate N_MIN is 3; the doc asks 4)
PATTERN_ATTEMPTS = 8           # fabrication_pattern redraws before the method concedes
Q1, Q2, Q_JITTER = 0.23, 0.71, 0.03   # per-piece point picks: the 0.23/0.71 quantiles of its principal axis,
                                      # jittered +-0.03 on redraws (never a fixed stride: clause (b))


class _NoRelief(Exception):
    """No usable bare-earth relief for the site box (a method-level reason, not a crash)."""

    def __init__(self, reason):
        self.reason = reason
        super().__init__(reason)


# ---------------------------------------------------------------- arguments and the picture

def _site_entry(site):
    """site argument -> the catalog entry dict (id/lon/lat/size_m): pass a dict, or an id looked up
    in web/data/sites.json (the catalog; the method never reads a platefit doc)."""
    if isinstance(site, dict):
        return site
    return propose._site(site)


def _picture_row(picture, site_id):
    """picture argument -> the web/data/plans.json row: pass a row dict, or an id (a duplicate id
    picks the row whose sites list holds site_id)."""
    if isinstance(picture, dict):
        return picture
    return propose._plans_row(picture, site_id)


def _page_picture(root, row):
    """The full leaf image the row's pairs refer to: the book scan, or the commons picture
    (the big cache, else the raw cache, else a network fetch - working phase only)."""
    if row.get("ia"):
        path = os.path.join(root, "data", "raw", "books", row["ia"], "full", row["file"])
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        return Image.open(path).convert("RGB")
    cache = os.path.join(root, "data", "raw", "commons", "big", row["id"] + ".jpg")
    if os.path.exists(cache):
        return Image.open(cache).convert("RGB")
    url = row.get("url") or ""
    for cand in (url, url.rsplit("/", 1)[-1]):  # the raw cache is keyed by the url, or by its tail
        p = os.path.join(root, "data", "raw", "commons", cand)
        if cand and os.path.exists(p):
            return Image.open(p).convert("RGB")
    doc = {"src": "commons", "plan": row["id"], "ref": row.get("ref"),
           "size": row.get("size"), "ia": None, "file": None}
    im, _ = plan_fit.load_picture(doc, root)  # fetches the big on demand
    return im


def _size_frame(row, im):
    """The doc's size frame (the row's size, else the image's) and the factor from it to the leaf image."""
    size = row.get("size") or im.size
    return [float(size[0]), float(size[1])], im.width / float(size[0])


def _panel_crop(row, size):
    """The map panel in the size frame: the row's map_box (fractions of the page), or the full
    frame when degenerate (< 2 px) - propose._anchor_pairs and batch_us._crop_px's rule."""
    w, h = size
    box = row.get("map_box") or (0.0, 0.0, 1.0, 1.0)
    x0, y0, x1, y1 = [float(f) * (w if i % 2 == 0 else h) for i, f in enumerate(box)]
    if x1 - x0 < 2.0 or y1 - y0 < 2.0:
        x0, y0, x1, y1 = 0.0, 0.0, w, h
    return [x0, y0, x1, y1]


def load_panel(root, row):
    """The page's map panel image plus the mapping into the doc's size frame.
    -> (panel image, fs, crop in the size frame, to_size(uv panel px) -> uv size frame)."""
    im = _page_picture(root, row)
    size, fs = _size_frame(row, im)
    crop = _panel_crop(row, size)
    lw, lh = im.size
    lx0 = min(lw, max(0, int(round(crop[0] * fs))))
    ly0 = min(lh, max(0, int(round(crop[1] * fs))))
    lx1 = min(lw, max(lx0 + 2, int(round(crop[2] * fs))))
    ly1 = min(lh, max(ly0 + 2, int(round(crop[3] * fs))))
    panel = im.crop((lx0, ly0, lx1, ly1))
    off = np.array(crop[:2], float)

    def to_size(uv):
        return np.asarray(uv, float) / fs + off

    return panel, fs, crop, to_size


# ---------------------------------------------------------------- the relief (frozen pipeline)

def _relief_z(root, sid, bbox, w, h, notes):
    """The DEM grid (metres, NaN = nodata) for the box at w x h: the committed offline cache, the
    working-phase cache, or a fetch (the only network of this module, working phase only)."""
    npz = os.path.join(root, "data", "inkfit", "relief", sid + ".npz")
    if os.path.exists(npz):
        d = np.load(npz)
        if "z" not in d:
            raise _NoRelief("relief cache %s has no z array" % npz)
        z = np.asarray(d["z"], np.float64)
        px_m = float(d["px_m"]) if "px_m" in d else PX_M
        bb = [float(v) for v in np.asarray(d["bbox"], float)] if "bbox" in d else None
        if z.shape == (h, w) and px_m == PX_M and bb is not None \
                and all(abs(a - b) <= 1.0 for a, b in zip(bb, bbox)):
            modern = np.asarray(d["modern"], bool) if "modern" in d else None
            if modern is not None and modern.shape != (h, w):
                notes.append("relief cache modern mask has shape %s, expected (%d, %d): ignoring it"
                             % (modern.shape, h, w))
                modern = None
            return z, modern
        notes.append("relief cache %s does not match the expected (%d, %d) grid at this box: refetching"
                     % (os.path.basename(npz), h, w))
    cache = os.path.join(root, "data", "sites", sid, "dem.npy")
    if os.path.exists(cache):
        z = np.asarray(np.load(cache), np.float64)
        if z.shape == (h, w):
            return z, None
        notes.append("cached dem.npy is %s, expected (%d, %d): refetching" % (z.shape, h, w))
    z = aw.fetch_dem(bbox, w, h)
    if z.shape != (h, w):
        raise RuntimeError("DEM fetch returned %s, expected (%d, %d)" % (z.shape, h, w))
    os.makedirs(os.path.dirname(cache), exist_ok=True)
    np.save(cache, z)
    return z, None


def _build_lrm(z, modern, water):
    """The local relief model: DEM minus a smoothed copy (frozen radius/clip, fit_plate's), with
    modern features and water set to NaN so only open ground is scored."""
    zf = aw.fill_nan(z)
    lrm = np.clip(aw.local_relief(zf, PX_M, radius_m=LRM_RADIUS_M), -CLIP_M, CLIP_M)
    if modern is not None:
        lrm[modern] = np.nan
    lrm[water] = np.nan
    return lrm


def relief(root, site):
    """The site's bare-earth relief grid for this method's frozen box: site_bbox at the catalog's
    size_m (1000x1000 default) at PX_M, water + modern masked. -> (lrm, w, h, bbox); notes go in;
    raises _NoRelief with a method-level reason when there is no usable data."""
    sm = site.get("size_m") or list(DEFAULT_SIZE_M)
    w_m, h_m = float(sm[0]), float(sm[1])
    bbox = aw.site_bbox(site["lon"], site["lat"], w_m, h_m)
    w, h = int(round(w_m / PX_M)), int(round(h_m / PX_M))
    notes = []
    try:
        z, modern_cached = _relief_z(root, site["id"], bbox, w, h, notes)
    except aw.NoLidar as e:
        raise _NoRelief(str(e) or "no bare-earth relief source covers the site box")
    if np.isnan(z).all():
        raise _NoRelief("no relief data in the site box (DEM all nodata)")
    water = aw.water_mask(z, PX_M)
    if modern_cached is None:
        try:
            modern = aw.modern_mask(bbox, w, h, PX_M)  # OSM; unavailable here only costs an open-ground mask
        except Exception as e:
            modern = None
            notes.append("modern mask unavailable (%s: %s)" % (type(e).__name__, str(e)[:120]))
    else:
        modern = modern_cached
    return _build_lrm(z, modern, water), w, h, bbox, notes


# ---------------------------------------------------------------- the search site (mirrors autofit.Site)

class InkSite:
    """The method's relief site: the same attributes and the same to_ground/relief_at/contrast/score
    as autofit.Site (ground(uv) = M @ [u-u0, -(v-v0)] + t in ground metres from the relief-box centre,
    (u0,v0) = c0), so autofit's Coarse/objective/refine/fit_site drive it unchanged - but the anchor
    ("hand") is the method's own seed and the LRM comes from the frozen pipeline (the per-site hand
    knobs in data/sites/<id>/site.json are hand-fit artefacts and are never read)."""

    def __init__(self, site, lrm, c0, s, rot):
        self.id = site["id"]
        self.lon, self.lat = site["lon"], site["lat"]
        self.px_m = PX_M
        self.lrm = lrm
        self.h, self.w = lrm.shape
        self.W_m = self.w * self.px_m
        self.H_m = self.h * self.px_m
        self.cx, self.cy = aw.to_merc(self.lon, self.lat)  # the box centre is the site centre
        self.side_m = SIDE_M
        self.c0 = np.asarray(c0, float)
        self.hand_s, self.hand_rot, self.hand_t = s, rot, np.zeros(2)  # fit_site is driven with one seed

    def to_ground(self, uv, M, t):
        d = np.stack([uv[:, 0] - self.c0[0], -(uv[:, 1] - self.c0[1])], 1)
        return d @ M.T + t

    def relief_at(self, en):
        col = (en[:, 0] + self.W_m / 2) / self.px_m
        row = (self.H_m / 2 - en[:, 1]) / self.px_m
        ok = (col >= 0) & (col < self.w - 1) & (row >= 0) & (row < self.h - 1)
        vals = np.full(len(en), np.nan)
        vals[ok] = map_coordinates(self.lrm, [row[ok], col[ok]], order=0)
        return vals

    def contrast(self, P, N, M, t):
        """Per-point ridge contrast (fit_plate's definition) for plate points P with plate-px normals N."""
        en = self.to_ground(P, M, t)
        n = np.stack([N[:, 0], -N[:, 1]], 1) @ np.linalg.inv(M)  # normals transform by M^-T
        n /= np.linalg.norm(n, axis=1, keepdims=True)
        on = self.relief_at(en)
        a = self.relief_at(en + n * self.side_m)
        b = self.relief_at(en - n * self.side_m)
        return on - np.maximum(a, b)

    def score(self, P, N, M, t, wts=None):
        c = self.contrast(P, N, M, t)
        good = np.isfinite(c)
        if good.mean() < 0.5:
            return -9.0
        if wts is None:
            return float(np.median(c[good]))
        return autofit.wmedian(c[good], wts[good])


def run_search(S, P, N, w, n_refine, log):
    """autofit's coarse-FFT + pattern-search refine from the single anchor seed (scale_factor 1,
    offsets 0: the window is the frozen one, the anchor IS the seed). -> {obj, coarse_obj, s, rot, t, top_coarse}."""
    seed = dict(scale_factor=1.0, rot_offset_deg=0.0, centre_offset_m=[0.0, 0.0])
    return autofit.fit_site(S, P, N, w, [seed], n_refine, log)[0]


# ---------------------------------------------------------------- seed, pieces, null, points

def seed_for(site, row):
    """The anchor: fit/propose.py's recorded scale (bar > ratio at recorded ppi > picture size) and
    north (the arrow unless untrustworthy; else north-up), centre the site - never a coordinate.
    Fallback when the catalog is not here (a hermetic tree): picture-size scale, north-up.
    -> (s ground m/px in the size frame or None, rot rad, source, note)."""
    try:
        pr = propose.propose_for(site["id"], row["id"])
        return pr.get("scale_m_px"), math.radians(pr.get("rot_deg") or 0.0), pr.get("scale_source"), pr.get("note")
    except Exception:
        pass
    s = propose._picture_scale({"size_m": site.get("size_m") or list(DEFAULT_SIZE_M)},
                               row.get("size") or [0, 0], row.get("map_box"))
    return s, 0.0, "picture_size", "propose has no catalog here: picture-size scale, north-up"


def _model_boxes(model, panel):
    """Non-map boxes from an injected model (the qwen_boxes contract: 0-1000-normalised, kinds from
    autowalls.P["box_kinds"]), in panel px. -> [] when the model answers none or cannot."""
    try:
        raw = model.boxes(panel)
    except Exception:
        return []
    W, H = panel.size
    boxes = []
    for b in raw if isinstance(raw, list) else []:
        try:
            kind = b.get("kind")
            x0, y0, x1, y1 = [float(v) for v in b["box"]]
        except (AttributeError, KeyError, TypeError, ValueError):
            continue
        if kind not in autowalls.P["box_kinds"] or min(x0, y0, x1, y1) < 0 or max(x0, y0, x1, y1) > 1000:
            continue
        boxes.append((min(x0, x1) * W / 1000, min(y0, y1) * H / 1000,
                      max(x0, x1) * W / 1000, max(y0, y1) * H / 1000))
    return boxes


def _keep_pieces(model, panel, pieces, notes):
    """The model's per-piece keep/drop (the injectable contract: model.label_pieces(panel, pieces)
    -> {piece idx: kind or {"kind": kind}}). No model, no answer, or an unusable answer: the
    no-model fallback keeps every piece, labelled as such in the variant."""
    if model is None:
        return pieces, ""
    try:
        ans = model.label_pieces(panel, pieces)
    except Exception as e:
        ans = None
        notes.append("piece labels unavailable (%s: %s)" % (type(e).__name__, str(e)[:120]))
    if ans is None or not isinstance(ans, dict):
        return pieces, " (no piece labels; all kept)"
    kinds = {}
    for k, v in ans.items():
        kind = v.get("kind") if isinstance(v, dict) else v
        try:
            kinds[int(k)] = str(kind)
        except (TypeError, ValueError):
            continue
    if not kinds:
        return pieces, " (rejected every piece; all kept)"
    kept = [p for p in pieces if kinds.get(p["idx"]) == "wall"]
    if not kept:
        return pieces, " (rejected every piece; all kept)"
    return kept, ""


def _variant(model, suffix=""):
    if model is None:
        return "no-model"
    return str(getattr(model, "name", None) or type(model).__name__) + suffix


def template_pieces(panel, model):
    """The panel's ink (the frozen extractor, autowalls.P unchanged) grouped into 8-connected
    pieces, then the model's keep/drop (the no-model fallback keeps every piece).
    -> (pieces sorted by (-length, idx), the variant label, notes)."""
    notes = []
    boxes = _model_boxes(model, panel) if model is not None else []
    (pts, nrm, w), dbg = autowalls.extract(panel, boxes, p=autowalls.P, debug=True)
    lab, n = ndi.label(dbg["keep"], structure=np.ones((3, 3)))
    if not n or len(pts) == 0:
        return [], _variant(model), notes
    comp = lab[pts[:, 1].astype(int), pts[:, 0].astype(int)]
    length = ndi.sum(dbg["keep"], lab, np.arange(1, n + 1))
    pieces = []
    for idx in range(1, n + 1):
        m = comp == idx
        if m.any():
            pieces.append(dict(idx=int(idx), length=int(length[idx - 1]),
                               pts=pts[m], nrm=nrm[m], w=w[m]))
    pieces.sort(key=lambda p: (-p["length"], p["idx"]))
    return _keep_pieces(model, panel, pieces, notes), _variant(model), notes


def _rot2(th):
    return np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]])


def scramble_pieces(pieces, to_size, pw, ph, seed=NULL_SEED):
    """The null template (frozen recipe, docs/autofit.md finding 2): each piece rigidly rotated
    U(0, 2 pi) about its centroid, the centroid translated by U(-0.4, 0.4) of the panel extent,
    clipped inside the panel; normals rotated with the piece. One seeded rng, pieces in order.
    -> (pts, nrm, w) in the size frame, the template of the scrambled search."""
    rng = np.random.default_rng(seed)
    P, N, W = [], [], []
    for pc in pieces:
        p = np.asarray(pc["pts"], float)
        th = rng.uniform(0.0, 2.0 * math.pi)
        R = _rot2(th)
        d = np.array([rng.uniform(-0.4, 0.4) * pw, rng.uniform(-0.4, 0.4) * ph])
        q = np.clip((p - p.mean(0)) @ R.T + p.mean(0) + d, 0.0, np.array([pw, ph]))
        P.append(to_size(q))
        N.append(np.asarray(pc["nrm"], float) @ R.T)
        W.append(pc["w"])
    return np.concatenate(P), np.concatenate(N), np.concatenate(W)


def _piece_pick(pc, to_size, q1, q2):
    """Up to two points from one piece (frozen recipe): the ones nearest the 0.23/0.71 quantiles
    of the piece's own principal axis (PCA) - two spots per wall, irregularly spaced, never a
    fixed stride (fabrication_pattern clause (b))."""
    uv = to_size(pc["pts"])
    if len(uv) == 1:
        return [uv[0]]
    x = uv - uv.mean(0)
    axis = np.linalg.eigh(x.T @ x)[1][:, -1]  # the principal direction
    proj = x @ axis
    out, chosen = [], set()
    for q in (q1, q2):
        idxs = np.argsort(np.abs(proj - np.quantile(proj, q)))
        i = next(j for j in idxs if j not in chosen)
        chosen.add(i)
        out.append(uv[i])
    return out


def choose_points(pieces, to_size, seed=POINTS_SEED, attempts=PATTERN_ATTEMPTS):
    """Which template points become the doc's pairs (frozen recipe, worked in the size frame where
    fabrication_pattern's px clauses live): per piece the 0.23/0.71 quantile picks, <= 2 per piece,
    longest pieces first, at most MAX_POINTS total; redrawn (jittered quantiles, seeded) until
    plan_fit.fabrication_pattern is silent; after `attempts` it concedes with the last pattern.
    -> (pts (n, 2) or None, reason or None)."""
    last = None
    for attempt in range(attempts):
        q1 = Q1 + (0.0 if attempt == 0 else np.random.default_rng(seed + attempt).uniform(-Q_JITTER, Q_JITTER))
        q2 = Q2 + (0.0 if attempt == 0 else np.random.default_rng(seed + attempt).uniform(-Q_JITTER, Q_JITTER))
        pts = []
        for pc in pieces:  # already (-length, idx) order
            if len(pts) >= MAX_POINTS:
                break
            pts.extend(_piece_pick(pc, to_size, q1, q2))
        if len(pts) < MIN_POINTS:
            return None, "not enough wall ink (%d candidate points, need 4)" % len(pts)
        last = plan_fit.fabrication_pattern([[u, v, 0.0, 0.0] for u, v in pts])
        if last is None:
            return np.asarray(pts, float), None
    return None, last


# ---------------------------------------------------------------- placement, pairs, doc

def map_pairs(S, uv, s, rot, t):
    """Template points (size frame) under the search placement -> doc pairs
    [[u, v, lon, lat]] at the platefit precision (1 dp px / 7 dp lon-lat)."""
    M = autofit.sim(s, rot)
    en = S.to_ground(uv, M, t)  # ground metres from the box centre
    k = 1.0 / aw.ground_scale(S.lat)  # ground metres -> Mercator metres
    out = []
    for (u, v), (e, n) in zip(uv, en):
        lon, lat = aw.to_lonlat(S.cx + e * k, S.cy + n * k)
        out.append([round(float(u), 1), round(float(v), 1), round(lon, 7), round(lat, 7)])
    return out


def placement_of(S, s, rot, t, crop):
    """The final placement as the platefit similarity (a, b): merc = a * (w - w0) + b with
    w = u - i v (the minus-v form, verified against propose's anchor), a = k * s * e^{i rot},
    b = zc + k t - a w0 - and the panel corners' lon/lat (the eyeball aid: the corners should sit
    on the site; tools/composite needs a built site, so they are printed instead)."""
    k = 1.0 / aw.ground_scale(S.lat)
    a = complex(k * s * math.cos(rot), k * s * math.sin(rot))
    b = complex(S.cx + k * t[0], S.cy + k * t[1]) - a * complex(S.c0[0], -S.c0[1])
    corners = []
    for u, v in ((crop[0], crop[1]), (crop[2], crop[1]), (crop[2], crop[3]), (crop[0], crop[3])):
        z = a * (u - 1j * v) + b
        corners.append([round(aw.to_lonlat(z.real, z.imag)[0], 7),
                        round(aw.to_lonlat(z.real, z.imag)[1], 7)])
    return {"a": [a.real, a.imag], "b": [b.real, b.imag], "s_m_px": round(float(s), 4),
            "rot_deg": round(math.degrees(rot), 2), "t_m": [round(float(t[0]), 1), round(float(t[1]), 1)],
            "u0v0": [round(float(S.c0[0]), 1), round(float(S.c0[1]), 1)], "k": round(k, 4)}, corners


def _doc(site, row, crop, pairs, score, at):
    """The platefit document this fit becomes: batch_us.write_doc's fields plus "fitter": "ink"
    (plan_fit.build's source line keys off it). Returned, NOT written: whether it is synced or
    queued for review is the 302c decision (the threshold set on 302b's held-out table)."""
    doc = {
        "site": site["id"],
        "plan": row["id"],
        "crop": [int(round(c)) for c in crop],
        "pairs": pairs,
        "label": row.get("label") or None,
        "title": row.get("title") or None,
        "cite": row.get("cite") or None,
        "at": at or datetime.now(timezone.utc).isoformat(),
        "auto": True,
        "score": score,
        "fitter": "ink",
    }
    if row.get("ia"):
        doc.update({"ia": row["ia"], "file": row["file"], "book": row.get("book")})
    else:  # a commons picture: the page's own keys for that kind (pipeline/plan_fit.py)
        doc.update({"ia": None, "file": None, "model": "similarity", "src": "commons",
                    "url": row.get("url"), "ref": row.get("ref"), "size": row.get("size")})
    return doc


def _round_stat(x, dp):
    x = float(x)
    return None if not math.isfinite(x) else round(x, dp)


# ---------------------------------------------------------------- the method

def fit(site, picture, model=None, root=None, n_refine=8, null=True, at=None, log=print):
    """One candidate picture of one site, fitted by its own ink against the site's bare-earth
    relief (the contract of task 302a).

    site: the catalog entry dict (id/lon/lat/size_m) or a site id (web/data/sites.json).
    picture: the web/data/plans.json row (a dict) or a plan id; book rows read
    data/raw/books/<ia>/full/<file>, commons rows the big cache (or a fetch, working phase).
    model: an injectable vision model (duck-typed: .boxes(im) -> 0-1000-normalised non-map boxes,
    .label_pieces(im, pieces) -> per-piece kind, .name optional); None = the no-model fallback.
    null: run the search-matched null (default). n_refine: the refine candidates (frozen 8).
    -> the result dict: site, plan, model (variant), reason (None or the review reason),
    n_pieces, n_points, seed {s_m_px, rot_deg, source, note}, objective {fit[, scramble, shifted,
    scramble_valid, shifted_valid]}, null (the higher null objective or None), confidence
    (obj_fit - null or None), placement {a, b, s_m_px, rot_deg, t_m, u0v0, k}, corners (the panel
    corners' lon/lat), gate {verdict, n, med, slope_o, io}, fabrication (None on success),
    pairs, doc (unwritten), notes, seconds. Pure except the relief fetch (data/sites/<id>/dem.npy)
    and the OSM modern-mask fetch (absent -> None, recorded).
    """
    t0 = time.time()
    root = str(root) if root else ROOT
    se = _site_entry(site)
    row = _picture_row(picture, se["id"])
    notes = []

    def result(**kw):
        base = {
            "site": se["id"], "plan": row["id"], "model": "no-model", "reason": None,
            "n_pieces": None, "n_points": None, "seed": None, "objective": None,
            "null": None, "confidence": None, "placement": None, "corners": None,
            "gate": None, "fabrication": None, "pairs": None, "doc": None,
            "notes": notes, "seconds": round(time.time() - t0, 1),
        }
        base.update(kw)
        return base

    panel, fs, crop, to_size = load_panel(root, row)
    pieces, variant, pnotes = template_pieces(panel, model)
    notes.extend(pnotes)
    if not pieces:
        return result(reason="no wall ink extracted")

    s0, rot0, source, snote = seed_for(se, row)
    if snote:
        notes.append(snote)
    seed_rec = {"s_m_px": _round_stat(s0, 4), "rot_deg": _round_stat(math.degrees(rot0), 2),
                "source": source, "note": snote}
    if s0 is None:
        return result(model=variant, n_pieces=len(pieces), seed=seed_rec,
                      reason="no anchor scale (the site has no size_m)")

    n_points = int(sum(len(pc["pts"]) for pc in pieces))
    P = np.concatenate([to_size(pc["pts"]) for pc in pieces])
    N = np.concatenate([pc["nrm"] for pc in pieces])
    W = np.concatenate([pc["w"] for pc in pieces])

    lrm, w, h, bbox, rnotes = relief(root, se)
    notes.extend(rnotes)

    c0 = [0.5 * (crop[0] + crop[2]), 0.5 * (crop[1] + crop[3])]
    S = InkSite(se, lrm, c0, s0, rot0)
    r = run_search(S, P, N, W, n_refine, log)
    objective = {"fit": _round_stat(r["obj"], 4)}
    if r["obj"] <= NO_VALID_OBJ:
        return result(model=variant, n_pieces=len(pieces), n_points=n_points, seed=seed_rec,
                      objective=objective, reason="search found no valid placement")

    nullest = None
    if null:
        Psc, Nsc, Wsc = scramble_pieces(pieces, to_size, panel.size[0], panel.size[1])
        rsc = run_search(S, Psc, Nsc, Wsc, n_refine, log)
        # the DEM shifted half the box north and half east (the frozen null; the masks' NaN holes
        # move with the terrain, the masks themselves are not re-fetched)
        lrm2 = ndi.shift(lrm, (-S.H_m / 2 / PX_M, S.W_m / 2 / PX_M), order=0, cval=np.nan)
        S2 = InkSite(se, lrm2, c0, s0, rot0)
        rsh = run_search(S2, P, N, W, n_refine, log)
        objective.update({"scramble": _round_stat(rsc["obj"], 4),
                          "shifted": _round_stat(rsh["obj"], 4),
                          "scramble_valid": bool(rsc["obj"] > NO_VALID_OBJ),
                          "shifted_valid": bool(rsh["obj"] > NO_VALID_OBJ)})
        nullest = max(rsc["obj"], rsh["obj"])

    pts, reason = choose_points(pieces, to_size)
    if pts is None:
        pl, corners = placement_of(S, r["s"], r["rot"], r["t"], crop)
        return result(model=variant, n_pieces=len(pieces), n_points=n_points, seed=seed_rec,
                      objective=objective, null=_round_stat(nullest, 4) if null else None,
                      confidence=_round_stat(r["obj"] - nullest, 4) if (null and nullest is not None) else None,
                      placement=pl, corners=corners, fabrication=reason, reason=reason)

    pairs = map_pairs(S, pts, r["s"], r["rot"], r["t"])
    pl, corners = placement_of(S, r["s"], r["rot"], r["t"], crop)
    a = pl["a"][0] + 1j * pl["a"][1]
    b = pl["b"][0] + 1j * pl["b"][1]
    verdict, stats = fit_gate.gate(pairs, (a, b))  # passes by construction: a second line of defence
    gate = {"verdict": verdict, "n": int(stats["n"]), "med": _round_stat(stats["med"], 3),
            "slope_o": _round_stat(stats["slope_o"], 4), "io": _round_stat(stats["io"], 3)}
    fab = plan_fit.fabrication_pattern([[u, v, 0.0, 0.0] for u, v, _, _ in pairs])  # checked in choose_points; this is the defence
    if fab is not None:
        return result(model=variant, n_pieces=len(pieces), n_points=n_points, seed=seed_rec,
                      objective=objective, null=_round_stat(nullest, 4) if null else None,
                      confidence=_round_stat(r["obj"] - nullest, 4) if (null and nullest is not None) else None,
                      placement=pl, corners=corners, fabrication=fab, reason=fab)
    score = _round_stat(stats["med"], 1)
    return result(model=variant, n_pieces=len(pieces), n_points=n_points, seed=seed_rec,
                  objective=objective, null=_round_stat(nullest, 4) if null else None,
                  confidence=_round_stat(r["obj"] - nullest, 4) if (null and nullest is not None) else None,
                  placement=pl, corners=corners, gate=gate, fabrication=None, pairs=pairs,
                  doc=_doc(se, row, crop, pairs, score, at))


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Fit one candidate picture of one site by its own ink (the 302a method).")
    ap.add_argument("site", help="a site id from web/data/sites.json")
    ap.add_argument("plan", help="a plan id (book row id or c_... commons id)")
    ap.add_argument("--no-null", action="store_true", help="skip the search-matched null")
    a = ap.parse_args(argv)
    se = propose._site(a.site)
    row = propose._plans_row(a.plan, a.site)
    r = fit(se, row, model=None, null=not a.no_null)
    print(json.dumps(r, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
