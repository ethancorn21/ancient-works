"""The batch, EU (task 203b, GOAL points 1-2): fit/batch_eu.py, hermetic.

The EU batch (203b) imports 203a's fitting loop from fit/batch_us.py and points it at every
non-US built site; this test runs that imported loop on a fixed sample of EU sites against a
throwaway tree (web/ + data/, hard-linked exactly like 203a's test - the tree is mostly
read-only data and data/raw stays a symlink it never follows; no server: the loop is a
file-based loop that never PUTs, so there is no port at all). No network (a socket-blocking
fixture fails loudly on any connection attempt), no model server: the recorded model's
answers are fixed inputs - 202's deterministic proposals (fit/propose.py) for the pinned
book pictures of the 6 region-less sites, and short two-feature answers for the
already-hand-fitted sites' other candidates - and the real gate (001, docs/gate.md
section 2) scores the placements. Two stub gates (always accept / always reject) pin the
document and item writers independently of the gate's thresholds, on a site computed (not
named) in the test.

The sample (all in web/data/sites.json as of this test; the pinned plan ids are the test's
fixed inputs - if plans.json gains rows for these sites the loop still ends every
candidate with a doc or an item, and a future 203b session extends the lists for an
intended change):

- the 6 region-less sites (203b's must-not-drop set: region None is part of the EU list
  by definition): newark (21 book candidates across five books - the workhorse), forthill
  (4), marietta (4); fudge, highbank and hopeton (zero candidates, but an old-style
  site.json hand fit each: the "already hand-fitted" bucket, no item - the merged loop's
  `and not rec["pre_fit"]` guard);
- bibracte (France): zero candidates, no hand fit, but a 201-era no-picture item - the
  run re-upserts it with the batch's searched wording, candidates stays empty, resolved
  stays null;
- avebury and old-sarum (England, already hand-fitted via platefit docs): a candidate
  with an existing doc is skipped, never re-fit; the other candidates get the short
  two-feature answers and become could-not-fit item entries.

202's 29 proposals on EU ground all pass the frozen gate (DECISIONS 2026-10-11) - the
documented "true case" holds for the region-less sites, so the expected outcome is 29 new
automatic documents, zero items from them, and the three no-candidate hand-fitted sites
untouched. After the runs the 20 pre-batch hand-fit documents and the 19 hand-fit
site.json files are byte-identical (tests/golden/hand_fit_docs.sha256); the 6 region-less
site.json files are NOT in that golden and are hashed by this test itself, pre and post.
The union check (box 2) is asserted in the weaker form over the temp tree; the full
0-missing / 0-in-both / 0-orphans assertion runs against the live checkout, skip-gated
until docs/batch_eu.md's "Sites run" matches the live EU partition (211's merge may grow
sites.json in the meantime; 212 re-covers the growth).
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
sys.path.insert(0, os.path.join(ROOT, "pipeline"))
import batch_us  # noqa: E402  203a's loop: the EU batch imports it, never copies it
import batch_eu  # noqa: E402
import fit_gate  # noqa: E402
import plan_fit  # noqa: E402
import propose  # noqa: E402

GOLDEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "golden", "hand_fit_docs.sha256")

NEWARK = "newark"
FORTHILL = "forthill"
MARIETTA = "marietta"
# The 6 sites with no region field at all (203b's must-not-drop set). fudge, highbank and
# hopeton have zero candidates but an old-style site.json hand fit.
REGIONLESS = [FORTHILL, "fudge", "highbank", "hopeton", MARIETTA, NEWARK]
# bibracte (France): zero candidates, no hand fit, a 201-era no-picture item.
NO_PIC = "bibracte-q650053"
AVEBURY = "avebury-q661855"
OLDSARUM = "old-sarum-q782719"

# The pinned sample inputs: 202's deterministic proposals of these exact pictures are the
# recorded answers. All 29 pass the frozen gate on EU ground (DECISIONS 2026-10-11) - the
# documented "true case" holds for the region-less sites, so the expected outcome is 29
# new automatic documents and zero items from them.
NEWARK_ANSWER_PLANS = [
    "ancientmonuments00squi_n0161_1", "ancientmonuments00squi_n0163_1",
    "ancientmonuments00squi_n0214_4", "annualreportofbu1218901891smit_n0416_1",
    "annualreportofbu1218901891smit_n0422_1", "annualreportofbu1218901891smit_n0580_1",
    "annualreportofbu1218901891smit_n0583_1", "annualreportofbu1218901891smit_n0584_1",
    "annualreportofbu1218901891smit_n0588_1", "annualreportofbu1218901891smit_n0592_1",
    "annualreportofbu1218901891smit_n0596_1", "b24849959_n0186_1", "b24849959_n0187_1",
    "b24849959_n0189_1", "b24849959_n0192_1", "b24849959_n0193_1", "b24849959_n0228_1",
    "b24849959_n0285_1", "descriptionsofan00whit_n0034_4",
    "ArcheologicalAtlasOfOhio_n0098_1", "ArcheologicalAtlasOfOhio_n0152_2",
]
FORTHILL_ANSWER_PLANS = [
    "ancientmonuments00squi_n0068_1", "b24849959_n0269_1", "b24849959_n0270_1",
    "ArcheologicalAtlasOfOhio_n0080_1",
]
MARIETTA_ANSWER_PLANS = [
    "ancientmonuments00squi_n0169_1", "b24849959_n0195_1", "b24849959_n0361_1",
    "ArcheologicalAtlasOfOhio_n0178_1",
]
# The short (two-feature) answers of the already-hand-fitted sites' fresh commons rows:
# 202's proposal trimmed to two pairs - below the four-pair floor, so the loop routes
# them to the review item as "could not fit" (the 201 lead the human finishes by dragging).
AVEBURY_SHORT = [
    "c_47849e3c40949668", "c_ffb3daac218b481f", "c_603d643cf5f87268",
    "c_1d28be9f93f5dbf3", "c_cb1aed83effb7c44",
]
OLDSARUM_SHORT = ["c_041083ec68b532f8", "c_ff62c9585a92b375", "c_b2701b5231da42f2"]

STUB_ACCEPT_SCORE = 12.5
STUB_REJECT = (False, 30.0, "stub: always rejects")


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


def _corner_pairs(site, row):
    """Four well-conditioned pairs: the page-px corners of the row's size frame on the site's
    corners (a real similarity, so plan_fit.similarity stays well conditioned)."""
    w, h = row["size"]
    pts = [(0.05 * w, 0.05 * h), (0.95 * w, 0.05 * h), (0.95 * w, 0.95 * h), (0.05 * w, 0.95 * h)]
    return [[round(u, 1), round(v, 1), round(lon, 7), round(lat, 7)]
            for (u, v), (lon, lat) in zip(pts, site["corners"])]


def _answers():
    """The test's recorded model answers for the 6 region-less sample sites: 202's
    deterministic proposals (five points each) of the pinned pictures, one source of truth
    for both the model the loop is given and the expectations below. bibracte has no
    candidate, so it needs no answer."""
    out = {}
    for sid, plans in ((NEWARK, NEWARK_ANSWER_PLANS),
                       (FORTHILL, FORTHILL_ANSWER_PLANS),
                       (MARIETTA, MARIETTA_ANSWER_PLANS)):
        site = _sites(ROOT)[sid]
        out[sid] = {}
        for plan in plans:
            try:
                out[sid][plan] = {"pairs": propose.propose_for(sid, plan)["pairs"]}
            except (ValueError, KeyError):
                out[sid][plan] = {"pairs": _corner_pairs(site, _row_for(sid, plan))}
    return out


def _short_answers():
    """The already-hand-fitted sites' fresh commons rows: 202's proposal trimmed to two pairs
    (below the four-pair floor of an automatic document) - the could-not-fit item path."""
    out = {}
    for sid, plans in ((AVEBURY, AVEBURY_SHORT), (OLDSARUM, OLDSARUM_SHORT)):
        site = _sites(ROOT)[sid]
        out[sid] = {}
        for plan in plans:
            try:
                pairs = propose.propose_for(sid, plan)["pairs"]
            except (ValueError, KeyError):
                pairs = _corner_pairs(site, _row_for(sid, plan))
            out[sid][plan] = {"pairs": pairs[:2], "note": "only two features matched"}
    return out


def _sample():
    """The 6 region-less sites plus bibracte: the hermetic sample (the only non-US sites
    whose expected outcome is fully determined by in-repo data: the region-less sites have
    tracked ground and 202's recorded proposals, bibracte a pre-existing item)."""
    return REGIONLESS + [NO_PIC]


def _recorded_model():
    return batch_us.recorded_model(_answers())


def _stub_site(tree):
    """The first non-US site with two or more candidates (with a recorded image size) and no
    pre-fit - computed, not named (today alauna-q4708853; a later merge may change which
    site it is, the test must not care)."""
    for sid in batch_eu.eu_sites(tree):
        fresh = [r for r in batch_us.candidates(sid, _rows())
                 if r.get("size") and r["id"] not in _pre(tree, sid)]
        if len(fresh) >= 2 and not batch_us.is_pre_fit(tree, sid):
            return sid
    pytest.fail("no non-US site with two or more candidates and no pre-fit")


def _expected(pairs):
    """What the loop must do with a recorded answer: an automatic doc (>= 4 pairs and the gate
    accepts the placement solved from the same pairs) or an item entry (fewer, or refused)."""
    if not pairs or len(pairs) < 4:
        return "item"
    a, b, _, _ = plan_fit.similarity(pairs)
    verdict, _ = fit_gate.gate(pairs, (a, b))
    return "auto" if verdict == fit_gate.ACCEPT else "item"


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


# ---------------------------------------------------------------- checks


def _check_pairs(pairs, row, min_n=4):
    assert len(pairs) >= min_n
    w, h = row.get("size") or [10**9, 10**9]
    for p in pairs:
        assert len(p) == 4
        u, v, lon, lat = [float(x) for x in p]
        assert u == round(u, 1) and v == round(v, 1)  # the platefit-doc convention: 1 dp px
        assert lon == round(lon, 7) and lat == round(lat, 7)  # and 7 dp lon/lat
        assert 0 <= u <= w and 0 <= v <= h


def _check_crop(crop, row):
    x0, y0, x1, y1 = [int(x) for x in crop]
    w, h = row.get("size") or [0, 0]
    assert 0 <= x0 < x1 <= w and 0 <= y0 < y1 <= h


def _check_doc(tree, sid, row):
    """An automatic document: the page's existing platefit format plus the auto mark and the
    gate's score, which must equal the gate's own measurement of the document's recorded
    anchors (recomputed here, independently of the batch's call)."""
    doc = json.loads((Path(tree) / "data" / "db" / "platefits" / ("%s.%s.json" % (sid, row["id"]))).read_text())
    assert doc["site"] == sid and doc["plan"] == row["id"]
    assert doc["auto"] is True
    assert isinstance(doc["score"], float) and doc["score"] >= 0
    _check_pairs(doc["pairs"], row)
    _check_crop(doc["crop"], row)
    if row.get("ia"):
        assert doc["ia"] == row["ia"] and doc["file"] == row["file"]
        assert doc.get("book") == row.get("book")
        assert doc.get("model") is None and doc.get("src") is None
    else:  # a commons picture: the page's own keys for that kind
        assert doc["model"] == "similarity" and doc["src"] == "commons"
        assert doc["ia"] is None and doc["file"] is None
        assert doc.get("url") == row.get("url") and doc.get("ref") == row.get("ref")
        assert doc.get("size") == row.get("size")
    assert doc.get("label") == (row.get("label") or None)
    assert doc.get("title") == (row.get("title") or None)
    assert doc.get("cite") == (row.get("cite") or None)
    assert isinstance(doc.get("at"), str) and doc["at"]
    a, b, _, _ = plan_fit.similarity(doc["pairs"])
    verdict, stats = fit_gate.gate(doc["pairs"], (a, b))
    assert verdict == fit_gate.ACCEPT, "the recorded score is not the gate's own: %s" % (sid, row["id"])
    assert doc["score"] == round(stats["med"], 1)


def _check_doc_stub(tree, sid, row, answer, score):
    """_check_doc without the gate re-computation: the stub's score is not a gate measurement
    (that is the point - the writer is pinned independently of the gate's thresholds)."""
    doc = json.loads((Path(tree) / "data" / "db" / "platefits" / ("%s.%s.json" % (sid, row["id"]))).read_text())
    assert doc["site"] == sid and doc["plan"] == row["id"] and doc["auto"] is True
    assert doc["score"] == score
    _check_pairs(doc["pairs"], row)
    _check_crop(doc["crop"], row)
    if row.get("ia"):
        assert doc["ia"] == row["ia"] and doc["file"] == row["file"] and doc.get("book") == row.get("book")
    else:
        assert doc["model"] == "similarity" and doc["src"] == "commons"
        assert doc.get("url") == row.get("url") and doc.get("ref") == row.get("ref")
    assert doc["pairs"] == batch_us._norm_pairs(answer["pairs"])
    assert isinstance(doc.get("at"), str) and doc["at"]
    return doc


def _check_entry(sid, row, entry, answer):
    """A review-item candidate (201's shape): the picture, the 200 evidence field when present,
    the pairs the human starts from, and what the batch learned (why, score, 202's extras)."""
    assert entry["plan"] == row["id"]
    assert entry.get("title") == (row.get("title") or row.get("label") or "")
    assert entry.get("url") == (row["url"] if row.get("url") else
                                ("books/%s/%s" % (row["ia"], row["file"]) if row.get("ia") else None))
    assert isinstance(entry.get("why"), str) and entry["why"]
    assert entry.get("evidence") == _source_evidence(ROOT, row)
    pairs = (answer or {}).get("pairs") or []
    if pairs:
        assert entry["pairs"] == batch_us._norm_pairs(pairs)
        _check_pairs(entry["pairs"], row, min_n=1)
    else:
        assert entry.get("pairs") == []
    if len(pairs) < 4:
        assert entry["why"] == ((answer or {}).get("note") or "no model answer")
        assert "gate_score" not in entry
    else:
        a, b, _, _ = plan_fit.similarity(pairs)
        verdict, stats = fit_gate.gate(pairs, (a, b))
        if verdict == fit_gate.ACCEPT:
            assert "gate_score" not in entry  # it became a doc, not an entry
        else:
            assert entry.get("gate_score") == round(stats["med"], 1)
    try:
        p = propose.propose_for(sid, row["id"])
    except (ValueError, KeyError):
        p = None
    if p is None:
        assert entry.get("coarse") is True
    else:
        for k in ("coarse", "ground", "scale_m_px", "rot_deg", "scale_source", "note"):
            if p.get(k) is not None:
                assert entry.get(k) == p[k]


def _table(text, header):
    """The doc ids of the markdown table under the given section header."""
    lines = text.splitlines()
    i = lines.index(header)
    rows = []
    for ln in lines[i + 1:]:
        if not ln.startswith("|"):
            if rows:
                break
            continue
        cells = [c.strip() for c in ln.strip("|").split("|")]
        if cells[0] in ("doc", "---"):
            continue
        rows.append(cells[0])
    return rows


# ---------------------------------------------------------------- tests


def test_sample_run_real_gate(tree):
    """Every sample-site candidate ends as an automatic doc or an item entry, in the right
    formats, under the real gate; the three no-candidate hand-fitted sites stay untouched
    (no item); bibracte's 201-era no-picture item is re-stamped with the batch's wording;
    the 6 region-less sites end covered."""
    sample = _sample()
    answers = _answers()
    # Snapshot the pre-run state BEFORE the run: pre_docs matches any existing <site>.*.json
    # file, including the automatic documents this very run writes, so a post-run snapshot
    # would swallow the batch's own output.
    pre_docs_before = {sid: _pre(tree, sid) for sid in sample}
    pre_fit_before = {sid: batch_us.is_pre_fit(tree, sid) for sid in sample}
    pre_items = {sid: _item(tree, sid) for sid in sample}
    records = batch_us.run_sites(tree, sample, batch_us.recorded_model(answers))
    assert sorted(records) == sorted(sample)

    for sid in sample:
        rec = records[sid]
        cands = batch_us.candidates(sid, _rows())
        assert set(rec["detail"]) == {r["id"] for r in cands}
        # every non-pre candidate: a doc or an item entry - GOAL point 1, per site
        expected = {r["id"]: _expected((answers.get(sid) or {}).get(r["id"], {}).get("pairs"))
                    for r in cands if r["id"] not in pre_docs_before[sid]}
        auto = {p for p, k in expected.items() if k == "auto"}
        item = {p for p, k in expected.items() if k == "item"}
        assert set(rec["auto"]) == auto
        # a candidate-less site without a pre-fit ends with its no-picture item; every other
        # site gets an item exactly when a candidate needs one
        want_item = bool(item) if cands else not rec["pre_fit"]
        assert rec["item"] == want_item
        assert rec["no_picture"] == (not cands and not rec["pre_fit"])
        assert rec["pre_fit"] == pre_fit_before[sid]
        if item:
            it = _item(tree, sid)
            reproposed = {r["id"] for r in cands if r["id"] not in pre_docs_before[sid]}
            assert {c["plan"] for c in it["candidates"]} == \
                {c["plan"] for c in (pre_items[sid] or {}).get("candidates", [])} | item
            for c in it["candidates"]:
                if c["plan"] in reproposed:
                    _check_entry(sid, _row_for(sid, c["plan"]), c,
                                 (answers.get(sid) or {}).get(c["plan"]))
            assert it.get("resolved") == (pre_items[sid] or {}).get("resolved")
        for plan in rec["auto"]:
            _check_doc(tree, sid, _row_for(sid, plan))

    # newark / forthill / marietta: 202's 5-point proposals pass the frozen gate on EU
    # ground (the documented "true case"), so every candidate becomes an automatic doc
    for sid, pinned in ((NEWARK, NEWARK_ANSWER_PLANS),
                        (FORTHILL, FORTHILL_ANSWER_PLANS),
                        (MARIETTA, MARIETTA_ANSWER_PLANS)):
        rec = records[sid]
        current = {r["id"] for r in batch_us.candidates(sid, _rows())}
        for plan in pinned:
            a, b, _, _ = plan_fit.similarity(answers[sid][plan]["pairs"])
            verdict, _ = fit_gate.gate(answers[sid][plan]["pairs"], (a, b))
            assert verdict == fit_gate.ACCEPT, "a 202 proposal must pass the frozen gate: %s" % plan
        assert set(rec["auto"]) == set(pinned) & current - set(pre_docs_before[sid])
        assert rec["item"] == bool((current - set(pinned)) - set(pre_docs_before[sid]))
        assert rec["pre_fit"]  # the old-style site.json hand fit: the site is covered either way

    # fudge / highbank / hopeton: zero candidates, an old-style hand fit each -> the
    # "already hand-fitted" bucket with NO no-picture item (the loop's `and not rec["pre_fit"]`
    # guard) and no file written at all
    for sid in ("fudge", "highbank", "hopeton"):
        rec = records[sid]
        assert rec["pre_fit"] and not rec["auto"] and not rec["item"] and not rec["no_picture"]
        assert _item(tree, sid) is None

    # bibracte: zero candidates, no hand fit -> the no-picture item, re-upserted with the
    # batch's searched wording over the 201-era one; candidates stays empty, resolved null
    rec = records[NO_PIC]
    assert rec["no_picture"] and rec["item"] and not rec["auto"] and not rec["pre_fit"]
    it = _item(tree, NO_PIC)
    assert it["site"] == NO_PIC and it["candidates"] == []
    assert it.get("resolved") is None
    nph = it["no_picture_found"]
    assert nph["searched"] == "web/data/plans.json (%d rows, matched by the sites field)" % len(_rows())
    assert nph.get("at")
    assert (Path(tree) / "data" / "review" / (NO_PIC + ".json")).is_file()  # no lead: the name stays


def test_hand_fitted_sites_get_items_for_their_other_pictures(tree):
    """The already-hand-fitted EU sites: a candidate whose doc exists (a golden hand fit, or
    an automatic doc a working run left behind) is skipped - never re-fit; the fresh
    candidates' short answers become could-not-fit entries in the site's one item (merged
    into the item a working run may have left, never replaced as a whole); no new doc for a
    short answer. The expectations are state-aware: the same test runs before and after the
    working phase (a working run turns some fresh candidates into pre-docs)."""
    sample = [AVEBURY, OLDSARUM]
    answers = _short_answers()
    before = {sid: set(_pre(tree, sid)) for sid in sample}
    live = {sid: _item(tree, sid) for sid in sample}
    golden = _golden()
    golden_before = {rel: _sha(os.path.join(tree, rel)) for rel in golden}
    records = batch_us.run_sites(tree, sample, batch_us.recorded_model(answers))
    for sid in sample:
        rec = records[sid]
        cands = [r["id"] for r in batch_us.candidates(sid, _rows())]
        fresh = [p for p in cands if p not in before[sid]]
        short = AVEBURY_SHORT if sid == AVEBURY else OLDSARUM_SHORT
        pinned = [p for p in short if p in set(fresh)]
        assert rec["pre_fit"] and not rec["auto"] and not rec["no_picture"]
        for plan in before[sid] & set(cands):  # a pre-existing doc's row: skipped, never re-fit
            assert rec["detail"][plan]["outcome"] == "skip"
        assert rec["item"] == bool(fresh)  # one entry per fresh candidate
        if not fresh:
            continue
        it = _item(tree, sid)
        assert it is not None and it["site"] == sid
        assert len(_item_files(tree, sid)) == 1  # merged, never a second item file
        assert it["resolved"] == (live[sid] or {}).get("resolved")  # write-once; not set here
        assert it["no_picture_found"] is None
        # the merged candidate set: the working run's entries survive, the fresh ones are added
        expected = ({c["plan"] for c in live[sid]["candidates"]} if live[sid] else set()) | set(fresh)
        assert {c["plan"] for c in it["candidates"]} == expected
        assert (Path(tree) / "data" / "review" /
                ("%s.%s.json" % (sid, it["candidates"][0]["plan"]))).is_file()  # the lead
        for c in it["candidates"]:
            if c["plan"] in pinned:
                _check_entry(sid, _row_for(sid, c["plan"]), c, answers[sid][c["plan"]])
        for plan in fresh:  # a short answer writes an item entry, never a doc
            assert not (Path(tree) / "data" / "db" / "platefits" / ("%s.%s.json" % (sid, plan))).exists()
    # the hand-fit docs (and the site.json files) of these sites stay byte-identical
    for rel, h in golden_before.items():
        assert _sha(os.path.join(tree, rel)) == h, "a hand-fit file changed: %s" % rel


def test_stub_gate_always_accept(tree, monkeypatch):
    """The document writer, pinned independently of the gate's thresholds: every candidate of
    the stub site whose model answers have four or more pairs becomes an automatic doc carrying
    the stub's score; the run writes no entries, so an existing item stays byte-identical
    (and one is not created when absent)."""
    sid = _stub_site(tree)
    site = _sites(tree)[sid]
    rows = {r["id"]: r for r in batch_us.candidates(sid, _rows())}
    fresh = [r for r in batch_us.candidates(sid, _rows())
             if r.get("size") and r["id"] not in _pre(tree, sid)]
    answers = {r["id"]: {"pairs": _corner_pairs(site, r)} for r in fresh}
    assert len(answers) >= 2
    # the batch's working run may have left this site an item: the all-accepted run writes
    # no entries, so the upsert is never called and the item's bytes do not move
    f = _item_files(tree, sid)
    item_before = f[0].read_bytes() if f else None
    monkeypatch.setattr(batch_us, "gate_placement",
                        lambda pairs, transform=None: (True, STUB_ACCEPT_SCORE, None))
    rec = batch_us.run_sites(tree, [sid], batch_us.recorded_model({sid: answers}))[sid]
    assert set(rec["auto"]) == set(answers)
    assert not rec["item"] and not rec["no_picture"]
    for plan, a in answers.items():
        _check_doc_stub(tree, sid, rows[plan], a, STUB_ACCEPT_SCORE)
    f = _item_files(tree, sid)
    if item_before is None:
        assert not f
    else:
        assert len(f) == 1 and f[0].read_bytes() == item_before


def test_stub_gate_always_reject(tree, monkeypatch):
    """The item writer, pinned: every refused candidate becomes one item entry (the 201 shape,
    carrying the pairs and the stub's score/why); the upsert merges into a pre-existing item,
    moves it to its lead name and never clears resolved."""
    sid = _stub_site(tree)
    resolved = {"doc": "%s.%s" % (sid, "hand-plan-0"), "at": "2026-01-01T00:00:00+00:00"}
    seed = {"site": sid, "candidates": [],
            "no_picture_found": {"searched": "seed", "at": "2026-01-01T00:00:00+00:00"},
            "resolved": resolved}
    # the batch's working run may have left this site an item: delete it in the temp tree
    # first, so the seeded one is the only one upsert's _find_item can reach (otherwise its
    # sort order finds the batch's <sid>.<lead>.json before the seeded <sid>.json and the
    # seed's resolved/lead assertions break). The files are hard-linked: unlinking the temp
    # path leaves the checkout's originals intact.
    for p in _item_files(tree, sid):
        p.unlink()
    (Path(tree) / "data" / "review" / (sid + ".json")).write_text(json.dumps(seed, indent=1))
    site = _sites(tree)[sid]
    rows = {r["id"]: r for r in batch_us.candidates(sid, _rows())}
    fresh = [r for r in batch_us.candidates(sid, _rows())
             if r.get("size") and r["id"] not in _pre(tree, sid)]
    answers = {r["id"]: {"pairs": _corner_pairs(site, r)} for r in fresh}
    assert answers
    monkeypatch.setattr(batch_us, "gate_placement",
                        lambda pairs, transform=None: STUB_REJECT)
    rec = batch_us.run_sites(tree, [sid], batch_us.recorded_model({sid: answers}))[sid]
    assert rec["auto"] == [] and rec["item"]
    lead = next(r["id"] for r in fresh if r["id"] in answers)
    p = Path(tree) / "data" / "review" / ("%s.%s.json" % (sid, lead))
    assert p.is_file()
    assert not (Path(tree) / "data" / "review" / (sid + ".json")).exists()  # the lead moved the file
    it = json.loads(p.read_text())
    assert it["site"] == sid
    assert it["resolved"] == resolved  # write-once: the upsert never clears it
    assert it["no_picture_found"] is None
    want = [r["id"] for r in fresh if r["id"] in answers]
    assert [c["plan"] for c in it["candidates"]] == want
    for c in it["candidates"]:
        assert c["why"] == STUB_REJECT[2] and c["gate_score"] == STUB_REJECT[1]
        assert c["pairs"] == batch_us._norm_pairs(answers[c["plan"]]["pairs"])
        assert c.get("title") == (rows[c["plan"]].get("title") or rows[c["plan"]].get("label") or "")
        assert c.get("evidence") == _source_evidence(ROOT, rows[c["plan"]])


def test_batch_adds_files_rewrites_none(tree):
    """Box 4: after the run the 20 hand-fit documents and the 19 hand-fit site files are
    byte-identical to the golden hashes; the 6 region-less site.json files (not in that
    golden) are byte-identical pre and post; every pre-existing file under data/ or web/
    stays byte-identical except the sample sites' own review items - the upsert's live-merge
    contract re-saves an item it touches (a re-upserted no-picture record carries a fresh
    timestamp), so those must keep their site, resolved and every candidate plan instead;
    every new file is an automatic document or a sample-site review item."""
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
    batch_us.run_sites(tree, _sample(), _recorded_model())
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
    for rel in after:
        if rel in before:
            continue
        if rel.startswith("data/db/platefits/"):
            doc = json.loads((Path(tree) / rel).read_text())
            assert doc["auto"] is True and doc["site"] in sample, rel
        elif rel.startswith("data/review/"):
            assert json.loads((Path(tree) / rel).read_text())["site"] in sample, rel
        else:
            pytest.fail("the batch wrote outside its own outputs: %s" % rel)


def test_report(tree, tmp_path):
    """Box 3: docs/batch_eu.md in the format of docs/batch_us.md, written by batch_eu's
    write_report: deterministic for the same records (byte-identical twice), the counts,
    the shared recorded seed, the seeded sample of automatically accepted fits (20 where
    there are at least 20, a page URL each - the exact seeded list), and the union section
    (the weaker form over the temp tree; the full assertion is the live test below). The
    default path is pinned to docs/batch_eu.md, never docs/batch_us.md."""
    sample = _sample()
    records = batch_us.run_sites(tree, sample, _recorded_model())
    p1, p2 = tmp_path / "r1.md", tmp_path / "r2.md"
    batch_eu.write_report(tree, records, path=p1)
    batch_eu.write_report(tree, records, path=p2)
    assert p1.read_bytes() == p2.read_bytes()
    text = p1.read_text()
    assert text.startswith("# The batch, EU (203b)")
    assert "Seed: %d" % batch_us.SEED in text  # the shared seed (20261010), 203a's constant
    assert "Sites run: %d" % len(sample) in text
    counts = batch_us.classify(records)
    for k in ("automatic fit", "review item", "already hand-fitted", "no picture found"):
        assert "- %s: %d" % (k, len(counts[k])) in text
    # the bucket split the EU sample is expected to produce (robust to plans.json growth:
    # a new row of a hand-fitted site keeps that site in its bucket, a new bibracte row
    # moves it from no-picture to review item)
    assert counts["automatic fit"] == [FORTHILL, MARIETTA, NEWARK]
    assert counts["already hand-fitted"] >= ["fudge", "highbank", "hopeton"]
    bibracte_cands = batch_us.candidates(NO_PIC, _rows())
    assert counts["no picture found"] == ([NO_PIC] if not bibracte_cands else [])
    assert counts["review item"] == ([NO_PIC] if bibracte_cands else [])
    # the seeded sample of automatically accepted fits: the exact list the seed reproduces,
    # a page URL per doc
    auto_sorted = sorted("%s.%s" % (r["site"], p) for r in records.values() for p in r["auto"])
    header = "## Sample of automatically accepted fits (for the human's 18/20 check)"
    docs = _table(text, header)
    k = min(20, len(auto_sorted))
    assert docs == random.Random(batch_us.SEED).sample(auto_sorted, k)
    docsites = {}
    for r in records.values():
        for p in r["auto"]:
            docsites["%s.%s" % (r["site"], p)] = r["site"]
    pages = {}
    for ln in text.splitlines():
        if not ln.startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip("|").split("|")]
        if cells and cells[0] in docs:
            pages[cells[0]] = cells[1]
    assert {d: "#" + docsites[d] for d in docs} == pages
    # the union section: exactly what union_section renders over the tree's state, at the end
    assert text.endswith(batch_eu.union_section(batch_eu.union_check(tree)))
    m = re.search(r"Coverage: (\d+) covered, (\d+) missing, (\d+) in both", text)
    assert m and int(m.group(3)) == 0
    n_sites = len(_sites(tree))
    assert int(m.group(1)) + int(m.group(2)) == n_sites
    assert "the %d with no region field are in the other list: %s" % (
        len(batch_eu.union_check(tree)["regionless"]),
        ", ".join(batch_eu.union_check(tree)["regionless"])) in text
    # the default path is pinned to docs/batch_eu.md (batch_us's own default is never written)
    out = batch_eu.write_report(tree, records)
    assert out == str(Path(tree) / "docs" / "batch_eu.md")
    assert Path(out).read_bytes() == p1.read_bytes()
    assert not (Path(tree) / "docs" / "batch_us.md").exists()


def test_union_check(tree):
    """Box 2, the weaker form over the temp tree: the partition lists come from sites.json
    alone and are disjoint (union = every built site, the 6 region-less in the EU list);
    the sample sites end covered; there are no orphan files, no bad doc names; and the EU
    run wrote no file naming a site outside its own sample (never a US site)."""
    before = _output_files(tree)
    sample = set(_sample())
    batch_us.run_sites(tree, _sample(), _recorded_model())
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
    'Sites run' matches the live EU partition: 211's merge may grow sites.json in the
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
