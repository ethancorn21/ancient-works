"""The batch, EU (task 203b, GOAL points 1-2): fit/batch_eu.py, hermetic, in the retired form.

The EU batch (203b) imports 203a's fitting loop from fit/batch_us.py and points it at every
non-US built site; the vision model's fitting pass is retired (GOAL point 2, 2026-10-13), so
the loop calls no model, runs no gate and writes no documents - the pretrained matcher
(fit/matchfit.py) is the only automatic fitter and it belongs to the one-site line. This
test runs the imported loop on a fixed sample of EU sites against a throwaway tree (web/ +
data/, hard-linked exactly like 203a's test - the tree is mostly read-only data and
data/raw stays a symlink it never follows; no server: the loop is a file-based loop that
never PUTs, so there is no port at all; no model either: the per-candidate verdicts are the
test's own recorded inputs - the three clauses the matcher records - passed as `run_eu`'s
`reasons`, and a socket-blocking fixture fails loudly on any connection attempt). An
uncovered candidate becomes a review item entry whose `why` is the matcher's recorded
reason; a run without reasons records "no matcher on this machine" (the recorded
environment fact). A candidate that already has a document (hand or matcher) is skipped,
never re-fit; a site with no candidate at all gets the batch's "no picture found" item.

The sample (all in web/data/sites.json as of this test; the sample sites are the test's
fixed inputs - if plans.json gains rows for them the loop still ends every candidate with
a doc or an item, and a future 203b session extends the sample for an intended change):

- the 6 region-less sites (203b's must-not-drop set: region None is part of the EU list
  by definition): newark (21 book candidates across five books - the workhorse), forthill
  (4), marietta (4); fudge, highbank and hopeton (zero candidates, but an old-style
  site.json hand fit each: the "already hand-fitted" bucket, no item - the merged loop's
  `and not rec["pre_fit"]` guard);
- yeavering-bell-camp-q17643662 (England): zero candidates, no hand fit, the cover
  search's no-picture item - the run re-stamps it with the batch's searched wording,
  candidates stays empty, resolved stays null;
- avebury and old-sarum (England, already hand-fitted via platefit docs): a candidate
  with an existing doc is skipped, never re-fit; the other candidates become item
  entries carrying the recorded reasons.

After the runs the 22 golden hand-fit documents and the 49 matcher documents (plus the
19 hand-fit site.json files) are byte-identical; the 6 region-less site.json files are
NOT in that golden and are hashed by this test itself, pre and post. The union check
(box 2) is asserted in the weaker form over the temp tree; the full 0-missing /
0-in-both / 0-orphans assertion runs against the live checkout, skip-gated until
docs/batch_eu.md's "Sites run" matches the live EU partition (a merge may grow sites.json
in the meantime; 212 re-covers the growth).
"""
import hashlib
import json
import os
import random
import re
import shutil
import socket
import sys
from pathlib import Path

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "fit"))
import batch_us  # noqa: E402  203a's loop: the EU batch imports it, never copies it
import batch_eu  # noqa: E402
import propose  # noqa: E402

GOLDEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "golden", "hand_fit_docs.sha256")

NEWARK = "newark"
FORTHILL = "forthill"
MARIETTA = "marietta"
# The 6 sites with no region field at all (203b's must-not-drop set). fudge, highbank and
# hopeton have zero candidates but an old-style site.json hand fit.
REGIONLESS = [FORTHILL, "fudge", "highbank", "hopeton", MARIETTA, NEWARK]
# Yeavering Bell (England): zero candidates, no hand fit, the cover search's no-picture item.
NO_PIC = "yeavering-bell-camp-q17643662"
AVEBURY = "avebury-q661855"
OLDSARUM = "old-sarum-q782719"

# The recorded environment fact: a plan the matcher never saw (it was not reachable).
NO_MATCHER = "no matcher on this machine"

# The three clauses the matcher (238) records per candidate: the judge's ("not sure"), the
# gate's (the matcher's fit was refused) and the unreachable picture. The test's recorded
# verdicts take one per plan id, deterministically.
_VERDICTS = ("not sure: 8 consistent points (need 10)",
             "median residual 106.4 m > 45.0 m",
             "picture not on this machine")


