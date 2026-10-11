"""Task 202: the proposed starting placement for a (site, picture) pair - fit/propose.py, end to end.

The 18 fixed sample (site, picture) pairs - the box's six tracked hand-fit sites (forthill, fudge,
highbank, hopeton, newark, marietta, through their S&D book rows), the nine indexed QID book rows of
the 20 hand-fit docs (their proposals share the doc's px frame, so the comparison is frame-direct),
and three hand-fitted commons pictures (format coverage) - are proposed, pinned byte-for-byte in
tests/golden/propose_202.json, and checked three ways:

1. FORMAT: 3-5 pairs on the panel's drawn features (the recorded map_box corners + centre, or the page
   corners + centre) in the row's size frame, px at 1 dp and lon/lat at 7 dp exactly as a platefit doc
   stores them; never snapped (the emitted u/v equal the recorded box geometry); the coarse flag and
   the ground (the fitkit FITKIT_GROUND convention: aerial only for a site with no LiDAR) are right.
   The aerial branch has no real sample pair (none of the 17 no-LiDAR sites has a picture row) and is
   asserted at the rule level on bibracte.
2. SELF-CONSISTENCY: re-fitting the emitted (rounded) pairs with the product's own solver
   (plan_fit.similarity, the same one 203a/203b feeds the pairs to) recovers the proposal's anchor
   (scale within 1e-3 m/px absolute or 2 % relative, rotation within 0.1 deg).
3. SANITY (the box's "a re-fit from the proposals of a hand-fit site lands within the hand fit's own
   residual range"), per the Option B decision (DECISIONS 2026-10-11: the cross-scan bridge of the
   old-style six is not a similarity, so no frame comparison is possible): the same-frame nine are
   re-fit from their doc pairs and compared to the proposal - bar-row scale within 50 % (calleva
   excluded: its Qwen bar box over-covers the bar, R2 in the prep), rotation in the hint band
   (trusted hint |d|<=15 deg or 70-110 deg; rejected hint <=35 deg or 70-110 deg; the 90-degree class
   lands in the second), panel-centre offset <= max(3 x hand max-resid, 100 m, 1.0 x panel diagonal).
   The old-style six (different scans of the same plate, no frame bridge): the proposed panel's
   physical size (m) vs the hand-fit earthwork's bounding box (m, from site.json plate.walls x fit)
   per side within 0.2-3 (marietta excluded: its wall trace is a single 80 m segment, not the drawn
   extent), the same rotation bands, and the distance from the site centre to the hand-fit earthwork
   centre (the recorded proxy of where the drawing sits on the ground) <= the same envelope.

No network, no server, no writes: the test reads repo data and the golden file only. Regenerate the
golden after an intended change: .venv/bin/python tests/test_propose.py --regen
"""
import hashlib
import json
import math
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
GOLDEN = ROOT / "tests" / "golden" / "propose_202.json"
sys.path.insert(0, str(ROOT / "fit"))
import propose as P  # noqa: E402  stdlib-only, the module under test
sys.path.insert(0, str(ROOT / "pipeline"))
try:
    import plan_fit  # noqa: E402  the product's solver (numpy/PIL); the same one 203a/203b use
    HAVE_PLAN_FIT = True
except ImportError:  # the driver venv is red (prep R6): re-fit checks skip, propose.py itself still runs
    plan_fit = None
    HAVE_PLAN_FIT = False

needs_fit = pytest.mark.skipif(
    not HAVE_PLAN_FIT, reason="plan_fit (numpy) unavailable - the driver venv is red? see prep 202 R6")

