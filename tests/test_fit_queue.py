"""The 'Ready to fit' queue (task 305), part 1: tools/fit_queue.py on a temp tree, no network.

The queue is the built sites with a candidate picture and no hand fit yet, one entry per site,
best candidate first, ordered so the site most worth seeing comes first. The generator reads
web/data/sites.json, the web/data/sites/<id>/ dirs, web/data/plans.json, the data/review/ item
files plus the data/db/platefits/ documents, data/books/index.jsonl for the starting placement,
and the data/catalog/ and data/books/ stores for 309's right-place check (both optional) and
never opens an image, so both tests run it as a subprocess with every socket dead and no
Finder/Amazon data anywhere near: the input contract is checked by construction. Each entry whose best row admits a starting placement carries the propose key
(fit/propose.propose_for: the anchor scale and rotation re-emitted as 3-5 page-px -> lon/lat
pairs), present exactly when the proposal anchors and never otherwise - the page (307b) opens
the map on it.

  test_fit_queue_synthetic   a small hand-built tree where every rule is pinned exactly: the
                             entry set (built + candidate + no hand fit, with the agent-doc,
                             no-picture-item, not-built and hand-doc-by-filename cases), the
                             candidate dedupe (a plan in both plans.json and an item resolves to
                             the plans row), the best-candidate rule (plan over view, then
                             drawing area, then plan id) and its one-word reason, the synthesized
                             row for a candidate whose only plans row names another site, the
                             propose key (bar scale + trustworthy north arrow hand-pinned; ratio
                             without a recorded ppi on the site-size fallback; and the no-propose
                             cases: no size_m, no size, an item candidate with no index row),
                             the site order, and the store's file format (indent=1, no trailing
                             newline, the 13 named row fields in column order).
  test_fit_queue_namesake    309's right-place check (804) on a small hand-built tree (a tiny
                             catalog plus book index/list, the Brighton-vs-Cambridgeshire
                             shape): a caption that places the picture elsewhere flags the pair
                             - the candidate leaves the source site's queue and lands in the
                             right site's entry (built), in the right site's review item
                             (unbuilt) or in the source site's own item (no right site in the
                             catalog, and the site with no candidate left leaves the queue);
                             a site whose county is unknown is never flagged (fail open); a
                             second run over the same tree is byte-identical (zero churn).
  test_fit_queue_real        the real checkout's inputs copied to a temp tree (the 305 ones plus
                             data/books/index.jsonl for the propose, and data/catalog/ and
                             data/books/ so the right-place check runs for real; the site dirs
                             stand in as empty: the rule is existence). The queue is derived
                             independently from the same inputs with the check's own functions
                             (tools/right_place) - including every entry's propose key, against
                             the same propose_for run - and the review-item upserts are
                             re-applied to a second pristine copy through the product's writer
                             and byte-compared against the generator's; none of it pinned to a
                             count (the population moves under the batch tasks, 803 precedent),
                             and every entry's invariants are re-checked. The checkout itself
                             comes out byte-identical.

Part 2 covers the save -> line step (box 3) through the real server with every socket in the
server process dead: a PUT to platefits runs tools/site_done.py for that site in the server's
own process (the drawing lands on the map, the site's square is recoloured, its review item is
resolved), no network.

Part 3 checks the page card (boxes 2 and 4) in a real headless browser, against the served tree,
driven with real clicks the way the owner does: the card on the home view (the next queued
site, its best candidate and the one-word reason, the count), Place (the existing fit tool opens
on that site and that row, its own clicking untouched), back out through the page's own buttons
(the card is unchanged), Skip (the card moves on, Undo skips appears) and Undo. A second run
loads the page with the browser's done map pre-seeded with the first queued site - the exact
key and value the card's own saveFit wrapper writes when a save lands - and shows the card
starting at entry 2. Runs only where Chrome is installed (the recipe is in PITFALLS); the
committed screenshots of the real checkout (book pages loading) live in docs/site_flow/.

Part 4 (task 307bb, the parent 307b's box 3) proves the placement in the same headless
Chrome on a FULL temp tree (the one-site line's home: tools/fit/pipeline present, the
picked entry's book page materialised locally): the card's own done map seeded past the
earlier queue entries puts the card on the pick, 'Place the drawing' opens the placement
on the works, one scripted drag, wheel and shift+wheel move, scale and turn the drawing,
the page's save writes the platefit doc (by: hand, the five placed pairs) from the
placement alone - read back from the temp tree, its own fit agrees with the placed anchor
(1e-3 scale, 0.01 deg) - and the one-site line lands the overlay in the tree; a fresh
run's Cancel brings the earlier overlay back exactly; the write surface is hashed around
the run; pinning on top is checked by hand (307d).
"""
import json
import math
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

import pytest
from PIL import Image

from conftest import copy_web, get, get_json, put_json

ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, str(ROOT / "fit"))
import propose  # noqa: E402  (fit/ has no __init__.py: the site_done.py convention)

# The page's row fields, in web/data/plans.json column order: what openPlan reads.
ROW_FIELDS = ["id", "book", "ia", "file", "title", "label", "size", "map_box",
              "sites", "cite", "url", "view", "ref"]

# The subprocess guard: every socket dies loudly, then the command runs exactly as
# `tools/fit_queue.py --root DIR` would.
GUARD = r"""
import runpy
import socket
import sys

def _dead(*args, **kwargs):
    raise AssertionError("the hermetic run attempted a network connection: %r" % (args,))

socket.socket.connect = _dead
socket.socket.connect_ex = _dead
socket.create_connection = _dead

args = sys.argv[1:] if sys.argv[0] == "-c" else sys.argv
script, *rest = args
sys.argv = [script] + rest
runpy.run_path(script, run_name="__main__")
"""


def _save_json(path, obj):
    """Same convention as the doc store (indent=1, no trailing newline)."""
    path = Path(path)
    tmp = str(path) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1)
    os.replace(tmp, path)


def _row(id_, book, ia, file_, title, label, size, map_box, sites, cite, url, view):
    return [id_, book, ia, file_, title, label, size, map_box, sites, cite, url, view, None]


def _build_synthetic_tree(tmp_path):
    """The hand-built tree: 13 sites in sites.json, 10 built (dirs), 12 plans rows, 5 review
    items, 3 fit documents, 4 stage-B index rows - every queue rule and every propose path
    covered by exactly one case."""
    tree = tmp_path / "tree"
    wd = tree / "web" / "data"
    wd.mkdir(parents=True)
    sites = []
    for i, (s, n) in enumerate([("s-alpha", "Alpha"), ("s-beta", "Beta"), ("s-gamma", "Gamma"),
                                ("s-eta", "Eta"), ("s-kappa", "Kappa"), ("s-view", "View"),
                                ("s-zeta", "Zeta"), ("s-delta", "Delta"), ("s-epsilon", "Epsilon"),
                                ("s-theta", "Theta"), ("s-iota", "Iota"), ("s-else", "Else"),
                                ("s-nope", "Nope")]):
        site = {"id": s, "name": n, "lon": -1.0 - 0.01 * i, "lat": 51.5 + 0.01 * i, "drawings": 0}
        # s-gamma deliberately has no size_m (its no-propose case); s-nope has one (for it the
        # missing piece is the row's size); s-eta's is pinned for the site-size fallback scale
        if s == "s-eta":
            site["size_m"] = [200, 150]
        elif s != "s-gamma":
            site["size_m"] = [100 + 10 * i, 80 + 10 * i]
        sites.append(site)
    _save_json(wd / "sites.json", {"sites": sites})
    for sid in ["s-alpha", "s-beta", "s-gamma", "s-eta", "s-kappa", "s-view",
                "s-zeta", "s-delta", "s-epsilon", "s-nope"]:
        (wd / "sites" / sid).mkdir(parents=True)
    _save_json(wd / "plans.json", {"cols": ROW_FIELDS, "rows": [
        # s-alpha: two plans + one view -> the bigger plan, "a true plan"
        _row("row-a1", "Book A", "ia-a", "p1.jpg", "Alpha plan 1", "Plate A1",
             [1000, 1000], [0.1, 0.1, 0.9, 0.9], ["s-alpha"], "cite-a", None, False),
        _row("row-a2", "Book A", "ia-a", "p2.jpg", "Alpha plan 2", "Plate A2",
             [500, 500], None, ["s-alpha"], "cite-a", None, False),
        _row("row-a3", "Book A", "ia-a", "p3.jpg", "Alpha view", "View A",
             [2000, 2000], None, ["s-alpha"], "cite-a", "media/commons/s-alpha/x.jpg", True),
        # s-beta: a plans view plus item candidates -> the item's plan wins (no plans row for it)
        _row("row-b1", "Book B", "ia-b", "p4.jpg", "Beta view", "View B",
             [800, 600], None, ["s-beta"], "cite-b", "media/commons/s-beta/y.jpg", True),
        # s-eta: one plan; an agent document of its own must not exclude the site
        _row("row-e1", "Book E", "ia-e", "p5.jpg", "Eta plan", "Plate E",
             [1000, 1000], [0, 0, 1, 1], ["s-eta"], "cite-e", None, False),
        # s-gamma: two plans, no view -> the bigger one, "the clearest scan"
        _row("row-g1", "Book G", "ia-g", "p6.jpg", "Gamma plan 1", "Plate G1",
             [400, 300], [0, 0, 0.5, 0.5], ["s-gamma"], "cite-g", None, False),
        _row("row-g2", "Book G", "ia-g", "p7.jpg", "Gamma plan 2", "Plate G2",
             [100, 100], [0, 0, 1, 1], ["s-gamma"], "cite-g", None, False),
        # s-zeta / s-delta: a candidate, but a hand document excludes each (site field / file name)
        _row("row-z1", "Book Z", "ia-z", "p8.jpg", "Zeta plan", "Plate Z",
             [1000, 1000], [0, 0, 1, 1], ["s-zeta"], "cite-z", None, False),
        _row("row-d1", "Book D", "ia-d", "p9.jpg", "Delta plan", "Plate D",
             [1000, 1000], [0, 0, 1, 1], ["s-delta"], "cite-d", None, False),
        # s-theta: a candidate, but the site is not built
        _row("row-t1", "Book T", "ia-t", "p10.jpg", "Theta plan", "Plate T",
             [1000, 1000], [0, 0, 1, 1], ["s-theta"], "cite-t", None, False),
        # id item-k1 names s-else only: s-kappa's item candidate must synthesize its own row
        _row("item-k1", "Book K", "ia-k", "pk.jpg", "Else plan", "Plate K",
             [3000, 2000], [0.5, 0.5, 1.0, 1.0], ["s-else"], "cite-k", None, False),
        # s-nope: no size (and no full_size in its index row) -> no propose
        _row("row-n1", "Book N", "ia-n", "pn.jpg", "Nope plan", "Plate N",
             None, None, ["s-nope"], "cite-n", None, False),
    ]})
    review = tree / "data" / "review"
    review.mkdir(parents=True)
    _save_json(review / "s-beta.json", {"site": "s-beta", "candidates": [
        {"plan": "item-b1", "title": "Beta plan from the item", "url": "media/commons/s-beta/z.jpg",
         "size": [3000, 2000], "map_box": [0.5, 0.5, 1.0, 1.0]},
        {"plan": "item-b2", "title": "Beta faint", "url": "media/commons/s-beta/w.jpg"},
    ], "resolved": None})
    _save_json(review / "s-kappa.item-k1.json", {"site": "s-kappa", "candidates": [
        {"plan": "item-k1", "title": "Kappa plan", "url": "media/commons/s-kappa/a.jpg",
         "size": [3000, 2000], "map_box": [0.5, 0.5, 1.0, 1.0]},
        {"plan": "item-k2", "title": "Kappa faint", "url": "media/commons/s-kappa/b.jpg"},
    ], "resolved": None})
    # resolved items still count: the site stays in the queue (no hand document)
    _save_json(review / "s-view.json", {"site": "s-view", "candidates": [
        {"plan": "item-v1", "title": "View faint", "url": "media/commons/s-view/c.jpg", "view": True},
        {"plan": "item-v2", "title": "View clear", "url": "media/commons/s-view/d.jpg",
         "view": True, "size": [100, 100]},
    ], "resolved": {"doc": "s-view.item-v9", "at": "2026-01-01T00:00:00+00:00"}})
    # a no-picture item is not a candidate
    _save_json(review / "s-epsilon.json", {"site": "s-epsilon", "candidates": [],
                                           "no_picture_found": {"searched": "web/data/plans.json",
                                                                "at": "2026-01-01T00:00:00+00:00"}})
    # an unbuilt site's item candidate never enters
    _save_json(review / "s-iota.json", {"site": "s-iota",
                                       "candidates": [{"plan": "item-i1", "title": "Iota candidate",
                                                       "url": "media/commons/s-iota/e.jpg"}],
                                       "resolved": None})
    # stage-B index rows (data/books/index.jsonl): the propose's inputs for the book rows
    books = tree / "data" / "books"
    books.mkdir(parents=True)
    (books / "index.jsonl").write_text("".join(json.dumps(r) + "\n" for r in [
        # s-alpha: bar span + trustworthy north arrow -> the bar scale over the bar's width
        {"id": "row-a1", "book": "Book A", "scale_text": "0 100 200 300 Feet",
         "blank_boxes": [{"kind": "scale_bar", "box": [0.15, 0.6, 0.85, 0.62]}],
         "north_angle_deg": 20, "north_arrow": True,
         "map_box": [0.1, 0.1, 0.9, 0.9], "full_size": [1000, 1000]},
        # s-eta: ratio, but Book E's ppi is not recorded -> the site-size fallback
        {"id": "row-e1", "book": "Book E", "scale_text": "500 Feet to the Inch.",
         "map_box": [0, 0, 1, 1], "full_size": [1000, 1000]},
        # s-gamma: no scale text (and the site has no size_m) -> no propose
        {"id": "row-g1", "book": "Book G", "map_box": [0, 0, 0.5, 0.5], "full_size": [400, 300]},
        # s-nope: no scale text and no full_size (the plans row's size is null too) -> no propose
        {"id": "row-n1", "book": "Book N"},
    ]), encoding="utf-8")
    pf = tree / "data" / "db" / "platefits"
    pf.mkdir(parents=True)
    _save_json(pf / "s-eta.row-e1.json", {"site": "s-eta", "plan": "row-e1", "by": "agent"})
    _save_json(pf / "s-zeta.row-z1.json", {"site": "s-zeta", "plan": "row-z1", "by": "hand"})
    # no `site` field: the file-name prefix (before the first dot) is the site
    _save_json(pf / "s-delta.row-d1.json", {"plan": "row-d1", "by": "hand"})
    return tree