# ---------------------------------------------------------------- fixtures


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """Hermetic: every connection attempt fails loudly (nothing in this test needs a socket)."""
    def dead(*_a, **_k):
        raise AssertionError("the batch test attempted a network connection")
    monkeypatch.setattr(socket.socket, "connect", dead)
    monkeypatch.setattr(socket, "create_connection", dead)


def _link_tree(src, dst):
    """The throwaway tree: every file hard-linked (zero disk use on this machine), a real copy
    only for the files the batch rewrites in place, symlinked subdirectories (data/raw -> the
    shared image store) re-linked as symlinks and never followed. Writes to the batch's own
    outputs are all atomic new inodes (os.replace), so they never touch the linked originals."""
    for dirpath, dirnames, filenames in os.walk(src):
        rel = os.path.relpath(dirpath, src)
        d = dst if rel == "." else os.path.join(dst, rel)
        os.makedirs(d, exist_ok=True)
        for name in dirnames:
            s = os.path.join(dirpath, name)
            if os.path.islink(s):  # data/raw: a symlink to the shared store, not a directory
                os.symlink(os.readlink(s), os.path.join(d, name))
        for name in filenames:
            s, t = os.path.join(dirpath, name), os.path.join(d, name)
            if os.path.islink(s):
                os.symlink(os.readlink(s), t)
            elif os.path.relpath(s, src) in _WRITE_IN_PLACE:
                shutil.copy2(s, t)
            else:
                try:
                    os.link(s, t)
                except OSError:  # different filesystem: a read-only symlink keeps it cheap
                    os.symlink(s, t)


# The files the batch rewrites in place (write_report's Path.write_text truncates its target):
# they must be real copies or the in-place write would land in this checkout. docs/ is not
# linked into the tree at all today, but the set stays explicit: if a later session links it,
# docs/batch_eu.md (written in place once it exists after the working run) must be a copy.
_WRITE_IN_PLACE = {"docs/batch_eu.md"}


@pytest.fixture()
def tree(tmp_path):
    """A throwaway view of the product tree (web/ + data/), hard-linked; the batch writes here only."""
    t = tmp_path / "aw203b"
    t.mkdir()
    _link_tree(os.path.join(ROOT, "web"), str(t / "web"))
    _link_tree(os.path.join(ROOT, "data"), str(t / "data"))
    return str(t)


@pytest.fixture()
def tmp_path_retention_policy():
    """Keep only failed runs' temp trees: the trees are hard-linked (near-zero disk) and the
    driver's 48 GB box has filled twice on retained copies."""
    return "failed"


# ---------------------------------------------------------------- helpers


def _sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _golden():
    out = {}
    for line in open(GOLDEN):
        h, p = line.split("  ")
        out[p.strip()] = h
    return out


def _rows():
    return batch_us._plans_rows(ROOT)


def _row_for(sid, plan):
    """The plans.json row of (site, plan) - the site's own candidate row, not a global id-
    keyed dict: a plan id may sit on two rows naming different sites (the Larned duplicate
    c_ffb3daac218b481f: one row per site, with a per-site url), and a by-id dict would return
    the wrong site's row for one of them."""
    for r in batch_us.candidates(sid, _rows()):
        if r["id"] == plan:
            return r
    raise KeyError(plan)


def _sites(root):
    return batch_us._sites(root)


def _pre(root, sid):
    return [p for p, _ in batch_us.pre_docs(root, sid)]


def _item_files(root, sid):
    """The paths of the review item files for a site in this tree (any name, keyed by the
    site field; one per site is 201's invariant)."""
    d = Path(root) / "data" / "review"
    if not d.is_dir():
        return []
    return [p for p in sorted(d.iterdir())
            if p.suffix == ".json" and json.loads(p.read_text()).get("site") == sid]


def _item(root, sid):
    """The parsed review item for a site in this tree, or None."""
    fs = _item_files(root, sid)
    return json.loads(fs[0].read_text()) if fs else None


def _source_evidence(root, row):
    """200's evidence field of the picture's source row, looked up directly from the jsonl files
    (the same lookup the item writer does, re-implemented here)."""
    if row["id"].startswith("c_"):
        p = Path(root) / "data" / "commons" / "files.jsonl"
        if not p.is_file():
            return None
        for line in p.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                t = r.get("title")
                if t and "c_" + hashlib.sha1(t.encode("utf-8")).hexdigest()[:16] == row["id"]:
                    return r.get("evidence")
        return None
    p = Path(root) / "data" / "books" / "index.jsonl"
    if not p.is_file():
        return None
    for line in p.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            if r.get("id") == row["id"]:
                return r.get("evidence")
    return None