# ---- the fixed sample ------------------------------------------------------
SD6 = [  # the box's six tracked hand-fit sites, through their S&D book rows
    ("forthill", "ancientmonuments00squi_n0068_1"),
    ("fudge", "ancientmonuments00squi_n0203_1"),
    ("highbank", "ancientmonuments00squi_n0126_1"),
    ("hopeton", "ancientmonuments00squi_n0129_1"),
    ("newark", "ancientmonuments00squi_n0161_1"),
    ("marietta", "ancientmonuments00squi_n0169_1"),
]
QID = [  # the nine indexed book rows of the 20 hand-fit docs (same frame as their doc)
    ("hembury-q3784763", "earthworkenglan01allcgoog_n0108_1"),
    ("avebury-q661855", "earthworkenglan01allcgoog_n0581_1"),
    ("aztalan-state-park-q4832928", "antiquitiesofwis00saph_n0182_1"),
    ("badbury-rings-q798831", "earthworkenglan01allcgoog_n0132_1"),
    ("calleva-atrebatum-q1027253", "earthworkenglan01allcgoog_n0360_1"),
    ("maiden-castle-q1232816", "earthworkenglan01allcgoog_n0124_1"),
    ("old-sarum-q782719", "earthworkenglan01allcgoog_n0142_1"),
    ("serpent-mound-q968802", "ancientmonuments00squi_n0210_1"),
    ("arbor-low-q630312", "earthworkenglan01allcgoog_n0597_1"),
]
COMMONS = [  # hand-fitted commons pictures (format coverage; no stage-B fields -> always coarse)
    ("castle-rising-castle-q1049485", "c_70f937b71ae63d6a"),
    ("mayburgh-henge-q1469390", "c_984782b9e35e8ded"),
    ("old-sarum-q782719", "c_8192abb966d030a3"),
]
SAMPLE = SD6 + QID + COMMONS
BIBRACTE = "bibracte-q650053"  # lidar: false, no picture row of its own - the aerial rule is unit-checked
PLATEFITS_DIR = ROOT / "data" / "db" / "platefits"

# Exclusions with a measured reason (the prep's R2 rule: never loosen an envelope for one site;
# record the measurement and exclude): calleva's Qwen bar box over-covers the bar (-73 % scale),
# marietta's wall trace is a single ~80 m segment inside a 1.5 x 2.1 km panel (0.05 ratio).
EXCLUDE_SCALE = {"calleva-atrebatum-q1027253", "marietta"}


def _key(site, plan):
    return f"{site} {plan}"


def _nz(x, dp):
    v = round(float(x), dp)
    return 0.0 if v == 0 else v  # keep the golden free of -0.0


# ---- readers (test setup; propose.py's own row readers are reused) ----------
def _doc(site, plan):
    return json.loads((PLATEFITS_DIR / f"{site}.{plan}.json").read_text())


def _site_json(sid):
    return json.loads((ROOT / "data" / "sites" / sid / "site.json").read_text())


def _row(site, plan):
    """The row in the frame the proposal uses (book index row / commons plans row)."""
    return P._index_row(plan) if not plan.startswith("c_") else P._plans_row(plan, site)


def _frame(row, plan):
    """The px frame of the row's pairs (the same one plan_fit.build would use)."""
    if plan.startswith("c_"):
        return row["size"]
    prow = P._plans_row(plan)
    return prow.get("size") or row.get("full_size")


def _band_ok(drot, rejected=False):
    """True when the proposed-vs-hand rotation delta is in the band: trusted hint |d|<=15 deg or
    70-110 deg; a rejected hint (|hint|>60) <=35 deg or 70-110 deg; the 90-degree class (north hint
    0 or missing, plate sideways - maiden, old-sarum, aztalan, old-sarum-commons) lands in the
    second band."""
    a = abs(drot)
    return a <= (35.0 if rejected else 15.0) or 70.0 <= a <= 110.0


def _rot_band(row, drot):
    """The row's band: rejected when its recorded north hint is untrustworthy (|deg| > 60)."""
    ang = row.get("north_angle_deg")
    rejected = row.get("north_arrow") is True and isinstance(ang, (int, float)) and abs(ang) > 60
    return _band_ok(drot, rejected)


# ---- the golden content ------------------------------------------------------
def build_sample():
    return {_key(s, p): P.propose_for(s, p) for s, p in SAMPLE}


def _refit(pairs):
    """(m/px, rot deg, max resid m) of a pair set, through the product's own solver."""
    a, b, resid, k = plan_fit.similarity(pairs)
    return abs(a) * k, math.degrees(math.atan2(a.imag, a.real)), float(max(resid))


def _panel_centre(row, plan):
    box = row.get("map_box")
    w, h = _frame(row, plan)
    x0, y0, x1, y1 = box if box else (0.0, 0.0, 1.0, 1.0)
    return 0.5 * (x0 + x1) * w, 0.5 * (y0 + y1) * h