def _run_generator(tree):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    return subprocess.run([sys.executable, "-c", GUARD, str(ROOT / "tools" / "fit_queue.py"),
                           "--root", str(tree)],
                          cwd=str(ROOT), env=env, capture_output=True, timeout=120)


def _reason_of(cands):
    """The contract's one-word reason, from the candidate mix (the synthetic test pins the
    values; this restates the contract for the derived real-data check)."""
    if len(cands) == 1:
        return "the only candidate"
    n_plans = sum(1 for c in cands if not c["view"])
    if 0 < n_plans < len(cands):
        return "a true plan"
    if n_plans:
        return "the clearest scan"
    return "the clearest view"


def test_fit_queue_synthetic(tmp_path):
    tree = _build_synthetic_tree(tmp_path)
    proc = _run_generator(tree)
    out = proc.stdout.decode("utf-8")
    err = proc.stderr.decode("utf-8")
    assert proc.returncode == 0, out + err
    assert err == ""
    assert out.splitlines()[0] == f"ready-to-fit queue: 7 site(s) -> {tree / 'web' / 'data' / 'fit_queue.json'}"

    raw = (tree / "web" / "data" / "fit_queue.json").read_bytes()
    q = json.loads(raw)
    # the store's file format: indent=1, no trailing newline
    assert raw == json.dumps(q, indent=1).encode("utf-8")
    assert not raw.endswith(b"\n")
    datetime.fromisoformat(q["at"])

    entries = q["entries"]
    # built + candidate + no hand fit, in the contract's order
    assert [e["site"] for e in entries] == ["s-beta", "s-kappa", "s-eta", "s-alpha", "s-gamma",
                                            "s-nope", "s-view"]
    by = {e["site"]: e for e in entries}

    # s-beta: the item's plan (no plans row for it) beats the plans row's view; the row is
    # synthesized from the candidate's stored fields, sites narrowed to the site
    e = by["s-beta"]
    assert [c["plan"] for c in e["candidates"]] == ["item-b1", "item-b2", "row-b1"]
    assert [c["draw_px"] for c in e["candidates"]] == [1500000, 0, 480000]
    assert [c["view"] for c in e["candidates"]] == [False, False, True]
    assert e["best"]["plan"] == "item-b1" and e["best"]["reason"] == "a true plan"
    assert e["best"]["row"] == {
        "id": "item-b1", "book": None, "ia": None, "file": None,
        "title": "Beta plan from the item", "label": None, "size": [3000, 2000],
        "map_box": [0.5, 0.5, 1.0, 1.0], "sites": ["s-beta"], "cite": None,
        "url": "media/commons/s-beta/z.jpg", "view": False, "ref": None,
    }

    # s-kappa: its item candidate shares its plan id with a plans row that names another
    # site - the row is synthesized, not the other site's row
    e = by["s-kappa"]
    assert e["best"]["plan"] == "item-k1" and e["best"]["reason"] == "the clearest scan"
    assert e["best"]["row"]["title"] == "Kappa plan"
    assert e["best"]["row"]["sites"] == ["s-kappa"]
    assert e["best"]["row"]["size"] == [3000, 2000]

    # s-eta: the agent document does not exclude
    e = by["s-eta"]
    assert e["best"]["plan"] == "row-e1" and e["best"]["reason"] == "the only candidate"
    assert e["best"]["row"]["sites"] == ["s-eta"]  # the plans row, verbatim
    assert e["best"]["row"]["map_box"] == [0, 0, 1, 1]

    # s-alpha: a true plan over the (bigger) view, then drawing area
    e = by["s-alpha"]
    assert [c["plan"] for c in e["candidates"]] == ["row-a1", "row-a2", "row-a3"]
    assert [c["draw_px"] for c in e["candidates"]] == [640000, 250000, 4000000]
    assert e["best"]["plan"] == "row-a1" and e["best"]["reason"] == "a true plan"

    # s-gamma: two plans, no view
    e = by["s-gamma"]
    assert [c["plan"] for c in e["candidates"]] == ["row-g1", "row-g2"]
    assert [c["draw_px"] for c in e["candidates"]] == [30000, 10000]
    assert e["best"]["plan"] == "row-g1" and e["best"]["reason"] == "the clearest scan"

    # s-view: all views, even resolved, and the site's view-best entry sorts after every
    # plan-best site no matter its area
    e = by["s-view"]
    assert [c["plan"] for c in e["candidates"]] == ["item-v2", "item-v1"]
    assert [c["draw_px"] for c in e["candidates"]] == [10000, 0]
    assert e["best"]["plan"] == "item-v2" and e["best"]["reason"] == "the clearest view"

    # the starting placement (the propose key): the bar scale over the bar's width, at the
    # trustworthy arrow's rotation (hand-pinned: 300 ft = 91.44 m over 700 px)
    e = by["s-alpha"]
    p = e["propose"]
    assert list(p.keys()) == ["pairs", "scale_m_px", "rot_deg", "scale_source", "coarse", "note"]
    assert p["scale_m_px"] == 0.1306
    assert p["rot_deg"] == 20.0 and p["scale_source"] == "bar" and p["coarse"] is False
    assert "scale from the scale bar" in p["note"]
    assert p["pairs"] == propose.propose_for("s-alpha", "row-a1", root=tree)["pairs"]
    # the panel geometry: the 4 corners plus the centre, in the row's size frame
    assert [(q[0], q[1]) for q in p["pairs"]] == [(100.0, 100.0), (900.0, 100.0),
                                                  (900.0, 900.0), (100.0, 900.0),
                                                  (500.0, 500.0)]

    # the ratio without a recorded ppi takes the site-size fallback: 200 m over the whole page
    e = by["s-eta"]
    p = e["propose"]
    assert p["scale_m_px"] == 0.2 and p["rot_deg"] == 0.0
    assert p["scale_source"] == "picture_size" and p["coarse"] is True
    assert "ppi not recorded" in p["note"]
    assert p["pairs"] == propose.propose_for("s-eta", "row-e1", root=tree)["pairs"]

    # the no-propose cases: no size_m, no size, and an item candidate with no index row
    for sid in ["s-gamma", "s-nope", "s-beta", "s-kappa", "s-view"]:
        assert "propose" not in by[sid], sid

    # the exclusions: hand documents (both field shapes), no candidate, not built
    for sid in ["s-zeta", "s-delta", "s-epsilon", "s-theta", "s-iota", "s-else"]:
        assert sid not in by


def _h(p):
    return Path(p).read_bytes()


def _derive_with_check(root):
    """309's right-place check re-derived independently from the checkout's own inputs:
    the same candidate maps the build gathers, the same flags over the PRE-MUTATION maps,
    then the same disposition (drop, move into the built right site, upsert into the
    right site's item or the source site's own item) - tools/right_place's committed API
    for the check itself, the 804 wiring's orchestration restated here. -> (the expected
    queue entries in the build's own order, {site: [item entries in processing order]})
    or (None, {}) for the no-op degrade (no stores: the build is exactly 305's)."""
    sys.path.insert(0, str(Path(root) / "tools"))
    sys.path.insert(0, str(Path(root) / "fit"))
    import fit_queue
    import right_place

    rows = fit_queue._plans_rows(root)
    item_cands = fit_queue._item_candidates(root)
    hand = fit_queue._hand_sites(root)
    built = fit_queue._built_sites(root)
    records = {}
    d = json.loads((Path(root) / "web" / "data" / "sites.json").read_text())
    for s in (d.get("sites") if isinstance(d, dict) else d) or []:
        if s.get("id"):
            records[s["id"]] = s
    cands = {}
    for sid, name in built:
        if sid not in hand:
            c = fit_queue._candidates(sid, rows, item_cands.get(sid) or [])
            if c:
                cands[sid] = c
    store = right_place.load(str(root))
    if not store["catalog"] and not store["index"] and not store["lists"]:
        return None, {}
    flags = {}
    for sid, cm in cands.items():
        sf = right_place.site_facts(store, records.get(sid) or {"id": sid})
        for plan, row in cm.items():
            f = right_place.picture_facts(store, plan, row)
            flagged, reason = right_place.check_pairing(sf, f)
            if flagged:
                flags[(sid, plan)] = (f, reason)
    names = {sid: name for sid, name in built}
    after = {sid: dict(cm) for sid, cm in cands.items()}
    eligible = {sid for sid, _ in built if sid not in hand}
    upserts = {}
    moved = set()
    for (sid, plan) in sorted(flags):
        f, reason = flags[(sid, plan)]
        row = after[sid].pop(plan)
        if not after[sid]:
            after.pop(sid)
        item_cand = None if any(row is r for r in rows) else fit_queue._item_candidate(item_cands, sid, plan)
        right = right_place.find_right_site(store, f, exclude=sid)
        tid = right[0][1].get("id") if right else None
        if tid is not None and tid in eligible:
            after.setdefault(tid, {})[plan] = {**row, "sites": [tid]}
            continue
        target = tid or sid
        if (target, plan) in moved:
            continue
        moved.add((target, plan))
        if any(c.get("plan") == plan for c in item_cands.get(target) or []):
            continue
        upserts.setdefault(target, []).append(fit_queue._place_entry(plan, row, item_cand, reason))
    # the owner's 2026-10-13 rule: sites.json lidar: false never enters the queue
    ss = json.loads((root / "web" / "data" / "sites.json").read_text())
    ss = ss.get("sites") if isinstance(ss, dict) else ss
    no_lidar = {s["id"] for s in ss if s.get("lidar") is False}
    entries = []
    for sid in after:
        if sid in no_lidar:
            continue
        e = fit_queue._entry(sid, names[sid], after[sid])
        p = fit_queue._entry_propose(root, sid, e["best"]["plan"])  # the 307b key: same run, same inputs
        if p is not None:
            e["propose"] = p
        entries.append(e)
    entries.sort(key=lambda e: fit_queue._best_key(e["best"]["plan"], e["best"]["row"]) + (e["name"],))
    return entries, upserts