def _recorded_reasons(sids):
    """The test's recorded matcher verdicts, state-aware: one per LIVE candidate (the live
    tree's plans.json), one of the three recorded clauses per plan id by sha1. `run_sites`
    must carry each one through, verbatim, to the item entry it writes for that plan."""
    out = {}
    for sid in sids:
        for r in batch_us.candidates(sid, _rows()):
            out[r["id"]] = _VERDICTS[int(hashlib.sha1(r["id"].encode()).hexdigest(), 16) % 3]
    return out


def _check_entry(sid, row, entry, why):
    """A review-item candidate the retired batch wrote (201's shape): the picture, the 200
    evidence field when present, 202's proposed starting placement (or the coarse fallback)
    and the matcher's recorded reason - no pairs (the matcher's points ride in its own
    document) and no gate score (the batch calls no gate)."""
    assert entry["plan"] == row["id"]
    assert entry.get("title") == (row.get("title") or row.get("label") or "")
    assert entry.get("url") == (row["url"] if row.get("url") else
                                ("books/%s/%s" % (row["ia"], row["file"]) if row.get("ia") else None))
    assert entry["why"] == why
    assert entry.get("evidence") == _source_evidence(ROOT, row)
    assert entry.get("pairs") == []
    assert "gate_score" not in entry
    # 202's proposal, the very call the batch makes (2-arg: the checkout's own data, which
    # the tree hard-links) - the same result, or the coarse fallback on its exceptions
    try:
        p = propose.propose_for(sid, row["id"])
    except (ValueError, KeyError):
        assert entry.get("coarse") is True
        return
    for k in ("coarse", "ground", "scale_m_px", "rot_deg", "scale_source", "note"):
        if p.get(k) is not None:
            assert entry.get(k) == p[k]


def _sample():
    """The 6 region-less sites plus the no-picture site: the hermetic sample (the only
    non-US sites whose expected outcome is fully determined by in-repo data)."""
    return REGIONLESS + [NO_PIC]


def _output_files(root):
    """The names of every file under the batch's two output directories (relative paths)."""
    out = set()
    for d in ("data/db/platefits", "data/review"):
        base = Path(root) / d
        if base.is_dir():
            for p in base.iterdir():
                if p.suffix == ".json":
                    out.add(str(p.relative_to(root)))
    return out


def _table(text, header):
    """The first column of the markdown table under the given section header."""
    lines = text.splitlines()
    i = lines.index(header)
    rows = []
    for ln in lines[i + 1:]:
        if not ln.startswith("|"):
            if rows:
                break
            continue
        cells = [c.strip() for c in ln.strip("|").split("|")]
        if cells[0] in ("doc", "---", "site"):
            continue
        rows.append(cells[0])
    return rows


def _syn_records(n_sites, n_per_site):
    """Records with n_sites * n_per_site automatic docs, for the 20-of-20-or-more sample
    branch (the retired batch writes none of its own, so the branch is pinned with
    synthetic records)."""
    out = {}
    for i in range(n_sites):
        sid = "syn-site-%d" % i
        auto = ["syn-plan-%d-%d" % (i, j) for j in range(n_per_site)]
        out[sid] = {"site": sid, "pre_fit": False, "pre_docs": [], "auto": auto, "item": False,
                    "no_picture": False,
                    "detail": {p: {"outcome": "auto", "score": 1.0} for p in auto}}
    return out


# ---------------------------------------------------------------- tests


