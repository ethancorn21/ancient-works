"""The 'Ready to fit' queue (task 305), part 1: tools/fit_queue.py on a temp tree, no network.

The queue is the built sites with a candidate picture and no hand fit yet, one entry per site,
best candidate first, ordered so the site most worth seeing comes first. The generator reads
exactly four inputs (web/data/sites.json, the web/data/sites/<id>/ dirs, web/data/plans.json,
the data/review/ item files plus the data/db/platefits/ documents) and never opens an image, so
both tests run it as a subprocess with every socket dead and no Finder/Amazon data anywhere
near: the four-input contract is checked by construction.

  test_fit_queue_synthetic   a small hand-built tree where every rule is pinned exactly: the
                             entry set (built + candidate + no hand fit, with the agent-doc,
                             no-picture-item, not-built and hand-doc-by-filename cases), the
                             candidate dedupe (a plan in both plans.json and an item resolves to
                             the plans row), the best-candidate rule (plan over view, then
                             drawing area, then plan id) and its one-word reason, the synthesized
                             row for a candidate whose only plans row names another site, the
                             site order, and the store's file format (indent=1, no trailing
                             newline, the 13 named row fields in column order).
  test_fit_queue_real        the real checkout's four inputs copied to a temp tree (the site
                             dirs stand in as empty: the rule is existence). The entry set is
                             derived independently from the same four inputs, never pinned to a
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
"""
import json
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

from conftest import get, get_json, put_json

ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    """The hand-built tree: 12 sites in sites.json, 9 built (dirs), 11 plans rows, 5 review
    items, 3 fit documents - every queue rule covered by exactly one case."""
    tree = tmp_path / "tree"
    wd = tree / "web" / "data"
    wd.mkdir(parents=True)
    sites = [
        {"id": s, "name": n, "drawings": 0}
        for s, n in [("s-alpha", "Alpha"), ("s-beta", "Beta"), ("s-gamma", "Gamma"),
                     ("s-eta", "Eta"), ("s-kappa", "Kappa"), ("s-view", "View"),
                     ("s-zeta", "Zeta"), ("s-delta", "Delta"), ("s-epsilon", "Epsilon"),
                     ("s-theta", "Theta"), ("s-iota", "Iota"), ("s-else", "Else")]
    ]
    _save_json(wd / "sites.json", {"sites": sites})
    for sid in ["s-alpha", "s-beta", "s-gamma", "s-eta", "s-kappa", "s-view",
                "s-zeta", "s-delta", "s-epsilon"]:
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
    assert out.splitlines()[0] == f"ready-to-fit queue: 6 site(s) -> {tree / 'web' / 'data' / 'fit_queue.json'}"

    raw = (tree / "web" / "data" / "fit_queue.json").read_bytes()
    q = json.loads(raw)
    # the store's file format: indent=1, no trailing newline
    assert raw == json.dumps(q, indent=1).encode("utf-8")
    assert not raw.endswith(b"\n")
    datetime.fromisoformat(q["at"])

    entries = q["entries"]
    # built + candidate + no hand fit, in the contract's order
    assert [e["site"] for e in entries] == ["s-beta", "s-kappa", "s-eta", "s-alpha", "s-gamma", "s-view"]
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

    # the exclusions: hand documents (both field shapes), no candidate, not built
    for sid in ["s-zeta", "s-delta", "s-epsilon", "s-theta", "s-iota", "s-else"]:
        assert sid not in by


def _h(p):
    return Path(p).read_bytes()


def test_fit_queue_real(tmp_path):
    """The generator on a copy of the real checkout's four inputs (the population is derived,
    never pinned: it moves under the batch tasks)."""
    raw_in = [ROOT / "web" / "data" / "sites.json", ROOT / "web" / "data" / "plans.json"]
    before = {_h(p) for p in raw_in} | {_h(p) for p in (ROOT / "data" / "review").iterdir() if p.is_file()} \
             | {_h(p) for p in (ROOT / "data" / "db" / "platefits").iterdir() if p.is_file()}

    tree = tmp_path / "tree"
    wd = tree / "web" / "data"
    wd.mkdir(parents=True)
    shutil.copy2(raw_in[0], wd / "sites.json")
    shutil.copy2(raw_in[1], wd / "plans.json")
    # the built dirs stand in as empty: the rule is the directory's existence
    for d in (ROOT / "web" / "data" / "sites").iterdir():
        if d.is_dir():
            (wd / "sites" / d.name).mkdir(parents=True)
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

    # the entry set, derived independently from the same four inputs
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
    expected = (built & (row_sites | item_sites)) - hand
    assert {e["site"] for e in entries} == expected
    assert len(entries) == len(expected)

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
    keys = [(bool(e["best"]["row"]["view"]),
             -next(c["draw_px"] for c in e["candidates"] if c["plan"] == e["best"]["plan"]),
             e["name"]) for e in entries]
    assert keys == sorted(keys)

    # the checkout itself is untouched
    after = {_h(p) for p in raw_in} | {_h(p) for p in (ROOT / "data" / "review").iterdir() if p.is_file()} \
            | {_h(p) for p in (ROOT / "data" / "db" / "platefits").iterdir() if p.is_file()}
    assert after == before


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


