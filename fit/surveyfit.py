"""The survey-sheet fit: an automatic fit of one candidate plan of one site whose matching points
come from the plan and the site's old survey sheet (task 304; the method is pre-registered in
docs/site_flow.md, "The one-shot held-out measurement of the survey-sheet fit", before the one run).

Two automatic fits have failed: the vision model invents its points (301), and drawing ink against
LiDAR relief landed 231-2204 m off on the 21 hand fits (302b). The idea: a survey map and an
antiquarian plan are both ink drawings of the same banks and ditches, often of the same decades, so
matching drawing to drawing should beat drawing to relief. The plan panel is matched against the
site's finest-scale survey sheet (OS six-inch 1st edition, Cassini, Etat-major, USGS historical
topo - kind "map"/"topo" in the site's depictions.json, already georeferenced by its corners) with
the lead's pre-trained cross-modal matcher MatchAnything-ELoFTR (zju-community/matchanything_eloftr,
Apache-2.0) served on the 5060 Ti behind the VM tunnel at http://127.0.0.1:8091 (POST /match
{image0, image1 base64, threshold 0.2, max_side 832} -> keypoints in the ORIGINAL pixel frames +
scores + sizes; GET /health). A RANSAC similarity (scale, rotation, translation) is fitted through
the matched pairs; the similarity is composed with the sheet's corners (a rectilinear map in Web
Mercator) to place the plan on the ground, carrying the sheet's georeference over.

Priors shrink the search (the 302b table showed scale ratios 0.24-13.2x and rotations to 126 deg
were what the relief search guessed wrong): where the plan's scale bar (or a printed ratio at the
recorded ppi) is recorded, the similarity's scale is constrained to a frozen band around
(plan m/px) / (sheet m/px from the corners); where the recorded north arrow is trustworthy
(propose._rotation's rule: arrow recorded and |deg| <= 60), the panel is rotated once at that
angle, otherwise a frozen coarse-to-fine rotation sweep (the panel image rotated before each match
call) is scored. Translation is solved from the matches.

Nulls are search-matched (the 302b recipe): (a) the 302b scramble of the panel (each ink piece
rigidly rotated about its centroid, centroid translated, one seeded RNG, the 302b seed convention)
against the real sheet; (b) the real panel against the sheet shifted half the box north and half
east (the 302b DEM shift applied to the sheet image, corners untouched). null = the higher of the
two null scores; margin = score(fit) - null. Score = the RANSAC inlier fraction reweighted by the
inliers' reprojection RMS; confidence is a monotone function of score and margin (the exact
formula is restated at the freeze commit).

The method never reads a platefit document (the 302b separation): the comparison with the hand
fits happens only in the evaluator fit/surveyfit_heldout.py, which reads each hand doc's stored
pairs solely to compute the held-out table. It writes nothing except the fit record it returns
(no caches: the matcher is remote, the images are read-only inputs).

The configuration constants below are FROZEN at the freeze commit (restated in docs/site_flow.md
with that commit's hash before the one run); they are provisional until then.

usage:
  .venv/bin/python fit/surveyfit.py <site> <plan> [--root DIR] [--matcher URL] [--no-null]
"""

import argparse
import base64
import io
import json
import math
import os
import re
import sys
import time
from datetime import datetime, timezone

import numpy as np
import requests
from PIL import Image
from scipy import ndimage as ndi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))
import aw  # noqa: E402
import autowalls  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inkfit  # noqa: E402  (the shared page/panel loader, the size-frame convention)
import propose  # noqa: E402  (the 302b anchor: the scale prior, the north-arrow rule)