def build_sanity_qid():
    out = {}
    for sid, plan in QID:
        row = P._index_row(plan)
        doc = _doc(sid, plan)
        frame = _frame(row, plan)
        # the same-frame premise of the whole check: doc frame == row frame
        assert doc.get("size") in (None, frame), f"{sid} {plan}: doc frame != row frame"
        mpx, rot, maxresid = _refit(doc["pairs"])
        prop = P.propose_for(sid, plan)
        a, b, _, k = plan_fit.similarity(doc["pairs"])
        u0, v0 = _panel_centre(row, plan)
        site = P._site(sid)
        z0 = complex(*P.to_merc(site["lon"], site["lat"]))
        centre = abs(a * complex(u0, -v0) + b - z0) * k
        dev = (prop["scale_m_px"] - mpx) / mpx * 100
        drot = (prop["rot_deg"] - rot + 180) % 360 - 180
        x0, y0, x1, y1 = row["map_box"]
        diag = math.hypot((x1 - x0) * frame[0], (y1 - y0) * frame[1]) * prop["scale_m_px"]
        env = max(3 * maxresid, 100.0, diag)
        # only recorded-scale (bar) rows are held to the hand-fit scale: a coarse anchor is a
        # seed, never held to the fit (the prep's measured 3x-10x deviations); calleva's bar box
        # over-covers the bar (R2)
        scale_ok = None if (sid in EXCLUDE_SCALE or prop["scale_source"] != "bar") else bool(abs(dev) <= 50)
        if sid in EXCLUDE_SCALE:
            assert abs(dev) > 50, f"{sid}: excluded but its deviation passes - drop the exclusion"
        out[sid] = {
            "plan": plan,
            "frame": list(frame),
            "hand": {"m_per_px": round(mpx, 4), "rot_deg": _nz(rot, 2), "maxresid_m": _nz(maxresid, 1)},
            "measured": {
                "scale_dev_pct": _nz(dev, 1), "drot_deg": _nz(drot, 1), "centre_dist_m": _nz(centre, 1),
                "envelope_m": _nz(env, 1),
                "checks": {"scale": None if scale_ok is None else bool(scale_ok),
                           "rot": bool(_rot_band(row, drot)), "centre": bool(centre <= env)},
            },
        }
    return out


def build_sanity_old_style():
    out = {}
    for sid, plan in SD6:
        fit = _site_json(sid)["plate"]["fit"]
        m00, m01, m10, m11, tE, tN = fit["affine"]
        u0, v0 = fit["u0v0"]
        pts = [(q[0], q[1]) for poly in _site_json(sid)["plate"]["walls"] for q in poly]
        ge = [m00 * (u - u0) + m01 * (v0 - v) + tE for u, v in pts]  # ground metres, site-centre origin
        gn = [m10 * (u - u0) + m11 * (v0 - v) + tN for u, v in pts]
        ew, eh = max(ge) - min(ge), max(gn) - min(gn)
        ce, cn = sum(ge) / len(ge), sum(gn) / len(gn)
        dist = math.hypot(ce, cn)
        prop = P.propose_for(sid, plan)
        row = P._index_row(plan)
        w, h = _frame(row, plan)
        x0, y0, x1, y1 = row["map_box"]
        pw, ph = (x1 - x0) * w * prop["scale_m_px"], (y1 - y0) * h * prop["scale_m_px"]
        diag = math.hypot((x1 - x0) * w, (y1 - y0) * h) * prop["scale_m_px"]
        ctrl = fit.get("control_resid_m")
        env = max(3 * max(ctrl) if ctrl else 0.0, 100.0, diag)
        drot = (prop["rot_deg"] - fit["rot_deg"] + 180) % 360 - 180
        ratios = [ew / pw, eh / ph]
        scale_ok = None if sid in EXCLUDE_SCALE else all(0.2 <= r <= 3 for r in ratios)
        if scale_ok is None:
            assert min(ratios) < 0.2, f"{sid}: excluded but its ratios pass - drop the exclusion"
        out[sid] = {
            "plan": plan,
            "hand": {
                "m_per_px": fit["m_per_px"], "rot_deg": fit["rot_deg"], "model": fit.get("model"),
                "resid_source": "control_resid_m" if ctrl else "none",
                "maxresid_m": _nz(max(ctrl), 1) if ctrl else None,
            },
            "measured": {
                "earthwork_m": [_nz(ew, 1), _nz(eh, 1)], "earthwork_centre_m": [_nz(ce, 1), _nz(cn, 1)],
                "panel_m": [_nz(pw, 1), _nz(ph, 1)], "diag_m": _nz(diag, 1),
                "side_ratios": [_nz(r, 3) for r in ratios], "centre_dist_m": _nz(dist, 1),
                "envelope_m": _nz(env, 1), "drot_deg": _nz(drot, 1),
                "checks": {"scale": None if scale_ok is None else bool(scale_ok),
                           "rot": bool(_rot_band(row, drot)), "centre": bool(dist <= env)},
            },
        }
    return out


