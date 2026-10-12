"""Task 304: the survey-sheet fit method (fit/surveyfit.py) tested end to end against a stub of
the MatchAnything-ELoFTR service - no GPU, no network, no fixed port (the stub listens on
127.0.0.1 with an OS-assigned ephemeral port, so parallel checkouts can run at once).

The synthetic world (all constants below, the measured outcomes in data/surveyfit/devlog.md):
a 400x400 "sheet" whose corners georeference a 2 km box at (2.0, 50.0) (the real aw.corners
geometry), 14 feature glyphs on a 7x2 grid (25/30 px pitch, centred at (195, 235)); and a
320x320 "plan" carrying the same glyphs under a known similarity z = a_true*w + b_true (the
plan's north theta_d degrees clockwise of page-up: a_true = (M_PX/k0)*e^{i*theta_d}, the 302b
anchor form) plus 4 junk glyphs with no sheet counterpart. The stub decodes the two sent
images, works out which world it is looking at (sheet real vs the 302b half-box shift; plan
unrotated vs rotated, via connected-component centroids), and answers with the corresponding
point pairs (true pairs in the ORIGINAL pixel frames, the way the service does, plus a fixed
junk set) - returning the full set only when the sent panel's rotation is the drawing's own,
the first six one fine step away, nothing beyond (a rotation-sensitive matcher), with the
returned plan-side points wobbling by up to 0.6 px per degree of error (match quality, not
just count, degrades). That makes the frozen rotation sweep meaningful: the true rotation is
the only (or best) orientation with full match quality.

The tests:
1. fixed rotation (the plan drawn north-42, fit with rot=42): the reported placement and panel
   corners recover the independently constructed true placement (the sign-convention lock);
2. the frozen sweep (north-up plan, no prior): recovers the placement, the fine grid wraps
   (best coarse 0 -> 348..12) and the stub sees at most 30+13 match calls, a couple of them
   duplicate payloads (a fine theta equal to a coarse one);
3. the sweep refining between coarse values (the plan drawn north-6: the coarse grid misses,
   the fine grid lands within one fine step);
4-5. the 302b nulls: the scramble of the panel and the sheet shifted half the box each score
   below the fit; null = the higher, margin and confidence positive;
6. the recorded-run pin (the test_gate pattern): data/surveyfit/fixture_match.json holds a
   fixed synthetic /match response and the module's own ransac + score output recorded from it
   (generated once, committed); re-running the frozen core must reproduce it exactly;
7. /health answering 500 is a method-level reason ("matcher unavailable"), not an exception.

The method under test is fit/surveyfit.py as committed; the test never reads a held-out
document and never opens a platefit doc.
"""
import base64
import io
import json
import math
import os
import sys
import threading
from collections import Counter
from functools import lru_cache
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import numpy as np
import pytest
from PIL import Image
from scipy import ndimage as ndi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "fit"))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))
import aw  # noqa: E402
import surveyfit as sf  # noqa: E402

FIXTURE = os.path.join(ROOT, "data", "surveyfit", "fixture_match.json")

# ---------------------------------------------------------------- the synthetic world (frozen)

LAT0, LON0 = 50.0, 2.0          # the site
SIZE_M = 2000.0                 # the site box (square, so the sheet's a_s is exactly real)
SHEET = 400                     # the sheet image, px (both sides)
PLAN = 320                      # the plan panel, px (both sides; the doc's size frame)
M_PX = 4.0                      # the plan's true scale: ground metres per plan px (size frame)
SHEET_R = 3.5                   # the sheet glyphs' radius, px
K0 = aw.ground_scale(LAT0)      # ground metres per Mercator metre at the site latitude
SITE_ID = "synthetic-site-304"
PLAN_ID = "c_synthfit304"
SITE = {"id": SITE_ID, "lon": LON0, "lat": LAT0, "size_m": [SIZE_M, SIZE_M]}
ROW = {"id": PLAN_ID, "size": [PLAN, PLAN]}
JUNK_SEED = 304777              # the stub's junk match pairs (one fixed seeded set)
JITTER_SEED = 304778            # the stub's per-glyph quality wobble (a separate fixed set)
JITTER_PX_PER_DEG = 0.6         # the stub's match-quality degradation, px per degree of error
CENTER = np.array([0.5 * PLAN, 0.5 * PLAN])     # the panel centre (the sweep rotates about it)
CANDIDATE_THETAS = [2.0 * i for i in range(180)]  # the stub's rotation-resolution candidates
HIT_PX = 2.0                    # a glyph counts as "seen" within this many px of its expected spot
ORIENTED_MIN = 8                # >= this many seen glyphs: the image is a real (rotated) plan