def test_sample_run_records_reasons(tree):
    """The retired loop over the sample: every uncovered candidate ends as a review item
    entry carrying the recorded reason verbatim (no pairs, no gate score, 202's proposal
    fields); a documented candidate is skipped, never re-fit; untouched entries survive
    whole; the no-candidate hand-fitted sites stay untouched (no item); the no-picture
    site's item is re-stamped with the batch's searched wording."""
    sample = _sample()
    rows_all = _rows()
    # Snapshot the pre-run state BEFORE the run: pre_docs matches any existing <site>.*.json
    # file, so a post-run snapshot would read the tree as it is after, not before.
    pre_docs_before = {sid: _pre(tree, sid) for sid in sample}
    pre_fit_before = {sid: batch_us.is_pre_fit(tree, sid) for sid in sample}
    pre_items = {sid: _item(tree, sid) for sid in sample}
    reasons = _recorded_reasons(sample)
    records = batch_us.run_sites(tree, sample, reasons)
    assert sorted(records) == sorted(sample)

    for sid in sample:
        rec = records[sid]
        pre = set(pre_docs_before[sid])
        cands = batch_us.candidates(sid, rows_all)
        assert set(rec["detail"]) == {r["id"] for r in cands}
        for plan, d in rec["detail"].items():
            if plan in pre:  # a documented picture: skipped, never re-fit
                assert d == {"outcome": "skip"}, (sid, plan, d)
            else:  # an uncovered picture: the recorded reason, verbatim
                assert d == {"outcome": "item", "why": reasons[plan]}, (sid, plan, d)
        assert rec["auto"] == []  # the retired batch writes no documents
        assert rec["pre_fit"] == pre_fit_before[sid]
        uncov = [r["id"] for r in cands if r["id"] not in pre]
        no_picture = not cands and not rec["pre_fit"]
        assert rec["no_picture"] == no_picture
        assert rec["item"] == bool(uncov or no_picture)
        if not rec["item"]:  # nothing written: the item stays as it was (or absent)
            assert _item(tree, sid) == pre_items[sid]
            continue
        assert len(_item_files(tree, sid)) == 1  # the lead follows candidates[0]: it cannot move
        it = _item(tree, sid)
        assert it is not None and it["site"] == sid
        # resolved is write-once: the upsert never clears or changes it
        assert it.get("resolved") == (pre_items[sid] or {}).get("resolved")
        if no_picture:
            assert it["candidates"] == []
            nph = it["no_picture_found"]
            assert nph["searched"] == \
                "web/data/plans.json (%d rows, matched by the sites field)" % len(rows_all)
            assert nph.get("at")
        else:
            old = {c["plan"]: c for c in (pre_items[sid] or {}).get("candidates", [])}
            assert {c["plan"] for c in it["candidates"]} == set(old) | set(uncov)
            for c in it["candidates"]:
                if c["plan"] in uncov:
                    _check_entry(sid, _row_for(sid, c["plan"]), c, reasons[c["plan"]])
                else:  # a candidate this run did not touch: it survives whole
                    assert c == old[c["plan"]]

    # fudge / highbank / hopeton: zero candidates, an old-style hand fit each -> the
    # "already hand-fitted" bucket with NO no-picture item (the loop's `and not rec["pre_fit"]`
    # guard) and no file written at all
    for sid in ("fudge", "highbank", "hopeton"):
        rec = records[sid]
        assert rec["pre_fit"] and not rec["auto"] and not rec["item"] and not rec["no_picture"]
        assert _item(tree, sid) is None

    # the no-picture site: zero candidates, no hand fit -> its item is re-stamped with the
    # batch's searched wording (the cover search's record is replaced); candidates stays
    # empty, resolved stays null, and with no lead candidate the file name stays <site>.json
    rec = records[NO_PIC]
    assert rec["no_picture"] and rec["item"] and not rec["auto"] and not rec["pre_fit"]
    it = _item(tree, NO_PIC)
    assert it["site"] == NO_PIC and it["candidates"] == []
    assert it.get("resolved") == (pre_items[NO_PIC] or {}).get("resolved")
    nph = it["no_picture_found"]
    assert nph["searched"] == "web/data/plans.json (%d rows, matched by the sites field)" % len(rows_all)
    assert nph.get("at")
    assert (Path(tree) / "data" / "review" / (NO_PIC + ".json")).is_file()  # no lead: the name stays