def test_fit_queue_real(tmp_path):
    """The generator on a copy of the real checkout's inputs (the population is derived,
    never pinned: it moves under the batch tasks). data/books/index.jsonl is copied too,
    so the propose can anchor, and data/catalog/ and data/books/ too, so 309's
    right-place check runs for real: the queue is compared against an independent
    re-derivation through the check's own functions (tools/right_place) and each entry's
    propose key against the same propose_for run; the review-item upserts are re-applied
    to a second pristine copy through the product's writer and byte-compared against the
    generator's. The checkout itself comes out byte-identical."""
    raw_in = [ROOT / "web" / "data" / "sites.json", ROOT / "web" / "data" / "plans.json",
              ROOT / "data" / "catalog" / "sites.jsonl", ROOT / "data" / "books" / "index.jsonl"]
    before = {_h(p) for p in raw_in} | {_h(p) for p in (ROOT / "data" / "review").iterdir() if p.is_file()} \
             | {_h(p) for p in (ROOT / "data" / "db" / "platefits").iterdir() if p.is_file()} \
             | {_h(p) for p in (ROOT / "data" / "books" / "lists").iterdir() if p.is_file()}

    tree = tmp_path / "tree"
    wd = tree / "web" / "data"
    wd.mkdir(parents=True)
    shutil.copy2(raw_in[0], wd / "sites.json")
    shutil.copy2(raw_in[1], wd / "plans.json")
    # the built dirs stand in as empty: the rule is the directory's existence
    for d in (ROOT / "web" / "data" / "sites").iterdir():
        if d.is_dir():
            (wd / "sites" / d.name).mkdir(parents=True)
    (tree / "data" / "books").mkdir(parents=True)
    shutil.copy2(raw_in[3], tree / "data" / "books" / "index.jsonl")  # the stage-B fields the propose reads
    # the right-place check's stores (without them the build degrades to 305's no-op)
    shutil.copytree(ROOT / "data" / "catalog", tree / "data" / "catalog")
    shutil.copytree(ROOT / "data" / "books" / "lists", tree / "data" / "books" / "lists")
    shutil.copytree(ROOT / "data" / "review", tree / "data" / "review")
    shutil.copytree(ROOT / "data" / "db" / "platefits", tree / "data" / "db" / "platefits")

    proc = _run_generator(tree)
    out = proc.stdout.decode("utf-8")
    err = proc.stderr.decode("utf-8")
    assert proc.returncode == 0, out + err
    assert err == ""

    q = json.loads((tree / "web" / "data" / "fit_queue.json").read_text())
    entries = q["entries"]
    assert entries, "the queue must not be empty: the owner has sites to fit"

    # the queue, derived independently with the check (or 305's entry set, when the
    # stores are absent and the check is the no-op degrade)
    expected, upserts = _derive_with_check(ROOT)
    if expected is not None:
        assert entries == expected, "the queue differs from the check's own derivation"
        # the review-item upserts: re-apply the derived entries to a second pristine
        # copy through the product's writer, then byte-compare every item file
        sys.path.insert(0, str(ROOT / "fit"))
        import review
        derive = tmp_path / "derive"
        shutil.copytree(ROOT / "data" / "review", derive / "data" / "review")
        for site, es in upserts.items():
            for e in es:
                review.upsert_item(derive, site, [e])
        gen_items = {p.name: p.read_bytes() for p in (tree / "data" / "review").glob("*.json")}
        drv_items = {p.name: p.read_bytes() for p in (derive / "data" / "review").glob("*.json")}
        assert set(gen_items) == set(drv_items), \
            "item files: %r vs %r" % (sorted(set(gen_items) - set(drv_items)),
                                     sorted(set(drv_items) - set(gen_items)))
        for name in gen_items:
            assert gen_items[name] == drv_items[name], name
    else:
        # no stores: the entry set, derived from the four 305 inputs
        sids = {s["id"] for s in json.loads(raw_in[0].read_text())["sites"]}
        built = {sid for sid in sids if (ROOT / "web" / "data" / "sites" / sid).is_dir()}
        cols = {c: i for i, c in enumerate(json.loads(raw_in[1].read_text())["cols"])}
        rows = [{k: r[i] for k, i in cols.items()} for r in json.loads(raw_in[1].read_text())["rows"]]
        row_sites = {sid for r in rows for sid in (r.get("sites") or []) if sid}
        item_sites = set()
        for p in sorted((ROOT / "data" / "review").glob("*.json")):
            it = json.loads(p.read_text())
            if it.get("site") and any(c.get("plan") for c in (it.get("candidates") or [])):
                item_sites.add(it["site"])
        hand = set()
        for p in (ROOT / "data" / "db" / "platefits").glob("*.json"):
            d = json.loads(p.read_text())
            if d.get("by") == "hand":
                hand.add(d.get("site") or p.name[:-5].split(".", 1)[0])
        expected_set = (built & (row_sites | item_sites)) - hand
        assert {e["site"] for e in entries} == expected_set
        assert len(entries) == len(expected_set)

    # every entry's invariants
    for e in entries:
        cands = e["candidates"]
        assert cands and e["best"]["plan"] == cands[0]["plan"]
        assert e["best"]["reason"] == _reason_of(cands)
        assert list(e["best"]["row"].keys()) == ROW_FIELDS
        assert e["best"]["row"]["id"] == e["best"]["plan"]
        if e["best"]["row"]["sites"] != [e["site"]]:
            assert e["site"] in e["best"]["row"]["sites"]
        areas = [c["draw_px"] for c in cands]
        assert all(a >= 0 for a in areas)

    # the starting placement: present exactly when the same propose_for run on the same tree
    # anchors (derived per entry, never a pinned count), equal to it, six keys in order.
    # The floor guards against a silently broken propose (it would fail identically in both
    # processes); every current entry anchors.
    anchored = 0
    for e in entries:
        try:
            expect = propose.propose_for(e["site"], e["best"]["plan"], root=tree)
        except Exception:
            assert "propose" not in e, e["site"]
            continue
        anchored += 1
        p = e["propose"]
        assert list(p.keys()) == ["pairs", "scale_m_px", "rot_deg", "scale_source",
                                  "coarse", "note"]
        assert p == {k: expect[k] for k in ("pairs", "scale_m_px", "rot_deg",
                                            "scale_source", "coarse", "note")}
        assert len(p["pairs"]) == 5 and all(len(q) == 4 for q in p["pairs"])
        assert p["scale_m_px"] is not None
    assert anchored, "no entry anchored: propose is broken the same way in both processes"
    keys = [(bool(e["best"]["row"]["view"]),
             -next(c["draw_px"] for c in e["candidates"] if c["plan"] == e["best"]["plan"]),
             e["best"]["plan"], e["name"]) for e in entries]  # the generator's _best_key + name
    assert keys == sorted(keys)

    # the checkout itself is untouched
    after = {_h(p) for p in raw_in} | {_h(p) for p in (ROOT / "data" / "review").iterdir() if p.is_file()} \
            | {_h(p) for p in (ROOT / "data" / "db" / "platefits").iterdir() if p.is_file()} \
            | {_h(p) for p in (ROOT / "data" / "books" / "lists").iterdir() if p.is_file()}
    assert after == before


# ---------------------------------------------------------------------------
# Part 1b: 309's right-place check (task 804): the queue build never pairs a
# picture with a namesake site. A small hand-built tree with a tiny catalog and
# book stores pins every disposition exactly, and a second run over the same
# tree must be byte-identical (the steady state: the same flags, the upserts
# skipped, zero churn).

NAMESAKE_IA = "allcroft1908book"  # the book index/lists key; the book is in right_place.BOOK_SCOPE


def _namesake_row(id_, file_, title, label, sites):
    return [id_, "allcroft_1908", NAMESAKE_IA, file_, title, label,
            [1000, 1000], None, sites, "cite", None, False, None]


def _namesake_item(site, plan, file_, label, title, reason):
    """The review item the check's upsert writes for a moved plans-origin candidate:
    the row's stored fields, the url's books/<ia>/<file> fallback, and the reason."""
    return {"site": site, "candidates": [
        {"book": "allcroft_1908", "ia": NAMESAKE_IA, "file": file_, "title": title,
         "label": label, "size": [1000, 1000], "map_box": None, "cite": "cite",
         "url": "books/%s/%s" % (NAMESAKE_IA, file_), "view": False, "ref": None,
         "plan": plan, "place_reason": reason}],
        "no_picture_found": None, "resolved": None}


def _build_namesake_tree(tmp_path):
    """Five built sites, four book rows, six catalog records - one namesake case per
    rule (the Brighton-vs-Cambridgeshire shape, scaled down): (a) a caption that
    places the picture in another county flags the pair, and with the right site
    built the candidate moves into its entry; (b) with the right site unbuilt its
    review item gains the candidate with the reason; (c)/(e) with no right site in
    the catalog the source site's own item gains it and the site (its only
    candidate flagged) leaves the queue; (d) a site whose county is in neither
    CLASSIC_UNITS nor IDENTITY is never flagged (fail open)."""
    tree = tmp_path / "namesake"
    wd = tree / "web" / "data"
    wd.mkdir(parents=True)
    sites = [
        {"id": s, "name": n, "region": "England"}
        for s, n in [("dyke-cambs-q1", "Devil's Dyke"),
                     ("dyke-sussex-q2", "Devil's Dyke Camp"),
                     ("dyke2-cambs-q10", "Bokerley Dyke"),
                     ("dyke3-cambs-q20", "Wickham Camp"),
                     ("dyke4-unknown-q30", "Wickham Camp")]
    ]
    _save_json(wd / "sites.json", {"sites": sites})
    for s in sites:
        (wd / "sites" / s["id"]).mkdir(parents=True)
    _save_json(wd / "plans.json", {"cols": ROW_FIELDS, "rows": [
        _namesake_row("p1", "p217.jpg", "devils dyke camp", "Fig 217", ["dyke-cambs-q1"]),
        _namesake_row("p2", "p218.jpg", "bokerley dyke", "Fig 218", ["dyke2-cambs-q10"]),
        _namesake_row("p3", "p219.jpg", "wickham camp", "Fig 219", ["dyke3-cambs-q20"]),
        _namesake_row("p4", "p220.jpg", "wickham camp in kent", "Fig 220", ["dyke4-unknown-q30"]),
    ]})
    cat = tree / "data" / "catalog"
    cat.mkdir(parents=True)
    with open(cat / "sites.jsonl", "w") as f:
        for r in [
            {"id": "dyke-cambs-q1", "qid": "Q1", "name": "Devil's Dyke", "region": "england",
             "admin": {"county": "Cambridgeshire"}},
            # the built right site of (a): Brighton resolves to sussex, West Sussex is sussex
            {"id": "dyke-sussex-q2", "qid": "Q2", "name": "Devil's Dyke Camp", "region": "england",
             "admin": {"parish": "Brighton", "county": "West Sussex"}},
            {"id": "dyke2-cambs-q10", "qid": "Q10", "name": "Bokerley Dyke", "region": "england",
             "admin": {"county": "Cambridgeshire"}},
            # the right site of (b): in the catalog, not in sites.json (unbuilt)
            {"id": "dyke2-sussex-q11", "qid": "Q11", "name": "Bokerley Dyke", "region": "england",
             "admin": {"parish": "Hove", "county": "West Sussex"}},
            {"id": "dyke3-cambs-q20", "qid": "Q20", "name": "Wickham Camp", "region": "england",
             "admin": {"county": "Cambridgeshire"}},
            # (d): the county is in neither CLASSIC_UNITS nor IDENTITY - the site is unknown
            {"id": "dyke4-unknown-q30", "qid": "Q30", "name": "Wickham Camp", "region": "england",
             "admin": {"county": "Xshire"}},
        ]:
            f.write(json.dumps(r) + "\n")
    books = tree / "data" / "books"
    (books / "lists").mkdir(parents=True)
    with open(books / "index.jsonl", "w") as f:
        for id_, fig, title in [("p1", "217", "DEVILS DYKE"), ("p2", "218", "BOKERLEY"),
                                ("p3", "219", "WICKHAM"), ("p4", "220", "WICKHAM")]:
            f.write(json.dumps({"id": id_, "book": "allcroft_1908", "ia_id": NAMESAKE_IA,
                                "fig": fig, "title": title, "place": None,
                                "site_names": []}) + "\n")
    _save_json(books / "lists" / (NAMESAKE_IA + ".json"),
               {"figures": [
                   {"fig": "217", "title": "The Devil's Dyke Camp, near Brighton"},
                   {"fig": "218", "title": "Bokerley Dyke, near Hove"},
                   {"fig": "219", "title": "Wickham Camp, near Hove"},
                   {"fig": "220", "title": "Wickham Camp, in Kent"},
               ]})
    return tree