def sheet_corners():
    """The sheet's four corners TL TR BR BL as [lon, lat] - the real aw.corners of a 2 km box."""
    return aw.corners(aw.site_bbox(LON0, LAT0, SIZE_M, SIZE_M))


@lru_cache(maxsize=1)
def _sheet_similarity():
    """The sheet's georeference (a_s, b_s) from its corners: the module's own sheet_similarity
    (the sheet side is data the method carries over, so the test may use the module for it)."""
    return sf.sheet_similarity(sheet_corners(), SHEET, SHEET)


@lru_cache(maxsize=1)
def sheet_centers():
    """The 14 sheet glyph centres, px: a 7x2 grid at 25/30 px pitch centred at (195, 235) -
    close enough to the sheet centre that the plan frame (the plan's scale 0.8 x the sheet's,
    the plan centre on the site centre) holds the whole grid in-frame at every theta_d the
    tests use, far enough off it that the 302b half-box shift ((x, y) -> (x + 200, y - 200))
    keeps exactly 8 glyphs (the 4 columns at x <= 198 and the 2 rows at y >= 202) and loses 6."""
    out = []
    for y in (220, 250):
        for i in range(7):
            out.append((120 + 25 * i, y))
    assert len(out) == 14
    return out


def true_placement(theta_d):
    """The plan's true placement in the doc's size frame, built independently of the method:
    z = a_true*w + b_true with a_true = (M_PX/k0)*e^{i*theta_d} (the 302b anchor: the drawn
    north is theta_d deg clockwise of page-up) and b_true chosen so the plan's centre lands on
    the site centre."""
    a = (M_PX / K0) * complex(math.cos(math.radians(theta_d)), math.sin(math.radians(theta_d)))
    zc = complex(*aw.to_merc(LON0, LAT0))
    b = zc - a * complex(0.5 * PLAN, -0.5 * PLAN)
    return a, b


def plan_centers(theta_d):
    """The plan glyph centres (size frame, sub-pixel): where the sheet glyphs sit under the
    true placement. Their radii from the panel centre range ~40-120 px, so a rotation in error
    by one fine step (2 deg) moves them by 1.4-4.2 px: most stay out of the 2 px hit window,
    the stub's rotation resolution is binary at the grid's own step, and the match-quality
    wobble below makes the true step the unique best in the sweep."""
    a_s, b_s = _sheet_similarity()
    a, b = true_placement(theta_d)
    out = []
    for (sx, sy) in sheet_centers():
        z = a_s * complex(sx, -sy) + b_s
        w = (z - b) / a
        out.append((w.real, -w.imag))
    return out


@lru_cache(maxsize=1)
def junk_plan_centers():
    """The 4 plan glyphs with no sheet counterpart (outlier rejection). Kept >= 25 px from every
    true centre (asserted): a rigid rotation preserves that gap, so no junk glyph can ever be
    mistaken for a true one at any candidate rotation."""
    out = [(15.0, 15.0), (305.0, 15.0), (15.0, 305.0), (305.0, 305.0)]
    for th in (0.0, 6.0, 42.0):
        truth = np.asarray(plan_centers(th), float)
        for j in out:
            assert (np.hypot(truth[:, 0] - j[0], truth[:, 1] - j[1]) >= 25.0).all(), \
                "a junk glyph sits within 25 px of a true one at theta_d=%g" % th
    return out


