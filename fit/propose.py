"""Propose a starting placement for a (site, picture) pair, for the model's fitting pass (task 202, GOAL.md point 2).

Given a site and an old picture (a book index row, or a commons picture), produce the STARTING POINT of
the fit: an anchor mapping the picture's map-panel centre onto the site centre at the recorded scale
and rotation (coarse when none is recorded), plus 3-5 proposed point pairs on the panel's drawn
features (the four corners plus the centre), in page pixels of the row's image frame -> lon/lat.

This is a starting point, NOT a fit (GOAL.md point 2): the pairs are never snapped or texture-matched,
this output never goes to the fit gate and never becomes a platefit doc on its own. Consumers: the
batch fitting tasks (203a/203b) feed ``pairs`` to ``pipeline.plan_fit.similarity`` as the model's
starting point and then record their own matched pairs; the review queue (201) shows the same
starting point to a human when the model cannot fit.

Contract (201 stores this dict verbatim in review items; keep the signature and keys stable -
this docstring is the single statement of it):

    propose_for(site_id, plan_id, root=ROOT) -> {
        "pairs": [[u, v, lon, lat], ... 3-5 of them; page px in the row's ``size`` frame,
            u/v rounded to 1 dp, lon/lat to 7 dp - the platefit-doc convention],
        "coarse": bool,               # True when the scale is not the recorded bar or ratio
        "ground": "relief" | "aerial",# the site's ground image (fitkit's FITKIT_GROUND:
                                       # aerial for a site with no LiDAR)
        "scale_m_px": float or None,  # anchor scale, metres per page px, rounded to 4 dp
        "rot_deg": float,             # anchor rotation (north-up = 0), rounded to 2 dp
        "scale_source": "bar" | "ratio" | "picture_size" | None,
        "note": str or None,          # coarse reasons / rejected north hint / pace assumption
    }

    ``root`` is the data tree the loaders read: ``web/data`` and ``data/books`` under it
    (default: this checkout, today's behaviour for every existing two-arg caller). The
    cache is keyed by root, so a generator or test run against a temp tree never collides
    with this checkout's data.

Deterministic (no timestamps); stdlib only, importable by 203a/203b in any environment.

The anchor is a similarity in the exact form ``pipeline.plan_fit.similarity`` inverts
(``merc = a * (w - w0) + z0``, ``w = u - i*v`` with image v down,
``a = (m_per_px / ground_scale(lat0)) * e^(i*theta)``), so a re-fit of the proposed pairs
recovers this anchor (a page's live preview starts from a real placement). The Mercator
one-liners mirror ``pipeline/aw.py``, which requires numpy and so cannot be imported here.

CLI: ``python3 fit/propose.py <site> <plan id>...``
"""

import argparse
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Scan pixels per inch of original plate, per book key (data/books/summary.md "Books and
# scans"). None = ppi not recorded for that scan (no published value exists: web lookup
# 2026-10-11 found nothing) -> a ratio-only row of that book takes the coarse path instead
# of a guessed scale.
BOOK_PPI = {
    "squier_davis_1848": 500.0,
    "thomas_1894": 360.0,
    "fowke_1902": 500.0,
    "allcroft_1908": 600.0,
    "mills_1914": 150.0,
    "lapham_1855": None,
    "squier_1851": None,
    "whittlesey_1850": None,
}

# Metres per unit. Pace = 0.5 yd is an assumption (flagged in the note when it is used).
UNIT_M = {
    "ft": 0.3048, "feet": 0.3048,
    "yd": 0.9144, "yard": 0.9144, "yards": 0.9144,
    "mi": 1609.344, "mile": 1609.344, "miles": 1609.344,
    "ch": 20.1168, "chain": 20.1168, "chains": 20.1168,
    "rod": 5.0292, "rods": 5.0292,
    "pace": 0.762, "paces": 0.762,
}

_WORD_NUM = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
    "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
}

_TOKEN = re.compile(r"[a-z]+[\.\-]*|\d+(?:\s*/\s*\d+)?")

# Mercator one-liners mirroring pipeline/aw.py (R = WGS84 equatorial radius), inlined so
# this module stays stdlib-only (aw.py imports numpy/PIL/scipy at its top).
_R = 6378137.0


def to_merc(lon, lat):
    return (math.radians(lon) * _R, math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)) * _R)


def to_lonlat(x, y):
    return (math.degrees(x / _R), math.degrees(2 * math.atan(math.exp(y / _R)) - math.pi / 2))


