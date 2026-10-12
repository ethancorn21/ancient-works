"""Fit provenance (task 303): every platefit document says who placed it, and the line never
passes an agent fit as a hand fit.

The store's contract (data/db/platefits): "by": "hand" (the page's save - server/serve.py stamps
it on every PUT, the owner's word on every pair) or "by": "agent" (every script/session path -
the batch stamps it in fit/batch_us.py write_doc; an agent session does the same). A document
without the mark is an agent fit only when it carries the batch's own "auto" mark (a batch
document predating the mark - the store self-heals it by stamping by: agent); any other unmarked
document has no provenance the line can act on and is refused (plan_fit.who_placed, build,
main; tools/site_done.py).

The cases, all hermetic (temp trees in the system temp dir, sockets dead or the network never
needed, ephemeral ports):

  a. the repo's store: every document has a trustworthy mark (by in hand/agent) or at least
     the batch's own auto mark (never unmarked non-auto - agent c's 203b may merge pre-migration
     EU documents, which the self-heal stamps at the next sync); the hand set is exactly the
     golden's 21 entries (the 20 golden hand fits + Maiden Castle's DPLA plan), byte-for-byte
     (sha256sum -c tests/golden/hand_fit_docs.sha256).
  b. the one-site line refuses an unmarked non-auto document end to end (the copied line run
     on a copy of Stonehenge's files, sockets dead, no model - the refusal precedes the build,
     so nothing is downloaded): the document is kept byte-identical (no stamp, no delete),
     nothing is built, and its candidate goes to the site's review item with
     plan_fit.NO_PROVENANCE verbatim - NOT the fabrication check's reason, even though the
     document's pairs ARE the model's pattern class (the refusal precedes the check: an
     unmarked pattern document is refused, not sent). 201's derived resolution then applies:
     the export records resolved {doc, at} into the item file (write-once) and the item leaves
     the page's open list - the refusal record stays in the item file, the page never shows it
     (the 201 contract a human may change, not 303's). The second run is byte-stable with
     identical lines: refusal is idempotent.
  c. an unmarked auto document is an agent fit - never hand, never refused: the 301 pattern
     document is sent to the item and deleted (as test_site_done_line pins it end to end); a
     non-pattern document with a current overlay is stamped by: agent into its file (key last,
     indent=1, no trailing newline) and skipped; and a PATTERN document with a current overlay
     is skipped when marked by: hand (the fabrication check polices the batch model, never a
     human's drag - a pattern document returns "skipped" only if the check did not fire) but
     sent and deleted when marked by: agent: the same pairs, one mark apart.
  d. the page's save is the owner's word: the real server (serve.py --port 0 against a temp
     tree with no pipeline/ - the fit worker dies on import, so no sweep and no network)
     stamps by: hand on every PUT to platefits (a stale by is overwritten in place, a new by
     lands last) and leaves every other collection's bytes raw.
"""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest

ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SID = "stonehenge-q39671"
SEED_PLAN = "c_022604d2be0becdc"  # one of the 7 golden Stonehenge pattern documents
LINECHECK_DOCS = ROOT / "tests" / "golden" / "stonehenge_linecheck_docs"
GOLDEN_SHA = ROOT / "tests" / "golden" / "hand_fit_docs.sha256"

# The subprocess guard: every socket dies loudly, then the copied command runs exactly
# as `tools/site_done.py <site>` would (the copied code runs on the copied data, never on
# this checkout - see tests/test_site_done.py).
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