@lru_cache(maxsize=1)
def junk_pairs():
    """The stub's 12 junk match pairs, one fixed seeded set (plan px, sheet px): what a matcher
    returns in addition to the true correspondences. Whatever RANSAC does with them is part of
    the world (the measured scores are in the devlog)."""
    rng = np.random.default_rng(JUNK_SEED)
    p = rng.uniform(4.0, PLAN - 4.0, size=(12, 2))
    q = rng.uniform(4.0, SHEET - 4.0, size=(12, 2))
    return [tuple(map(float, t)) for t in p] , [tuple(map(float, t)) for t in q]


def _rasterize(centers, radius, side):
    """Discs of the given radius (px) centred at the (possibly sub-pixel) centres, rasterised at
    4x supersampling and box-downsampled - a sub-pixel-centred blob the way the plan's derived
    centres need it; black on white."""
    ss = 4
    acc = np.zeros((side * ss, side * ss), float)
    Y, X = np.mgrid[0:side * ss, 0:side * ss]
    r8 = ss * radius
    for (cx, cy) in centers:
        acc += ((X - ss * cx) ** 2 + (Y - ss * cy) ** 2) <= r8 * r8
    acc = acc.reshape(side, ss, side, ss).mean(axis=(1, 3))
    ink = acc >= 0.3
    return Image.fromarray(np.repeat((255 * (~ink))[..., None], 3, axis=2).astype("uint8"), "RGB")


@lru_cache(maxsize=1)
def sheet_image():
    return _rasterize(sheet_centers(), SHEET_R, SHEET)


@lru_cache(maxsize=8)
def plan_image(theta_d):
    r = SHEET_R * abs(_sheet_similarity()[0]) / abs(true_placement(theta_d)[0])
    return _rasterize(plan_centers(theta_d), r, PLAN)


def build_tree(root, theta_d):
    """The hermetic tree fit() needs: the site's sheet (depictions.json + webp) and the plan
    picture (the commons big cache, a lossy JPEG to stand in for a scanned picture)."""
    site_dir = os.path.join(root, "web", "data", "sites", SITE_ID)
    os.makedirs(site_dir, exist_ok=True)
    big_dir = os.path.join(root, "data", "raw", "commons", "big")
    os.makedirs(big_dir, exist_ok=True)
    dep = {"kind": "map", "file": "synth_sheet.webp", "scale": "1:10,560", "year": "1843",
           "corners": sheet_corners()}
    with open(os.path.join(site_dir, "depictions.json"), "w") as f:
        json.dump({"depictions": [dep]}, f)
    sheet_image().save(os.path.join(site_dir, "synth_sheet.webp"), "WEBP", quality=95)
    plan_image(theta_d).save(os.path.join(big_dir, PLAN_ID + ".jpg"), "JPEG", quality=95)


def build_world(theta_d):
    """Everything the stub needs to know about this world (no images)."""
    a_s, b_s = _sheet_similarity()
    a, b = true_placement(theta_d)
    jp, jq = junk_pairs()
    return {"theta_d": theta_d, "a_s": a_s, "b_s": b_s, "a_true": a, "b_true": b,
            "sheet_centers": sheet_centers(), "plan_centers": plan_centers(theta_d),
            "junk_plan": junk_plan_centers(), "junk_p0": jp, "junk_p1": jq}


# ---------------------------------------------------------------- the stub matcher

def _ink(im):
    return (np.asarray(im) < 128).any(axis=2)


def _centroids(ink):
    lab, n = ndi.label(ink, structure=np.ones((3, 3)))
    if not n:
        return np.zeros((0, 2))
    # scipy 1.18: with an index array, one (cy, cx) tuple per label, not per axis
    com = ndi.center_of_mass(ink, lab, np.arange(1, n + 1))
    return np.array([(c[1], c[0]) for c in com], float)


def _expected(theta, centers):
    """Where the glyphs would sit if the image were rotated by `theta` (the module's own
    visual-CCW matrix about the panel centre) - the stub checks ink/centroids against these."""
    th = math.radians(theta)
    R = np.array([[math.cos(th), math.sin(th)], [-math.sin(th), math.cos(th)]])
    c = np.asarray(centers, float)
    return CENTER + (c - CENTER) @ R.T