# ---------------------------------------------------------------- the frozen configuration (frozen at the freeze commit)
MATCHER_URL = "http://127.0.0.1:8091"
MATCH_TIMEOUT = 30.0      # s per /match call; one retry (the GPU call runs ~1 s warm)
MATCH_THRESHOLD = 0.2     # the lead's smoke-test value, part of the service's own API contract
MAX_SIDE = 832           # the lead's smoke-test value
SEED = 20261012          # the 302b seed convention: one constant for every seeded draw here
RANSAC_ITERS = 400       # 2-pair samples
RANSAC_MIN_INLIERS = 3
INLIER_PX = 8.0          # reprojection threshold in sheet px (the lead's smoke test used 8 px)
SCALE_TOL = 1.5          # the scale band = the prior times (1/SAMPLE, SAMPLE)
SWEEP_COARSE_DEG = 12.0  # coarse grid, 0..360 by this step (30 calls)
SWEEP_FINE_DEG = 2.0     # fine grid, +- one coarse step around the best coarse (13 calls)
SHIFT_NORTH_FRAC = 0.5   # the 302b DEM null, applied to the sheet image
SHIFT_EAST_FRAC = 0.5
SHEET_FILL = 255         # the vacated border of the shifted sheet (white, as the sheet's own paper)
SHEET_KINDS = ("map", "topo")


class SurveyFitError(Exception):
    """A method-level reason (no sheet, matcher down, no matches) - reported in the result's
    "reason", never raised out of fit()."""


# ---------------------------------------------------------------- the matcher client

def png_b64(im):
    """A PIL image as base64 PNG (the /match payload format)."""
    buf = io.BytesIO()
    im.save(buf, "PNG")
    return base64.b64encode(buf.getvalue()).decode()


class MatchClient:
    """The MatchAnything-ELoFTR service behind the VM tunnel: the only network of this module."""

    def __init__(self, url=MATCHER_URL, timeout=MATCH_TIMEOUT):
        self.url = url.rstrip("/")
        self.timeout = timeout

    def healthy(self):
        try:
            r = requests.get(self.url + "/health", timeout=self.timeout)
            return r.status_code == 200
        except Exception:
            return False

    def match(self, im0, im1, threshold=MATCH_THRESHOLD, max_side=MAX_SIDE):
        """POST /match, one retry. -> the parsed response (keypoints0/keypoints1 in the ORIGINAL
        pixel frames, scores, size0, size1); raises SurveyFitError when it fails twice."""
        body = {"image0": png_b64(im0), "image1": png_b64(im1),
                "threshold": threshold, "max_side": max_side}
        last = None
        for _ in range(2):
            try:
                r = requests.post(self.url + "/match", json=body, timeout=self.timeout * 4)
                r.raise_for_status()
                d = r.json()
                if not isinstance(d.get("keypoints0"), list):
                    raise ValueError("unexpected /match response: %r" % str(d)[:200])
                return d
            except Exception as e:  # a GPU hickup: one retry, then the method-level reason
                last = e
        raise SurveyFitError("matcher /match failed twice at %s: %s: %s"
                             % (self.url, type(last).__name__, str(last)[:150]))


# ---------------------------------------------------------------- image operations

def rotate_image(im, deg):
    """Rotate `deg` degrees counterclockwise on screen (PIL's convention), same size, the corner
    holes filled white."""
    return im.rotate(deg, resample=Image.BICUBIC, expand=False, fillcolor=(255, 255, 255))


def shift_sheet_image(im, north_frac=SHIFT_NORTH_FRAC, east_frac=SHIFT_EAST_FRAC):
    """The 302b DEM null applied to the sheet image: the content moved half the box north and half
    east (order=0, nearest sample, the vacated border filled white); the corners - the
    georeference - are untouched, exactly as the shifted DEM kept its box coordinates."""
    a = np.asarray(im, float)
    h, w = a.shape[:2]
    out = ndi.shift(a, shift=(-h * north_frac, w * east_frac), order=0, cval=float(SHEET_FILL))
    return Image.fromarray(np.rint(out).astype("uint8"))


# ---------------------------------------------------------------- the sheet and its georeference

def _scale_denom(s):
    """'1:10,560' / 'c. 1:36,000' -> 10560.0 / 36000.0; None when the string is absent or odd."""
    if not isinstance(s, str):
        return None
    t = s.strip().lower()
    if t.startswith("c."):
        t = t[2:].strip()
    m = re.match(r"^1:(\d[\d,]*)$", t)
    if not m:
        return None
    return float(m.group(1).replace(",", ""))