def build_sanity_commons():
    out = {}
    for sid, plan in COMMONS:
        doc = _doc(sid, plan)
        mpx, rot, maxresid = _refit(doc["pairs"])
        prop = P.propose_for(sid, plan)
        drot = (prop["rot_deg"] - rot + 180) % 360 - 180
        out[sid] = {
            "plan": plan,
            "hand": {"m_per_px": round(mpx, 4), "rot_deg": _nz(rot, 2), "maxresid_m": _nz(maxresid, 1)},
            "measured": {"drot_deg": _nz(drot, 1), "checks": {"rot": bool(_band_ok(drot))}},
        }
    return out


def build_golden_text():
    doc = {
        "note": ("Task 202 golden: the 18 proposed starting placements (sample) and the measured "
                 "hand-fit comparisons (sanity) a starting point must pass; exclusions are recorded "
                 "in the checks nulls. Regenerate only for an intended change: "
                 ".venv/bin/python tests/test_propose.py --regen"),
        "sample": build_sample(),
        "sanity": {
            "qid": build_sanity_qid(),
            "old_style": build_sanity_old_style(),
            "commons": build_sanity_commons(),
        },
    }
    return json.dumps(doc, indent=1, sort_keys=True) + "\n"


# ---- the tests ---------------------------------------------------------------

def test_parse_scale_table():
    """The measured corpus of scale texts, through the public parse_scale (the known-bad ones
    must parse to None -> coarse, never a guess)."""
    span = [
        ("0 100 200 300 Feet", 91.44), ("0 500 feet", 152.4), ("0 1/2 1 mile", 1609.344),
        ("0 5 10 chains", 201.168), ("0 100 feet 200 300", 91.44),
        ("0 100 200 300 400 500 Scale of Feet", 152.4), ("SCALE 500 FEET", 152.4),
    ]
    for text, metres in span:
        got = P.parse_scale(text)
        assert got and got[0] == "span" and abs(got[1] - metres) < 1e-9, (text, got)
    ratio = [
        ("SCALE 300 ft. to the Inch.", 91.44), ("Scale 20 ft. to an inch.", 6.096),
        ("2 Ch. (352 Ft.) to the inch", 40.2336), ("12 Rods 200 feet to an inch.", 60.3504),
        ("Forty feet to the inch", 12.192), ("1/2 Miles to an Inch", 804.672),
        ("1000 ft. to Inch.", 304.8), ("Scale: 1 in. = 100 feet", 30.48), ("1 in = 240 feet", 73.152),
        ("1 in. = 100 ft. 1/2 in. = 50 ft. 1/4 in. = 25 ft.", 30.48),
        ("one inch equals three miles", 4828.032), ("SCALE 1/32m.", 32.0),
        ("1/20 OF NATURE", 0.508), ("SCALE 400 ft to the Inch.", 121.92),
        ("SCALE. 1300 ft. to the Inch.", 396.24),
    ]
    for text, m_in in ratio:
        got = P.parse_scale(text)
        assert got and got[0] == "ratio" and abs(got[1] - m_in) < 1e-9, (text, got)
    for text in ["0 1/4 1/2", "no. 10 to one inch", "scale miles", "Scale of Fee[t]", "Scale", ""]:
        assert P.parse_scale(text) is None, text