def test_no_reasons_records_no_matcher(tree):
    """The CLI form (no `reasons`): the matcher never saw any candidate (it is not
    reachable from this loop at all), so every uncovered candidate is recorded with the
    recorded environment fact - in the detail and in the item entry. Entries the upsert
    did not touch keep their old reasons."""
    sample = _sample()
    records = batch_eu.run_eu(tree)
    uncov = {plan for r in records.values() if not r.get("error")
             for plan, d in r["detail"].items() if d["outcome"] == "item"}
    assert uncov, "the sample must have an uncovered candidate"
    for sid, r in records.items():
        if sid not in set(sample):
            continue
        for plan, d in r["detail"].items():
            if d["outcome"] == "item":
                assert d["why"] == NO_MATCHER, (sid, plan, d)
        if r["item"]:
            it = _item(tree, sid)
            for c in it["candidates"]:
                if c["plan"] in uncov:
                    assert c["why"] == NO_MATCHER, (sid, c["plan"], c)


def test_batch_adds_items_rewrites_none(tree):
    """After the run the 22 golden hand-fit documents and the 19 hand-fit site.json files
    are byte-identical to the golden hashes; the 6 region-less site.json files (not in that
    golden) are byte-identical pre and post; every pre-existing file under data/ or web/
    stays byte-identical except the sample sites' own review items - the upsert's
    live-merge contract re-saves an item it touches (a re-upserted no-picture record
    carries a fresh timestamp), so those must keep their site, resolved and every
    candidate plan instead; no new file anywhere except the sample sites' review items -
    in particular none under data/db/platefits (the retired batch writes no documents)."""
    golden = _golden()
    assert {rel: _sha(os.path.join(tree, rel)) for rel in golden} == golden  # the copy is pre-batch
    old_style = ["data/sites/%s/site.json" % s for s in REGIONLESS]

    def all_files():
        out = {}
        for top in ("data", "web"):
            base = Path(tree) / top
            for f in base.rglob("*"):
                if f.is_file():
                    out[str(f.relative_to(tree))] = _sha(f)
        return out

    before = all_files()
    old_before = {rel: before[rel] for rel in old_style if rel in before}
    assert set(old_before) == set(old_style)  # all six exist in the tree
    sample = set(_sample())
    # the sample sites' own item files: the only pre-existing files the run may re-save
    review_before = {}
    for rel in before:
        if rel.startswith("data/review/") and rel.endswith(".json"):
            it = json.loads((Path(tree) / rel).read_text())
            if it.get("site") in sample:
                review_before[rel] = {"site": it["site"],
                                      "resolved": it.get("resolved"),
                                      "plans": {c["plan"] for c in it.get("candidates", [])}}
    batch_us.run_sites(tree, _sample())
    after = all_files()

    for rel, h in before.items():
        if rel in review_before:  # the upsert may re-save the sample's own items
            it = json.loads((Path(tree) / rel).read_text())
            assert it.get("site") == review_before[rel]["site"], rel
            assert it.get("resolved") == review_before[rel]["resolved"], \
                "the upsert must never clear or change resolved: %s" % rel
            assert review_before[rel]["plans"] <= {c["plan"] for c in it.get("candidates", [])}, \
                "a candidate plan was dropped: %s" % rel
        else:  # the batch rewrites nothing else
            assert after.get(rel) == h, "the batch rewrote %s" % rel
    for rel, h in golden.items():  # the hand fits: byte-identical to the golden
        assert after.get(rel) == h, "a hand-fit file changed: %s" % rel
    for rel, h in old_before.items():  # the old-style hand fits: byte-identical pre and post
        assert after.get(rel) == h, "an old-style site.json changed: %s" % rel
    new = [rel for rel in after if rel not in before]
    assert not [rel for rel in new if rel.startswith("data/db/platefits/")], \
        "the retired batch wrote documents: %s" % new
    for rel in new:
        assert rel.startswith("data/review/"), \
            "the batch wrote outside its own outputs: %s" % rel
        assert json.loads((Path(tree) / rel).read_text())["site"] in sample, rel