def load_sheet(root, site_id, kinds=SHEET_KINDS):
    """The site's finest-scale depiction of the given kinds (its .webp mosaic + its corners):
    the smallest recorded scale denominator wins, ties broken by kind then file order.
    -> (depiction dict, PIL image, corners [[lon, lat], ...] x 4, TL TR BR BL).
    Raises SurveyFitError (a method-level reason) when the site has no such sheet."""
    path = os.path.join(root, "web", "data", "sites", site_id, "depictions.json")
    if not os.path.exists(path):
        raise SurveyFitError("no sheet (no depictions for %s)" % site_id)
    dep = json.load(open(path)).get("depictions", [])
    cands = [d for d in dep if d.get("kind") in kinds and d.get("file")]
    if not cands:
        raise SurveyFitError("no sheet (no %s depiction for %s)" % ("/".join(kinds), site_id))
    cands.sort(key=lambda d: (_scale_denom(d.get("scale")) if _scale_denom(d.get("scale")) is not None else 1e18,
                              0 if d["kind"] == "map" else 1, d["file"]))
    dep = cands[0]
    fpath = os.path.join(root, "web", "data", "sites", site_id, dep["file"])
    if not os.path.exists(fpath):
        raise SurveyFitError("sheet image missing for %s: %s" % (site_id, dep["file"]))
    return dep, Image.open(fpath).convert("RGB"), [[float(c[0]), float(c[1])] for c in dep["corners"]]


# ---------------------------------------------------------------- complex similarities (w = x - i y, the codebase's convention)

def _ls_sim(p, q):
    """The complex least-squares similarity q = a*p + b through the pairs (p, q) (p, q complex
    arrays, the w = x - i y convention). Exact for a consistent set."""
    pw = p - p.mean()
    qw = q - q.mean()
    den = float(np.sum(np.abs(pw) ** 2))
    if den == 0:
        raise ValueError("degenerate similarity (all points equal)")
    a = complex(np.sum(qw * np.conj(pw)) / den)
    b = complex(q.mean() - a * p.mean())
    return a, b


def ransac(p0, p1, inlier_px=INLIER_PX, seed=SEED, iters=RANSAC_ITERS, s_band=None):
    """A RANSAC complex similarity p1 = a*p0 + b: 2-pair exact samples (one seeded RNG, the 302b
    convention), a least-squares refinement on the inliers, the reprojection measured in p1's
    pixel units. s_band (lo, hi) rejects candidate scales outside it (the scale-prior constraint).
    -> (a, b, mask, rms); a is None when no model with >= RANSAC_MIN_INLIERS inliers was found."""
    n = min(len(p0), len(p1))
    p0 = np.asarray(p0[:n], complex)
    p1 = np.asarray(p1[:n], complex)
    mask = np.zeros(n, bool)
    if n < RANSAC_MIN_INLIERS:
        return None, None, mask, math.inf
    rng = np.random.default_rng(seed)
    best_k, best_rms, best_ab = 0, math.inf, None
    for _ in range(iters):
        i, j = int(rng.integers(n)), int(rng.integers(n))
        if i == j:
            continue
        den = p0[i] - p0[j]
        if abs(den) < 1e-9:
            continue
        a = (p1[i] - p1[j]) / den
        if s_band is not None and not (s_band[0] <= abs(a) <= s_band[1]):
            continue
        b = p1[i] - a * p0[i]
        d = np.abs(a * p0 + b - p1)
        m = d < inlier_px
        k = int(m.sum())
        if k < RANSAC_MIN_INLIERS or k < best_k:
            continue
        a2, b2 = _ls_sim(p0[m], p1[m])
        d2 = np.abs(a2 * p0 + b2 - p1)
        m2 = d2 < inlier_px
        k2 = int(m2.sum())
        rms2 = float(np.sqrt(np.mean(d2[m2] ** 2))) if k2 else math.inf
        if k2 > best_k or (k2 == best_k and rms2 < best_rms):
            best_k, best_rms, best_ab, mask = k2, rms2, (a2, b2), m2
    if best_ab is None:
        return None, None, mask, math.inf
    return best_ab[0], best_ab[1], mask, best_rms


