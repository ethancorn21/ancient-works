"""The batch, US (task 203a, GOAL point 2): fit/batch_us.py, hermetic, in the retired form.

The vision model's fitting pass is retired (GOAL point 2, 2026-10-13: "the local Qwen models
never place a drawing and never write point pairs or coordinates"; the pass fabricated ~100
fits on 2026-10-11 that 212b deleted): the batch calls no model, runs no gate and writes no
documents. The pretrained matcher (fit/matchfit.py) is the only automatic fitter and it
belongs to the one-site line, not to this batch. The retired loop runs here on a fixed
sample of US sites against a throwaway tree (web/ + data/, hard-linked - the tree is ~0.5 GB
of mostly-read-only data and the 48 GB disk fills, so the tree hard-links every file and
copies only the one the batch rewrites in place; data/raw stays a symlink to the shared
image store it already points at - and there is no server: the batch is a file-based loop
that never PUTs, so there is no port at all; and no model either: the per-candidate verdicts
are the test's own recorded inputs - the three clauses the matcher records - passed as
`run_sites`' `reasons`, and a socket-blocking fixture fails loudly on any connection
attempt). An uncovered candidate becomes a review item entry whose `why` is the matcher's
recorded reason for that picture (the judge's clause, the gate's clause when the matcher's
fit was refused, "picture not on this machine"); a run without reasons records "no matcher
on this machine" (the recorded environment fact, the 302g pattern). A candidate that
already has a document (hand or matcher) is skipped, never re-fit: the item upsert
replaces a candidate's entry whole, so the skip guard is the only thing protecting the
audit notes. A site with no candidate at all and no pre-existing fit gets the batch's
"no picture found" item. After the runs the 22 golden hand-fit documents and the 49
matcher documents (plus the 19 hand-fit site.json files) are byte-identical: the batch
added review items, it rewrote nothing and writes no documents at all anymore.

The sample (region US): serpent-mound-q968802 (16 candidates, one documented - the
remaining 15 become item entries carrying the recorded reasons), cahokia-q333661 (5
candidates, two documented - the item the matcher already resolved gets its fresh
entries), mound-bottom-q14710093 (its only candidate IS its document: nothing written),
and the first US site, sorted, with no candidate at all today (aberdeen-mound-q4666953:
the "no picture found" item). The sample sites are the test's fixed inputs: if plans.json
gains rows for them the loop still ends every candidate with a doc or an item, and a
future 203a session extends the sample for an intended change.
"""
import hashlib
import json
import os
import random
import shutil
import socket
import sys
from pathlib import Path

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "fit"))
import batch_us  # noqa: E402
import propose  # noqa: E402

GOLDEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "golden", "hand_fit_docs.sha256")

SERPENT = "serpent-mound-q968802"
CAHOKIA = "cahokia-q333661"
MOUNDBOTTOM = "mound-bottom-q14710093"

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
# they must be real copies or the in-place write would land in this checkout. Every other write
# (upsert_item) creates a new inode and never touches a hard-linked original.
_WRITE_IN_PLACE = {"docs/batch_us.md"}


@pytest.fixture()
def tree(tmp_path):
    """A throwaway view of the product tree (web/ + data/), hard-linked; the batch writes here only."""
    t = tmp_path / "aw203a"
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
    """The fixed sample: the three named sites and the first US site, sorted, with no
    candidate at all (the no-picture branch)."""
    zero = [s for s in batch_us.us_sites(ROOT) if not batch_us.candidates(s, _rows())]
    assert zero, "no US site without a candidate left: the no-picture branch has no sample"
    return [SERPENT, CAHOKIA, MOUNDBOTTOM, zero[0]]


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


def _per_candidate_rows(text):
    """The report's per-candidate table: its 5-cell rows, in order."""
    lines = text.splitlines()
    i = lines.index("## Per candidate")
    rows = []
    for ln in lines[i + 1:]:
        if not ln.startswith("|"):
            if rows:
                break
            continue
        cells = [c.strip() for c in ln.strip("|").split("|")]
        if cells[0] in ("site", "---"):
            continue
        rows.append(cells)
    return rows


