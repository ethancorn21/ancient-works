"""The batch, US (task 203a, GOAL points 1-2): fit/batch_us.py, hermetic.

The fitting loop (candidates -> model -> similarity -> gate -> automatic platefit document /
review item) is run on a fixed sample of US sites against a throwaway copy of the tree (web/ +
data/ minus data/raw/, like conftest's served - but no server: the batch is a file-based loop
that never PUTs, so there is no port at all; the page's view of the results is 212's one pass,
not this test's). No network, no model server: the recorded model's answers are fixed inputs -
202's deterministic proposals (fit/propose.py) for the pinned serpent-mound pictures, a
two-feature answer and a no-answer picture for the pinned cahokia ones - and a socket-blocking
fixture fails loudly on any connection attempt. The real gate (001, docs/gate.md section 2)
scores the placements and its own measurement is re-checked against every written document;
two stub gates (always accept / always reject) pin the document and item writers independently
of the gate's thresholds. After the runs the 20 pre-batch hand-fit documents and the 19
hand-fit site files are byte-identical (tests/golden/hand_fit_docs.sha256): the batch added
files, it rewrote none.

The sample (region US): serpent-mound-q968802 (16 candidates today, one of them its pre-batch
hand-fit document - the 15 others get 202's 5-point proposals, the gate's documented "true
case"), cahokia-q333661 (the model finds two features on three pictures and nothing on a
fourth: a review item), mound-bottom-q14710093 (its only candidate IS its hand-fit document:
nothing written), and the first US site, sorted, with no candidate at all today
(aberdeen-mound-q4666953: the "no picture found" item). The stub-gate cases use the first
US site with two or more candidates, no pre-fit and no existing item
(today angel-mounds-q4530064). The pinned plan ids are the test's fixed inputs: if plans.json
gains rows for these sites the loop still ends every candidate with a doc or an item, and a
future 203a session extends the lists for an intended change.
"""
import hashlib
import json
import os
import shutil
import socket
import sys
from pathlib import Path

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "fit"))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))
import batch_us  # noqa: E402
import fit_gate  # noqa: E402
import plan_fit  # noqa: E402
import propose  # noqa: E402

GOLDEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "golden", "hand_fit_docs.sha256")

SERPENT = "serpent-mound-q968802"
CAHOKIA = "cahokia-q333661"
MOUNDBOTTOM = "mound-bottom-q14710093"

# The pinned sample inputs (202's proposals of these exact pictures are the recorded answers).
SERPENT_ANSWER_PLANS = [
    "annualreportofbu1218901891smit_n0636_1",
    "b24849959_n0306_1", "b24849959_n0308_1", "b24849959_n0309_1", "b24849959_n0313_1",
    "c_dd2c553d611e610b", "c_27c818e3c6c9b9c8", "c_8ebd42607fbb96d8", "c_7b01a4bb50d68b56",
    "c_52dfe1fc979edf2c", "c_2c260a03d1f8df1c", "c_393a505b4f0e4c81", "c_ad1c0730a0fa94c3",
    "c_15ff865e5f3d8ddb", "c_b07ef12c515af39b",
]
CAHOKIA_TWO_PAIR = [
    "ancientmonuments00squi_n0309_1",
    "annualreportofbu1218901891smit_n0200_1",
    "c_1a7c2a11c3a0dd21",
]
CAHOKIA_NO_ANSWER = ["c_8c44bb427b76aa7a"]
MOUNDBOTTOM_PRE = ["c_0b98157d7af17d6e"]

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


@pytest.fixture()
def tree(tmp_path):
    """A throwaway copy of the product tree (web/ + data/ minus data/raw/); the batch writes here only."""
    t = tmp_path / "aw203a"
    t.mkdir()
    shutil.copytree(os.path.join(ROOT, "web"), str(t / "web"))

    def ignore(d, names):
        return [n for n in names if os.path.join(d, n) == os.path.join(ROOT, "data", "raw")]
    shutil.copytree(os.path.join(ROOT, "data"), str(t / "data"), ignore=ignore)
    return str(t)


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