def test_fit_queue_namesake(tmp_path):
    """Every disposition of 309's right-place check, pinned on a small tree (the
    Brighton-vs-Cambridgeshire shape): (a) the flagged candidate leaves its source
    site's queue and lands in the built right site's entry with sites narrowed to it;
    (b) with the right site unbuilt its review item gains the candidate with the
    reason; (c)/(e) with no passing right site the source site's own item gains it
    and the site leaves the queue (its only candidate flagged); (d) an unknown-county
    site is never flagged (fail open). The item files are byte-pinned (the move of
    (a) wrote nothing for its source); a second run over the same tree is
    byte-identical (zero churn). No network: the guard kills every socket."""
    tree = _build_namesake_tree(tmp_path)
    proc = _run_generator(tree)
    out = proc.stdout.decode("utf-8")
    err = proc.stderr.decode("utf-8")
    assert proc.returncode == 0, out + err
    assert err == ""
    assert out.splitlines()[0] == \
        f"ready-to-fit queue: 2 site(s) -> {tree / 'web' / 'data' / 'fit_queue.json'}"

    q = json.loads((tree / "web" / "data" / "fit_queue.json").read_text())
    entries = q["entries"]
    # (a) + (d): the moved candidate lands in the built right site's entry (its
    # source emptied and gone); the unknown-county site keeps its contradictory candidate
    assert [e["site"] for e in entries] == ["dyke-sussex-q2", "dyke4-unknown-q30"]
    e2, e30 = entries
    assert [c["plan"] for c in e2["candidates"]] == ["p1"]
    assert e2["best"]["plan"] == "p1" and e2["best"]["reason"] == "the only candidate"
    assert e2["best"]["row"]["sites"] == ["dyke-sussex-q2"]
    assert e30["best"]["plan"] == "p4" and e30["best"]["reason"] == "the only candidate"
    for gone in ("dyke-cambs-q1", "dyke2-cambs-q10", "dyke3-cambs-q20"):
        assert gone not in {e["site"] for e in entries}

    # (b) + (c)/(e): exactly two item files; the unbuilt right site's item and the
    # source site's own item, each byte-pinned with the check's reason string
    raws = {p.name: p.read_bytes() for p in sorted((tree / "data" / "review").glob("*.json"))}
    assert list(raws) == ["dyke2-sussex-q11.p2.json", "dyke3-cambs-q20.p3.json"]
    for name, plan, file_, label, title in [
            ("dyke2-sussex-q11.p2.json", "p2", "p218.jpg", "Fig 218", "bokerley dyke"),
            ("dyke3-cambs-q20.p3.json", "p3", "p219.jpg", "Fig 219", "wickham camp")]:
        site = name.rsplit(".", 2)[0]
        expected = _namesake_item(site, plan, file_, label, title,
                                  "same name, other place: near Hove vs Cambridgeshire")
        assert raws[name] == json.dumps(expected, indent=1).encode("utf-8"), name

    # (f) a second run over the same tree: identical queue (apart from `at`) and
    # byte-identical item files - the upserts are skipped, zero churn
    queue1 = (tree / "web" / "data" / "fit_queue.json").read_bytes()
    proc = _run_generator(tree)
    assert proc.returncode == 0 and proc.stderr == b""
    queue2 = (tree / "web" / "data" / "fit_queue.json").read_bytes()
    assert json.loads(queue2)["entries"] == json.loads(queue1)["entries"]
    raws2 = {p.name: p.read_bytes() for p in sorted((tree / "data" / "review").glob("*.json"))}
    assert raws2 == raws


# ---------------------------------------------------------------------------
# Part 2: the save -> one-site line (task 305, box 3): a PUT to platefits runs
# tools/site_done.py for that site in the server's own process. No network: every
# socket in the server process is dead (the guard names the call that tried), the
# line's model is None, and the picture is read from the tree's own data/raw copy.

AT = "2026-10-12T00:00:00.000Z"  # the owner's save timestamp; the line records it verbatim


def _item_of(root, site):
    """The site's review item in a tree, keyed by its `site` field (data/review/README.md).
    -> (path, item) or (None, None)."""
    d = Path(root) / "data" / "review"
    if not d.is_dir():
        return None, None
    for p in sorted(d.glob("*.json")):
        item = json.loads(p.read_text())
        if item.get("site") == site:
            return p, item
    return None, None


def _rows_naming(root, site):
    """The plans.json rows that name the site (the line's candidate rows)."""
    d = json.loads((Path(root) / "web" / "data" / "plans.json").read_text())
    cols = {c: i for i, c in enumerate(d["cols"])}
    return [{k: r[i] for k, i in cols.items()} for r in d["rows"] if site in (r[cols["sites"]] or [])]


def _review_items():
    """The checkout's review items keyed by their `site` field (data/review/README.md)."""
    items = {}
    for p in (ROOT / "data" / "review").glob("*.json"):
        it = json.loads(p.read_text())
        if it.get("site"):
            items[it["site"]] = it
    return items


def _line_eligible(e, it):
    """The one-site line's constraints on a queue entry (the part 2 pick and the part 4
    placement pick both require them): a book row whose page is in this checkout's data/raw
    (the line reads it locally), an unresolved review item for the site carrying that row as
    a candidate with the page's save-floor pairs (the line's export resolves it by the saved
    doc), and no platefits documents for the site yet (the line then builds exactly one new
    overlay). -> the site's uncovered rows (a row naming it, no doc, no item candidate),
    or None when any constraint fails."""
    row = e["best"]["row"]
    ia, file_ = row.get("ia"), row.get("file")
    if not (ia and file_):
        return None  # a book row: the page's save needs ia/file, and the line reads the page locally
    if not (ROOT / "data" / "raw" / "books" / ia / "full" / file_).is_file():
        return None  # no local page: the line would need the network
    if not it or (it.get("resolved") or {}).get("doc"):
        return None  # an unresolved item, so the line's export resolves it by the saved doc
    cand = next((c for c in it.get("candidates") or [] if c.get("plan") == row["id"]), None)
    if not cand or len(cand.get("pairs") or []) < 3:
        return None  # the page's save floor for a similarity fit
    docs = {json.loads(p.read_text()).get("plan")
            for p in (ROOT / "data" / "db" / "platefits").glob("*.json")
            if p.name.startswith(e["site"] + ".")}
    if docs:
        return None  # an existing doc would make the line build a second overlay
    item_plans = {c.get("plan") for c in it["candidates"]}
    return [r["id"] for r in _rows_naming(ROOT, e["site"])
            if r["id"] not in docs and r["id"] not in item_plans]


def _pick_site():
    """The first queue entry the line test can use: a book row whose page is in this checkout's
    data/raw (the line reads it locally), whose site's review item is unresolved and carries that
    row as a candidate with the page's save-floor pairs, and which has no platefits documents yet
    (the line then builds exactly one new overlay: drawings changes by one, the open count drops
    by one, and the item resolves by the saved doc) - _line_eligible. The pick prefers a site
    with at least one uncovered row (a row naming it, no doc, no item candidate), so the
    no-matcher path runs and lands in the item as "no matcher on this machine"; a pick without
    one skips that assertion. Derived, never pinned (803: the population moves under the batch tasks).
    -> (entry, item, uncovered) or None."""
    q = json.loads((ROOT / "web" / "data" / "fit_queue.json").read_text())
    items = _review_items()
    picks = []
    for e in q["entries"]:
        it = items.get(e["site"])
        uncovered = _line_eligible(e, it)
        if uncovered is None:
            continue
        picks.append((e, it, uncovered))
    if not picks:
        return None
    picks.sort(key=lambda p: not p[2])  # an uncovered row first: the no-matcher path runs
    return picks[0]