def _resolve_theta(world, cents):
    """The sent plan image's rotation, to the grid's own 2 deg resolution: the candidate whose
    expected glyph positions best match the measured component centroids.
    -> (theta or None when the image is not a recognisable rotated plan, the per-glyph
    measured centroids for the resolved theta)."""
    if cents.shape[0] == 0:      # a panel with no ink: nothing to resolve
        return None, {}
    best = None
    for th in CANDIDATE_THETAS:
        e = _expected(th, world["plan_centers"])
        d = np.linalg.norm(cents[:, None, :] - e[None, :, :], axis=2)
        hits = int((d.min(axis=0) < HIT_PX).sum())
        if hits >= ORIENTED_MIN and (best is None or hits > best[1]):
            best = (th, hits)
    if best is None:
        return None, {}
    th = best[0]
    e = _expected(th, world["plan_centers"])
    d = np.linalg.norm(cents[:, None, :] - e[None, :, :], axis=2)
    j = d.argmin(axis=0)
    matched = {i: tuple(float(v) for v in cents[k])
               for i, k in enumerate(j) if d[k, i] < HIT_PX}
    return th, matched


def _sheet_state(world, ink1):
    """Classify the sent sheet: the real sheet (glyphs at the world centres), the 302b shift
    (glyphs at the shifted positions, only the surviving quadrant), or neither."""
    orig = [c for c in world["sheet_centers"]]
    shifted = [(x + 200, y - 200) for (x, y) in orig
               if x + 200 <= SHEET - 2 and y - 200 >= 2]

    def seen(pts):
        n = 0
        for (x, y) in pts:
            ix, iy = int(round(x)), int(round(y))
            if 0 <= ix < SHEET and 0 <= iy < SHEET and \
                    ink1[max(0, iy - 1):iy + 2, max(0, ix - 1):ix + 2].any():
                n += 1
        return n
    if seen(orig) >= SHEET_R * 4:      # 14 real glyphs: >= 12 seen -> the real sheet
        return "real"
    if len(shifted) and seen(shifted) == len(shifted):
        return "shifted"
    return "unknown"


def _take(world, sheet_state, theta):
    """Which true pairs this (plan orientation, sheet state) call returns: the survivors (all
    14 on the real sheet, the in-frame subset on the shifted one) degraded by the angular
    error of the sent panel vs the drawing's own rotation - the matcher's rotation
    sensitivity, what the frozen sweep scores: the full set at the true rotation, the first six
    one fine step away, none beyond."""
    surv = list(range(14)) if sheet_state == "real" else [
        i for i, (x, y) in enumerate(world["sheet_centers"])
        if x + 200 <= SHEET - 2 and y - 200 >= 2]
    delta = abs((theta - world["theta_d"] + 180.0) % 360.0 - 180.0)
    if delta <= 3.0:
        return surv
    if delta <= 15.0:
        return surv[:6]
    return []


def _jitter(theta, i, delta):
    """A returned plan-side point's wobble: up to JITTER_PX_PER_DEG px per degree of angular
    error, deterministic per (theta, i) - a repeated call at the same theta returns the same
    points, and match quality (not just match count) degrades away from the true rotation.
    -> (dx, dy) in plan px."""
    amp = JITTER_PX_PER_DEG * delta
    if amp <= 0:
        return 0.0, 0.0
    rng = np.random.default_rng((int(round(theta * 10.0)) * 100000 + i + JITTER_SEED) % 2 ** 32)
    return float(rng.uniform(-amp, amp)), float(rng.uniform(-amp, amp))


def match_response(world, im0, im1):
    """The stub's /match answer: true pairs (plan-side measured centroids in the SENT frame
    plus the quality wobble, sheet-side world positions) + the fixed junk set, as the service
    returns them (the original pixel frames)."""
    sheet_state = _sheet_state(world, _ink(im1))
    theta, matched = _resolve_theta(world, _centroids(_ink(im0)))
    p0, p1 = [], []
    if theta is not None and sheet_state != "unknown":
        delta = abs((theta - world["theta_d"] + 180.0) % 360.0 - 180.0)
        for i in _take(world, sheet_state, theta):
            if i not in matched:
                continue
            sx, sy = world["sheet_centers"][i]
            if sheet_state == "shifted":
                sx, sy = sx + 200, sy - 200
            dx, dy = _jitter(theta, i, delta)
            px, py = matched[i]
            p0.append([px + dx, py + dy])
            p1.append([sx, sy])
    for a, b in zip(world["junk_p0"], world["junk_p1"]):
        p0.append(list(a))
        p1.append(list(b))
    return {"keypoints0": p0, "keypoints1": p1, "scores": [1.0] * len(p0),
            "size0": [PLAN, PLAN], "size1": [SHEET, SHEET]}