def _rows_by_id():
    return {r["id"]: r for r in _rows()}


def _sites(root):
    return batch_us._sites(root)


def _pre(root, sid):
    return [p for p, _ in batch_us.pre_docs(root, sid)]


def _item(root, sid):
    """The parsed review item for a site in this tree, or None."""
    d = Path(root) / "data" / "review"
    if not d.is_dir():
        return None
    for p in sorted(d.iterdir()):
        if p.suffix == ".json":
            item = json.loads(p.read_text())
            if item.get("site") == sid:
                return item
    return None


def _corner_pairs(site, row):
    """Four well-conditioned pairs: the page-px corners of the row's size frame on the site's
    corners (a real similarity, so plan_fit.similarity stays well conditioned)."""
    w, h = row["size"]
    pts = [(0.05 * w, 0.05 * h), (0.95 * w, 0.05 * h), (0.95 * w, 0.95 * h), (0.05 * w, 0.95 * h)]
    return [[round(u, 1), round(v, 1), round(lon, 7), round(lat, 7)]
            for (u, v), (lon, lat) in zip(pts, site["corners"])]


def _answers():
    """The test's recorded model answers: {site: {plan: answer or None}} - one source of truth
    for both the model the loop is given and the expectations below. The answers are 202's
    deterministic proposals (serpent-mound: five points; cahokia: two), plus a no-answer picture."""
    site = _sites(ROOT)[CAHOKIA]
    out = {SERPENT: {}, CAHOKIA: {}}
    for plan in SERPENT_ANSWER_PLANS:
        out[SERPENT][plan] = {"pairs": propose.propose_for(SERPENT, plan)["pairs"]}
    for plan in CAHOKIA_TWO_PAIR:
        try:
            src = propose.propose_for(CAHOKIA, plan)["pairs"]
        except (ValueError, KeyError):
            src = _corner_pairs(site, propose._plans_row(plan, CAHOKIA))
        out[CAHOKIA][plan] = {"pairs": src[:2], "note": "only two features matched"}
    return out


def _answer_pairs(answers, sid, plan):
    a = (answers.get(sid) or {}).get(plan) or {}
    return a.get("pairs")


def _sample():
    """The fixed sample: the three named hand-fit-reference sites and the first US site,
    sorted, with no candidate at all (the no-picture branch)."""
    zero = [s for s in batch_us.us_sites(ROOT) if not batch_us.candidates(s, _rows())]
    assert zero, "no US site without a candidate left: the no-picture branch has no sample"
    return [SERPENT, CAHOKIA, MOUNDBOTTOM, zero[0]]


def _stub_site(tree):
    """The first US site with two or more candidates, no pre-fit and no existing item."""
    for sid in batch_us.us_sites(ROOT):
        nonpre = [r["id"] for r in batch_us.candidates(sid, _rows()) if r["id"] not in _pre(tree, sid)]
        if len(nonpre) >= 2 and not batch_us.is_pre_fit(tree, sid) and _item(tree, sid) is None:
            return sid
    pytest.fail("no US site with two or more candidates, no pre-fit and no existing item")


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
    # (/ and % are same-precedence, left-associative: the format must be parenthesized)
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


def _check_doc_stub(tree, sid, row, answer, score):
    """_check_doc without the gate re-computation: the stub's score is not a gate measurement
    (that is the point - the writer is pinned independently of the gate's thresholds)."""
    # (/ and % are same-precedence, left-associative: the format must be parenthesized)
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


def _syn_records(n_sites, n_per_site):
    """Records with n_sites * n_per_site automatic docs, for the >= 20 sample branch."""
    out = {}
    for i in range(n_sites):
        sid = "syn-site-%d" % i
        auto = ["syn-plan-%d-%d" % (i, j) for j in range(n_per_site)]
        out[sid] = {"site": sid, "pre_fit": False, "pre_docs": [], "auto": auto, "item": False,
                    "no_picture": False,
                    "detail": {p: {"outcome": "auto", "score": 1.0} for p in auto}}
    return out