@pytest.fixture(scope="module")
def line_served(tmp_path_factory):
    """The real server on an ephemeral port over a FULL copy of this checkout: conftest's served
    tree strips tools/, fit/ and pipeline/ (the worker dies on the import there, which
    test_review pins); this copy keeps them, so a platefits PUT really runs the one-site line
    in-process. Every socket in the server process is dead (the guard's AssertionError names the
    call): the line is network-free by contract. In the checkout the per-site web/data/sites dirs
    are mostly symlinks into the shared store (a few hand-fit ones are real files); the copy above
    materializes them into the tree, so the line's writes can only land in the tree (the test
    re-checks below that nothing in the picked site's dir is a link). The server's stdout is pulled
    by its own reader thread (a blocking readline: a select() on the buffered reader's fd misses
    lines the reader has already pulled, and a whole-process stall under parallel-agent load can
    swallow a short window, so the test gives the line 180 s - it measures ~23 s here).
    -> {"base", "tree", "proc", "entry", "item", "size", "uncovered", "out"}"""
    pick = _pick_site()
    assert pick, ("no queue entry with a local book page and an unresolved item carrying it "
                  "with save-floor pairs - the save -> line test is vacuous")
    entry, item, uncovered = pick
    row = entry["best"]["row"]
    tree = tmp_path_factory.mktemp("awline")
    copy_web(tree, real={entry["site"]})
    for d in ("server", "tools", "fit", "pipeline"):
        shutil.copytree(str(ROOT / d), str(tree / d))

    def ignore(d, names):  # data/raw (book scans) and the gitignored elevation grids (data/sites/*/dem.npy)
        return [n for n in names if os.path.join(d, n) == str(ROOT / "data" / "raw") or n.endswith((".npy", ".npz"))]

    shutil.copytree(str(ROOT / "data"), str(tree / "data"), ignore=ignore)
    # the one page the line needs: a real file under the tree's own data/raw (the checkout's data/raw
    # is a symlink into the shared store, and the test must not write through it)
    img = ROOT / "data" / "raw" / "books" / row["ia"] / "full" / row["file"]
    dst = tree / "data" / "raw" / "books" / row["ia"] / "full" / row["file"]
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(img), dst)
    proc = subprocess.Popen([sys.executable, "-c", GUARD, "server/serve.py", "--port", "0"],
                            cwd=str(tree), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out = []

    def _reader():
        for line in proc.stdout:  # blocking reads in their own thread: no select, no prefetch gap
            out.append(line.rstrip("\n"))

    threading.Thread(target=_reader, daemon=True).start()
    url = None
    deadline = time.time() + 90
    while time.time() < deadline and proc.poll() is None:
        for line in list(out):
            m = re.match(r"(?:Resurface|Ancient Works) on (\S+)", line)
            if m:
                url = m.group(1)
                break
        if url:
            break
        time.sleep(0.2)
    if not url:
        proc.kill()
        raise AssertionError("server did not report its address (startup: %r)" % out[-10:])
    deadline = time.time() + 30
    while time.time() < deadline:
        try:
            if get(url + "/")[0] == 200:
                break
        except OSError:
            time.sleep(0.2)
    else:
        proc.kill()
        raise AssertionError("server is not answering at " + url)
    yield {"base": url.rstrip("/"), "tree": Path(tree), "proc": proc,
           "entry": entry, "item": item, "size": Image.open(dst).size,
           "uncovered": uncovered, "out": out}
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()


def test_save_runs_the_one_site_line(line_served):
    """Box 3: when the owner saves a fit, the server runs the one-site line (tools/site_done.py)
    for that site in its own process: the drawing is on the map (depictions.json and the webps),
    the site's square is recoloured (sites.json's drawings) and the site's review item is resolved
    (write-once {doc, at}) - without any other step. The document is built exactly as the page's
    saveFit builds it (the row's fields, the crop from the row's map_box and size or the whole
    page, the candidate's proposed pairs as the human's drag) and is stamped by: hand by the store
    (303). Every socket in the server process is dead, so the matcher is unreachable and the run
    is network-free: any unfitted candidate is recorded in the item as "no matcher on this
    machine" (checked when the picked site has one - the pick prefers it), and the page is read
    from the tree's own
    data/raw copy. The site is derived from the real queue (never pinned, 803): the first entry
    with a local book page and an unresolved item carrying it. The server's stdout is pulled by a
    reader thread and the line gets 180 s (it measures ~23 s, the heavy first import included).
    Writes land in the temp tree, never in the shared store behind the checkout's symlinks
    (realpath check)."""
    base, tree, proc, out = line_served["base"], line_served["tree"], line_served["proc"], line_served["out"]
    entry, item_before = line_served["entry"], line_served["item"]
    site, row, plan = entry["site"], entry["best"]["row"], entry["best"]["plan"]
    doc_id = site + "." + plan

    # ---- the document, exactly as the page's saveFit builds it ----
    cand = [c for c in item_before["candidates"] if c["plan"] == plan][0]
    pairs = [list(p) for p in cand.get("pairs") or []]
    assert len(pairs) >= 3  # the page's save floor for a similarity fit
    W, H = line_served["size"]
    mb, size = row.get("map_box"), row.get("size") or [W, H]
    crop = ([round(mb[0] * size[0]), round(mb[1] * size[1]),
             round(mb[2] * size[0]), round(mb[3] * size[1])] if mb else [0, 0, W, H])
    doc = {"site": site, "plan": plan, "ia": row["ia"], "file": row["file"], "crop": crop,
           "model": "similarity", "src": "book", "url": row.get("url"), "ref": row.get("ref"),
           "size": [W, H], "pairs": pairs, "label": row.get("label"), "title": row.get("title"),
           "book": row.get("book"), "cite": row.get("cite"), "at": AT}

    # ---- before: what the line must change ----
    sd = tree / "web" / "data" / "sites" / site
    assert not sd.is_symlink()  # the fixture materialized it: writes must not reach the shared store
    dep_path = sd / "depictions.json"
    deps_before = json.loads(dep_path.read_text()) if dep_path.exists() else {"depictions": []}
    assert not any((d.get("fit") or {}).get("doc") == doc_id for d in deps_before["depictions"])
    drawings_before = next(s["drawings"] for s in
                           json.loads((tree / "web" / "data" / "sites.json").read_text())["sites"]
                           if s["id"] == site)
    item_path, item_now = _item_of(tree, site)
    assert item_now is not None and not (item_now.get("resolved") or {}).get("doc")
    status, rv_before = get_json(base + "/data/review.json")
    assert status == 200
    open_before = [it["site"] for it in rv_before["items"]]

    # ---- the owner's save, through the real store ----
    status, body = put_json(base + "/api/db/platefits/" + doc_id, doc)
    assert status == 200 and json.loads(body) == {"ok": True}

    # ---- poll: the line puts the drawing on the map, then reports finished (exit 0); the server
    # stays up the whole time (the owner's page is live while the line runs) ----
    t0 = time.time()
    fit_entry = None
    finished = False
    want = "one-site line for %s: finished (exit 0)" % site
    while time.time() - t0 < 180:
        assert get(base + "/")[0] == 200
        if not fit_entry and dep_path.exists():
            for d in json.loads(dep_path.read_text())["depictions"]:
                if (d.get("fit") or {}).get("doc") == doc_id and (d.get("fit") or {}).get("at") == AT:
                    fit_entry = d
                    break
        if fit_entry and not finished and any(want in ln for ln in out):
            finished = True
        if fit_entry and finished:
            break
        time.sleep(1)
    assert fit_entry, "the one-site line never put the drawing on the map within 180 s: %r" % out[-20:]
    assert finished, "the one-site line never reported finished (exit 0) within 180 s: %r" % out[-20:]

    # ---- the line's own words: it ran, and it never touched the network ----
    assert not any("attempted a network connection" in ln for ln in out), out[-20:]
    assert not any("one-site line" in ln and "failed" in ln for ln in out), out[-20:]

    # ---- the stored document: the owner's pairs and timestamp, stamped by: hand ----
    status, stored = get_json(base + "/api/db/platefits/" + doc_id)
    assert status == 200
    assert stored["by"] == "hand"
    assert stored["at"] == AT and stored["pairs"] == pairs

    # ---- the drawing on the map: the overlay and its ink exist in the tree, the fit is recorded
    # (a hand fit is built with no check, and the source line says so) ----
    assert fit_entry["kind"] == "plan"
    assert fit_entry["file"] == "plan_" + plan + ".webp"
    assert fit_entry.get("ink") == "plan_" + plan + "_ink.webp"
    for f in (fit_entry["file"], fit_entry["ink"]):
        p = sd / f
        assert p.exists(), f
        assert os.path.realpath(str(p)).startswith(str(tree)), "a test fit must not land in the shared store"
    fit = fit_entry["fit"]
    assert fit["pairs"] == len(pairs) and fit["model"] == "similarity"
    assert fit["at"] == AT and fit["doc"] == doc_id
    assert isinstance(fit["m_per_px"], float) and fit["m_per_px"] > 0
    assert isinstance(fit["rot_deg"], (int, float))
    assert len(fit["resid_m"]) == len(pairs) and all(r >= 0 for r in fit["resid_m"])
    assert "Placed by hand" in fit_entry["source"]

    # ---- the site's square: the drawing count follows the overlay ----
    drawings_after = next(s["drawings"] for s in
                          json.loads((tree / "web" / "data" / "sites.json").read_text())["sites"]
                          if s["id"] == site)
    assert drawings_after == drawings_before + 1

    # ---- the review item: resolved write-once by the saved document; every other uncovered
    # candidate (when the pick has any) was recorded in the item as "no matcher on this machine"
    # (the matcher was not reachable in the server process); the file did not move (its lead
    # candidate is unchanged) ----
    item_path2, item_after = _item_of(tree, site)
    assert item_path2 == item_path
    assert item_after["resolved"] == {"doc": doc_id, "at": AT}
    uncovered = [r["id"] for r in _rows_naming(tree, site)
                 if r["id"] != plan and r["id"] not in {c.get("plan") for c in item_before["candidates"]}]
    if uncovered:
        after_cands = {c["plan"]: c for c in item_after["candidates"]}
        for u in uncovered:
            assert after_cands.get(u, {}).get("why") == "no matcher on this machine", u

    # ---- the page's review file: republished, and the saved site's item left the open list ----
    status, rv_after = get_json(base + "/data/review.json")
    assert status == 200
    assert rv_after["at"] != rv_before["at"]  # the export re-ran
    open_after = [it["site"] for it in rv_after["items"]]
    assert site not in open_after, "the saved site's resolved item must leave the open list"
    assert len(open_after) == len(open_before) - (1 if site in open_before else 0)


# ---------------------------------------------------------------------------
# Part 3: the page card (task 305, boxes 2 and 4), checked in a real headless
# browser: web/fitqueue.js on the served temp tree, driven with real clicks the
# way the owner does. The committed screenshots in docs/site_flow/ come from
# the same script (PROBE_SCRIPT) run against the real checkout, where the book
# pages load.

# the VM's headless Chrome and playwright-core; another machine points AW_CHROME / AW_NODE_MODULES at its own
CHROME = os.environ.get("AW_CHROME", "/opt/google/chrome/chrome")
NODE_MODULES = os.environ.get("AW_NODE_MODULES", "/home/agent/tools/shot/node_modules")

PROBE_SCRIPT = r"""
// node fitqueue_probe.mjs <base_url> <out_dir> <done_site | none>
// The 'Ready to fit' card (web/fitqueue.js) as the owner drives it, in headless Chrome:
// boot on the home view -> read the card -> real click 'Place the drawing' (the fit tool
// opens on the queue's site and row) -> the fit view's back button -> the site view's
// 'All sites' back -> read the card again -> Skip -> read -> Undo skips -> read.
// done_site (anything but 'none') pre-seeds the browser's localStorage aw.fitQueue.done
// with {done_site: <timestamp>} before any page script runs - the exact key and value the
// card's saveFit wrapper writes when a save lands - so the load starts at the next entry.
// Prints one [eval] line with the stage states, then every console/pageerror/reqfail line;
// screenshots land in <out_dir>/ as 1-card.png, 2-place.png, 2b-backout.png, 3-skip.png.
import { createRequire } from 'module';
const require = createRequire('/Users/ethan/code/projects/interpreter/package.json');
const { chromium } = require('playwright-core');
const [url, outdir, doneSite] = process.argv.slice(2);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const browser = await chromium.launch({ channel: 'chrome', headless: true,
  args: ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 1200, height: 800 }, colorScheme: 'light' });
const lines = [];
page.on('console', m => lines.push('[console] ' + m.type() + ' ' + m.text()));
page.on('pageerror', e => lines.push('[pageerror] ' + e.message));
page.on('requestfailed', r => lines.push('[reqfail] ' + r.url() + ' ' + (r.failure() && r.failure().errorText)));
if (doneSite !== 'none')
  await page.addInitScript(s => {
    try { localStorage.setItem('aw.fitQueue.done', JSON.stringify({ [s]: '2026-10-12T00:00:00.000Z' })); } catch {}
  }, doneSite);
await page.goto(url);
const boot = await page.evaluate(async () => {
  if (typeof FQ === 'undefined') return { ok: false, why: 'fitqueue.js did not define FQ' };
  let ok = false;
  try {
    const t0 = Date.now();
    while (Date.now() - t0 < 60000) {
      if (S.ready && S.sites.length && FQ.loaded && FQ.entries.length) { ok = true; break; }
      await new Promise(r => setTimeout(r, 250));
    }
  } catch {}
  let extra = {};
  try { extra = { ready: !!S.ready, sites: S.sites.length, plans: P.rows.length,
                 entries: FQ.entries.length, done: FQ.done, tab: S.tab }; } catch {}
  return Object.assign({ ok }, extra);
});
const out = { boot };
const card = () => page.evaluate(() => {
  const c = document.getElementById('fqcard');
  return c ? { text: c.textContent, reset: !!document.getElementById('fqreset') } : null;
});
out.card1 = await card();
await page.screenshot({ path: outdir + '/1-card.png' });
// the owner clicks 'Place the drawing': the existing fit tool opens on the queue's site and row
await page.click('#fqplace', { timeout: 20000 });
// openPlan's picture either loads or the page's own hint says it could not: wait for either
await page.evaluate(async () => {
  const t0 = Date.now();
  while (Date.now() - t0 < 60000) {
    try {
      if (P.plan && (P.img !== null ||
          (document.getElementById('fithint') || {}).textContent === 'Could not load the page scan.'))
        return;
    } catch {}
    await new Promise(r => setTimeout(r, 250));
  }
});
await sleep(500);
out.place = await page.evaluate(() => ({
  imgLoaded: P.img !== null, active: P.active, site: P.site && P.site.id,
  plan: P.plan && P.plan.id, model: P.model, ground: S.ground, pending: P.pending,
  pane: !document.getElementById('fitpane').hidden,
  fitname: (document.getElementById('fitname') || {}).textContent || null,
  hint: (document.getElementById('fithint') || {}).textContent || null,
  h2: (document.querySelector('#body h2.site-title') || {}).textContent || null,
  saveDisabled: document.getElementById('fsave') ? document.getElementById('fsave').disabled : null,
  back: (document.getElementById('fitback') || {}).textContent || null,
  done: FQ.done, skipped: FQ.skipped
}));
await page.screenshot({ path: outdir + '/2-place.png' });
// back out through the page's own buttons: the fit view's back, then the site view's
await page.click('#fitback', { timeout: 20000 });
await sleep(800);
out.back1 = await page.evaluate(() => ({
  active: P.active, pane: !document.getElementById('fitpane').hidden,
  h2: (document.querySelector('#body h2.site-title') || {}).textContent || null,
  back: (document.getElementById('back') || {}).textContent || null
}));
await page.click('#back', { timeout: 20000 });
await sleep(800);
out.card2 = await card();
await page.screenshot({ path: outdir + '/2b-backout.png' });
// Skip moves the card on (Undo skips appears); Undo restores it
await page.click('#fqskip', { timeout: 20000 });
await sleep(400);
out.card3 = await card();
await page.screenshot({ path: outdir + '/3-skip.png' });
await page.click('#fqreset', { timeout: 20000 });
await sleep(400);
out.card4 = await card();
console.log('[eval] ' + JSON.stringify(out));
for (const ln of lines) console.log(ln);
await browser.close();
"""


def _headless_or_skip():
    if not (os.path.exists(CHROME) and os.path.isdir(NODE_MODULES)):
        pytest.skip("headless Chrome is not installed on this machine (the recipe is in PITFALLS.md)")


def _run_probe(base, outdir, done_site):
    """Run the card probe against a served tree. done_site (anything but 'none') pre-seeds
    the browser's aw.fitQueue.done with that one site - the exact key the card's saveFit
    wrapper writes when a save lands. -> (the stage states the probe printed, the process)."""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "fitqueue_probe.mjs").write_text(PROBE_SCRIPT, encoding="utf-8")
    p = subprocess.run(["node", str(outdir / "fitqueue_probe.mjs"), base, str(outdir), done_site],
                       cwd=str(ROOT), env=dict(os.environ, NODE_PATH=NODE_MODULES),
                       capture_output=True, encoding="utf-8", errors="replace", timeout=240)
    data = None
    for ln in (p.stdout or "").splitlines():
        if ln.startswith("[eval]"):
            data = json.loads(ln[len("[eval]"):])
    assert p.returncode == 0, (p.returncode, p.stdout[-2000:], p.stderr[-2000:])
    assert data is not None, p.stdout[-2000:]
    return data, p