def test_report(tree, tmp_path):
    """Box 3: docs/batch_eu.md in the format of docs/batch_us.md, written by batch_eu's
    write_report: deterministic for the same records (byte-identical twice), the counts
    (no automatic fit anymore; a hand-fitted site with an item stays in its bucket), the
    shared recorded seed, the seeded sample of automatically accepted fits (empty for the
    retired batch; the 20-of-20-or-more branch pinned with synthetic records), and the
    union section (the weaker form over the temp tree; the full assertion is the live
    test below). The default path is pinned to docs/batch_eu.md, never docs/batch_us.md."""
    sample = _sample()
    records = batch_us.run_sites(tree, sample)
    p1, p2 = tmp_path / "r1.md", tmp_path / "r2.md"
    batch_eu.write_report(tree, records, path=p1)
    batch_eu.write_report(tree, records, path=p2)
    assert p1.read_bytes() == p2.read_bytes()
    text = p1.read_text()
    assert text.startswith("# The batch, EU (203b)")
    assert "Seed: %d" % batch_us.SEED in text  # the shared seed (20261010), 203a's constant
    assert "Sites run: %d" % len(sample) in text
    counts = batch_us.classify(records)
    assert counts["automatic fit"] == []  # the retired batch writes no documents
    for k in ("automatic fit", "review item", "already hand-fitted", "no picture found"):
        assert "- %s: %d" % (k, len(counts[k])) in text
    # the bucket split the EU sample is expected to produce (state-aware: classify checks
    # pre_fit before item, so a hand-fitted site with an item stays in its bucket; a new
    # row of the no-picture site would move it to review item)
    assert counts["already hand-fitted"] == sorted(
        s for s in REGIONLESS if batch_us.is_pre_fit(tree, s))
    if batch_us.candidates(NO_PIC, _rows()):
        assert counts["no picture found"] == [] and NO_PIC in counts["review item"]
    else:
        assert counts["no picture found"] == [NO_PIC] and NO_PIC not in counts["review item"]
    header = "## Sample of automatically accepted fits (for the human's 18/20 check)"
    assert _table(text, header) == ["(none)"]
    # the union section: exactly what union_section renders over the tree's state, at the end
    assert text.endswith(batch_eu.union_section(batch_eu.union_check(tree)))
    m = re.search(r"Coverage: (\d+) covered, (\d+) missing, (\d+) in both", text)
    assert m and int(m.group(3)) == 0
    n_sites = len(_sites(tree))
    assert int(m.group(1)) + int(m.group(2)) == n_sites
    check = batch_eu.union_check(tree)
    assert "the %d with no region field are in the other list: %s" % (
        len(check["regionless"]), ", ".join(check["regionless"])) in text
    # the default path is pinned to docs/batch_eu.md (batch_us's own default is never written)
    out = batch_eu.write_report(tree, records)
    assert out == str(Path(tree) / "docs" / "batch_eu.md")
    assert Path(out).read_bytes() == p1.read_bytes()
    assert not (Path(tree) / "docs" / "batch_us.md").exists()

    # the seeded sample of automatically accepted fits, through this module's writer,
    # pinned with synthetic records: the exact list the seed reproduces
    big = _syn_records(2, 11)  # 22 auto docs: the 20-of-20-or-more branch
    q1 = tmp_path / "q1.md"
    batch_eu.write_report(tree, big, path=q1)
    docs = _table(q1.read_text(), header)
    big_auto = sorted("%s.%s" % (r["site"], p) for r in big.values() for p in r["auto"])
    assert docs == random.Random(batch_us.SEED).sample(big_auto, 20)