def _handler(world, healthy, state):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            if self.path == "/health":
                body = b'{"model": "stub-matchanything-eloftr", "device": "test"}'
                code = 200 if healthy else 500
                if not healthy:
                    body = b'{"error": "stub is down"}'
            else:
                code, body = 404, b"{}"
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            if self.path != "/match":
                self.send_response(404)
                self.end_headers()
                return
            n = int(self.headers.get("Content-Length", 0))
            d = json.loads(self.rfile.read(n))
            im0 = Image.open(io.BytesIO(base64.b64decode(d["image0"]))).convert("RGB")
            im1 = Image.open(io.BytesIO(base64.b64decode(d["image1"]))).convert("RGB")
            state["calls"].append((d["image0"], d["image1"]))
            body = json.dumps(match_response(world, im0, im1)).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
    return H


def start_stub(world, healthy=True):
    """The stub service on an OS-assigned ephemeral port (never a fixed one).
    -> (MatchClient, state dict with the recorded payloads, server)."""
    state = {"calls": []}
    server = ThreadingHTTPServer(("127.0.0.1", 0), _handler(world, healthy, state))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    client = sf.MatchClient("http://127.0.0.1:%d" % server.server_address[1])
    return client, state, server


def run_fit(theta_d, tmp_path, rot, null, healthy=True):
    """One fit() against the stub for this world; the server is shut down after.
    -> (result, state, logs)."""
    build_tree(str(tmp_path), theta_d)
    client, state, server = start_stub(build_world(theta_d), healthy)
    logs = []
    try:
        result = sf.fit(SITE, ROW, client=client, root=str(tmp_path), null=null,
                        rot=rot, log=logs.append)
    finally:
        server.shutdown()
        server.server_close()
    return result, state, logs


def _corner_error_m(corners, theta_d):
    """The reported panel corners vs the true ones: ground metres (Mercator metres x k0),
    the 302b corner-error metric."""
    a, b = true_placement(theta_d)
    truth = []
    for u, v in ((0.0, 0.0), (float(PLAN), 0.0), (float(PLAN), float(PLAN)), (0.0, float(PLAN))):
        z = a * (u - 1j * v) + b
        truth.append(complex(*aw.to_merc(*aw.to_lonlat(z.real, z.imag))))
    out = []
    for c, t in zip(corners, truth):
        e = complex(*aw.to_merc(c[0], c[1]))
        out.append(abs(e - t) * K0)
    return out


def _placement_error_m(result, theta_d):
    """The reported (a, b) vs the true (a, b): |db| in ground metres, |da| in ground m/px."""
    a, b = true_placement(theta_d)
    ar = complex(*result["placement"]["a"])
    br = complex(*result["placement"]["b"])
    return abs(ar - a) * K0, abs(br - b) * K0


# ---------------------------------------------------------------- the tests

def test_fixed_rotation_recovers_known_placement(tmp_path):
    """The sign-convention lock: a plan drawn with its north 42 deg clockwise of page-up, fit
    with rot=+42 (the method's own prior would fix the rotation here), recovers the true
    placement built independently of the method."""
    r, _state, _logs = run_fit(42.0, tmp_path, rot=42.0, null=False)
    assert r["reason"] is None, r
    assert r["theta"] == 42.0
    da, db = _placement_error_m(r, 42.0)
    assert db < 2.0, "placement centre %g m from the true one" % db
    assert da < 0.1, "placement scale off by %g m/px" % da
    assert abs(r["placement"]["rot_deg"] - 42.0) < 1.0, r["placement"]
    errs = _corner_error_m(r["corners"], 42.0)
    assert all(e < 2.0 for e in errs), "panel corners %g m off" % max(errs)


