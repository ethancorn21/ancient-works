"""The "Ready to fit" queue (task 305): the built sites with candidate pictures but no hand fit yet,
one per entry, ordered so the site most worth seeing comes first.

usage: tools/fit_queue.py [--root DIR]  -> web/data/fit_queue.json

The owner's hand fits are the only fits that land right (the automatic ones are tasks 301/302b), so the
page shows him the next site of this queue with its best candidate already loaded, and his save runs the
one-site line on that site (server/serve.py). One site at a time: when he saves, that site is finished.

A site is in the queue exactly when all three hold:

  built        it has an entry in web/data/sites.json AND a web/data/sites/<id>/ directory (the same
               rule as tools/site_done.py);
  a candidate  web/data/plans.json names it in a row's sites field, or one of its data/review/ item
               files holds it a candidate (all item files count, open and resolved: the item's `site`
               field is the key, never the file name);
  no hand fit  none of the site's data/db/platefits/ documents carries by: "hand" (agent documents do
               not disqualify: the owner is still free to place a better one).

And one rule more (309): the queue never pairs a picture with a namesake site. When the
catalog and book stores are present (data/catalog/, data/books/ - both optional), every
candidate is checked by tools/right_place: the picture's caption place words and county
against the site's county/state (an unknown place never flags). A flagged candidate
leaves its site's queue - into the right site's entry or review item when the catalog
names one, else into the source site's own review item - carrying the reason "same name,
other place: <caption place> vs <site place>" (a review-candidate extra, data/review/
README.md). A tree without those stores builds exactly 305's queue.

The best candidate: a true plan over a bird's-eye view, then the larger drawing area (a book row: its
map_box fraction of the page size in px; a row with no box, or a commons row: the whole page/image; an
item candidate with no size stored: 0), then the plan id (stable). The one-word reason says why it won:
"the only candidate", "a true plan" (a plan chosen while a view exists), "the clearest scan" (best of
several plans), "the clearest view" (the views win). Sites are ordered by the same rule applied to each
site's best candidate, then by the site's name - the cleanest, most ink to click on comes first.

Each entry whose best row admits a starting placement carries it as the propose key - the anchor
mapping the picture's panel centre onto the site at the recorded scale and rotation (fit/propose.py
propose_for: bar scale, printed ratio at the book's ppi, the site-size fallback, the north arrow where
trustworthy) re-emitted as 3-5 page-px -> lon/lat pairs - so the page (307b) opens the map on the works
before any clicking. A row the proposal cannot anchor (no size, no size_m, no stage-B index row, no
index file) gets no propose key: the page falls back to the three-point flow for it.

Stdlib only: it reads the four inputs above plus data/books/index.jsonl (the stage-B fields
scale_text, blank_boxes, north_angle_deg, north_arrow, map_box, full_size - fit/propose.py, which
computes the propose, is stdlib-only too) and data/catalog/ with data/books/ for the right-place check
(both optional) and never opens an image (the sizes come from the json files), so the owner's Mac can
run it with any python. Its only imports are tools/right_place.py, fit/review.py and fit/propose.py -
all stdlib-only, no pipeline/. Finder/Amazon data never enters the queue.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Self-inserted on purpose: runpy.run_path (the test's guard) does not put this script's
# directory on sys.path, so the imports below would fail without the inserts.
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "fit"))

import right_place  # noqa: E402
import review  # noqa: E402
import propose as _propose  # noqa: E402  (fit/ has no __init__.py: the site_done.py convention)

# The row's named fields, in web/data/plans.json column order (the page's openPlan reads them).
ROW_FIELDS = ("id", "book", "ia", "file", "title", "label", "size", "map_box",
              "sites", "cite", "url", "view", "ref")


def _save_json(path, obj):
    """Atomic JSON write, same convention as the doc store (indent=1, no trailing newline)."""
    path = Path(path)
    tmp = str(path) + "." + str(os.getpid()) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1)
    os.replace(tmp, path)


def _load_json(path):
    """The file's JSON, or None when the file is absent (the page is served without it too);
    a malformed file fails loudly."""
    path = Path(path)
    if not path.is_file():
        return None
    return json.loads(path.read_text())


def _plans_rows(root):
    """The web/data/plans.json rows as named dicts, in file order (the page's P.rows shape)."""
    d = _load_json(Path(root) / "web" / "data" / "plans.json") or {}
    cols = {c: i for i, c in enumerate(d.get("cols") or [])}
    return [{k: r[i] for k, i in cols.items()} for r in d.get("rows") or []]


def _built_sites(root):
    """The built sites as (id, name) in sites.json order: an entry in web/data/sites.json and a
    web/data/sites/<id>/ directory (the same rule as tools/site_done.py)."""
    d = _load_json(Path(root) / "web" / "data" / "sites.json")
    ss = d.get("sites") if isinstance(d, dict) else d
    base = Path(root) / "web" / "data" / "sites"
    return [(s["id"], s.get("name") or s["id"]) for s in (ss or [])
            if s.get("id") and (base / s["id"]).is_dir()]


def _no_lidar_sites(root):
    """The sites whose sites.json entry says lidar: false (aerial-photograph ground only). The
    owner, 2026-10-13: fits on aerial photographs alone mostly do not line up, so the queue
    offers LiDAR sites only. Their review items stay; they just do not enter the queue."""
    d = _load_json(Path(root) / "web" / "data" / "sites.json")
    ss = d.get("sites") if isinstance(d, dict) else d
    return {s["id"] for s in (ss or []) if s.get("id") and s.get("lidar") is False}


def _item_candidates(root):
    """The candidates of every data/review/ item file, keyed by the item's `site` field (open and
    resolved items alike: a resolved item's candidates are still the site's candidate pictures - what
    takes a site out of the queue is a hand document, not a resolution)."""
    out = {}
    d = Path(root) / "data" / "review"
    if not d.is_dir():
        return out
    for p in sorted(d.iterdir()):
        if p.suffix != ".json":
            continue
        item = json.loads(p.read_text())
        sid = item.get("site")
        if not sid:
            continue
        for c in item.get("candidates") or []:
            if c.get("plan"):
                out.setdefault(sid, []).append(c)
    return out


def _hand_sites(root):
    """The site ids that already have a by: "hand" fit document (the doc's `site` field, or, for a
    doc without one, the id prefix before the first dot of its file name)."""
    out = set()
    d = Path(root) / "data" / "db" / "platefits"
    if not d.is_dir():
        return out
    for p in sorted(d.iterdir()):
        if p.suffix != ".json":
            continue
        doc = json.loads(p.read_text())
        if doc.get("by") == "hand":
            out.add(doc.get("site") or p.name[:-5].split(".", 1)[0])
    return out


def _synth_row(c, site_id):
    """The row the page synthesizes when a candidate has no plans.json row naming the site
    (web/review.js rvResolveRow, same fields): the candidate's stored fields, sites narrowed
    to this site."""
    return {
        "id": c.get("plan"), "book": c.get("book"), "ia": c.get("ia"), "file": c.get("file"),
        "title": c.get("title") or c.get("plan"), "label": c.get("label"), "size": c.get("size"),
        "map_box": c.get("map_box"), "sites": [site_id], "cite": c.get("cite"), "url": c.get("url"),
        "view": c.get("view") or False, "ref": c.get("ref"),
    }


def _candidates(site_id, rows, item_cands):
    """The site's candidate pictures keyed by plan id: the plans.json rows naming it plus its item
    candidates, deduped by plan (a plan in both resolves to the plans row: the richer one). File
    order, plans rows first. A picture the item marks dropped (the lead's or the owner's "not this
    structure", fit/matchfit.py skips it too) is no candidate, whichever store names it."""
    dropped = {c["plan"] for c in item_cands if c.get("dropped")}
    out = {}
    for r in rows:
        if r.get("id") and site_id in (r.get("sites") or []) and r["id"] not in dropped:
            out.setdefault(r["id"], r)
    for c in item_cands:
        if c["plan"] not in dropped:
            out.setdefault(c["plan"], _synth_row(c, site_id))
    return out


def _draw_px(row):
    """The drawing's area in page px: the map_box fraction of the page/image size; a row without a
    box is the whole page/image; 0 when no size is stored."""
    size = row.get("size") or [0, 0]
    mb = row.get("map_box")
    if isinstance(mb, (list, tuple)) and len(mb) == 4:
        w = max(0.0, float(mb[2]) - float(mb[0])) * float(size[0])
        h = max(0.0, float(mb[3]) - float(mb[1])) * float(size[1])
        return int(round(w * h))
    return int(float(size[0]) * float(size[1]))


def _best_key(plan, row):
    """True plan over a view, then the larger drawing, then the plan id (stable)."""
    return (bool(row.get("view")), -_draw_px(row), plan)


def _reason(cands):
    """The one word for why the winner won: the only candidate; a true plan (chosen while a view
    exists); the clearest scan (best of several plans); the clearest view (the views win)."""
    if len(cands) == 1:
        return "the only candidate"
    plans = [r for r in cands.values() if not r.get("view")]
    if plans and len(plans) < len(cands):
        return "a true plan"
    if plans:
        return "the clearest scan"
    return "the clearest view"


def _site_records(root):
    """The web/data/sites.json records keyed by id: right_place.site_facts reads the
    site's region and place (a site without a record falls back to its id alone - an
    unknown place, which never flags)."""
    d = _load_json(Path(root) / "web" / "data" / "sites.json")
    ss = d.get("sites") if isinstance(d, dict) else d
    return {s["id"]: s for s in (ss or []) if s.get("id")}


def _place_store(root):
    """The right-place check's stores (tools/right_place.load: the catalog, the book
    index, the book lists - each optional), or None when there is nothing to check
    against: the no-op degrade that keeps a catalog-less tree building exactly as
    before (305's synthetic test)."""
    store = right_place.load(root)
    if not store["catalog"] and not store["index"] and not store["lists"]:
        return None
    return store


def _place_flags(root, store, cands):
    """The right-place check (309) over every candidate the build would emit, computed
    over the pre-mutation maps (a move into a site never feeds that site's own flag
    decision in this build) -> {(site, plan): (facts, reason)}: the namesake
    mismatches only - a picture with an unknown place never flags (the check's
    fail-open rule, tools/right_place.py's docstring)."""
    records = _site_records(root)
    flags = {}
    for sid, cm in cands.items():
        sf = right_place.site_facts(store, records.get(sid) or {"id": sid})
        for plan, row in cm.items():
            facts = right_place.picture_facts(store, plan, row)
            flagged, reason = right_place.check_pairing(sf, facts)
            if flagged:
                flags[(sid, plan)] = (facts, reason)
    return flags


def _item_candidate(item_cands, sid, plan):
    """The item candidate a queue candidate came from (None when it came from
    plans.json): the stored fields are what a move writes into the target's item."""
    return next((c for c in item_cands.get(sid) or [] if c.get("plan") == plan), None)


def _place_entry(plan, row, item_cand, reason):
    """The review-item candidate the check writes for a moved picture (data/review/
    README.md's pass-through extra, the 203a gate_score/why pattern): the candidate's
    stored fields - the item's own entry when it came from one (its pairs and evidence
    travel with it), the row's fields when it came from plans.json - plus the reason.
    Deterministic from the stored fields: a re-run over unchanged inputs writes the
    same bytes."""
    if item_cand is not None:
        e = dict(item_cand)
    else:
        e = {
            "book": row.get("book"), "ia": row.get("ia"), "file": row.get("file"),
            "title": row.get("title") or row.get("label") or plan,
            "label": row.get("label"), "size": row.get("size"), "map_box": row.get("map_box"),
            "cite": row.get("cite"),
            "url": row.get("url") if row.get("url") else
                  ("books/%s/%s" % (row["ia"], row["file"]) if row.get("ia") else None),
            "view": bool(row.get("view")), "ref": row.get("ref"),
        }
    e["plan"] = plan
    e["place_reason"] = reason
    return e


def _apply_flags(root, store, cands, rows, item_cands, hand, built, flags):
    """The disposition of every flag (804), applied to the candidate maps: the candidate
    leaves its source site's queue (a site with no candidate left leaves the queue
    entirely); where the check finds the right site in the catalog (top of
    find_right_site, min_score 0.5) the candidate is moved there - into that site's
    entry when the site is built and in the queue (the row's sites narrowed to it),
    into its review item when it is not - and with no passing site it is upserted
    into the source site's own review item. The target item is never written when it
    already holds the plan: a batch's own entry keeps its pairs and evidence, and a
    flagged candidate the source item already carries is re-flagged and dropped every
    build - the intended steady state, zero churn."""
    eligible = {sid for sid, _n in built if sid not in hand}
    moved = set()
    for (sid, plan) in sorted(flags):
        facts, reason = flags[(sid, plan)]
        row = cands[sid].pop(plan)
        if not cands[sid]:
            del cands[sid]
        item_cand = None if any(row is r for r in rows) else _item_candidate(item_cands, sid, plan)
        right = right_place.find_right_site(store, facts, exclude=sid)
        tid = right[0][1].get("id") if right else None
        if tid is not None and tid in eligible:
            cands.setdefault(tid, {})[plan] = {**row, "sites": [tid]}
            continue
        target = tid or sid
        if (target, plan) in moved:
            continue
        moved.add((target, plan))
        if any(c.get("plan") == plan for c in item_cands.get(target) or []):
            continue
        review.upsert_item(root, target, [_place_entry(plan, row, item_cand, reason)])


def _entry(sid, name, cands):
    """The site's queue entry: its best candidate (plan over view, then drawing area, then
    plan id), the one-word reason, and the whole candidate list in the same order."""
    plan, row = min(cands.items(), key=lambda kv: _best_key(kv[0], kv[1]))
    return {
        "site": sid,
        "name": name,
        "best": {"plan": plan, "reason": _reason(cands),
                 "row": {k: row.get(k) for k in ROW_FIELDS}},
        "candidates": [
            {"plan": p, "title": r.get("title") or p, "book": r.get("book"),
             "view": bool(r.get("view")), "draw_px": _draw_px(r)}
            for p, r in sorted(cands.items(), key=lambda kv: _best_key(kv[0], kv[1]))
        ],
    }


def _entry_propose(root, site_id, plan):
    """The entry's starting placement for the page (307b): fit/propose.propose_for's keys in the
    entry's order {pairs, scale_m_px, rot_deg, scale_source, coarse, note}, "ground" dropped (the
    page derives it from site.lidar, as it already does in fqPlace). None when the proposal cannot
    anchor (no size, no size_m, no stage-B row, no index file) - fail open: the page falls back
    to the three-point flow for that row."""
    try:
        p = _propose.propose_for(site_id, plan, root=root)
    except Exception:
        return None
    return {k: p[k] for k in ("pairs", "scale_m_px", "rot_deg", "scale_source", "coarse", "note")}


def build(root):
    """The queue, ready to serialize: one entry per built site with a candidate and no
    hand fit, ordered by each site's best candidate (plan over view, then drawing area,
    then name). Two-phase (309): the sites' candidate maps are gathered first; the
    right-place check decides every flag over those pre-mutation maps (a move into a
    site can never feed that site's own decision in this build); only then are the
    drops, moves and review upserts applied, and the entries derived from the result.
    Each entry whose best row admits a starting placement then carries the propose key
    (307b: fit/propose.py, fail open - no key when the proposal cannot anchor). Without
    the catalog and book stores the check is a no-op and the build is exactly 305's
    plus the propose key."""
    rows = _plans_rows(root)
    item_cands = _item_candidates(root)
    hand = _hand_sites(root)
    built = _built_sites(root)
    cands = {}
    for sid, name in built:
        if sid in hand:
            continue
        c = _candidates(sid, rows, item_cands.get(sid) or [])
        if c:
            cands[sid] = c
    store = _place_store(root)
    if store is not None:
        flags = _place_flags(root, store, cands)
        _apply_flags(root, store, cands, rows, item_cands, hand, built, flags)
    no_lidar = _no_lidar_sites(root)
    entries = []
    for sid, name in built:
        if sid not in cands or sid in no_lidar:
            continue
        e = _entry(sid, name, cands[sid])
        p = _entry_propose(root, sid, e["best"]["plan"])  # the key lands after "candidates" (the page's order)
        if p is not None:
            e["propose"] = p
        entries.append(e)
    entries.sort(key=lambda e: _best_key(e["best"]["plan"], e["best"]["row"]) + (e["name"],))
    return {"at": datetime.now(timezone.utc).isoformat(), "entries": entries}


def main(argv=None):
    ap = argparse.ArgumentParser(description="The 'Ready to fit' queue (task 305) -> web/data/fit_queue.json.")
    ap.add_argument("--root", default=str(ROOT), help="the data root (default: this checkout)")
    a = ap.parse_args(argv)
    q = build(a.root)
    path = Path(a.root) / "web" / "data" / "fit_queue.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    _save_json(path, q)
    n = len(q["entries"])
    print(f"ready-to-fit queue: {n} site(s) -> {path}")
    for i, e in enumerate(q["entries"][:5], 1):
        print(f"  {i}. {e['name']} ({e['site']}): {e['best']['row'].get('title') or e['best']['plan']} - {e['best']['reason']}")
    if n > 5:
        print(f"  ... {n - 5} more")
    return 0


if __name__ == "__main__":
    sys.exit(main())