# ---------------------------------------------------------------- tests


def test_sample_run_real_gate(tree):
    """Every sample-site candidate ends as an automatic doc or an item entry, in the right
    formats, under the real gate; the pre-batch hand-fit documents are skipped; the
    zero-candidate site gets its no-picture item."""
    sample = _sample()
    rows = _rows_by_id()
    answers = _answers()
    # Snapshot the pre-batch state BEFORE the run: pre_docs matches any existing <site>.*.json file,
    # including the automatic documents this very run writes, so a post-run snapshot would swallow
    # the batch's own output (a pre-fit site and its new docs both read as "pre").
    pre_docs_before = {sid: _pre(tree, sid) for sid in sample}
    pre_fit_before = {sid: batch_us.is_pre_fit(tree, sid) for sid in sample}
    pre_items = {sid: _item(tree, sid) for sid in sample}
    records = batch_us.run_sites(tree, sample, batch_us.recorded_model(answers))
    assert sorted(records) == sorted(sample)

    for sid in sample:
        rec = records[sid]
        pre = pre_docs_before[sid]
        cands = batch_us.candidates(sid, _rows())
        assert set(rec["detail"]) == {r["id"] for r in cands}
        # every non-pre candidate: a doc or an item entry - GOAL point 1, per site
        expected = {r["id"]: _expected(_answer_pairs(answers, sid, r["id"]))
                    for r in cands if r["id"] not in pre}
        auto = {p for p, k in expected.items() if k == "auto"}
        item = {p for p, k in expected.items() if k == "item"}
        assert set(rec["auto"]) == auto
        # a candidate-less site without a pre-fit ends with its no-picture item (no candidate entries
        # to predict it from); every other site gets an item exactly when a candidate needs one
        want_item = bool(item) if cands else not rec["pre_fit"]
        assert rec["item"] == want_item
        assert rec["pre_fit"] == pre_fit_before[sid]
        if item:
            it = _item(tree, sid)
            want = [r["id"] for r in cands if r["id"] in item]
            assert [c["plan"] for c in it["candidates"]] == want
            for c in it["candidates"]:
                _check_entry(sid, rows[c["plan"]], c, (answers.get(sid) or {}).get(c["plan"]))
            assert it.get("resolved") == (pre_items[sid] or {}).get("resolved")
        for plan in rec["auto"]:
            _check_doc(tree, sid, rows[plan])

    # serpent-mound: 202's 5-point proposals pass the frozen gate (the documented true case)
    rec = records[SERPENT]
    nonpre = {r["id"] for r in batch_us.candidates(SERPENT, _rows())} - set(pre_docs_before[SERPENT])
    for plan in SERPENT_ANSWER_PLANS:
        a, b, _, _ = plan_fit.similarity(answers[SERPENT][plan]["pairs"])
        verdict, _ = fit_gate.gate(answers[SERPENT][plan]["pairs"], (a, b))
        assert verdict == fit_gate.ACCEPT, "a 202 proposal must pass the frozen gate: %s" % plan
    assert set(rec["auto"]) >= set(SERPENT_ANSWER_PLANS)
    assert rec["item"] == bool(nonpre - set(SERPENT_ANSWER_PLANS))

    # cahokia: the short and missing answers become one item; its lead names the file
    rec = records[CAHOKIA]
    assert rec["auto"] == []
    assert rec["item"]
    first = next(r["id"] for r in batch_us.candidates(CAHOKIA, _rows()) if r["id"] not in pre_docs_before[CAHOKIA])
    assert (Path(tree) / "data" / "review" / ("%s.%s.json" % (CAHOKIA, first))).is_file()
    it = _item(tree, CAHOKIA)
    assert {c["plan"] for c in it["candidates"]} == set(CAHOKIA_TWO_PAIR) | set(CAHOKIA_NO_ANSWER)

    # mound-bottom: its only candidate is its hand-fit document - nothing written, no item
    rec = records[MOUNDBOTTOM]
    assert rec["pre_fit"] and set(rec["detail"]) == set(MOUNDBOTTOM_PRE)
    assert all(d["outcome"] == "skip" for d in rec["detail"].values())
    assert not rec["auto"] and not rec["item"] and not rec["no_picture"]
    assert _item(tree, MOUNDBOTTOM) is None

    # the zero-candidate site: the no-picture item (one per site, 201's shape)
    z = sample[-1]
    rec = records[z]
    assert rec["no_picture"] and rec["item"] and not rec["auto"] and not rec["pre_fit"]
    p = Path(tree) / "data" / "review" / (z + ".json")
    assert p.is_file()
    it = json.loads(p.read_text())
    assert it["site"] == z and it["candidates"] == []
    assert it.get("resolved") == (pre_items[z] or {}).get("resolved")
    nph = it["no_picture_found"]
    assert isinstance(nph, dict) and "web/data/plans.json" in nph.get("searched", "") and nph.get("at")