def test_sample_format():
    """Every proposal: 3-5 pairs in the row's size frame, the documented rounding, the coarse
    flag, the ground, and the scale source the row's evidence should give."""
    for sid, plan in SAMPLE:
        prop = P.propose_for(sid, plan)
        assert set(prop) == {"pairs", "coarse", "ground", "scale_m_px", "rot_deg", "scale_source", "note"}
        assert 3 <= len(prop["pairs"]) <= 5
        row = _row(sid, plan)
        w, h = _frame(row, plan)
        for u, v, lon, lat in prop["pairs"]:
            assert round(u, 1) == u and round(v, 1) == v, (sid, plan, u, v)  # px 1 dp
            assert round(lon, 7) == lon and round(lat, 7) == lat, (sid, plan, lon, lat)  # 7 dp
            assert 0.0 <= u <= w and 0.0 <= v <= h, (sid, plan, u, v)  # inside the frame
        assert prop["ground"] in ("relief", "aerial")
        assert prop["ground"] == "relief", f"{sid}: sample sites all have a relief ground image"
        if plan.startswith("c_"):  # commons: no stage-B fields -> coarse, picture-size scale, north-up
            assert prop["coarse"] is True and prop["scale_source"] == "picture_size"
            assert prop["rot_deg"] == 0.0 and prop["scale_m_px"] is not None
        else:
            rowb = P._index_row(plan)
            if plan in ("ancientmonuments00squi_n0210_1", "earthworkenglan01allcgoog_n0597_1",
                        "antiquitiesofwis00saph_n0182_1"):  # serpent / arbor-low / aztalan: coarse
                assert prop["coarse"] is True and prop["scale_source"] == "picture_size"
            elif rowb.get("book") == "squier_davis_1848":  # the six S&D rows: ratio text in a boxed bar
                assert prop["coarse"] is False and prop["scale_source"] == "ratio"
            else:  # the six Allcroft bar rows: tick-list span over the bar box
                assert prop["coarse"] is False and prop["scale_source"] == "bar"


def test_no_snapping():
    """The pairs sit exactly on the recorded map_box geometry (corners + centre, or the page
    corners + centre): a proposal is a starting point, never a moved point."""
    for sid, plan in SAMPLE:
        prop = P.propose_for(sid, plan)
        row = _row(sid, plan)
        w, h = _frame(row, plan)
        box = row.get("map_box")
        x0, y0, x1, y1 = box if box else (0.0, 0.0, 1.0, 1.0)
        expected = [[round(x0 * w, 1), round(y0 * h, 1)], [round(x1 * w, 1), round(y0 * h, 1)],
                    [round(x1 * w, 1), round(y1 * h, 1)], [round(x0 * w, 1), round(y1 * h, 1)],
                    [round(0.5 * (x0 + x1) * w, 1), round(0.5 * (y0 + y1) * h, 1)]]
        assert [[p[0], p[1]] for p in prop["pairs"]] == expected, (sid, plan)


def test_ground_rule_aerial():
    """The fitkit ground convention: aerial exactly for a site with no LiDAR. No no-LiDAR site has
    a picture row, so the aerial branch is asserted at the rule level on bibracte."""
    assert P._site(BIBRACTE).get("lidar") is False
    site = P._site(BIBRACTE)
    scale = P._picture_scale(site, [1000, 1000], (0.1, 0.1, 0.9, 0.9))
    assert scale is not None
    pairs = P._anchor_pairs(site, [1000, 1000], (0.1, 0.1, 0.9, 0.9), scale, 0.0)
    assert P._proposal(site, pairs, True, scale, "picture_size", 0.0, ["aerial branch"])["ground"] == "aerial"


@needs_fit
def test_self_consistency():
    """Re-fitting the emitted (rounded) pairs with the product's own solver recovers the anchor -
    203a/203b start from exactly this."""
    for sid, plan in SAMPLE:
        prop = P.propose_for(sid, plan)
        mpx, rot, _ = _refit(prop["pairs"])
        ds = abs(mpx - prop["scale_m_px"])
        dr = abs((rot - prop["rot_deg"] + 180) % 360 - 180)
        assert ds <= max(1e-3, 0.02 * prop["scale_m_px"]), (sid, plan, ds)
        assert dr <= 0.1, (sid, plan, dr)


@needs_fit
def test_sanity_qid():
    """The same-frame nine vs their hand fit: bar-row scale within 50 % (calleva excluded, R2),
    rotation in the hint band, panel-centre offset inside the envelope."""
    for sid, plan in QID:
        row = P._index_row(plan)
        doc = _doc(sid, plan)
        frame = _frame(row, plan)
        assert doc.get("size") in (None, frame)  # the same-frame premise, per site
        mpx, rot, maxresid = _refit(doc["pairs"])
        prop = P.propose_for(sid, plan)
        dev = (prop["scale_m_px"] - mpx) / mpx * 100
        drot = (prop["rot_deg"] - rot + 180) % 360 - 180
        a, b, _, k = plan_fit.similarity(doc["pairs"])
        u0, v0 = _panel_centre(row, plan)
        site = P._site(sid)
        centre = abs(a * complex(u0, -v0) + b - complex(*P.to_merc(site["lon"], site["lat"]))) * k
        x0, y0, x1, y1 = row["map_box"]
        diag = math.hypot((x1 - x0) * frame[0], (y1 - y0) * frame[1]) * prop["scale_m_px"]
        env = max(3 * maxresid, 100.0, diag)
        if sid not in EXCLUDE_SCALE and prop["scale_source"] == "bar":
            assert abs(dev) <= 50, (sid, dev)
        assert _rot_band(row, drot), (sid, drot)
        assert centre <= env, (sid, centre, env)