def _pick_site():
    """The first queue entry the line test can use: a book row whose page is in this checkout's
    data/raw (the line reads it locally), whose site's review item is unresolved and carries that
    row as a candidate with the page's save-floor pairs, and which has no platefits documents yet
    (the line then builds exactly one new overlay: drawings changes by one, the open count drops
    by one, and the item resolves by the saved doc). The pick prefers a site with at least one
    uncovered row (a row naming it, no doc, no item candidate), so the line's model=None path
    runs and lands in the item as "no model answer"; a pick without one skips that assertion.
    Derived, never pinned (803: the population moves under the batch tasks).
    -> (entry, item, uncovered) or None."""
    q = json.loads((ROOT / "web" / "data" / "fit_queue.json").read_text())
    items = {}
    for p in (ROOT / "data" / "review").glob("*.json"):
        it = json.loads(p.read_text())
        if it.get("site"):
            items[it["site"]] = it
    picks = []
    for e in q["entries"]:
        row = e["best"]["row"]
        ia, file_ = row.get("ia"), row.get("file")
        if not (ia and file_):
            continue  # a book row: the page's save needs ia/file, and the line reads the page locally
        if not (ROOT / "data" / "raw" / "books" / ia / "full" / file_).is_file():
            continue  # no local page: the line would need the network
        it = items.get(e["site"])
        if not it or (it.get("resolved") or {}).get("doc"):
            continue  # an unresolved item, so the line's export resolves it by the saved doc
        cand = next((c for c in it.get("candidates") or [] if c.get("plan") == row["id"]), None)
        if not cand or len(cand.get("pairs") or []) < 3:
            continue  # the page's save floor for a similarity fit
        docs = {json.loads(p.read_text()).get("plan")
                for p in (ROOT / "data" / "db" / "platefits").glob("*.json")
                if p.name.startswith(e["site"] + ".")}
        if docs:
            continue  # an existing doc would make the line build a second overlay
        item_plans = {c.get("plan") for c in it["candidates"]}
        uncovered = [r["id"] for r in _rows_naming(ROOT, e["site"])
                     if r["id"] not in docs and r["id"] not in item_plans]
        picks.append((e, it, uncovered))
    if not picks:
        return None
    picks.sort(key=lambda p: not p[2])  # an uncovered row first: the no-model path runs
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
    for d in ("web", "server", "tools", "fit", "pipeline"):
        shutil.copytree(str(ROOT / d), str(tree / d))

    def ignore(d, names):
        return [n for n in names if os.path.join(d, n) == str(ROOT / "data" / "raw")]

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
            m = re.match(r"Ancient Works on (\S+)", line)
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
    (303). The line's model is None and every socket in the server process is dead, so the run is
    network-free: any unfitted candidate lands in the item as "no model answer" (checked when the
    picked site has one - the pick prefers it), and the page is read from the tree's own
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
    # candidate (when the pick has any) went to the item as "no model answer" (the line has no
    # model); the file did not move (its lead candidate is unchanged) ----
    item_path2, item_after = _item_of(tree, site)
    assert item_path2 == item_path
    assert item_after["resolved"] == {"doc": doc_id, "at": AT}
    uncovered = [r["id"] for r in _rows_naming(tree, site)
                 if r["id"] != plan and r["id"] not in {c.get("plan") for c in item_before["candidates"]}]
    if uncovered:
        after_cands = {c["plan"]: c for c in item_after["candidates"]}
        for u in uncovered:
            assert after_cands.get(u, {}).get("why") == "no model answer", u

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

CHROME = "/opt/google/chrome/chrome"
NODE_MODULES = "/home/agent/tools/shot/node_modules"

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
    # MapLibre aborts relief-tile fetches that leave the map's view during the card's flyTo
    # (a page-caused reqfail, expected); no other request may fail at the network level
    assert not any(ln.startswith("[reqfail]") and "/tiles/" not in ln for ln in p.stdout.splitlines()), \
        p.stdout[-2000:]
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
    # MapLibre aborts relief-tile fetches that leave the map's view during the card's flyTo
    # (a page-caused reqfail, expected); no other request may fail at the network level
    assert not any(ln.startswith("[reqfail]") and "/tiles/" not in ln for ln in p.stdout.splitlines()), \
        p.stdout[-2000:]
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