def test_stub_gate_always_accept(tree, monkeypatch):
    """The document writer, pinned independently of the gate's thresholds: every candidate of
    a two-candidate site whose model answers have four or more pairs becomes an automatic doc
    carrying the stub's score, and no item is written."""
    sid = _stub_site(tree)
    site = _sites(tree)[sid]
    rows = _rows_by_id()
    nonpre = [r for r in batch_us.candidates(sid, _rows()) if r["id"] not in _pre(tree, sid)]
    assert len(nonpre) >= 2
    answers = {r["id"]: {"pairs": _corner_pairs(site, r)} for r in nonpre if r.get("size")}
    monkeypatch.setattr(batch_us, "gate_placement",
                        lambda pairs, transform=None: (True, STUB_ACCEPT_SCORE, None))
    rec = batch_us.run_sites(tree, [sid], batch_us.recorded_model({sid: answers}))[sid]
    assert set(rec["auto"]) == set(answers)
    assert not rec["item"] and not rec["no_picture"]
    for plan, a in answers.items():
        _check_doc_stub(tree, sid, rows[plan], a, STUB_ACCEPT_SCORE)
    assert _item(tree, sid) is None


def test_stub_gate_always_reject(tree, monkeypatch):
    """The item writer, pinned: every refused candidate becomes one item entry (the 201 shape,
    carrying the pairs and the stub's score/why); the upsert merges into a pre-existing item,
    moves it to its lead name and never clears resolved."""
    sid = _stub_site(tree)
    resolved = {"doc": "%s.%s" % (sid, "hand-plan-0"), "at": "2026-01-01T00:00:00+00:00"}
    seed = {"site": sid, "candidates": [],
            "no_picture_found": {"searched": "seed", "at": "2026-01-01T00:00:00+00:00"},
            "resolved": resolved}
    (Path(tree) / "data" / "review" / (sid + ".json")).write_text(json.dumps(seed, indent=1))
    site = _sites(tree)[sid]
    rows = _rows_by_id()
    nonpre = [r for r in batch_us.candidates(sid, _rows()) if r["id"] not in _pre(tree, sid)]
    answers = {r["id"]: {"pairs": _corner_pairs(site, r)} for r in nonpre if r.get("size")}
    assert answers
    monkeypatch.setattr(batch_us, "gate_placement",
                        lambda pairs, transform=None: STUB_REJECT)
    rec = batch_us.run_sites(tree, [sid], batch_us.recorded_model({sid: answers}))[sid]
    assert rec["auto"] == [] and rec["item"]
    lead = next(r["id"] for r in nonpre if r["id"] in answers)
    p = Path(tree) / "data" / "review" / ("%s.%s.json" % (sid, lead))
    assert p.is_file()
    assert not (Path(tree) / "data" / "review" / (sid + ".json")).exists()  # the lead moved the file
    it = json.loads(p.read_text())
    assert it["site"] == sid
    assert it["resolved"] == resolved  # write-once: the upsert never clears it
    assert it["no_picture_found"] is None
    want = [r["id"] for r in nonpre if r["id"] in answers]
    assert [c["plan"] for c in it["candidates"]] == want
    for c in it["candidates"]:
        assert c["why"] == STUB_REJECT[2] and c["gate_score"] == STUB_REJECT[1]
        assert c["pairs"] == batch_us._norm_pairs(answers[c["plan"]]["pairs"])
        assert c.get("title") == (rows[c["plan"]].get("title") or rows[c["plan"]].get("label") or "")
        assert c.get("evidence") == _source_evidence(ROOT, rows[c["plan"]])