def _h(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _key(p):
    """The file's identity in a hash map: repo-relative inside this checkout, absolute in the temp tree."""
    p = Path(p)
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


def _hash_all(paths):
    """Hash every file under the given paths (files directly, directories one level deep -
    every data dir here is flat): the proof the run wrote nothing outside the tree."""
    out = {}
    for p in paths:
        p = Path(p)
        if p.is_dir():
            for f in sorted(p.iterdir()):
                if f.is_file():
                    out[_key(f)] = _h(f)
        else:
            out[_key(p)] = _h(p)
    return out


def _save_json(path, obj):
    """Same convention as the doc store (indent=1, no trailing newline)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = str(path) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1)
    os.replace(tmp, path)


def _doc_bytes(doc):
    return json.dumps(doc, indent=1).encode("utf-8")


# The line under test, loaded from this checkout (its own sys.path inserts make batch_us,
# build_site, plan_fit and review import exactly as they do in the subprocess).
def _load_site_done():
    spec = importlib.util.spec_from_file_location("site_done_under_test", ROOT / "tools" / "site_done.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SITE_DONE = _load_site_done()
plan_fit = SITE_DONE.plan_fit


def _golden_doc(plan):
    """One of the 7 deleted Stonehenge pattern documents, recovered verbatim from git history."""
    return json.loads((LINECHECK_DOCS / f"{SID}.{plan}.json").read_text())


def _item(root):
    """The site's review item (path, dict) in the given tree, keyed by its site field."""
    for p in sorted((Path(root) / "data" / "review").glob("*.json")):
        item = json.loads(p.read_text())
        if item.get("site") == SID:
            return p, item
    return None, None


def _rows(root):
    """The site's candidate pictures: the web/data/plans.json rows naming it."""
    d = json.loads((Path(root) / "web" / "data" / "plans.json").read_text())
    cols = {c: i for i, c in enumerate(d["cols"])}
    rows = [{k: r[i] for k, i in cols.items()} for r in d["rows"]]
    return [r for r in rows if SID in (r.get("sites") or [])]


def _run(tree):
    """The one-site line on the copied tree: `tools/site_done.py <site>`, no model."""
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    return subprocess.run([sys.executable, "-c", GUARD, str(tree / "tools" / "site_done.py"), SID],
                          cwd=str(tree), env=env, capture_output=True, timeout=600)


def put_json(url, obj, timeout=10):
    req = urllib.request.Request(url, data=json.dumps(obj).encode(), method="PUT",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read()


def get_json(url, timeout=10):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return r.status, json.loads(r.read())


# ---------------------------------------------------------------------------
# a. the repo's store
# ---------------------------------------------------------------------------

def test_every_doc_carries_provenance():
    """Every document in data/db/platefits/ says who placed it (or at least carries the batch's
    own auto mark); the hand set is exactly the golden's 21 entries, byte-for-byte."""
    platefit_entries = []
    for ln in GOLDEN_SHA.read_text().splitlines():
        m = re.match(r"^[0-9a-f]{64}\s+(data/db/platefits/[^ ]+)$", ln)
        if m:
            platefit_entries.append(m.group(1))
    assert len(platefit_entries) == 21, \
        f"the golden now holds {len(platefit_entries)} platefit entries, not 21 - extend this test on purpose"

    store = ROOT / "data" / "db" / "platefits"
    hand, unmarked_auto = set(), 0
    for f in sorted(store.iterdir()):
        if not f.is_file() or f.suffix != ".json":
            continue
        doc = json.loads(f.read_text())
        by = doc.get("by")
        if by in ("hand", "agent"):
            if by == "hand":
                hand.add(str(f.relative_to(ROOT)))
        elif doc.get("auto"):
            unmarked_auto += 1  # a pre-migration batch document: the store self-heals it
        else:
            pytest.fail(f"{f.name}: no 'by' and not the batch's own auto - the line cannot place it "
                        f"(page saves write hand; agent paths write agent)")
    golden_files = set(platefit_entries)
    assert hand == golden_files, \
        f"hand set drifted from the golden: extra {sorted(hand - golden_files)}, missing {sorted(golden_files - hand)}"
    # the golden is byte-for-byte: no hand fit's pairs were ever moved
    p = subprocess.run(["sha256sum", "-c", str(GOLDEN_SHA)], cwd=ROOT,
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stdout[-2000:] + p.stderr[-500:]
    assert unmarked_auto >= 0  # (no assertion: the count legitimately changes as 203b's docs are stamped)


# ---------------------------------------------------------------------------
# b. the line refuses an unmarked non-auto document (end to end)
# ---------------------------------------------------------------------------

def _preconditions_b():
    """Fail loudly if the repo state this test seeds has drifted (before anything is copied)."""
    if list((ROOT / "data" / "db" / "platefits").glob(SID + ".*.json")):
        pytest.fail(f"the repo holds {SID} fit documents again: the test expects the post-line state "
                    "(the line deleted them; the goldens are the record)")
    item_path, item = _item(ROOT)
    if item is None:
        pytest.fail(f"the {SID} review item is missing")
    if len(item["candidates"]) != 13:
        pytest.fail(f"the {SID} item no longer holds 13 candidates; found {len(item['candidates'])}")
    if SEED_PLAN not in {c["plan"] for c in item["candidates"]}:
        pytest.fail(f"the {SID} item no longer lists {SEED_PLAN}: the seed's upsert could not replace it in place")
    if (item["candidates"][0]["plan"] == SEED_PLAN):
        pytest.fail(f"{SEED_PLAN} became the item's lead: the upsert would move the item file, breaking the test")
    doc = _golden_doc(SEED_PLAN)
    if not doc.get("auto") or doc.get("by") in ("hand", "agent"):
        pytest.fail(f"golden doc {SEED_PLAN} is no longer an unmarked auto document: the seed premise is void")
    if plan_fit.fabrication_pattern(doc.get("pairs") or []) is None:
        pytest.fail(f"the line's fabrication check no longer fires on golden doc {SEED_PLAN}: the check drifted")
    if plan_fit.who_placed({k: v for k, v in doc.items() if k != "auto"}) is not None:
        pytest.fail("the seed (the golden doc with its auto mark stripped) is not unplaced anymore: the premise is void")
    if len(_rows(ROOT)) != 13:
        pytest.fail(f"plans.json no longer lists 13 {SID} candidates: the no-batch-run precondition is void")
    rr = json.loads((ROOT / "web" / "data" / "review.json").read_text())
    if not any(e.get("site") == SID for e in rr["items"]):
        pytest.fail("the open review page no longer lists the Stonehenge item")
    return item_path, item


def _build_tree_b(tmp_path, seed):
    """The throwaway tree: the code, the site's data as in the repo, the full review queue and
    fit document store - plus the seed: one golden pattern document with its auto mark
    stripped (unmarked, non-auto: the 303 case)."""
    tree = tmp_path / "tree"
    for d in ("tools", "fit", "pipeline"):
        shutil.copytree(ROOT / d, tree / d, ignore=shutil.ignore_patterns("__pycache__"))
    wd = tree / "web" / "data"
    wd.mkdir(parents=True)
    for name in ("plans.json", "review.json", "sites.json"):
        shutil.copy2(ROOT / "web" / "data" / name, wd / name)
    shutil.copytree(ROOT / "web" / "data" / "sites" / SID, wd / "sites" / SID)
    shutil.copytree(ROOT / "data" / "review", tree / "data" / "review")
    # 309's right-place check names its unbuilt right sites from the catalog: the line's
    # export reads it (an absent store would warn on those items, and this test asserts no warnings)
    cd = tree / "data" / "catalog"
    cd.mkdir()
    shutil.copy2(ROOT / "data" / "catalog" / "sites.jsonl", cd / "sites.jsonl")
    pf = tree / "data" / "db" / "platefits"
    pf.mkdir(parents=True)
    for f in sorted((ROOT / "data" / "db" / "platefits").iterdir()):
        if f.is_file():
            shutil.copy2(f, pf / f.name)
    _save_json(pf / f"{SID}.{SEED_PLAN}.json", seed)  # the seed: unmarked non-auto
    # the commons row store: the refused entry records the 200 evidence field from here
    cd = tree / "data" / "commons"
    cd.mkdir(parents=True)
    shutil.copy2(ROOT / "data" / "commons" / "files.jsonl", cd / "files.jsonl")
    return tree


def test_line_refuses_unmarked_non_auto_doc(tmp_path):
    item_path, item = _preconditions_b()
    seed = {k: v for k, v in _golden_doc(SEED_PLAN).items() if k != "auto"}
    resolved = f"{SID}.{SEED_PLAN}"
    n_item = len(item["candidates"])
    item_name = item_path.name

    checkout = [ROOT / "web" / "data" / "sites.json",
                ROOT / "web" / "data" / "review.json",
                ROOT / "web" / "data" / "plans.json",
                ROOT / "web" / "data" / "sites" / SID,
                ROOT / "data" / "review",
                ROOT / "data" / "catalog",
                ROOT / "data" / "db" / "platefits",
                ROOT / "data" / "commons" / "files.jsonl",
                LINECHECK_DOCS]
    before = _hash_all(checkout)

    tree = _build_tree_b(tmp_path, seed)
    proc = _run(tree)
    out = proc.stdout.decode("utf-8")
    err = proc.stderr.decode("utf-8")
    assert proc.returncode == 0, out + err
    assert err == "", err
    lines = out.splitlines()

    # the whole run, line by line: the unmarked non-auto document is refused - refused
    # precedes everything (no build, no delete, no fabrication check)
    assert lines[0] == 'fit  no model given: unfitted pictures (if any) go to the review item as "no model answer"'
    assert lines[1] == f"site {SID}: the one-site line (fit -> sync -> entry -> review)"
    assert lines[2] == (f"fit  {n_item} candidate picture(s): 1 fitted (doc), "
                        f"{n_item - 1} in the review item -> no batch run needed")
    assert lines[3] == f"sync {seed.get('title') or SEED_PLAN}: refused ({plan_fit.NO_PROVENANCE})"
    assert lines[4] == "entry  web/data/sites.json: drawings 0 -> 0"
    n_open = len(json.loads((ROOT / "web" / "data" / "review.json").read_text())["items"])
    n_total = len(list((ROOT / "data" / "review").glob("*.json")))
    assert lines[5] == (f"review {item_name}: {n_item} candidate(s), resolved by {resolved}; "
                        f"page now has {n_open - 1} open of {n_total} items")
    # the per-picture report: every candidate picture named, and only the line's own lines exist
    expected = []
    for row in sorted(_rows(ROOT), key=lambda r: r["id"]):
        pid, title = row["id"], row.get("title") or row.get("label") or row["id"]
        if pid == SEED_PLAN:
            expected.append(f"  {title} ({pid}): refused ({plan_fit.NO_PROVENANCE})")
        else:
            cand = next(c for c in item["candidates"] if c["plan"] == pid)
            gate = cand.get("gate_score")
            why = (f"gate {gate} m - " if gate is not None else "") + (cand.get("why") or "no model answer")
            expected.append(f"  {title} ({pid}): sent to the review queue ({why}); the item is resolved by {resolved}")
    assert lines[6:6 + len(expected)] == expected
    assert lines[6 + len(expected)] == "done"
    assert len(lines) == 6 + len(expected) + 1

    # the document is kept byte-identical: no stamp, no delete (a good hand fit that lost its
    # mark is not destroyed)
    seed_path = tree / "data" / "db" / "platefits" / f"{SID}.{SEED_PLAN}.json"
    assert seed_path.is_file()
    assert seed_path.read_bytes() == _doc_bytes(seed)
    # nothing was built: the site dir is still exactly the repo's (2 survey maps, 0 drawings)
    site = tree / "web" / "data" / "sites" / SID
    assert {f.name for f in site.iterdir() if f.name.startswith("plan_")} == set()
    assert (site / "depictions.json").read_bytes() == (ROOT / "web" / "data" / "sites" / SID / "depictions.json").read_bytes()
    assert (tree / "web" / "data" / "sites.json").read_bytes() == (ROOT / "web" / "data" / "sites.json").read_bytes()
    # the review item: still at its own path (the lead is a book row, so the upsert kept the
    # name); the refused candidate is exactly what the line's own _provenance_entry builds -
    # why is plan_fit.NO_PROVENANCE verbatim, not the fabrication check's reason
    item_tree = tree / "data" / "review" / item_name
    assert item_tree.is_file()
    it = json.loads(item_tree.read_text())
    assert it["site"] == SID
    assert it["resolved"] == {"doc": resolved, "at": seed.get("at")}  # 201's derived resolution, write-once
    got = next(c for c in it["candidates"] if c["plan"] == SEED_PLAN)
    assert got == SITE_DONE._provenance_entry(seed, str(tree))
    assert got["why"] == plan_fit.NO_PROVENANCE
    assert (got["why"] or "").startswith("line check:") is False
    assert [c for c in it["candidates"] if c["plan"] != SEED_PLAN] == \
        [c for c in item["candidates"] if c["plan"] != SEED_PLAN]  # the other 12, in place
    assert len(it["candidates"]) == n_item
    # the page: the item left the open list (a refused document resolves its item by 201's
    # contract) - everything else on the page is exactly the repo's
    repo_open = json.loads((ROOT / "web" / "data" / "review.json").read_text())["items"]
    tr = json.loads((tree / "web" / "data" / "review.json").read_text())
    assert tr["items"] == [e for e in repo_open if e["site"] != SID]
    # a one-site run touches only that site's files: every other item and every other document
    # (the site's own item is the one file the line rewrote - checked above, in content and shape)
    for name in sorted(set(os.listdir(tree / "data" / "review")) | set(os.listdir(ROOT / "data" / "review"))):
        if name == item_name:
            continue
        assert _h(tree / "data" / "review" / name) == _h(ROOT / "data" / "review" / name), name
    for name in sorted(set(os.listdir(tree / "data" / "db" / "platefits")) |
                      set(os.listdir(ROOT / "data" / "db" / "platefits"))):
        if name == f"{SID}.{SEED_PLAN}.json":
            continue  # the seed exists only in the tree; its bytes were checked above
        assert _h(tree / "data" / "db" / "platefits" / name) == _h(ROOT / "data" / "db" / "platefits" / name), name
    assert _hash_all(checkout) == before  # and the checkout itself is untouched

    # a second run: the refusal is idempotent - identical lines, and nothing changes but the
    # review page's timestamp
    hashes = _hash_all([site, tree / "web" / "data" / "sites.json", tree / "web" / "data" / "review.json",
                        tree / "data" / "review", tree / "data" / "db" / "platefits"])
    proc2 = _run(tree)
    out2 = proc2.stdout.decode("utf-8")
    assert proc2.returncode == 0, out2 + proc2.stderr.decode("utf-8")
    assert out2.splitlines() == lines
    review_key = _key(tree / "web" / "data" / "review.json")
    assert _hash_all([site, tree / "web" / "data" / "sites.json",
                      tree / "data" / "review", tree / "data" / "db" / "platefits"]) == \
        {k: v for k, v in hashes.items() if k != review_key}
    tr2 = json.loads((tree / "web" / "data" / "review.json").read_text())
    assert tr2["items"] == tr["items"]
    assert _hash_all(checkout) == before


# ---------------------------------------------------------------------------
# c. an unmarked auto document is an agent fit (never hand, never refused)
# ---------------------------------------------------------------------------

def _call_sync(tree, sid, plan, doc):
    """The one document's sync, in-process (its prints captured): (action, detail, printed line)."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        action, detail = SITE_DONE._sync_doc(str(tree), sid, plan, doc)
    return action, detail, buf.getvalue().strip()


def _mini_tree(base, doc, overlay):
    """The smallest tree _sync_doc needs: the document in its store slot, and (when `overlay`)
    a site dir whose depictions.json already carries this doc's overlay, current (same at,
    same doc id) - so "skipped" needs no download, no model, no network."""
    t = Path(base)
    _save_json(t / "data" / "db" / "platefits" / f"{doc['site']}.{doc['plan']}.json", doc)
    if overlay:
        sd = t / "web" / "data" / "sites" / doc["site"]
        dep = {"depictions": [{"kind": "plan", "file": f"plan_{doc['plan']}.webp",
                               "fit": {"model": "similarity", "at": doc.get("at"),
                                       "doc": f"{doc['site']}.{doc['plan']}"}}]}
        _save_json(sd / "depictions.json", dep)
    return t


def test_unmarked_auto_doc_is_an_agent(tmp_path):
    # the documented truth table, the module's own function
    assert plan_fit.who_placed({}) is None
    assert plan_fit.who_placed({"auto": True}) == "agent"
    assert plan_fit.who_placed({"by": "hand"}) == "hand"
    assert plan_fit.who_placed({"by": "hand", "auto": True}) == "hand"  # the page's save is the owner's word
    assert plan_fit.who_placed({"by": "agent", "auto": True}) == "agent"

    # (i) the 301 pattern document, unmarked auto: treated as agent - never refused; sent to
    # the item with the check's reason and deleted (the e2e twin of this is test_site_done_line)
    doc = _golden_doc(SEED_PLAN)
    assert doc.get("auto") and doc.get("by") not in ("hand", "agent")
    pattern = plan_fit.fabrication_pattern(doc["pairs"])
    assert pattern, "premise: the golden document's pairs are the model's pattern class"
    t1 = _mini_tree(tmp_path / "t1", doc, overlay=False)
    action, detail, line = _call_sync(t1, SID, SEED_PLAN, doc)
    assert (action, detail) == ("sent", pattern)
    assert line == f"sync {doc.get('title') or SEED_PLAN}: sent to the review queue (line check: {pattern})"
    assert not (t1 / "data" / "db" / "platefits" / f"{SID}.{SEED_PLAN}.json").exists()
    item = json.loads((t1 / "data" / "review" / f"{SID}.{SEED_PLAN}.json").read_text())
    assert item["candidates"] == [SITE_DONE._pattern_entry(doc, pattern, str(t1))]

    # (ii) an unmarked auto document with a current overlay: stamped by: agent into its file,
    # then skipped (network-free: the overlay is current, so nothing is downloaded or rebuilt)
    non_pattern = [[13.4, 22.6], [27.9, 55.1], [88.2, 60.8], [121.7, 134.3]]  # dodge every clause
    assert plan_fit.fabrication_pattern(non_pattern) is None, "the test coordinates must stay non-pattern"
    doc2 = {"site": "prov-fake-q1", "plan": "c_f00d000000000001",
            "at": "2026-10-11T00:00:00+00:00", "auto": True, "score": 12.5,
            "pairs": [[u, v, -2.9756073, 53.2282398] for u, v in non_pattern]}
    t2 = _mini_tree(tmp_path / "t2", doc2, overlay=True)
    action, detail, line = _call_sync(t2, "prov-fake-q1", doc2["plan"], doc2)
    assert (action, detail) == ("skipped", None)
    assert line == f"sync {doc2['plan']}: skipped: overlay already current (at {doc2['at']})"
    p2 = t2 / "data" / "db" / "platefits" / f"prov-fake-q1.{doc2['plan']}.json"
    assert p2.read_bytes() == _doc_bytes({**doc2, "by": "agent"})  # key last, indent=1, no trailing newline
    # a second pass reads the file back: the mark is there, so no re-stamp (byte-stable)
    doc2b = json.loads(p2.read_text())
    action2, _, _ = _call_sync(t2, "prov-fake-q1", doc2["plan"], doc2b)
    assert action2 == "skipped"
    assert p2.read_bytes() == _doc_bytes({**doc2, "by": "agent"})

    # (iii) the hand exemption, the same pattern document with a current overlay: marked
    # by: hand it is skipped (a pattern document returns "skipped" ONLY if the check did not
    # fire - the check polices the batch model, never a human's drag); marked by: agent it is
    # sent and deleted. One mark apart.
    for mark, expect in (("hand", "skipped"), ("agent", "sent")):
        doc3 = {**doc, "by": mark}
        t3 = _mini_tree(tmp_path / f"t3_{mark}", doc3, overlay=True)
        action, detail, _ = _call_sync(t3, SID, SEED_PLAN, doc3)
        if mark == "hand":
            assert (action, detail) == ("skipped", None)
            assert (t3 / "data" / "db" / "platefits" / f"{SID}.{SEED_PLAN}.json").read_bytes() == _doc_bytes(doc3)
            assert not list((t3 / "data" / "review").glob("*.json"))  # no candidate upserted: the check never ran
        else:
            assert (action, detail) == ("sent", pattern)
            assert not (t3 / "data" / "db" / "platefits" / f"{SID}.{SEED_PLAN}.json").exists()
            item3 = json.loads((t3 / "data" / "review" / f"{SID}.{SEED_PLAN}.json").read_text())
            assert item3["candidates"] == [SITE_DONE._pattern_entry(doc3, pattern, str(t3))]


# ---------------------------------------------------------------------------
# d. the page's save writes hand (the real server, ephemeral port, no sweep)
# ---------------------------------------------------------------------------

def _serve(tmp_path):
    """serve.py against a temp tree with no pipeline/ (the fit worker dies on import: no
    sweep, no network) and an empty web/. -> (Popen, base_url, tree)."""
    tree = tmp_path / "tree"
    (tree / "web").mkdir(parents=True)
    shutil.copytree(ROOT / "server", tree / "server", ignore=shutil.ignore_patterns("__pycache__"))
    proc = subprocess.Popen([sys.executable, "server/serve.py", "--port", "0"],
                            cwd=str(tree), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    url = None
    deadline = time.time() + 90
    while time.time() < deadline and proc.poll() is None:
        line = proc.stdout.readline()
        m = re.match(r"Ancient Works on (\S+)", line) if line else None
        if m:
            url = m.group(1)
            break
    assert url, "server did not report its address (startup: %r)" % proc.stdout.read()[-2000:]
    return proc, url.rstrip("/"), tree


def test_page_save_stamps_hand(tmp_path):
    proc, base, tree = _serve(tmp_path)
    try:
        doc_path = "provtest-p1.c_aaaabbbbccccdddd"
        doc = {"site": "provtest-p1", "plan": "c_aaaabbbbccccdddd", "crop": [0, 0, 100, 100],
               "pairs": [[13.4, 22.6, -2.9756073, 53.2282398], [827.0, 570.0, -2.974283, 53.2272404]],
               "at": "2026-10-11T00:00:00+00:00", "title": "a fit saved from the page"}
        # a page save without the mark: the server stamps by: hand (key lands last)
        st, body = put_json(base + f"/api/db/platefits/{doc_path}", doc)
        assert st == 200 and json.loads(body) == {"ok": True}
        st, got = get_json(base + f"/api/db/platefits/{doc_path}")
        assert st == 200
        assert got == {**doc, "by": "hand"}
        f = tree / "data" / "db" / "platefits" / (doc_path + ".json")
        assert f.read_bytes() == _doc_bytes({**doc, "by": "hand"})
        # a later save carrying a stale by (a batch or a session wrote it first): the owner's
        # word wins, overwritten in place (the key keeps its position)
        doc2 = {"site": doc["site"], "by": "agent", "plan": doc["plan"], "crop": doc["crop"],
                "pairs": doc["pairs"], "at": doc["at"], "title": doc["title"]}
        st, body = put_json(base + f"/api/db/platefits/{doc_path}", doc2)
        assert st == 200
        st, got = get_json(base + f"/api/db/platefits/{doc_path}")
        assert st == 200
        assert got == {**doc, "by": "hand"}
        assert f.read_bytes() == _doc_bytes({**doc2, "by": "hand"})
        # every other collection passes through raw: no stamp, the bytes are the request's
        st, body = put_json(base + "/api/db/awtest303/t1", {"a": 1, "b": 2})
        assert st == 200
        st, got = get_json(base + "/api/db/awtest303/t1")
        assert st == 200 and got == {"a": 1, "b": 2}
        assert (tree / "data" / "db" / "awtest303" / "t1.json").read_bytes() == \
            _doc_bytes({"a": 1, "b": 2})
        # no sweep: the worker died on import (no pipeline/ in the tree) - nothing outside
        # the two collections' store slots was ever written
        files = {str(p.relative_to(tree)) for p in tree.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
        assert files == {"server/serve.py", "server/relief_tiles.py", "server/aibox/clef_server.py",
                         f"data/db/platefits/{doc_path}.json", "data/db/awtest303/t1.json"}, files
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