def _syn_records(n_sites, n_per_site):
    """Records with n_sites * n_per_site automatic docs, for the sample branch (the retired
    batch writes none of its own, so the seeded sample is pinned with synthetic records)."""
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
    whole; a candidate-less site without a pre-fit gets the no-picture item; a fully
    covered site has nothing written."""
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
            rows_by_id = {r["id"]: r for r in cands}
            for c in it["candidates"]:
                if c["plan"] in uncov:
                    _check_entry(sid, rows_by_id[c["plan"]], c, reasons[c["plan"]])
                else:  # a candidate this run did not touch: it survives whole
                    assert c == old[c["plan"]]

    # mound-bottom: its only candidate IS its document - nothing written at all
    rec = records[MOUNDBOTTOM]
    assert rec["pre_fit"]
    assert all(d == {"outcome": "skip"} for d in rec["detail"].values())
    assert not rec["auto"] and not rec["item"] and not rec["no_picture"]
    assert _item(tree, MOUNDBOTTOM) is None

    # the zero-candidate site: the batch's no-picture item (one per site, 201's shape)
    z = sample[-1]
    rec = records[z]
    assert rec["no_picture"] and rec["item"] and not rec["auto"] and not rec["pre_fit"]
    p = Path(tree) / "data" / "review" / (z + ".json")
    assert p.is_file()
    it = json.loads(p.read_text())
    assert it["site"] == z and it["candidates"] == []
    assert it.get("resolved") == (pre_items[z] or {}).get("resolved")
    nph = it["no_picture_found"]
    assert "web/data/plans.json" in nph.get("searched", "") and nph.get("at")


def test_no_reasons_records_no_matcher(tree):
    """The CLI form (no `reasons`): the matcher never saw any candidate (it is not
    reachable from this loop at all), so every uncovered candidate is recorded with the
    recorded environment fact - in the detail and in the item entry. Entries the upsert
    did not touch keep their old reasons."""
    sample = _sample()
    records = batch_us.run_sites(tree, sample)
    uncov = {plan for r in records.values() for plan, d in r["detail"].items()
             if d["outcome"] == "item"}
    assert uncov, "the sample must have an uncovered candidate"
    for sid, r in records.items():
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
    are byte-identical to the golden hashes; every pre-existing file under data/ or web/
    stays byte-identical except the sample sites' own review items - the upsert's
    live-merge contract re-saves an item it touches (a re-upserted no-picture record
    carries a fresh timestamp), so those must keep their site, resolved and every
    candidate plan instead; no new file anywhere except the sample sites' review items -
    in particular none under data/db/platefits (the retired batch writes no documents)."""
    golden = _golden()
    assert {rel: _sha(os.path.join(tree, rel)) for rel in golden} == golden  # the copy is pre-batch

    def all_files():
        out = {}
        for top in ("data", "web"):
            base = Path(tree) / top
            for f in base.rglob("*"):
                if f.is_file():
                    out[str(f.relative_to(tree))] = _sha(f)
        return out

    before = all_files()
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
    new = [rel for rel in after if rel not in before]
    assert not [rel for rel in new if rel.startswith("data/db/platefits/")], \
        "the retired batch wrote documents: %s" % new
    for rel in new:
        assert rel.startswith("data/review/"), \
            "the batch wrote outside its own outputs: %s" % rel
        assert json.loads((Path(tree) / rel).read_text())["site"] in sample, rel


def test_report_reproducible_from_seed(tree, tmp_path):
    """The report is deterministic for the same records and the recorded seed: the counts
    (no automatic fit anymore), the seeded sample of automatically accepted fits (empty
    for the retired batch; the full-sample-is-a-seeded-shuffle and the 20-of-20-or-more
    branches pinned with synthetic records), and the per-candidate table (the recorded
    reason, or the environment fact, per picture)."""
    sample = _sample()
    records = batch_us.run_sites(tree, sample)
    p1, p2 = tmp_path / "r1.md", tmp_path / "r2.md"
    batch_us.write_report(tree, records, path=p1)
    batch_us.write_report(tree, records, path=p2)
    assert p1.read_bytes() == p2.read_bytes()
    text = p1.read_text()
    assert text.startswith("# The batch, US (203a)")
    assert "Seed: %d" % batch_us.SEED in text
    assert "Sites run: %d" % len(sample) in text
    counts = batch_us.classify(records)
    assert counts["automatic fit"] == []  # the retired batch writes no documents
    for k in ("automatic fit", "review item", "already hand-fitted", "no picture found"):
        assert "- %s: %d" % (k, len(counts[k])) in text
    header = "## Sample of automatically accepted fits (for the human's 18/20 check)"
    assert _table(text, header) == ["(none)"]

    # the per-candidate table: "skip" for the documented, the environment fact for the
    # uncovered (the CLI form), the no-picture row for the candidate-less site - sites
    # and plans sorted, the gate column empty (the batch calls no gate)
    expected = []
    for sid in sorted(sample):
        r = records[sid]
        if not r["detail"]:
            outcome = "no-picture" if r.get("no_picture") else "no candidate changed"
            expected.append([sid, "-", outcome, "", ""])
            continue
        for plan in sorted(r["detail"]):
            d = r["detail"][plan]
            if d["outcome"] == "skip":
                expected.append([sid, plan, "skip", "", ""])
            else:
                expected.append([sid, plan, "item", "", NO_MATCHER])
    assert _per_candidate_rows(text) == expected

    # the seeded sample of automatically accepted fits, pinned with synthetic records:
    # a FULL sample is a seeded shuffle of the population, not the sorted order
    small = _syn_records(1, 3)
    s1 = tmp_path / "s1.md"
    batch_us.write_report(tree, small, path=s1)
    small_auto = sorted("%s.%s" % (r["site"], p) for r in small.values() for p in r["auto"])
    assert _table(s1.read_text(), header) == random.Random(batch_us.SEED).sample(small_auto, 3)

    big = _syn_records(2, 11)  # 22 auto docs: the 20-of-20-or-more branch
    q1 = tmp_path / "q1.md"
    batch_us.write_report(tree, big, path=q1)
    qtext = q1.read_text()
    docs = _table(qtext, header)
    big_auto = sorted("%s.%s" % (r["site"], p) for r in big.values() for p in r["auto"])
    assert docs == random.Random(batch_us.SEED).sample(big_auto, 20)
    docsites = {}
    for r in big.values():
        for p in r["auto"]:
            docsites["%s.%s" % (r["site"], p)] = r["site"]
    seen = 0
    for ln in qtext.splitlines():
        if not ln.startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip("|").split("|")]
        if len(cells) == 3 and cells[0] in docs:
            seen += 1
            assert cells[1] == "#" + docsites[cells[0]]  # a page URL per sample fit
            assert cells[2] == "1.0"
    assert seen == 20