# ---------------------------------------------------------------- score and confidence

def score(n_inliers, n_pairs, rms):
    """The pre-registered score: the RANSAC inlier fraction reweighted by the inliers'
    reprojection RMS (0.0 when there is no model or no pairs)."""
    if n_pairs == 0 or n_inliers == 0 or not math.isfinite(rms):
        return 0.0
    return (n_inliers / n_pairs) / (1.0 + rms / INLIER_PX)


def confidence(s, null):
    """The pre-registered confidence: a monotone function of score and margin
    (score - the higher null score). Provisional until the freeze commit restates it:
    confidence = score * margin, floored at 0."""
    if s is None or not math.isfinite(s):
        return 0.0
    margin = s - (null if null is not None and math.isfinite(null) else 0.0)
    return max(0.0, s * margin)


# ---------------------------------------------------------------- priors (the 302b anchor, never a coordinate)

def priors(se, row):
    """The plan's priors for this (site, plan) from the 302b anchor (fit/propose.py):
    -> (plan_m_px or None, rot_deg or None, notes). plan_m_px is the anchor scale (m/px in the
    doc's size frame) and is trustworthy only from a recorded bar or a printed ratio at the
    recorded ppi (picture-size anchors are the coarse fallback: no scale constraint). rot_deg is
    the recorded north angle when propose._rotation's rule trusts it (arrow recorded, |deg| <= 60),
    else None (the sweep runs). A missing catalog here (a hermetic tree) degrades to no priors."""
    notes = []
    plan_m_px = None
    try:
        pr = propose.propose_for(se["id"], row["id"])
        if pr.get("scale_source") in ("bar", "ratio") and pr.get("scale_m_px"):
            plan_m_px = float(pr["scale_m_px"])
            notes.append("scale prior from the recorded %s (%.4f m/px)"
                         % (pr["scale_source"], plan_m_px))
        if pr.get("note"):
            notes.append("anchor: " + pr["note"])
    except Exception as e:
        notes.append("no catalog anchor here (%s: %s): no scale/rotation prior"
                     % (type(e).__name__, str(e)[:120]))
    rot = None
    try:
        ir = propose._index_row(row["id"])
        ang, arrow = ir.get("north_angle_deg"), ir.get("north_arrow")
        if isinstance(ang, (int, float)) and arrow is True and abs(ang) <= 60.0:
            rot = float(ang)
            notes.append("rotation fixed by the recorded north arrow (%.1f deg)" % rot)
    except Exception:
        pass
    return plan_m_px, rot, notes


# ---------------------------------------------------------------- the panel image rotation bookkeeping

def rotated_panel_map(theta_deg, fs, off, w, h):
    """(A, t): rotated-panel px = A @ (u, v) + t, (u, v) in the doc's size frame. The plan's north
    sits at theta (the 302b rot_deg convention: the size-frame -> ground similarity carries the
    factor e^{i theta}; a drawn plan with its north arrow theta deg clockwise of page-up has
    theta = +theta); the panel image is rotated by +theta (PIL's rotate(+deg) is counterclockwise
    on screen) about the panel centre C to bring it back north-up; the unrotated panel px are
    fs*(u - off). A = fs * R_vis(+theta) (a uniform scale, so a similarity).
    (Sign check: a visual rotation by phi multiplies the w = x - i y frame by e^{i phi}, so an
    image whose content factor is e^{i theta} is northed again by a visual +theta.)"""
    th = math.radians(theta_deg)
    c, s = math.cos(th), math.sin(th)
    # the visual (on-screen counterclockwise) rotation by +theta in (x right, y down)
    R = np.array([[c, s], [-s, c]])
    A = fs * R
    C = np.array([0.5 * w, 0.5 * h])
    t = C - R @ C - R @ (fs * np.asarray(off))
    return A, t