def ground_scale(lat):
    """Metres on the ground per Mercator metre at this latitude."""
    return math.cos(math.radians(lat))


def _tokens(s):
    return _TOKEN.findall(s.lower())


def _num_at(toks, i):
    """The number value at token i (integer, "a/b" fraction, or a word number, including
    "N hundred (and M)") -> (value or None, index after the consumed tokens)."""
    t = toks[i]
    v = None
    if "/" in t:
        a, b = (x.strip() for x in t.split("/", 1))
        if a.isdigit() and b.isdigit() and int(b) > 0:
            v = int(a) / int(b)
    elif t.isdigit():
        v = float(t)
    else:
        w = t.rstrip(".,;:")
        if w in _WORD_NUM:
            v = float(_WORD_NUM[w])
            j = i + 1
            if v and j < len(toks) and toks[j].rstrip(".,;:") == "hundred":
                v *= 100
                j += 1
                if j < len(toks) and toks[j].rstrip(".,;:") == "and" and j + 1 < len(toks):
                    w2 = toks[j + 1].rstrip(".,;:")
                    if w2 in _WORD_NUM:
                        v += _WORD_NUM[w2]
                        j += 1
                return v, j
    return (v, i + 1) if v is not None else (None, i + 1)


def _unit_in(s):
    for t in _tokens(s):
        u = t.rstrip(".,;:")
        if u in UNIT_M:
            return u
    return None


def _first_quantity(s):
    """First "<number> <unit>" quantity in s -> metres, or None (e.g. "no. 10" has no unit)."""
    toks = _tokens(s)
    i = 0
    while i < len(toks):
        v, j = _num_at(toks, i)
        if v is None:
            i += 1
            continue
        for k in range(j, min(j + 3, len(toks))):
            u = toks[k].rstrip(".,;:")
            if u in UNIT_M:
                return v * UNIT_M[u]
        return None
    return None


def _ratio_m_per_inch(t):
    """'N <unit> to the/an inch' style (incl. "2 Ch. (352 Ft.)", "Forty feet", fractions) ->
    metres per inch of the original plate, or None."""
    m = re.search(r"(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)\s+of\s+nature", t)
    if m:  # "1/20 OF NATURE": 1 unit = 20 of the same unit; one inch = 25.4 mm
        return float(m.group(2)) / float(m.group(1)) * 0.0254
    m = re.search(r"1\s*[:/]\s*(\d+(?:\.\d+)?)\s*m\b", t)
    if m:  # "SCALE 1/32m." / "1:32 m": N metres per inch
        return float(m.group(1))
    m = re.search(r"^(?:scale[:.]*\s*)?(?:1|one)\s+(?:in|inch|inches)\.?\s*(?:equals?|is|=)\s+(.+)$", t)
    if m:  # "one inch equals three miles" / "1 in = 240 feet"
        return _first_quantity(m.group(1))
    if " to " in t:
        head, tail = t.split(" to ", 1)
        if re.match(r"^\s*(?:a|an|the|one)?\s*(?:inch|in)\.?\b", tail):
            return _first_quantity(head)
    return None


def _span_m(t):
    """Tick list ("0 100 200 300 Feet" -> last - first) or a single "N <unit>" (the whole
    bar) -> (metres, unit key) or (None, None). No unit word -> None (never a guess)."""
    unit = _unit_in(t)
    if not unit:
        return None, None
    toks = _tokens(t)
    nums = []
    i = 0
    while i < len(toks):
        v, j = _num_at(toks, i)
        if v is not None:
            nums.append(v)
        i = j
    if not nums:
        return None, None
    span = nums[0] if len(nums) == 1 else max(nums) - min(nums)
    return span * UNIT_M[unit], unit


def parse_scale(text):
    """Parse a plate's scale text.

    -> ("span", metres, unit) : the bar's drawn length represents `metres` (a tick list,
       or a single "N <unit>" which is the whole bar); unit is the UNIT_M key used.
    -> ("ratio", metres_per_inch, None): one inch of the original plate represents
       `metres` ("300 ft. to the Inch.", "1 in = 240 feet", "1/32m", "1/20 OF NATURE").
    -> None: no trustworthy scale (e.g. "0 1/4 1/2" has no unit, "no. 10 to one inch",
       "scale miles" has no number) - never a guess.
    """
    if not text:
        return None
    t = " ".join(str(text).split()).lower()
    r = _ratio_m_per_inch(t)
    if r is not None:
        return ("ratio", r, None)
    m, unit = _span_m(t)
    if m is not None:
        return ("span", m, unit)
    return None