def test_card_in_the_browser(served, tmp_path_factory):
    """Box 2 + 4 (the page half, checked in a real browser): a headless load of the page on
    the served temp tree shows the 'Ready to fit' card on the home view - the next queued
    site, its best candidate and the one-word reason, 'N to go' - and the probe drives it
    the way the owner does, with real clicks: 'Place the drawing' opens the EXISTING fit
    tool on that site and that row (the card never changes the tool's own clicking: the
    fit view renders, the picture is the row's, the page's Save is at its save-floor),
    back out through the page's own buttons and the card is unchanged, 'Skip' moves it on
    ('Undo skips' appears) and undo restores it. The temp tree has no data/raw, so the
    candidate's picture 404s and the fit tool keeps the row with its own hint: the
    assertions are on the page's state, not on pixels. The full click-through (the
    owner's own points on the plate, the save, the drawing on the map) is the owner's Mac
    - this tree has no page to click - and the save -> line half of box 3 is
    test_save_runs_the_one_site_line. No network, ephemeral port."""
    _headless_or_skip()
    base, tree = served
    entries = json.loads((tree / "web" / "data" / "fit_queue.json").read_text())["entries"]
    assert len(entries) >= 3, "the card test needs at least three queue entries"
    e1, e2 = entries[0], entries[1]
    sites = {s["id"]: s for s in json.loads((tree / "web" / "data" / "sites.json").read_text())["sites"]}
    data, p = _run_probe(base, tmp_path_factory.mktemp("fqshot"), "none")
    assert data["boot"]["ok"], (data["boot"], p.stdout[-2000:])
    assert "[pageerror]" not in p.stdout, p.stdout[-2000:]
    # Page-caused reqfails, expected: MapLibre aborts tile fetches that leave the map's
    # view during the card's flyTo - the local relief tiles (/tiles/) and the page's base
    # imagery, the live Esri feed (server.arcgisonline.com/.../MapServer/tile/... - note
    # the SINGULAR 'tile/', which a '/tiles/' exclusion alone misses); no other request
    # may fail at the network level
    assert not any(ln.startswith("[reqfail]") and "/tiles/" not in ln and "arcgisonline" not in ln and "MapServer/tile/" not in ln
                   for ln in p.stdout.splitlines()), p.stdout[-2000:]
    assert data["boot"]["entries"] == len(entries)  # the file's queue is what the page loaded

    # card 1: the next queued site, its best candidate, the reason, the count
    c1 = data["card1"]
    assert c1, "no card on the home view: %r" % data["boot"]
    row = e1["best"]["row"]
    assert "Ready to fit" in c1["text"] and "%d to go" % len(entries) in c1["text"]
    assert e1["name"] in c1["text"]
    assert (row["title"] or row["id"]) in c1["text"]
    assert e1["best"]["reason"] in c1["text"]
    assert c1["reset"] is False  # nothing skipped yet

    # place: the existing fit tool opens on this site and this row, its own state intact
    pl = data["place"]
    assert pl["site"] == e1["site"] and pl["plan"] == e1["best"]["plan"]
    assert pl["active"] is True and pl["pane"] is True and pl["pending"] is None
    s1 = sites[e1["site"]]
    assert pl["ground"] == ("imagery" if s1.get("lidar") is False else "relief")
    assert pl["model"] == ("view" if row["view"] else "plan")
    assert pl["h2"] == (row["title"] or "Old plan")
    assert pl["fitname"] == " \u00b7 ".join(x for x in (row["book"], row["label"], row["title"]) if x)
    assert pl["back"] == "\u2190 " + (e1["name"] or e1["site"])
    assert pl["saveDisabled"] is True  # no points yet: the page's save floor is untouched
    assert pl["done"] == {} and pl["skipped"] == []  # placing does not mark anything
    # this tree has no data/raw: the candidate's picture (a book page or a commons file)
    # 404s, and the fit tool keeps the row with its own hint
    assert pl["imgLoaded"] is False
    assert pl["hint"] == "Could not load the page scan."

    # back out through the page's own buttons: the fit view's back, then the site view's;
    # the fit pane closes again and the card is unchanged
    assert data["back1"]["active"] is False and data["back1"]["pane"] is False
    assert data["back1"]["h2"] == (e1["name"] or e1["site"])
    assert data["back1"]["back"] == "\u2190 All sites"
    assert data["card2"]["text"] == c1["text"]

    # skip: the card moves on and offers an undo; undo restores it
    c3 = data["card3"]
    assert c3 and e2["name"] in c3["text"] and e1["name"] not in c3["text"]
    assert "%d to go" % (len(entries) - 1) in c3["text"]
    assert c3["reset"] is True and "Undo 1 skip" in c3["text"]
    assert data["card4"]["text"] == c1["text"]


def test_card_done_mark_moves_on(served, tmp_path_factory):
    """Box 4 (the queue moves on after a save, checked in a real browser): a fresh page
    load with the browser's aw.fitQueue.done pre-seeded with the FIRST queued site - the
    exact key and value the card's own saveFit wrapper writes when a save lands
    (web/fitqueue.js) - starts at entry 2: the done site stays marked (the self-heal
    against the file keeps it: it is still in the file) and the card shows the next site
    with one fewer to go. The card then behaves like any other: Place opens entry 2's
    row, Skip moves on to entry 3, and the done site never comes back in this session
    (undo restores entry 2). No network, ephemeral port."""
    _headless_or_skip()
    base, tree = served
    entries = json.loads((tree / "web" / "data" / "fit_queue.json").read_text())["entries"]
    assert len(entries) >= 3, "the card test needs at least three queue entries"
    e1, e2, e3 = entries[0], entries[1], entries[2]
    data, p = _run_probe(base, tmp_path_factory.mktemp("fqshotdone"), e1["site"])
    assert data["boot"]["ok"], (data["boot"], p.stdout[-2000:])
    assert "[pageerror]" not in p.stdout, p.stdout[-2000:]
    # Page-caused reqfails, expected: MapLibre aborts tile fetches that leave the map's
    # view during the card's flyTo - the local relief tiles (/tiles/) and the page's base
    # imagery, the live Esri feed (server.arcgisonline.com/.../MapServer/tile/... - note
    # the SINGULAR 'tile/', which a '/tiles/' exclusion alone misses); no other request
    # may fail at the network level
    assert not any(ln.startswith("[reqfail]") and "/tiles/" not in ln and "arcgisonline" not in ln and "MapServer/tile/" not in ln
                   for ln in p.stdout.splitlines()), p.stdout[-2000:]
    assert data["boot"]["done"] == {e1["site"]: "2026-10-12T00:00:00.000Z"}, data["boot"]["done"]

    # the card starts at entry 2: the done site is skipped at load, one fewer to go
    c1 = data["card1"]
    assert c1, "no card on the home view: %r" % data["boot"]
    row2 = e2["best"]["row"]
    assert e2["name"] in c1["text"] and e1["name"] not in c1["text"]
    assert (row2["title"] or row2["id"]) in c1["text"]
    assert e2["best"]["reason"] in c1["text"]
    assert "%d to go" % (len(entries) - 1) in c1["text"]

    # place from the advanced card opens entry 2's site and row
    pl = data["place"]
    assert pl["site"] == e2["site"] and pl["plan"] == e2["best"]["plan"]
    assert pl["active"] is True and pl["pending"] is None
    assert pl["done"] == {e1["site"]: "2026-10-12T00:00:00.000Z"}  # placing changes nothing

    # skip from entry 2 goes to entry 3; the done site never comes back this session;
    # undo restores entry 2 (not the done entry 1)
    c3 = data["card3"]
    assert c3 and e3["name"] in c3["text"] and e1["name"] not in c3["text"]
    assert e2["name"] not in c3["text"]
    assert data["card4"]["text"] == c1["text"]
    assert e1["name"] not in data["card4"]["text"]



# ---------------------------------------------------------------------------
# Part 4: place mode end to end (task 307bb, rewritten 2026-10-13: the owner's rule "no unit
# tests, only end-to-end"). Headless Chrome on a FULL temp tree (part 2's recipe: tools/fit/pipeline
# present, the picked entry's book page materialised locally, every socket in the server dead). The
# probe checks only what the owner sees or gets - the toolbar, the drawing's corner handles on screen,
# where the ground is on screen, which file each map layer shows, and the files the server writes -
# never the page's own variables, so the way the tool computes a placement can change freely.
# Run 1 places, moves (drag on and off the drawing, wheel, toolbar, shift/alt+wheel), undoes and
# saves, then checks the overlay lands where the drawing was; run 2 cancels; run 3 skips and marks a
# picture "Not this structure". The test reads the files back and hashes the checkout around the run.