# ---------------------------------------------------------------- the nulls (the 302b recipe)

def panel_pieces(im):
    """The panel's ink as 8-connected pieces: the frozen autowalls extractor's keep mask, labelled
    exactly as inkfit.template_pieces (3x3 connectivity, (-length, idx) order) - but as pixel
    masks, since the null template is an image, not centre lines.
    -> [(mask (h, w) bool, centroid (x, y), length, idx), ...]."""
    (_, _, _), dbg = autowalls.extract(im, (), p=autowalls.P, debug=True)
    keep = dbg["keep"]
    lab, n = ndi.label(keep, structure=np.ones((3, 3)))
    if not n:
        return []
    length = ndi.sum(keep, lab, np.arange(1, n + 1))
    out = []
    for idx in range(1, n + 1):
        if length[idx - 1] < 1:
            continue
        m = lab == idx
        cy, cx = ndi.center_of_mass(m)
        out.append((m, (float(cx), float(cy)), float(length[idx - 1]), idx))
    out.sort(key=lambda p: (-p[2], p[3]))
    return out


def scramble_draws(pieces, w, h, seed=SEED):
    """The 302b scramble draws: one seeded RNG, pieces in (-length, idx) order, per piece a
    rotation U(0, 2 pi) about its centroid and a centroid translation U(-0.4, 0.4) of the panel
    extent (inkfit.scramble_pieces' formula). -> [(theta, dx, dy), ...]."""
    rng = np.random.default_rng(seed)
    out = []
    for _p, _c, _l, _i in pieces:
        out.append((float(rng.uniform(0.0, 2.0 * math.pi)),
                    float(rng.uniform(-0.4, 0.4) * w),
                    float(rng.uniform(-0.4, 0.4) * h)))
    return out


def scramble_image(im, pieces, draws):
    """The scrambled panel image (the 302b null recipe, pixel-exact): each piece's pixels
    q = R @ (p - c) + c + d with R the 302b point matrix (a rigid rotation about the centroid, the
    centroid translated), placed at the nearest integer and clipped to the panel, on a white panel
    of the same size. No interpolation: a null template, not a picture."""
    h, w = np.asarray(im).shape[:2]
    canvas = np.zeros((h, w), bool)
    for (mask, (cx, cy), _l, _i), (th, dx, dy) in zip(pieces, draws):
        ys, xs = np.nonzero(mask)
        p = np.stack([xs, ys], 1).astype(float)
        c = math.cos(th)
        s = math.sin(th)
        R = np.array([[c, -s], [s, c]])
        q = (p - np.array([cx, cy])) @ R.T + np.array([cx, cy]) + np.array([dx, dy])
        q = np.clip(q, 0.0, np.array([w - 1, h - 1]))
        q = np.rint(q).astype(int)
        canvas[q[:, 1], q[:, 0]] = True
    rgb = np.repeat((255 * (~canvas))[..., None], 3, axis=2).astype("uint8")
    return Image.fromarray(rgb, "RGB")


# ---------------------------------------------------------------- composition onto the ground

def composite_placement(A, t, a_r, b_r, a_s, b_s, size, crop):
    """Compose size frame -> rotated panel px (the affine A, t; the map extends beyond the panel
    image, being an affine) -> sheet px (the match's similarity a_r, b_r) -> Web Mercator (the
    sheet's a_s, b_s). The composition is a similarity; it is recovered by a least squares over
    the four full-frame corners (no hand-derived algebra) and returned with the panel's ground
    corners (the reported placement, the pre-registration's "the plan panel's corners on the
    ground"). size = the doc's size frame (w, h); crop = the panel's box in it.
    -> (a, b, panel_corners [[lon, lat] x 4])."""
    size_w, size_h = float(size[0]), float(size[1])
    samples = np.array([[0.0, 0.0], [size_w, 0.0], [size_w, size_h], [0.0, size_h]], float)
    zw = np.array([x - 1j * y for x, y in samples])
    z = np.array([a_s * (a_r * complex(px[0], -px[1]) + b_r) + b_s
                  for px in (samples @ A.T + t)])
    a, b = _ls_sim(zw, z)
    corners = []
    for u, v in ((crop[0], crop[1]), (crop[2], crop[1]), (crop[2], crop[3]), (crop[0], crop[3])):
        zz = a * (u - 1j * v) + b
        lon, lat = aw.to_lonlat(zz.real, zz.imag)
        corners.append([round(lon, 7), round(lat, 7)])
    return a, b, corners