def test_batch_adds_files_rewrites_none(tree):
    """Box 4: after the run the 20 hand-fit documents and the 19 hand-fit site files are
    byte-identical to the golden hashes; no pre-existing file under data/ or web/ changed
    bytes; every new file is an automatic document or a sample-site review item."""
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
    batch_us.run_sites(tree, _sample(), _recorded_model())
    after = all_files()

    for rel, h in before.items():  # the batch rewrites nothing
        assert after.get(rel) == h, "the batch rewrote %s" % rel
    for rel, h in golden.items():  # the hand fits: byte-identical to the golden
        assert after.get(rel) == h, "a hand-fit file changed: %s" % rel
    sample = set(_sample())
    for rel, _h in after.items():
        if rel in before:
            continue
        if rel.startswith("data/db/platefits/"):
            doc = json.loads((Path(tree) / rel).read_text())
            assert doc["auto"] is True and doc["site"] in sample, rel
        elif rel.startswith("data/review/"):
            assert json.loads((Path(tree) / rel).read_text())["site"] in sample, rel
        else:
            pytest.fail("the batch wrote outside its own outputs: %s" % rel)


def _recorded_model():
    return batch_us.recorded_model(_answers())


def test_report_reproducible_from_seed(tree, tmp_path):
    """Box 5: the report is deterministic for the same records and the recorded seed: the
    counts, the seeded sample of automatically accepted fits (a page URL each), and the
    20-of-20-or-more branch (synthetic 22-doc records)."""
    sample = _sample()
    records = batch_us.run_sites(tree, sample, _recorded_model())
    p1, p2 = tmp_path / "r1.md", tmp_path / "r2.md"
    batch_us.write_report(tree, records, path=p1)
    batch_us.write_report(tree, records, path=p2)
    assert p1.read_bytes() == p2.read_bytes()
    text = p1.read_text()
    assert "Seed: %d" % batch_us.SEED in text
    assert "Sites run: %d" % len(sample) in text
    counts = batch_us.classify(records)
    for k in ("automatic fit", "review item", "already hand-fitted", "no picture found"):
        assert "- %s: %d" % (k, len(counts[k])) in text
    n_auto = sum(len(r["auto"]) for r in records.values())
    assert n_auto >= 1, "the pinned serpent-mound proposals must pass the real gate"
    header = "## Sample of automatically accepted fits (for the human's 18/20 check)"  # the report's exact section header
    docs = _table(text, header)
    assert len(docs) == min(20, n_auto)
    auto_set = {"%s.%s" % (r["site"], p) for r in records.values() for p in r["auto"]}
    if n_auto < 20:
        assert set(docs) == auto_set  # all of them, in some seeded order
    for ln in text.splitlines():
        if ln.startswith("| %s |" % docs[0]):
            assert "#" in ln  # a page URL per sample fit
            break
    else:
        pytest.fail("the sample table does not list its docs with a page URL")

    big = _syn_records(2, 11)  # 22 auto docs: the 20-of-20-or-more branch
    q1, q2 = tmp_path / "q1.md", tmp_path / "q2.md"
    batch_us.write_report(tree, big, path=q1)
    batch_us.write_report(tree, big, path=q2)
    assert q1.read_bytes() == q2.read_bytes()
    big_docs = _table(q1.read_text(), header)
    assert len(big_docs) == 20
    big_auto = {"%s.%s" % (r["site"], p) for r in big.values() for p in r["auto"]}
    assert set(big_docs) <= big_auto