PLACE_PROBE = r"""// node place_probe.mjs <base_url> <site> <plan> <tree> <out_dir> <done_json>
// Place mode end to end, as the owner uses it, in headless Chrome on a full served temp tree.
// Only what a person can see or get is checked: the page (DOM, the toolbar, the drawing's four corner
// handles on screen, pixels), the map's view (where a ground point is on screen, the zoom, which layer
// shows which file) and the files the server writes. Never the page's own variables (P, S, FQ, _fk*):
// how the tool computes a placement is free to change; what the owner sees and saves is not.
// Run 1: card -> Place -> the drawing on the works -> drag on it, drag off it, wheel, toolbar scale and
// turn, shift/alt+wheel, Undo and Ctrl+Z -> Save -> the overlay lands where the drawing was placed.
// Run 2: Place -> Cancel -> the earlier overlay is back. Run 3: Place -> Skip site -> Not this structure.
// One [ok]/[FAIL] line per check, then RESULT PASS/FAIL; exit 0/1.
import { createRequire } from 'module';
import { readFileSync, readdirSync } from 'fs';
const require = createRequire(process.env.NODE_PATH + '/');
const { chromium } = require('playwright-core');
const [url, site, plan, tree, outdir, doneJson] = process.argv.slice(2);
const doneMap = JSON.parse(doneJson);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const failures = [];
const check = (name, cond, info) => {
  console.log((cond ? '[ok] ' : '[FAIL] ') + name + (cond ? '' : ' :: ' + JSON.stringify(info)));
  if (!cond) failures.push(name);
};
const readJson = p => { try { return JSON.parse(readFileSync(p, 'utf8')); } catch { return null; } };
const queue = readJson(tree + '/web/data/fit_queue.json');
const entry = queue.entries.find(e => e.site === site);
const propC = entry.propose.pairs[entry.propose.pairs.length - 1];  // the queue file's starting centre [u, v, lon, lat]

const browser = await chromium.launch({ channel: 'chrome', headless: true,
  args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const lines = [];
async function openPage(tag) {
  const page = await browser.newPage({ viewport: { width: 1280, height: 820 }, colorScheme: 'light' });
  page.on('pageerror', e => lines.push(`[pageerror ${tag}] ` + e.message));
  page.on('requestfailed', r => lines.push(`[reqfail ${tag}] ` + r.url() + ' ' + (r.failure() && r.failure().errorText)));
  await page.addInitScript(({ done }) => { try { localStorage.setItem('aw.fitQueue.done', JSON.stringify(done)); } catch {} }, { done: doneMap });
  await page.goto(url);
  await page.waitForSelector('#fqplace', { timeout: 60000 });
  return page;
}
// the drawing's four corners as the owner sees them: the visible corner handles' centres, in page px
const quad = page => page.evaluate(() => [...document.querySelectorAll('.gpin.fk-handle')]
  .filter(el => el.style.display !== 'none').map(el => { const r = el.getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2]; }));
const centroid = q => [q.reduce((s, p) => s + p[0], 0) / q.length, q.reduce((s, p) => s + p[1], 0) / q.length];
const edge = q => Math.hypot(q[1][0] - q[0][0], q[1][1] - q[0][1]);
const angle = q => Math.atan2(q[1][1] - q[0][1], q[1][0] - q[0][0]) * 180 / Math.PI;  // screen y down: + = clockwise
const near = (a, b, tol) => a.length === b.length && a.every((p, i) => Math.hypot(p[0] - b[i][0], p[1] - b[i][1]) <= tol);
const shifted = (a, b, d, tol) => a.length === b.length && a.every((p, i) => Math.hypot(b[i][0] - p[0] - d[0], b[i][1] - p[1] - d[1]) <= tol);
const inside = (q, x, y) => { let c = false; for (let i = 0, j = q.length - 1; i < q.length; j = i++) {
  const a = q[i], b = q[j]; if ((a[1] > y) !== (b[1] > y) && x < (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]) + a[0]) c = !c; } return c; };
const groundOnScreen = (page, ll) => page.evaluate(ll => { const r = map.getCanvas().getBoundingClientRect(), q = map.project(ll); return [q.x + r.left, q.y + r.top]; }, ll);
const zoom = page => page.evaluate(() => map.getZoom());
const onMap = (page, x, y) => page.evaluate(([x, y]) => { const el = document.elementFromPoint(x, y); return !!el && el.tagName === 'CANVAS' && !!el.closest('.maplibregl-canvas-container'); }, [x, y]);
const layer = (page, s) => page.evaluate(s => ({ vis: map.getLayer('dep-' + s) ? map.getLayoutProperty('dep-' + s, 'visibility') : null,
  src: map.getSource('dep-' + s) ? map.getSource('dep-' + s).url : null }), s);
async function drag(page, from, d) {
  await page.mouse.move(from[0], from[1]); await page.mouse.down();
  await page.mouse.move(from[0] + d[0], from[1] + d[1], { steps: 8 }); await page.mouse.up(); await sleep(500);
}
async function placeAndWait(page) {
  await page.click('#fqplace', { timeout: 20000 });
  await page.waitForSelector('#fkbar', { timeout: 60000 });
  await page.waitForFunction(() => [...document.querySelectorAll('.gpin.fk-handle')].filter(el => el.style.display !== 'none').length === 4, null, { timeout: 30000 });
  await sleep(2500);  // the fly-to onto the works
}

// ================= run 1 =================
const page = await openPage('1');
const before1 = await layer(page, site);
await placeAndWait(page);
let q0 = await quad(page);
const startC = await groundOnScreen(page, [propC[2], propC[3]]);
check('place: the toolbar shows every control with its key',
  await page.evaluate(() => { const t = document.getElementById('fkbar').textContent;
    return ['Move', 'Scale', 'Turn', 'Undo', 'Skip site', 'Not this structure', 'Cancel', 'Save on the map', 'wheel'].every(w => t.includes(w)); }));
check('place: the drawing opens on the works (its corners around the queue\'s starting spot)', q0.length === 4 && inside(q0, ...startC), { q0, startC });
check('place: the earlier overlay is hidden while placing', !before1.vis || (await layer(page, site)).vis === 'none', before1);
check('place: the panel\'s instruction box and buttons are out of the way',
  await page.evaluate(() => [...document.querySelectorAll('#body .step, #body .tools')].every(el => getComputedStyle(el).display === 'none')));
await page.screenshot({ path: outdir + '/1-placed.png' });

// drag ON the drawing: the drawing follows the pointer, the ground stays put
const c0 = centroid(q0);
check('drag on: the drawing\'s middle is on the map, not under a panel', await onMap(page, ...c0), c0);
const g0 = await groundOnScreen(page, [propC[2], propC[3]]);
await drag(page, c0, [60, 25]);
const q1 = await quad(page), g1 = await groundOnScreen(page, [propC[2], propC[3]]);
check('drag on the drawing moves the drawing by the pointer', shifted(q0, q1, [60, 25], 2.5), { q0, q1 });
check('drag on the drawing leaves the map where it was', Math.hypot(g1[0] - g0[0], g1[1] - g0[1]) < 1, { g0, g1 });

// drag OFF the drawing: the map pans and the drawing rides with the ground
let off = null;
for (const y of [260, 340, 420, 500, 580]) for (const x of [1180, 1120, 1060, 1000, 940, 880]) {
  if (!off && !inside(q1, x, y) && await onMap(page, x, y)) off = [x, y];
}
check('drag off: found a spot of open map', !!off);
await drag(page, off, [-90, 35]);
const q2 = await quad(page), g2 = await groundOnScreen(page, [propC[2], propC[3]]);
// the map keeps gliding a little after the release (MapLibre's pan inertia): at least the drag, same direction
const pd = [g2[0] - g1[0], g2[1] - g1[1]], cosd = (pd[0] * -90 + pd[1] * 35) / (Math.hypot(...pd) * Math.hypot(90, 35));
check('drag off the drawing pans the map', Math.hypot(...pd) >= 0.95 * Math.hypot(90, 35) && cosd > 0.99, { g1, g2 });
check('drag off the drawing: the drawing stays on its ground (moves with the map)', shifted(q1, q2, [g2[0] - g1[0], g2[1] - g1[1]], 2.5), { q1, q2 });

// plain wheel: the map zooms, the drawing stays on its ground (grows with the map)
const z2 = await zoom(page), e2 = edge(q2);
await page.mouse.move(...off); await page.mouse.wheel(0, -240); await sleep(900);
const q3 = await quad(page), z3 = await zoom(page);
check('wheel zooms the map', z3 > z2 + 0.1, { z2, z3 });
check('wheel: the drawing scales with the map (stays on its ground)', Math.abs(edge(q3) / e2 / 2 ** (z3 - z2) - 1) < 0.02, { e2, e3: edge(q3), dz: z3 - z2 });

// toolbar scale and turn, then the wheels with keys
await page.click('#fkbar [data-a="s+"]'); await sleep(400);
const q4 = await quad(page);
check('toolbar +: the drawing grows 5% about its middle', Math.abs(edge(q4) / edge(q3) - 1.05) < 0.005 && near([centroid(q4)], [centroid(q3)], 1.5), { r: edge(q4) / edge(q3) });
await page.click('#fkbar [data-a="r+"]'); await sleep(400);
const q5 = await quad(page);
check('toolbar turn-right: the drawing turns 1 degree clockwise on screen', Math.abs(angle(q5) - angle(q4) - 1) < 0.15, { a4: angle(q4), a5: angle(q5) });
await page.click('#fkbar [data-a="r-"]', { modifiers: ['Shift'] }); await sleep(400);
const q6 = await quad(page);
check('toolbar turn-left with shift: 5 degrees counterclockwise', Math.abs(angle(q6) - angle(q5) + 5) < 0.2, { a5: angle(q5), a6: angle(q6) });
const z6 = await zoom(page);
await page.mouse.move(...off);
await page.keyboard.down('Shift'); await page.mouse.wheel(0, -100); await page.keyboard.up('Shift'); await sleep(800);
const q7 = await quad(page);
check('shift+wheel up grows the drawing, the map does not zoom', edge(q7) > edge(q6) * 1.1 && Math.abs((await zoom(page)) - z6) < 1e-6, { e6: edge(q6), e7: edge(q7) });
await page.keyboard.down('Alt'); await page.mouse.wheel(0, 200); await page.keyboard.up('Alt'); await sleep(800);
const q8 = await quad(page);
check('alt+wheel down turns the drawing clockwise, the map does not zoom', Math.abs(angle(q8) - angle(q7) - 2) < 0.2 && Math.abs((await zoom(page)) - z6) < 1e-6, { a7: angle(q7), a8: angle(q8) });
await page.screenshot({ path: outdir + '/2-moved.png' });

// undo walks back every step: alt+wheel, shift+wheel, shift turn, turn, +, the drag on (pans and zooms are the map's, not undone)
const back = [q7, q6, q5, q4, q3];
let undoOk = true;
for (let i = 0; i < back.length; i++) {
  if (i === 1) await page.keyboard.press('Control+z'); else await page.click('#fkundo');
  await sleep(400);
  const q = await quad(page);
  if (!near(q, back[i], 1.5)) { undoOk = false; check(`undo step ${i + 1} puts the drawing back`, false, { q, want: back[i] }); break; }
}
check('Undo (button and Ctrl+Z) walks every change back in order', undoOk);
await page.click('#fkundo'); await sleep(400);
const q9 = await quad(page), g9 = await groundOnScreen(page, [propC[2], propC[3]]);
check('undoing the drag puts the drawing back on its starting spot', inside(q9, ...g9), { q9, g9 });
check('Undo greys out when there is nothing left to undo', await page.evaluate(() => document.getElementById('fkundo').disabled));

// move it once more, then save from the toolbar: the overlay must land where the drawing is
await drag(page, centroid(q9), [40, -20]);
await page.click('#fkbar [data-a="s+"]'); await page.click('#fkbar [data-a="r+"]'); await sleep(500);
const qs = await quad(page);
const placedLL = await page.evaluate(q => { const r = map.getCanvas().getBoundingClientRect();
  return q.map(([x, y]) => { const u = map.unproject([x - r.left, y - r.top]); return [u.lng, u.lat]; }); }, qs);
const mpp = await page.evaluate(() => 156543.03392 * Math.cos(map.getCenter().lat * Math.PI / 180) / 2 ** map.getZoom());
await page.click('#fkbar [data-a="save"]');
await page.waitForFunction(() => !document.getElementById('fkbar'), null, { timeout: 120000 }).catch(() => {});
check('save: the toolbar closes when the overlay is on the map', await page.evaluate(() => !document.getElementById('fkbar')));
const docId = site + '.' + plan;
const doc = readJson(tree + '/data/db/platefits/' + docId + '.json');
check('save: the fit was written to the store, as a hand fit', !!doc && doc.by === 'hand' && doc.site === site && doc.plan === plan, doc && { by: doc.by });
let overlay = null;
for (let i = 0; i < 40 && !overlay; i++) {
  overlay = ((readJson(tree + '/web/data/sites/' + site + '/depictions.json') || {}).depictions || []).find(d => (d.fit || {}).doc === docId) || null;
  if (!overlay) await sleep(1500);
}
check('save: the overlay was made', !!overlay);
if (overlay) {
  const k = Math.cos(placedLL[0][1] * Math.PI / 180), M = ll => [ll[0] * 111319.49 * k, ll[1] * 111319.49];
  const err = overlay.corners.map((c, i) => Math.hypot(M(c)[0] - M(placedLL[i])[0], M(c)[1] - M(placedLL[i])[1]));
  check('save: the overlay\'s corners are where the drawing\'s corners were placed (within 3 screen px)', Math.max(...err) <= 3 * mpp + 0.5, { err, mpp });
  const shown = await layer(page, site);
  check('save: the map now shows the new overlay', shown.vis === 'visible' && !!shown.src && (shown.src.endsWith('/' + overlay.file) || shown.src.endsWith('/' + overlay.ink)), { shown, file: overlay.file });
}
await page.screenshot({ path: outdir + '/3-saved.png' });

// ================= run 2: Cancel =================
const page2 = await openPage('2');
await sleep(1500);
await placeAndWait(page2);
const during = await layer(page2, site);
await page2.click('#fkbar [data-a="cancel"]'); await sleep(1500);
const after2 = await layer(page2, site);
check('cancel: the toolbar and the corner handles go', await page2.evaluate(() => !document.getElementById('fkbar') && !document.querySelector('.gpin.fk-handle')));
check('cancel: the overlay that was hidden while placing is back', during.vis === 'none' && after2.vis === 'visible' && !!after2.src, { during, after2 });
await page2.screenshot({ path: outdir + '/4-cancel.png' });

// ================= run 3: Skip site, Not this structure =================
const page3 = await openPage('3');
await placeAndWait(page3);
const name1 = await page3.evaluate(() => (document.getElementById('fitback') || {}).textContent || '');
await page3.click('#fkbar [data-a="skip"]');
await page3.waitForFunction(n => { const b = document.getElementById('fitback'); return b && b.textContent !== n; }, name1, { timeout: 60000 }).catch(() => {});
await sleep(1500);
const name2 = await page3.evaluate(() => (document.getElementById('fitback') || {}).textContent || '');
const i0 = queue.entries.findIndex(e => e.site === site), next = queue.entries.slice(i0 + 1)[0];
check('Skip site opens the next queued site straight away', !!next && name2.includes(next.name || next.site), { name1, name2, next: next && next.name });
const title2 = await page3.evaluate(() => (document.querySelector('#body h2.site-title') || {}).textContent || '');
// Not this: on the toolbar while placed, in the panel otherwise (a picture with no starting placement)
const barNot = await page3.evaluate(() => !!document.querySelector('#fkbar [data-a="not"]'));
await page3.click(barNot ? '#fkbar [data-a="not"]' : '#fknot');
await page3.waitForFunction(t => (document.querySelector('#body h2.site-title') || {}).textContent !== t, title2, { timeout: 60000 }).catch(() => {});
await sleep(1000);
const item = (() => { for (const f of readdirSync(tree + '/data/review')) {
  const it = readJson(tree + '/data/review/' + f); if (it && it.site === next.site) return it; } return null; })();
const dropped = !!item && (item.candidates || []).some(c => c.plan === next.best.plan && c.dropped === true);
check('Not this structure: the picture is marked dropped for the site', dropped, item && item.candidates.map(c => [c.plan, c.dropped]));
const q2file = await (await fetch(url.replace(/\/$/, '') + '/data/fit_queue.json?t=' + Date.now())).json();
check('Not this structure: the served queue no longer offers that picture for the site',
  !q2file.entries.some(e => e.site === next.site && e.best.plan === next.best.plan), next.best.plan);
const title3 = await page3.evaluate(() => (document.querySelector('#body h2.site-title') || {}).textContent || '');
check('Not this structure moves on to another picture', title3 !== title2, { title2, title3 });
await page3.screenshot({ path: outdir + '/5-notthis.png' });

for (const ln of lines) console.log(ln);
check('no page errors in any run', !lines.some(ln => ln.startsWith('[pageerror')));
check('no network-level request failures outside the map tiles',
  !lines.some(ln => ln.startsWith('[reqfail') && !ln.includes('/tiles/') && !ln.includes('arcgisonline') && !ln.includes('MapServer/tile/')));
console.log(failures.length ? 'RESULT FAIL: ' + failures.join(' | ') : 'RESULT PASS');
await browser.close();
process.exit(failures.length ? 1 : 0);
"""


def _survives_page_filter(dep):
    """The page's surveyOldEnough, mirrored: web/index.html:444-445, applied by loadDeps at
    :449 - a {map, aerial, topo} depiction passes only with a year (a falsy year fails, as in
    the JS `x.year &&`) <= current year - 150; every other kind passes unconditionally. The
    data's year is int or None (the only shapes in web/data/sites/*/depictions.json), so this
    matches the JS truthiness and coercion exactly for it."""
    cutoff = datetime.now().year - 150  # new Date().getFullYear() - 150, same machine and zone
    return [d for d in (dep or {}).get("depictions") or []
            if d.get("kind") not in ("map", "aerial", "topo") or (d.get("year") and d["year"] <= cutoff)]