# ---------------------------------------------------------------- the method

def _match_theta(client, panel, sheet_im, theta, band, log):
    """One match call for one panel rotation (the unrotated panel image is passed; the rotation
    by +theta is applied here) + the RANSAC fit through its pairs.
    -> a record dict (theta, a, b, mask, n, rms, score, a/b in the rotated-panel -> sheet frame)."""
    p_im = panel if theta == 0 else rotate_image(panel, theta)
    resp = client.match(p_im, sheet_im)
    k0 = _xy(resp.get("keypoints0"))
    k1 = _xy(resp.get("keypoints1"))
    n = min(len(k0), len(k1))
    wp0 = np.array([x - 1j * y for x, y in k0[:n]])
    wp1 = np.array([x - 1j * y for x, y in k1[:n]])
    a_r, b_r, mask, rms = ransac(wp0, wp1, s_band=band)
    s = score(int(mask.sum()), n, rms)
    log("    theta=%6.1f: %4d pairs, %4d inliers, rms %8.3f px, score %.4f"
        % (theta, n, int(mask.sum()), rms, s))
    return dict(theta=theta, a=a_r, b=b_r, mask=mask, n=n, rms=rms, score=s)


def _xy(kp):
    """keypoints [[x, y], ...] (the service's original-pixel-frame list) -> (n, 2) float."""
    out = []
    for k in kp or []:
        try:
            if isinstance(k, dict):
                out.append((float(k["x"]), float(k["y"])))
            else:
                out.append((float(k[0]), float(k[1])))
        except (KeyError, IndexError, TypeError, ValueError):
            continue
    return out


def _sweep(client, panel, sheet_im, band, log):
    """The frozen coarse-to-fine rotation sweep: 0..360 by SWEEP_COARSE_DEG, then
    +- one coarse step around the best coarse by SWEEP_FINE_DEG; the best record by score wins.
    (With a scale prior the RANSAC identifies the rotation directly; without one, the residual
    rotation is absorbed by the free RANSAC, so the score varies with theta through the matcher's
    own match quality - which is what the sweep scores.)"""
    best = None
    coarse = [i * SWEEP_COARSE_DEG for i in range(int(360.0 / SWEEP_COARSE_DEG))]
    for th in coarse:
        rec = _match_theta(client, panel, sheet_im, th, band, log)
        if best is None or rec["score"] > best["score"]:
            best = rec
    fine = []
    lo = best["theta"] - SWEEP_COARSE_DEG
    hi = best["theta"] + SWEEP_COARSE_DEG
    th = lo
    while th <= hi + 1e-9:
        v = round(th % 360.0, 1)
        if all(abs(v - f) > 1e-9 for f in fine):
            fine.append(v)
        th += SWEEP_FINE_DEG
    for th in fine:
        rec = _match_theta(client, panel, sheet_im, th, band, log)
        if rec["score"] > best["score"]:
            best = rec
    return best