def test_hand_fitted_sites_get_items_for_their_other_pictures(tree):
    """The already-hand-fitted EU sites: a candidate whose doc exists (a golden hand fit,
    or a matcher document a working run left behind) is skipped - never re-fit; the fresh
    candidates become item entries carrying the recorded reasons (merged into the item a
    working run may have left, never replaced as a whole; the untouched entries survive
    whole); no new document for any fresh candidate. The expectations are state-aware:
    the same test runs before and after any working phase (a later run turns some fresh
    candidates into pre-docs)."""
    sample = [AVEBURY, OLDSARUM]
    rows_all = _rows()
    before = {sid: set(_pre(tree, sid)) for sid in sample}
    live = {sid: _item(tree, sid) for sid in sample}
    golden = _golden()
    golden_before = {rel: _sha(os.path.join(tree, rel)) for rel in golden}
    reasons = _recorded_reasons(sample)
    records = batch_us.run_sites(tree, sample, reasons)
    for sid in sample:
        rec = records[sid]
        cands = [r["id"] for r in batch_us.candidates(sid, rows_all)]
        fresh = [p for p in cands if p not in before[sid]]
        assert rec["pre_fit"] and not rec["auto"] and not rec["no_picture"]
        for plan in before[sid] & set(cands):  # a pre-existing doc's row: skipped, never re-fit
            assert rec["detail"][plan] == {"outcome": "skip"}
        for plan in fresh:
            assert rec["detail"][plan] == {"outcome": "item", "why": reasons[plan]}
        assert rec["item"] == bool(fresh)  # one entry per fresh candidate
        if not fresh:
            assert _item(tree, sid) == live[sid]
            continue
        it = _item(tree, sid)
        assert it is not None and it["site"] == sid
        assert len(_item_files(tree, sid)) == 1  # merged, never a second item file
        assert it["resolved"] == (live[sid] or {}).get("resolved")  # write-once
        assert it["no_picture_found"] is None
        # the merged candidate set: the working run's entries survive, the fresh ones are added
        old = {c["plan"]: c for c in (live[sid] or {}).get("candidates", [])}
        assert {c["plan"] for c in it["candidates"]} == set(old) | set(fresh)
        assert (Path(tree) / "data" / "review" /
                ("%s.%s.json" % (sid, it["candidates"][0]["plan"]))).is_file()  # the lead
        for c in it["candidates"]:
            if c["plan"] in fresh:
                _check_entry(sid, _row_for(sid, c["plan"]), c, reasons[c["plan"]])
            else:  # an entry this run did not touch: it survives whole
                assert c == old[c["plan"]]
        for plan in fresh:  # a fresh candidate writes an item entry, never a doc
            assert not (Path(tree) / "data" / "db" / "platefits" / ("%s.%s.json" % (sid, plan))).exists()
    # the hand-fit docs (and the site.json files) of these sites stay byte-identical
    for rel, h in golden_before.items():
        assert _sha(os.path.join(tree, rel)) == h, "a hand-fit file changed: %s" % rel


def test_union_check(tree):
    """Box 2, the weaker form over the temp tree: the partition lists come from sites.json
    alone and are disjoint (union = every built site, the 6 region-less in the EU list);
    the sample sites end covered; there are no orphan files, no bad doc names; and the EU
    run wrote no file naming a site outside its own sample (never a US site)."""
    before = _output_files(tree)
    sample = set(_sample())
    batch_us.run_sites(tree, _sample())
    check = batch_eu.union_check(tree)
    sites = _sites(tree)
    assert check["in_both"] == []
    assert set(check["us"]) | set(check["eu"]) == set(sites)
    assert set(check["regionless"]) == {s for s in sites if not sites[s].get("region")}
    assert set(REGIONLESS) <= set(check["regionless"])
    for sid in sample:  # box 1, per site: a fit (pre-existing or new) or an open item
        assert check["covered"][sid]["covered"]
    assert not check["orphan_docs"] and not check["orphan_items"] and not check["bad_doc_names"]
    for p in _output_files(tree) - before:  # every file this run wrote
        sid = json.loads((Path(tree) / p).read_text()).get("site")
        assert sid in sample, "the EU run named a site outside its own sample: %s" % p


def test_union_full_coverage_live():
    """Box 2, the full form, against the live checkout (read-only): every built site is
    covered exactly once - 0 missing, 0 in both, 0 orphans, no bad doc names. Meaningful
    only once both batches' working runs are committed, so skip-gated until docs/batch_eu.md's
    'Sites run' matches the live EU partition: a merge may grow sites.json in the
    meantime (the live population is never pinned here - 212 re-covers the growth), and a
    stale report must not pass."""
    sites = _sites(ROOT)
    eu = batch_eu.eu_sites(ROOT)
    report = Path(ROOT) / "docs" / "batch_eu.md"
    if not report.is_file():
        pytest.skip("the EU working run has not happened yet (docs/batch_eu.md missing)")
    m = re.search(r"Sites run: (\d+)", report.read_text())
    if not m or int(m.group(1)) != len(eu):
        pytest.skip("docs/batch_eu.md's 'Sites run' (%s) does not match the live EU list "
                    "(%d): the population changed since the run" % (m and m.group(1), len(eu)))
    check = batch_eu.union_check(ROOT)
    assert check["in_both"] == []
    assert check["orphan_docs"] == [] and check["orphan_items"] == []
    assert check["bad_doc_names"] == []
    assert check["missing"] == [], \
        "built sites without a fit or an open item: %s" % ", ".join(check["missing"])
    for sid in check["regionless"]:
        assert check["covered"][sid]["covered"]