_CACHE = {}


def _cache_key(root, kind):
    """The cache key: root and file kind, so several trees in one process (this checkout
    and a --root temp tree) never read each other's data."""
    return (str(root), kind)


def _index_row(plan_id, root=ROOT):
    """The book index row by id (the stage-B fields: scale_text, blank_boxes, north_*, map_box)."""
    key = _cache_key(root, "index")
    if key not in _CACHE:
        idx = {}
        p = Path(root) / "data" / "books" / "index.jsonl"
        for line in p.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                if r.get("id"):
                    idx[r["id"]] = r
        _CACHE[key] = idx
    r = _CACHE[key].get(plan_id)
    if r is None:
        raise ValueError("no book index row for plan %r" % plan_id)
    return r


def _plans_rows(root=ROOT):
    key = _cache_key(root, "plans")
    if key not in _CACHE:
        d = json.loads((Path(root) / "web" / "data" / "plans.json").read_text())
        cols = {c: i for i, c in enumerate(d["cols"])}
        _CACHE[key] = [{k: r[i] for k, i in cols.items()} for r in d["rows"]]
    return _CACHE[key]


def _plans_row(plan_id, site_id=None, root=ROOT):
    """The plans.json row by id; duplicate ids (a picture offered to several sites) pick
    the row whose sites list contains site_id, else the first."""
    rows = [r for r in _plans_rows(root) if r["id"] == plan_id]
    if not rows:
        raise ValueError("no plans row for %r" % plan_id)
    if len(rows) > 1 and site_id:
        for r in rows:
            if site_id in (r.get("sites") or []):
                return r
    return rows[0]


def _site(site_id, root=ROOT):
    key = _cache_key(root, "sites")
    if key not in _CACHE:
        d = json.loads((Path(root) / "web" / "data" / "sites.json").read_text())
        ss = d.get("sites") if isinstance(d, dict) else d
        _CACHE[key] = {s["id"]: s for s in ss if s.get("id")}
    s = _CACHE[key].get(site_id)
    if s is None:
        raise ValueError("no site %r in web/data/sites.json" % site_id)
    return s


def _bar_box(row):
    """The row's scale-bar box (fractions of the page) or None: box presence beats the
    scale_bar boolean (a box is recorded even when the boolean is false)."""
    for b in row.get("blank_boxes") or []:
        if b.get("kind") == "scale_bar":
            return b.get("box")
    return None


def _fmt(x):
    return "%g" % x


def _picture_scale(site, size, box):
    """Coarse scale: the site box (its ground image is that many metres over size_m px)
    against the panel's largest extent in page px. None when the site has no size_m."""
    sm = site.get("size_m")
    if not sm:
        return None
    w, h = size
    x0, y0, x1, y1 = box if box else (0.0, 0.0, 1.0, 1.0)
    return max(sm) / max((x1 - x0) * w, (y1 - y0) * h)


def _scale(row, size, box, site):
    """The anchor scale (m/page px), its source, and note parts for this book row."""
    notes = []
    text = row.get("scale_text")
    barbox = _bar_box(row)
    ppi = BOOK_PPI.get(row.get("book"))
    parsed = parse_scale(text) if text else None
    if barbox is not None and parsed and parsed[0] == "span":
        bw = (barbox[2] - barbox[0]) * size[0]
        bh = (barbox[3] - barbox[1]) * size[1]
        notes.append("scale from the scale bar: %r" % text)
        if parsed[2] in ("pace", "paces"):
            notes.append("pace = 0.5 yd (assumed)")
        return parsed[1] / max(bw, bh), "bar", notes
    if parsed and parsed[0] == "ratio":
        if ppi:
            if barbox is not None:
                notes.append("scale from the printed ratio at %s ppi (the scale-bar box holds the ratio text, not ticks)" % _fmt(ppi))
            else:
                notes.append("scale from the printed ratio at %s ppi" % _fmt(ppi))
            return parsed[1] / ppi, "ratio", notes
        notes.append("ratio %r unusable: %s scan ppi not recorded" % (text, row.get("book")))
    if parsed and parsed[0] == "span" and barbox is None:
        notes.append("scale text %r is a bar span but no scale-bar box is recorded" % text)
    elif text is not None and parsed is None:
        notes.append("no usable scale text: %r" % text)
    elif text is None:
        notes.append("no scale text recorded")
    m = _picture_scale(site, size, box)
    if m is None:
        notes.append("no usable scale and the site has no size_m: no anchor scale")
        return None, None, notes
    return m, "picture_size", notes