def fit(se, row, client=None, root=None, null=True, rot=None, kinds=SHEET_KINDS, at=None, log=print):
    """One candidate plan of one site, fitted against the site's survey sheet (the 304 method;
    the protocol in docs/site_flow.md).

    se: the catalog entry dict (id/lon/lat/size_m) or a site id; row: the web/data/plans.json row
    dict or a plan id. client: a MatchClient (default: the 8091 tunnel). rot: a fixed plan-north
    angle in deg to try (None = the priors: the recorded arrow when trustworthy, else the frozen
    sweep). null: run the 302b nulls (default). kinds: the sheet depiction kinds
    (default map/topo; the aerial column passes ("aerial",)). at: the run timestamp to stamp.
    -> the result dict: site, plan, matcher, sheet, priors, theta, n_matches, n_inliers, rms_px,
    objective {fit, scramble, shifted}, null, margin, confidence, placement {a, b, s_m_px,
    rot_deg}, corners (the panel's ground corners), reason (None or the method-level reason),
    notes, at, seconds. Never raises for method-level reasons."""
    t0 = time.time()
    root = str(root) if root else ROOT
    se = se if isinstance(se, dict) else propose._site(se)
    row = row if isinstance(row, dict) else propose._plans_row(row, se["id"])
    client = client or MatchClient()
    notes = []

    def result(**kw):
        base = {
            "site": se["id"], "plan": row["id"],
            "matcher": {"url": client.url, "threshold": MATCH_THRESHOLD, "max_side": MAX_SIDE},
            "sheet": None, "priors": {"plan_m_px": None, "rot_fixed": None},
            "theta": None, "n_matches": None, "n_inliers": None, "rms_px": None,
            "objective": None, "null": None, "margin": None, "confidence": None,
            "placement": None, "corners": None, "reason": None,
            "notes": notes, "at": at or datetime.now(timezone.utc).isoformat(),
            "seconds": round(time.time() - t0, 1),
        }
        base.update(kw)
        return base

    if not client.healthy():
        return result(reason="matcher unavailable at %s (GET /health failed)" % client.url)

    panel, fs, crop, _to_size = inkfit.load_panel(root, row)
    plan_m_px, rot_fixed, pnotes = priors(se, row)
    notes.extend(pnotes)

    try:
        dep, sheet_im, corners = load_sheet(root, se["id"], kinds=kinds)
    except SurveyFitError as e:
        return result(reason=str(e))
    sheet_rec = {"file": dep.get("file"), "kind": dep.get("kind"), "scale": dep.get("scale"),
                 "year": dep.get("year")}
    w, h = sheet_im.size
    a_s, b_s = sheet_similarity(corners, w, h)
    notes.append("sheet %s (%s, %s)" % (dep.get("file"), dep.get("scale"), dep.get("kind")))

    band = None
    if plan_m_px:
        smp = sheet_m_px(a_s, b_s, corners)
        prior = plan_m_px / smp
        band = (prior / SCALE_TOL, prior * SCALE_TOL)
        notes.append("scale prior %.4f (band x%.2f) from plan %.4f / sheet %.4f m/px"
                     % (prior, SCALE_TOL, plan_m_px, smp))

    size = row.get("size") or [float(panel.width), float(panel.height)]
    size = [float(size[0]), float(size[1])]

    thetas = [rot_fixed] if rot_fixed is not None else None
    if rot is not None:
        thetas = [rot]
    try:
        if thetas is not None:
            best = max((_match_theta(client, panel, sheet_im, th, band, log) for th in thetas),
                       key=lambda r: r["score"], default=None)
        else:
            best = _sweep(client, panel, sheet_im, band, log)
    except SurveyFitError as e:
        return result(sheet=sheet_rec, priors={"plan_m_px": plan_m_px, "rot_fixed": rot_fixed},
                      reason=str(e))

    if best is None or best["a"] is None:
        return result(sheet=sheet_rec, priors={"plan_m_px": plan_m_px, "rot_fixed": rot_fixed},
                      n_matches=best["n"] if best else None,
                      reason="no consistent match (RANSAC found no similarity)")

    A, t = rotated_panel_map(best["theta"], fs, crop[:2], panel.width, panel.height)
    a, b, panel_corners = composite_placement(A, t, best["a"], best["b"], a_s, b_s, size, crop)
    k0 = aw.ground_scale(float(se.get("lat", 0.0)))
    placement = {"a": [round(a.real, 10), round(a.imag, 10)],
                 "b": [round(b.real, 10), round(b.imag, 10)],
                 "s_m_px": round(abs(a) * k0, 4),
                 "rot_deg": round(math.degrees(math.atan2(a.imag, a.real)), 2),
                 "theta": best["theta"]}

    objective = {"fit": round(best["score"], 4)}
    nullest = None
    if null:
        objs = {}
        pieces = panel_pieces(panel)
        draws = scramble_draws(pieces, panel.width, panel.height)
        psc = scramble_image(panel, pieces, draws)
        try:
            rsc = _match_theta(client, psc, sheet_im, best["theta"], band, log)
            objs["scramble"] = round(rsc["score"], 4)
            sh = shift_sheet_image(sheet_im)
            rsh = _match_theta(client, panel, sh, best["theta"], band, log)
            objs["shifted"] = round(rsh["score"], 4)
        except SurveyFitError as e:
            return result(sheet=sheet_rec, priors={"plan_m_px": plan_m_px, "rot_fixed": rot_fixed},
                          theta=best["theta"], n_matches=best["n"],
                          n_inliers=int(best["mask"]), rms_px=round(best["rms"], 3),
                          objective=objective, placement=placement, corners=panel_corners,
                          reason="null match failed: " + str(e))
        nullest = max(objs.values())
        objective.update(objs)

    margin = round(best["score"] - nullest, 4) if nullest is not None else None
    return result(sheet=sheet_rec, priors={"plan_m_px": plan_m_px, "rot_fixed": rot_fixed},
                  theta=best["theta"], n_matches=best["n"], n_inliers=int(best["mask"].sum()),
                  rms_px=round(best["rms"], 3), objective=objective, null=nullest, margin=margin,
                  confidence=round(confidence(best["score"], nullest), 4) if nullest is not None
                  else round(confidence(best["score"], 0.0), 4),
                  placement=placement, corners=panel_corners)