def test_sweep_recovers_north_up_plan(tmp_path):
    """No trustworthy prior (a hermetic tree has no catalog): the frozen coarse-to-fine sweep
    runs. The true rotation 0 is a coarse value and the first one, so the fine grid wraps
    (348..12): the stub sees at most 30+13 match calls, a couple of them duplicate payloads
    (the fine list dedups only within itself, so a fine theta equal to a coarse one is sent
    twice)."""
    r, state, logs = run_fit(0.0, tmp_path, rot=None, null=False)
    assert r["reason"] is None, r
    assert r["theta"] == 0.0
    da, db = _placement_error_m(r, 0.0)
    assert db < 2.0 and da < 0.1
    assert all(e < 2.0 for e in _corner_error_m(r["corners"], 0.0))
    n = len(state["calls"])
    assert 30 <= n <= 43, "the sweep made %d match calls" % n
    dupes = [p for p, c in Counter(state["calls"]).items() if c >= 2]
    assert len(dupes) >= 2, "the wrapping fine grid should re-send at least the 0 and 12 deg images"


def test_sweep_refines_between_coarse_values(tmp_path):
    """The plan drawn north-6: no coarse value is within the degradation band, so only the
    fine grid (around the first-best coarse) reaches the true rotation; the placement is
    recovered either way (the composition is exact in the sent frame)."""
    r, _state, _logs = run_fit(6.0, tmp_path, rot=None, null=False)
    assert r["reason"] is None, r
    assert r["theta"] in (4.0, 6.0, 8.0), "sweep ended at theta=%s" % r["theta"]
    assert r["theta"] % 12.0 != 0.0, "the true rotation is not a coarse value"
    da, db = _placement_error_m(r, 6.0)
    assert db < 2.0 and da < 0.1
    assert all(e < 2.0 for e in _corner_error_m(r["corners"], 6.0))


def test_scramble_null_scores_below_fit(tmp_path):
    """The 302b scramble of the panel (the module's own recipe, the 302b seed) against the real
    sheet: the stub has no true correspondences to find there, so the null scores below the
    fit and the margin and confidence are positive."""
    r, _state, _logs = run_fit(0.0, tmp_path, rot=0.0, null=True)
    assert r["reason"] is None, r
    fit, scr = r["objective"]["fit"], r["objective"]["scramble"]
    assert fit > 0.0 and scr < fit, "fit %g vs scramble %g" % (fit, scr)
    assert r["null"] is not None and 0.0 <= r["null"] < fit
    assert r["margin"] > 0.0 and r["confidence"] > 0.0
    da, db = _placement_error_m(r, 0.0)
    assert db < 2.0 and da < 0.1
    assert all(e < 2.0 for e in _corner_error_m(r["corners"], 0.0))


def test_shifted_sheet_null_scores_below_fit(tmp_path):
    """The real panel against the 302b-shifted sheet image: only the in-frame quadrant of the
    sheet still carries true correspondences, so the null scores below the fit."""
    r, _state, _logs = run_fit(0.0, tmp_path, rot=0.0, null=True)
    assert r["reason"] is None, r
    fit, sh = r["objective"]["fit"], r["objective"]["shifted"]
    assert fit > 0.0 and sh < fit, "fit %g vs shifted %g" % (fit, sh)
    assert r["null"] == max(r["objective"]["scramble"], sh) or \
        abs(r["null"] - max(r["objective"]["scramble"], sh)) < 1e-3
    assert r["margin"] > 0.0 and r["confidence"] > 0.0