def _rotation(row):
    """(rot_deg, note or None): the recorded north angle unless it is untrustworthy
    (no arrow, or |deg| > 60 - a flipped/rotated hint), else north-up with the rejected
    hint kept in the note."""
    ang = row.get("north_angle_deg")
    arrow = row.get("north_arrow")
    if isinstance(ang, (int, float)):
        if arrow is True and abs(ang) <= 60.0:
            return float(ang), None
        reason = "|deg| > 60" if abs(ang) > 60 else "no north arrow"
        return 0.0, "north hint %s deg rejected (%s): plate left north-up" % (_fmt(ang), reason)
    return 0.0, None


def _anchor_pairs(site, size, box, m_per_px, rot_deg):
    """The 5 proposed pairs (4 panel corners + centre, or 4 page corners + page centre)
    in the row's size frame, from the anchor similarity."""
    w, h = size
    x0, y0, x1, y1 = box if box else (0.0, 0.0, 1.0, 1.0)
    if (x1 - x0) * w < 2.0 or (y1 - y0) * h < 2.0:
        x0, y0, x1, y1 = 0.0, 0.0, 1.0, 1.0
    u0 = 0.5 * (x0 + x1) * w
    v0 = 0.5 * (y0 + y1) * h
    zx0, zy0 = to_merc(site["lon"], site["lat"])
    k = ground_scale(site["lat"])
    a = (m_per_px / k) * complex(math.cos(math.radians(rot_deg)), math.sin(math.radians(rot_deg)))
    wc = complex(u0, -v0)
    zc = complex(zx0, zy0)
    pts = [(x0 * w, y0 * h), (x1 * w, y0 * h), (x1 * w, y1 * h), (x0 * w, y1 * h), (u0, v0)]
    pairs = []
    for u, v in pts:
        z = a * (complex(u, -v) - wc) + zc
        lon, lat = to_lonlat(z.real, z.imag)
        pairs.append([round(u, 1), round(v, 1), round(lon, 7), round(lat, 7)])
    return pairs


def _proposal(site, pairs, coarse, scale, source, rot, notes):
    return {
        "pairs": pairs,
        "coarse": coarse,
        "ground": "aerial" if site.get("lidar") is False else "relief",
        "scale_m_px": None if scale is None else round(scale, 4),
        "rot_deg": round(rot, 2),
        "scale_source": source,
        "note": None if not notes else "; ".join(notes),
    }


def propose_for(site_id, plan_id, root=ROOT):
    """The proposed starting placement of plan_id's picture for site_id (contract above).
    ``root`` is the data tree the loaders read (default: this checkout)."""
    site = _site(site_id, root)
    if plan_id.startswith("c_"):
        row = _plans_row(plan_id, site_id, root)
        size = row.get("size")
        if not size:
            raise ValueError("commons row %r has no size" % plan_id)
        scale = _picture_scale(site, size, row.get("map_box"))
        if scale is None:
            raise ValueError("site %r has no size_m: no coarse anchor" % site_id)
        notes = ["commons row: no stage-B fields: coarse anchor"]
        if row.get("view"):
            notes.append("perspective picture: the similarity anchor is a seed only")
        pairs = _anchor_pairs(site, size, row.get("map_box"), scale, 0.0)
        return _proposal(site, pairs, True, scale, "picture_size", 0.0, notes)
    row = _index_row(plan_id, root)
    size = _plans_row(plan_id, site_id, root).get("size") or row.get("full_size")
    if not size:
        raise ValueError("row %r has no size frame (size/full_size both null)" % plan_id)
    box = row.get("map_box")
    scale, source, notes = _scale(row, size, box, site)
    rot, rnote = _rotation(row)
    if rnote:
        notes.append(rnote)
    if scale is None:
        raise ValueError("site %r has no size_m: no anchor scale" % site_id)
    pairs = _anchor_pairs(site, size, box, scale, rot)
    return _proposal(site, pairs, source not in ("bar", "ratio"), scale, source, rot, notes)


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Propose the starting placement (anchor + 3-5 pairs) for (site, picture) pairs.")
    ap.add_argument("site", help="a site id from web/data/sites.json")
    ap.add_argument("plan", nargs="+", help="plan ids (book row ids or c_... commons ids)")
    a = ap.parse_args(argv)
    for plan in a.plan:
        print(json.dumps(propose_for(a.site, plan), indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
