"""The one-site line (task 300): tools/site_done.py, end to end, hermetic - with Stonehenge's
fabrication-check incident re-seeded, so the check itself is re-verified on every run (task 301).

The batch's gate passes the model's documented fabrication class by construction (the gate scores
the fit against the same points the model invented - docs/gate.md section 7), so the line
re-checks every document's stored page-px pairs with plan_fit.fabrication_pattern before syncing:
a pattern document is never built, its candidate is upserted into the site's review item with the
reason, and its fit document is deleted. This test re-creates that incident in the system temp
dir and runs the copied line on it:

  seed   the 7 fabricated Stonehenge documents, recovered verbatim from git history
         (tests/golden/stonehenge_linecheck_docs/), back into the tree's data/db/platefits, and
         the site's review item rewound to the 6 batch candidates the line's upsert only appended
         to; the site dir and sites.json stay exactly as in the repo (2 survey maps, 0 drawings);
  run    the copied line (this checkout's code, run against the copied data, sockets dead - any
         network attempt fails loudly: the pretrained matcher is unreachable so it is never
         called, and no picture is fetched);
  check  exit 0; the per-picture report, line by line (7 "sent to the review queue (line check:
         ...)" and no overlay built); the site's depictions.json and sites.json byte-identical to
         the repo's (the entry stays at 0 drawings); the upserted item byte-identical to the
         repo's current 13-candidate item (the run reproduces the live run exactly); the 7
         pattern documents gone from the tree's store; every other item and every other fit
         document byte-identical (a one-site run touches only that site's files); the published
         review page's queue equal to the repo's. Then a second run: 0 documents -> no batch
         run, the 13 item candidates reported, and only the review page's timestamp changed.

The preconditions are pinned like test_batch_us pins its sample: the repo holds no Stonehenge
documents; its item holds exactly the 7 "line check:" candidates the golden documents would
produce (recomputed with the line's own _pattern_entry - so drift in the check, the documents,
or the evidence rows fails loudly); and plans.json's 13 Stonehenge rows equal the documents plus
the item's other 6 candidates (the no-batch-run precondition). If any of that changes, this test
fails before it seeds and must be extended on purpose.
"""
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SID = "stonehenge-q39671"
GOLDEN = ROOT / "tests" / "golden" / "stonehenge_linecheck_docs"

# The subprocess guard: every socket dies loudly, then the copied command runs exactly
# as `tools/site_done.py <site>` would (runpy with run_name="__main__" executes its
# __main__ block; site_done resolves its data root from its own path, so the COPIED
# code runs on the COPIED data, never on this checkout).
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


def _item():
    """The site's review item (path, dict) in this checkout, keyed by its site field."""
    for p in sorted((ROOT / "data" / "review").glob("*.json")):
        item = json.loads(p.read_text())
        if item.get("site") == SID:
            return p, item
    return None, None


def _rows():
    """The site's candidate pictures: the web/data/plans.json rows naming it."""
    d = json.loads((ROOT / "web" / "data" / "plans.json").read_text())
    cols = {c: i for i, c in enumerate(d["cols"])}
    rows = [{k: r[i] for k, i in cols.items()} for r in d["rows"]]
    return [r for r in rows if SID in (r.get("sites") or [])]


def _save_json(path, obj):
    """Same convention as fit/review.py _save_json (indent=1, no trailing newline)."""
    path = Path(path)
    tmp = str(path) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1)
    os.replace(tmp, path)