@needs_fit
def test_sanity_old_style():
    """Option B for the old-style six (no frame bridge between the two scans): the proposed panel's
    physical size vs the hand-fit earthwork's bounding box per side within 0.2-3 (marietta's wall
    trace is a single ~80 m segment, excluded with its measured ratio), the rotation band, and the
    site-centre-to-earthwork-centre distance inside the envelope."""
    for sid, plan in SD6:
        fit = _site_json(sid)["plate"]["fit"]
        row = P._index_row(plan)
        m00, m01, m10, m11, tE, tN = fit["affine"]
        u0, v0 = fit["u0v0"]
        pts = [(q[0], q[1]) for poly in _site_json(sid)["plate"]["walls"] for q in poly]
        ge = [m00 * (u - u0) + m01 * (v0 - v) + tE for u, v in pts]
        gn = [m10 * (u - u0) + m11 * (v0 - v) + tN for u, v in pts]
        ew, eh = max(ge) - min(ge), max(gn) - min(gn)
        dist = math.hypot(sum(ge) / len(ge), sum(gn) / len(gn))
        prop = P.propose_for(sid, plan)
        w, h = _frame(row, plan)
        x0, y0, x1, y1 = row["map_box"]
        pw, ph = (x1 - x0) * w * prop["scale_m_px"], (y1 - y0) * h * prop["scale_m_px"]
        diag = math.hypot((x1 - x0) * w, (y1 - y0) * h) * prop["scale_m_px"]
        ctrl = fit.get("control_resid_m")
        env = max(3 * max(ctrl) if ctrl else 0.0, 100.0, diag)
        drot = (prop["rot_deg"] - fit["rot_deg"] + 180) % 360 - 180
        if sid not in EXCLUDE_SCALE:
            assert all(0.2 <= r <= 3 for r in (ew / pw, eh / ph)), (sid, ew / pw, eh / ph)
        assert _rot_band(row, drot), (sid, drot)
        assert dist <= env, (sid, dist, env)


@needs_fit
def test_sanity_commons():
    for sid, plan in COMMONS:
        doc = _doc(sid, plan)
        _, rot, _ = _refit(doc["pairs"])
        prop = P.propose_for(sid, plan)
        drot = (prop["rot_deg"] - rot + 180) % 360 - 180
        assert _band_ok(drot), (sid, drot)


@needs_fit
def test_golden():
    """The byte-exact golden: the 18 proposals plus the measured sanity numbers. Any change to
    propose.py or to the repo data it reads fails this; regenerate only for an intended change."""
    assert GOLDEN.read_text() == build_golden_text()


def test_cli():
    """The CLI prints the proposal JSON (indent=1, sorted keys) - what a human eyeballs."""
    sid, plan = SAMPLE[0]
    out = subprocess.run([sys.executable, str(ROOT / "fit" / "propose.py"), sid, plan],
                         capture_output=True, text=True, check=True)
    assert out.stdout == json.dumps(P.propose_for(sid, plan), indent=1, sort_keys=True) + "\n"


# Regression guard: the 20 hand-fit docs must be byte-identical through the whole run.
_DOCS_SHA = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(PLATEFITS_DIR.glob("*.json"))}


def test_platefit_docs_untouched():
    now = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(PLATEFITS_DIR.glob("*.json"))}
    assert now == _DOCS_SHA


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--regen", action="store_true", help="regenerate tests/golden/propose_202.json")
    args = ap.parse_args()
    if args.regen:
        assert HAVE_PLAN_FIT, "regen needs the venv (plan_fit): .venv/bin/python"
        GOLDEN.write_text(build_golden_text())
        print(f"wrote {GOLDEN}")
    else:
        sys.exit(pytest.main([__file__, "-q"]))