def _page_auto_select(dep):
    """The depiction a fresh page auto-selects for the site, or None: web/index.html:688
    DRAWING plus select()'s auto-select at :866 - the first surviving {plan, drawing, view}
    depiction, else the last surviving 'map'. Only a returned depiction becomes the page's
    dep-<site> layer: applyDep (web/index.html:453) creates it only from the filtered list, and
    startFit (web/fitkit.js:575) hides it in place mode only when the layer exists - so the
    seed check and Cancel are non-vacuous exactly for such a site."""
    surv = _survives_page_filter(dep)
    for d in surv:  # select(): ds.find(x => DRAWING.has(x.kind))
        if d.get("kind") in ("plan", "drawing", "view"):
            return d
    maps = [d for d in surv if d.get("kind") == "map"]  # || ds.filter(x => x.kind === 'map').pop()
    return maps[-1] if maps else None


def _pick_place():
    """The first queue entry (file order) that place mode can run end to end: a proposal (the
    placement's anchor), the one-site line's constraints (_line_eligible: a local book page, an
    unresolved item carrying the row, no docs yet) and an overlay the PAGE will show for the site
    (its raw depictions survive the page's surveyOldEnough filter and its auto-select picks one
    of them - _page_auto_select), so the seed check and Cancel are non-vacuous. Derived, never
    pinned.
    -> (entry, done map seeding the card past every earlier entry) or None."""
    q = json.loads((ROOT / "web" / "data" / "fit_queue.json").read_text())
    items = _review_items()
    for i, e in enumerate(q["entries"]):
        if not e.get("propose") or _line_eligible(e, items.get(e["site"])) is None:
            continue
        dep = ROOT / "web" / "data" / "sites" / e["site"] / "depictions.json"
        if _page_auto_select(json.loads(dep.read_text()) if dep.is_file() else None) is None:
            continue
        return e, {x["site"]: AT for x in q["entries"][:i]}
    return None


@pytest.fixture
def place_served(tmp_path_factory):
    """part 2's line_served recipe for the place pick: the real server on an ephemeral port over a
    full copy of this checkout, the picked page in the tree's own data/raw, every socket dead.
    -> {"base", "tree", "entry", "done", "out"}"""
    _headless_or_skip()
    pick = _pick_place()
    assert pick, "no queue entry with a proposal, a local book page, an unresolved item and an overlay - vacuous"
    entry, done = pick
    row = entry["best"]["row"]
    tree = tmp_path_factory.mktemp("awplace")
    copy_web(tree, real={entry["site"]})
    for d in ("server", "tools", "fit", "pipeline"):
        shutil.copytree(str(ROOT / d), str(tree / d))

    def ignore(d, names):  # data/raw (book scans) and the gitignored elevation grids (data/sites/*/dem.npy)
        return [n for n in names if os.path.join(d, n) == str(ROOT / "data" / "raw") or n.endswith((".npy", ".npz"))]

    shutil.copytree(str(ROOT / "data"), str(tree / "data"), ignore=ignore)
    dst = tree / "data" / "raw" / "books" / row["ia"] / "full" / row["file"]
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(ROOT / "data" / "raw" / "books" / row["ia"] / "full" / row["file"]), dst)
    proc = subprocess.Popen([sys.executable, "-c", GUARD, "server/serve.py", "--port", "0"],
                            cwd=str(tree), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out = []

    def _reader():
        for line in proc.stdout:
            out.append(line.rstrip("\n"))

    threading.Thread(target=_reader, daemon=True).start()
    url = None
    deadline = time.time() + 90
    while time.time() < deadline and proc.poll() is None and not url:
        for line in list(out):
            m = re.match(r"(?:Resurface|Ancient Works) on (\S+)", line)
            if m:
                url = m.group(1)
                break
        time.sleep(0.2)
    if not url:
        proc.kill()
        raise AssertionError("server did not report its address (startup: %r)" % out[-10:])
    yield {"base": url.rstrip("/"), "tree": Path(tree), "entry": entry, "done": done, "out": out}
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()


def _write_surface():
    """Every file a save could touch in the checkout (the store, the review items, the page data),
    hashed: the run must leave all of it untouched."""
    paths = list((ROOT / "data" / "db" / "platefits").glob("*.json")) + list((ROOT / "data" / "review").glob("*.json"))
    paths += list((ROOT / "data" / "db" / "notthis").glob("*.json"))
    paths += [ROOT / "web" / "data" / "sites.json", ROOT / "web" / "data" / "review.json", ROOT / "web" / "data" / "fit_queue.json"]
    return {str(p): _h(p) for p in paths if p.is_file()}


def test_placement_gestures_and_save_in_the_browser(place_served, tmp_path_factory):
    """Place mode as the owner uses it, end to end: on a real queue site with a starting placement the
    drawing opens on the works under a toolbar that names every control; dragging on the drawing moves
    it, dragging off it pans the map with the drawing staying on its ground, the wheel zooms the map,
    the toolbar and shift/alt+wheel scale and turn it (turn-right is clockwise on screen), Undo and
    Ctrl+Z walk every change back; Save writes a hand fit and the overlay lands where the drawing was
    placed and shows on the map; Cancel brings the earlier overlay back; Skip site opens the next
    queued site; Not this structure drops the picture for that site and the served queue stops
    offering it. Hermetic: the checkout's write surface hashes the same before and after."""
    base, tree, entry, out = place_served["base"], place_served["tree"], place_served["entry"], place_served["out"]
    site, plan = entry["site"], entry["best"]["plan"]
    doc_id = site + "." + plan
    surface = _write_surface()
    outdir = tmp_path_factory.mktemp("f4shot")
    (outdir / "place_probe.mjs").write_text(PLACE_PROBE, encoding="utf-8")
    p = subprocess.run(["node", str(outdir / "place_probe.mjs"), base, site, plan, str(tree), str(outdir),
                        json.dumps(place_served["done"])],
                       cwd=str(ROOT), env=dict(os.environ, NODE_PATH=NODE_MODULES),
                       capture_output=True, encoding="utf-8", errors="replace", timeout=600)
    (outdir / "probe.log").write_text(p.stdout + p.stderr, encoding="utf-8")  # every check, beside the screenshots
    assert p.returncode == 0 and "RESULT PASS" in p.stdout, (p.returncode, p.stdout[-4000:], p.stderr[-2000:], out[-20:])
    # the saved fit and its overlay, read back from the tree
    doc = json.loads((tree / "data" / "db" / "platefits" / (doc_id + ".json")).read_text())
    assert doc["by"] == "hand" and doc["site"] == site and doc["plan"] == plan
    sd = tree / "web" / "data" / "sites" / site
    assert not sd.is_symlink()
    assert any((d.get("fit") or {}).get("doc") == doc_id for d in json.loads((sd / "depictions.json").read_text())["depictions"])
    assert list((tree / "data" / "db" / "notthis").glob("*.json")), "Not this structure left no record"
    assert not any("attempted a network connection" in ln for ln in out), out[-20:]
    assert _write_surface() == surface, "the run wrote into the checkout"


# ---------------------------------------------------------------------------
# Part 5: the block diagram end to end (2026-10-13): the drawing the map shows is draped on the
# block, the section opens on request, the ground follows the map. Pixels and DOM only.

BLOCK_PROBE = r"""// node block_probe.mjs <base_url> <site> <out_dir>
// The block diagram end to end, as the owner sees it: a site whose old drawing shows on the map ->
// Block diagram -> the drawing is draped on the block (survey-red pixels in the 3D view, its name in
// the legend) and goes when "Show the old drawing" is unticked; the block opens closed (no section
// key) and "Open the section" splits it (the view changes, the section key appears); the ground
// follows the map's Aerial photograph button (the legend says so). Pixels and DOM only.
import { createRequire } from 'module';
const require = createRequire(process.env.NODE_PATH + '/');
const { chromium } = require('playwright-core');
const [url, site, outdir] = process.argv.slice(2);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const failures = [];
const check = (name, cond, info) => {
  console.log((cond ? '[ok] ' : '[FAIL] ') + name + (cond ? '' : ' :: ' + JSON.stringify(info)));
  if (!cond) failures.push(name);
};
const browser = await chromium.launch({ channel: 'chrome', headless: true,
  args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 1280, height: 820 }, colorScheme: 'light' });
const errs = [];
page.on('pageerror', e => errs.push(e.message));
await page.goto(`${url}/#${site}`);
await page.waitForSelector('#t-block', { timeout: 60000 });
await sleep(2500);
// the survey-red share of the 3D view, read off a screenshot of it
const red = async () => {
  const png = (await page.locator('#stage').screenshot()).toString('base64');
  return page.evaluate(async b64 => {
    const im = new Image(); im.src = 'data:image/png;base64,' + b64; await im.decode();
    const c = document.createElement('canvas'); c.width = im.width; c.height = im.height;
    const g = c.getContext('2d'); g.drawImage(im, 0, 0);
    const d = g.getImageData(0, 0, c.width, c.height).data; let n = 0;
    for (let i = 0; i < d.length; i += 4) if (d[i] > 150 && d[i] - d[i + 1] > 70 && d[i] - d[i + 2] > 40) n++;
    return n / (d.length / 4);
  }, png);
};
const legend = () => page.evaluate(() => (document.getElementById('explain') || {}).textContent || '');
// sites open on the aerial photograph: start the block on the LiDAR relief, switch to aerial at the end
if (await page.$('#g-relief')) { await page.click('#g-relief'); await sleep(800); }
await page.click('#t-block');
await page.waitForFunction(() => { const l = document.getElementById('loading'); return l && l.hidden; }, null, { timeout: 60000 });
await sleep(1500);
const r1 = await red(), l1 = await legend();
await page.screenshot({ path: outdir + '/b1-block.png' });
check('block: the old drawing is named in the legend', l1.includes('Old drawing'), l1.slice(0, 300));
check('block: the drawing is draped on the block (survey-red on the 3D view)', r1 > 0.0002, r1);
check('block: opens closed (no section key, Open the section unticked)',
  !l1.includes('Cut through the middle') && await page.evaluate(() => !document.getElementById('b-gap').checked));
const shot = async () => (await page.locator('#stage').screenshot()).toString('base64');
const s1 = await shot();
await page.click('#b-gap'); await sleep(800);
const l2 = await legend(), s2 = await shot();
check('Open the section: the block splits (the view changes) and the section key appears', s2 !== s1 && l2.includes('Cut through the middle'));
await page.screenshot({ path: outdir + '/b2-open.png' });
await page.click('#b-plate'); await sleep(800);
const r3 = await red();
check('unticking Show the old drawing takes it off the block', r3 < r1 * 0.3, { r1, r3 });
await page.click('#b-plate'); await sleep(500);
await page.click('#g-imagery'); await sleep(2500);
const l4 = await legend();
check('the block\'s ground follows the map\'s Aerial photograph button', l4.includes('aerial photograph'), l4.slice(0, 200));
await page.screenshot({ path: outdir + '/b3-aerial.png' });
check('no page errors', errs.length === 0, errs);
console.log(failures.length ? 'RESULT FAIL: ' + failures.join(' | ') : 'RESULT PASS');
await browser.close();
process.exit(failures.length ? 1 : 0);
"""


def _pick_block_site():
    """The first built site (sites.json order) with a block and an old drawing the page opens on (a
    non-empty depictions.json). Derived, never pinned."""
    for s in json.loads((ROOT / "web" / "data" / "sites.json").read_text())["sites"]:
        dep = ROOT / "web" / "data" / "sites" / s["id"] / "depictions.json"
        if s.get("block") and s.get("drawings") and dep.is_file() and json.loads(dep.read_text()).get("depictions"):
            return s["id"]
    return None


def test_block_diagram_carries_the_drawing(served, tmp_path_factory):
    """The owner opens a site whose old drawing shows on the map and switches to Block diagram: the
    drawing is on the block (survey-red pixels in the 3D view, named in the legend) and goes when
    unticked; the block starts closed and Open the section splits it; the block's ground follows the
    map's Aerial photograph button."""
    _headless_or_skip()
    base, _ = served
    site = _pick_block_site()
    assert site, "no built site with a block and an old drawing - vacuous"
    outdir = tmp_path_factory.mktemp("blockshot")
    (outdir / "block_probe.mjs").write_text(BLOCK_PROBE, encoding="utf-8")
    p = subprocess.run(["node", str(outdir / "block_probe.mjs"), base, site, str(outdir)],
                       cwd=str(ROOT), env=dict(os.environ, NODE_PATH=NODE_MODULES),
                       capture_output=True, encoding="utf-8", errors="replace", timeout=300)
    (outdir / "probe.log").write_text(p.stdout + p.stderr, encoding="utf-8")
    assert p.returncode == 0 and "RESULT PASS" in p.stdout, (p.returncode, p.stdout[-4000:], p.stderr[-2000:])