def test_recorded_match_response_reproduces_ransac_and_score():
    """The recorded-run pin (the test_gate pattern): the fixture is a fixed synthetic /match
    response (the ideal true pairs of the north-42 world + the fixed junk set) with the
    module's own ransac + score output recorded from it; the frozen core must reproduce it
    exactly, or the frozen configuration drifted."""
    assert os.path.exists(FIXTURE), "run: .venv/bin/python tests/test_surveyfit.py --emit-fixture"
    fx = json.load(open(FIXTURE))
    p0 = np.array([x - 1j * y for x, y in fx["keypoints0"]])
    p1 = np.array([x - 1j * y for x, y in fx["keypoints1"]])
    a, b, mask, rms = sf.ransac(p0, p1)
    s = sf.score(int(mask.sum()), len(p0), rms)
    rec = fx["ransac"]
    assert a is not None, "the fixture response must yield a similarity"
    assert (a.real, a.imag) == (rec["a"][0], rec["a"][1]), "ransac a drifted"
    assert (b.real, b.imag) == (rec["b"][0], rec["b"][1]), "ransac b drifted"
    assert int(mask.sum()) == rec["n_inliers"], "ransac inliers drifted"
    assert rms == rec["rms"], "ransac rms drifted: %r vs %r" % (rms, rec["rms"])
    assert s == fx["score"], "score drifted: %r vs %r" % (s, fx["score"])
    assert rec["n_inliers"] >= 14, "the true pairs must be the inliers"


def test_matcher_unavailable_is_a_method_reason(tmp_path):
    """/health answering 500 is a method-level reason, never an exception, and no /match is
    attempted."""
    r, state, _logs = run_fit(0.0, tmp_path, rot=0.0, null=False, healthy=False)
    assert r["reason"] is not None and r["reason"].startswith("matcher unavailable"), r
    assert r["placement"] is None and r["objective"] is None
    assert state["calls"] == [], "no /match call may be attempted once /health fails"


# ---------------------------------------------------------------- fixture generation (run once, commit)

def _ideal_response(theta_d):
    """The fixed synthetic /match response for the fixture: the ideal true pairs (no
    measurement jitter) as the service would return them for the fit-phase call, plus the
    fixed junk set."""
    world = build_world(theta_d)
    a_s, b_s = world["a_s"], world["b_s"]
    a, b = world["a_true"], world["b_true"]
    p0, p1 = [], []
    for (sx, sy) in world["sheet_centers"]:
        z = a_s * complex(sx, -sy) + b_s
        w = (z - b) / a
        q = CENTER + (np.array([w.real, -w.imag]) - CENTER) @ \
            np.array([[math.cos(math.radians(theta_d)), math.sin(math.radians(theta_d))],
                     [-math.sin(math.radians(theta_d)), math.cos(math.radians(theta_d))]]).T
        p0.append([float(q[0]), float(q[1])])
        p1.append([sx, sy])
    for a_, b_ in zip(world["junk_p0"], world["junk_p1"]):
        p0.append(list(a_))
        p1.append(list(b_))
    return p0, p1


def emit_fixture():
    p0, p1 = _ideal_response(42.0)
    w0 = np.array([x - 1j * y for x, y in p0])
    w1 = np.array([x - 1j * y for x, y in p1])
    a, b, mask, rms = sf.ransac(w0, w1)
    os.makedirs(os.path.dirname(FIXTURE), exist_ok=True)
    fx = {
        "world": {"note": "the synthetic north-42 world of this test: the ideal true pairs of "
                          "the plan (14) + the fixed junk set (12), response format of the "
                          "MatchAnything-ELoFTR /match endpoint (original pixel frames)",
                  "theta_d": 42.0, "lat": LAT0, "lon": LON0, "size_m": SIZE_M,
                  "sheet_px": SHEET, "plan_px": PLAN, "m_px": M_PX, "junk_seed": JUNK_SEED},
        "keypoints0": p0, "keypoints1": p1, "scores": [1.0] * len(p0),
        "ransac": {"a": [a.real, a.imag], "b": [b.real, b.imag],
                   "n_inliers": int(mask.sum()), "rms": rms},
        "score": sf.score(int(mask.sum()), len(p0), rms),
    }
    with open(FIXTURE, "w") as f:
        json.dump(fx, f, indent=1)
        f.write("\n")
    print("wrote %s: %d pairs, %d inliers, rms %g, score %g"
          % (FIXTURE, len(p0), int(mask.sum()), rms, fx["score"]))


if __name__ == "__main__":
    emit_fixture()
