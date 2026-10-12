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

The page card and the save -> line step (the rest of the acceptance boxes) land with the
serve.py worker: tests/test_fit_queue.py grows a part 2 then.
"""
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest

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