# The line under test, loaded from this checkout (its own sys.path inserts make batch_us,
# build_site, plan_fit and review import exactly as they do in the subprocess).
def _load_site_done():
    spec = importlib.util.spec_from_file_location("site_done_under_test", ROOT / "tools" / "site_done.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SITE_DONE = _load_site_done()
plan_fit = SITE_DONE.plan_fit
review = SITE_DONE.review


def _golden_docs():
    """The 7 fabricated Stonehenge documents, recovered from git history, by plan id."""
    docs = {}
    for f in sorted(GOLDEN.glob("*.json")):
        doc = json.loads(f.read_text())
        docs[doc["plan"]] = doc
    return docs


def _preconditions():
    """Fail loudly if the repo state this test pins has drifted (before anything is seeded)."""
    golden_files = sorted(GOLDEN.glob("*.json"))
    if len(golden_files) != 7:
        pytest.fail(f"tests/golden/stonehenge_linecheck_docs must hold exactly the 7 deleted "
                    f"Stonehenge pattern documents, found {len(golden_files)}")
    docs = {}
    for f in golden_files:
        doc = json.loads(f.read_text())
        if doc.get("site") != SID or doc.get("plan") != f.name[len(SID) + 1:-5]:
            pytest.fail(f"golden doc {f.name} no longer matches its file name/site")
        docs[doc["plan"]] = doc

    if list((ROOT / "data" / "db" / "platefits").glob(SID + ".*.json")):
        pytest.fail(f"the repo holds {SID} fit documents again: the test expects the post-line state "
                    "(the line deleted them; the goldens are the record)")

    item_path, item = _item()
    if item is None:
        pytest.fail(f"the {SID} review item is missing")
    cands = item.get("candidates") or []
    pat = [c for c in cands if (c.get("why") or "").startswith("line check:")]
    orig = [c for c in cands if not (c.get("why") or "").startswith("line check:")]
    # the batch part grows as new pictures of the site arrive (6 in 2026-10-11, 7 since the 211 pictures)
    if len(pat) != 7 or not orig:
        pytest.fail(f"the {SID} item no longer holds the 7 line check entries plus batch ones; "
                    f"found {len(cands)} ({len(pat)} line check, {len(orig)} batch)")
    if {c["plan"] for c in pat} != set(docs):
        pytest.fail("the item's line-check candidates and the golden documents disagree on plans")
    if {c["plan"] for c in orig} & set(docs):
        pytest.fail("the item's batch candidates and the golden documents overlap on plans")

    # the check still fires, and the repo's recorded entry is exactly what the line would build today
    for plan, doc in docs.items():
        pattern = plan_fit.fabrication_pattern(doc.get("pairs") or [])
        if not pattern:
            pytest.fail(f"the line's fabrication check no longer fires on golden doc {plan}: the check drifted")
        expected = SITE_DONE._pattern_entry(doc, pattern, str(ROOT))
        actual = next(c for c in pat if c["plan"] == plan)
        if actual != expected:
            pytest.fail(f"the recorded line-check entry for {plan} no longer matches what the line "
                        f"would build today (drift in the golden doc, the check, or the evidence row): "
                        f"recorded {actual}, rebuilt {expected}")

    rows = _rows()
    row_ids = {r["id"] for r in rows}
    covered = set(docs) | {c["plan"] for c in orig}
    if covered != row_ids:
        pytest.fail(f"plans.json no longer lists exactly the item's {len(cands)} {SID} candidates "
                    f"({len(rows)} rows): the no-batch-run precondition is void")

    rr = json.loads((ROOT / "web" / "data" / "review.json").read_text())
    for e in rr["items"]:
        if e.get("site") == SID:
            if e.get("candidates") != cands:
                pytest.fail("the published review page's Stonehenge entry no longer matches its item file")
            return
    pytest.fail("the open review page no longer lists the Stonehenge item")


def _build_tree(tmp_path, docs, item, pre_item):
    """The throwaway tree: the code, the site's data as in the repo, the full review queue and
    fit document store, plus the 7 golden pattern documents and the item rewound to pre-line."""
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
    for f in sorted(GOLDEN.glob("*.json")):
        shutil.copy2(f, pf / f.name)
    # the commons row store: _pattern_entry records the 200 evidence field from here
    cd = tree / "data" / "commons"
    cd.mkdir(parents=True)
    shutil.copy2(ROOT / "data" / "commons" / "files.jsonl", cd / "files.jsonl")
    # the item rewound to pre-line: the upsert only appended the 7 line-check candidates,
    # so removing them restores the file the batch left (written in the item's own convention)
    _save_json(tree / "data" / "review" / Path(item).name, pre_item)
    return tree


def _run(tree):
    """The command on the tree: `tools/site_done.py <site>` (copied code, copied data; sockets
    dead: the matcher is unreachable and never called)."""
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    return subprocess.run([sys.executable, "-c", GUARD, str(tree / "tools" / "site_done.py"), SID],
                          cwd=str(tree), env=env, capture_output=True, timeout=600)


def test_site_done_line(tmp_path):
    _preconditions()
    docs = _golden_docs()
    item_path, item = _item()
    cands = item["candidates"]
    pat = {c["plan"]: c for c in cands if (c.get("why") or "").startswith("line check:")}
    orig = [c for c in cands if c["plan"] not in pat]
    pre_item = {**item, "candidates": list(orig)}
    rows = _rows()
    n_open = len(json.loads((ROOT / "web" / "data" / "review.json").read_text())["items"])
    n_total = len(list((ROOT / "data" / "review").glob("*.json")))
    review_json = json.loads((ROOT / "web" / "data" / "review.json").read_text())

    checkout = [ROOT / "web" / "data" / "sites.json",
                ROOT / "web" / "data" / "review.json",
                ROOT / "web" / "data" / "plans.json",
                ROOT / "web" / "data" / "sites" / SID,
                ROOT / "data" / "review",
                ROOT / "data" / "catalog",
                ROOT / "data" / "db" / "platefits",
                ROOT / "data" / "commons" / "files.jsonl",
                GOLDEN]
    before = _hash_all(checkout)

    tree = _build_tree(tmp_path, docs, item_path, pre_item)
    proc = _run(tree)
    out = proc.stdout.decode("utf-8")
    err = proc.stderr.decode("utf-8")
    assert proc.returncode == 0, out + err
    assert err == ""
    lines = out.splitlines()
    site = tree / "web" / "data" / "sites" / SID
    patterns = {p: plan_fit.fabrication_pattern(d["pairs"]) for p, d in docs.items()}

    # the whole run, line by line: the seeded pattern documents hit the pre-sync check, go to
    # the item with the reason, and are deleted - none of them is built
    assert lines[0] == f"site {SID}: the one-site line (fit -> sync -> entry -> review)"
    assert lines[1] == (f"fit  {len(rows)} candidate picture(s): {len(docs)} fitted (doc), "
                        f"{len(orig)} in the review item -> no batch run needed")
    for plan in sorted(docs):
        title = docs[plan].get("title") or plan
        assert f"sync {title}: sent to the review queue (line check: {patterns[plan]})" in lines
    assert f"entry  web/data/sites.json: drawings 0 -> 0" in lines
    review_line = (f"review {Path(item_path).name}: {len(cands)} candidate(s), open; "
                   f"page now has {n_open} open of {n_total} items")
    assert review_line in lines
    # the per-picture report: every candidate picture named, and only the line's own lines exist
    expected_summary = []
    for row in sorted(rows, key=lambda r: r["id"]):
        pid, title = row["id"], row.get("title") or row.get("label") or pid
        if pid in patterns:
            sc = f", gate {docs[pid].get('score')} m" if docs[pid].get("score") is not None else ""
            expected_summary.append(f"  {title} ({pid}): sent to the review queue (line check: {patterns[pid]}{sc})")
        else:
            cand = next(c for c in orig if c["plan"] == pid)
            gate = cand.get("gate_score")
            why = (f"gate {gate} m - " if gate is not None else "") + (cand.get("why") or "no model answer")
            expected_summary.append(f"  {title} ({pid}): sent to the review queue ({why})")
    assert lines[lines.index(review_line) + 1:] == expected_summary + ["done"]
    assert len(lines) == 2 + len(docs) + 2 + len(rows) + 1

    # nothing was built: the site dir is still exactly the repo's (2 survey maps, 0 drawings)
    assert {f.name for f in site.iterdir() if f.name.startswith("plan_")} == set()
    assert (site / "depictions.json").read_bytes() == \
        (ROOT / "web" / "data" / "sites" / SID / "depictions.json").read_bytes()
    assert (tree / "web" / "data" / "sites.json").read_bytes() == \
        (ROOT / "web" / "data" / "sites.json").read_bytes()
    # the upserted item is byte-identical to the repo's current 13-candidate item: the run
    # reproduces the live run exactly (same entries, same order, same serialization)
    assert (tree / "data" / "review" / Path(item_path).name).read_bytes() == Path(item_path).read_bytes()
    # the pattern documents are gone, so a later batch run re-fits the pictures
    assert list((tree / "data" / "db" / "platefits").glob(SID + ".*.json")) == []
    # a one-site run touches only that site's files: every other item and every other document
    for name in sorted(set(os.listdir(tree / "data" / "review")) | set(os.listdir(ROOT / "data" / "review"))):
        assert _h(tree / "data" / "review" / name) == _h(ROOT / "data" / "review" / name), name
    for name in sorted(set(os.listdir(tree / "data" / "db" / "platefits")) |
                      set(os.listdir(ROOT / "data" / "db" / "platefits"))):
        assert _h(tree / "data" / "db" / "platefits" / name) == _h(ROOT / "data" / "db" / "platefits" / name), name
    # the published page: the same open queue as the repo's (only the timestamp is new)
    tr = json.loads((tree / "web" / "data" / "review.json").read_text())
    assert tr["items"] == review_json["items"]
    assert _hash_all(checkout) == before  # and the checkout itself is untouched

    # a second run: the documents are gone, so every picture is an item candidate; the line
    # re-confirms and changes nothing but the review page's timestamp
    hashes = _hash_all([site, tree / "web" / "data" / "sites.json", tree / "web" / "data" / "review.json",
                        tree / "data" / "review", tree / "data" / "db" / "platefits"])
    proc2 = _run(tree)
    out2 = proc2.stdout.decode("utf-8")
    assert proc2.returncode == 0, out2 + proc2.stderr.decode("utf-8")
    lines2 = out2.splitlines()
    assert lines2[0] == lines[0]
    assert lines2[1] == (f"fit  {len(rows)} candidate picture(s): 0 fitted (doc), "
                         f"{len(cands)} in the review item -> no batch run needed")
    assert not any(l.startswith("sync ") for l in lines2)
    # every picture is reported from the item: the 7 line-check candidates with their
    # recorded reason and gate score, the 6 batch candidates with theirs
    expected_summary2 = []
    for row in sorted(rows, key=lambda r: r["id"]):
        title = row.get("title") or row.get("label") or row["id"]
        cand = next(c for c in cands if c["plan"] == row["id"])
        gate = cand.get("gate_score")
        why = (f"gate {gate} m - " if gate is not None else "") + (cand.get("why") or "no model answer")
        expected_summary2.append(f"  {title} ({row['id']}): sent to the review queue ({why})")
    assert lines2[lines2.index(review_line) + 1:] == expected_summary2 + ["done"]
    # nothing but the review page's timestamp changed
    review_key = _key(tree / "web" / "data" / "review.json")
    assert _hash_all([site, tree / "web" / "data" / "sites.json",
                      tree / "data" / "review", tree / "data" / "db" / "platefits"]) == \
        {k: v for k, v in hashes.items() if k != review_key}
    tr2 = json.loads((tree / "web" / "data" / "review.json").read_text())
    assert tr2["items"] == review_json["items"]
    assert _hash_all(checkout) == before