def sheet_similarity(corners, w, h):  # noqa: E402  (called from fit; kept with the sheet helpers)
    """The sheet's georeference as a Web-Mercator similarity in the sheet pixel frame
    (z = a*w + b, w = x - i y): the pixel grid's corners (0,0), (w,0), (w,h), (0,h) against the
    depiction corners TL TR BR BL. A north-up rectilinear image: exact when the sheet's ground
    metres per pixel are equal in x and y (a square box), else a least-squares compromise."""
    wp = np.array([0.0 - 0.0j, float(w) - 0.0j, complex(w, -h), 0.0 - 1j * h])
    z = np.array([complex(*aw.to_merc(c[0], c[1])) for c in corners])
    return _ls_sim(wp, z)


def sheet_m_px(a, b, corners):
    """Ground metres per sheet pixel: |a| (Mercator metres per pixel) at the corners' mean
    latitude (aw.ground_scale)."""
    lat = float(np.mean([c[1] for c in corners]))
    return abs(a) * aw.ground_scale(lat)


def _json_default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    return float(o)


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Fit one candidate plan of one site against the site's survey sheet (the 304 method).")
    ap.add_argument("site", help="a site id from web/data/sites.json")
    ap.add_argument("plan", help="a plan id (book row id or c_... commons id)")
    ap.add_argument("--root", default=None, help="the project root (default: this checkout)")
    ap.add_argument("--matcher", default=MATCHER_URL, help="the ELoFTR service URL")
    ap.add_argument("--no-null", action="store_true", help="skip the 302b nulls")
    a = ap.parse_args(argv)
    se = propose._site(a.site)
    row = propose._plans_row(a.plan, a.site)
    client = MatchClient(a.matcher)
    old = sys.stdout
    sys.stdout = sys.stderr  # the match calls print progress; the JSON result stays on stdout
    try:
        r = fit(se, row, client=client, root=a.root, null=not a.no_null)
    finally:
        sys.stdout = old
    print(json.dumps(r, indent=1, default=_json_default))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
