"""The Numancia staging (task 210, GOAL.md point 4): the one excavation plan of the 1860s campaigns -
LÁMINA IV, fig. 5, "Plano de las excavaciones hechas en el sitio de Numancia" of Saavedra's work in RAH
Memorias tomo IX (1879, public domain; Internet Archive item memoriasdelareal009real, leaf 507 - the item
has no per-leaf image, so the row's picture is rendered locally from the PDF and the row carries no
fetchable thumb) - staged by fit/src_numancia.py into this task's own files (files/classified_numancia.jsonl;
no new site, the row ties to the EXISTING catalog site `numancia`, extras_numancia.jsonl stays absent).
The tests are offline: a socket-blocking fixture makes any network fetch fail loud, so the evidence check
runs from the stored fields only (200's fail-closed box). The negative control pins the trap the caption
record exists for: the named place resolving to a far site (Mons) instead of the recorded point - it must
be reported FAIL, never kept, while the stored distance still reproduces (the failure is the distance
itself, not a stale record). The golden files (tests/golden/src_numancia_sample.json,
src_numancia_evidence.txt) pin the staged rows and the offline check's exact output; they are regenerated
only via the module's --golden flag for an intended change. The rendered image lives in the gitignored
data/raw/ (per worktree, re-derived by --render): the tests check the path convention, never the file's
existence. Task 226 extends the guard's test: test_check_staged_three_states covers the three states of
the canonical clash guard hermetically (staged row absent from the canonical files / present with
identical content = an already-merged no-op / present with different content = still fails loud),
pointing the module's canonical path constants at constructed temp copies, so it holds whether or not
211's live merge has run on this checkout.
"""
import hashlib
import json
import os
import socket
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for d in (os.path.join(ROOT, "fit"), os.path.join(ROOT, "pipeline")):
    if d not in sys.path:
        sys.path.insert(0, d)
import evidence  # noqa: E402  fit/evidence.py, the evidence contract
import src_numancia as num  # noqa: E402  fit/src_numancia.py, the module under test


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """The check is offline by contract; make any network attempt in these tests fail loud."""
    def boom(*args, **kwargs):
        raise AssertionError(f"network access attempted: {args} {kwargs}")
    monkeypatch.setattr(socket, "socket", boom)
    monkeypatch.setattr(socket, "create_connection", boom)
    monkeypatch.setattr(socket, "getaddrinfo", boom)


def test_check_staged_files_join_and_pass(capsys):
    """src_numancia --check, offline: the staged files join (exactly one row, the EXISTING numancia site
    whose catalog point matches the stored evidence point, the QID/year/by/name/mime fields, classified
    1:1 as a hand-recorded plan, (site, title) unique, a staged row already in the canonical files.jsonl
    is a no-op only when identical to the canonical row (211's first-row-wins merge) - a same-key
    different row still fails loud, the sha1(title) image-path convention) and the row PASSes the
    evidence check (the caption route, 26.1 m). The render image is gitignored and worktree-local: its
    absence is a note, not a failure."""
    code = num.check_staged()
    out = capsys.readouterr().out
    assert code == 0, out
    assert "join:" not in out, f"join problems:\n{out}"
    assert "evidence: 1 rows, 1 pass, 0 fail, 0 no-tie" in out, out
    assert f"{'PASS':4s} {'caption_coords':15s} numancia|{num.TITLE}" in out, out

    files = num._load(num.FILES)
    assert len(files) == 1
    r = files[0]
    # the image-path convention (commons.local): <sha1(title)[:16]>.jpg in the site's data/raw/commons dir
    assert os.path.basename(num._image_path()) == \
        hashlib.sha1(r["title"].encode()).hexdigest()[:16] + ".jpg" == "0fa271e2444f7bfc.jpg"
    cls = num._load(num.CLASSIFIED)
    assert len(cls) == 1 and (cls[0]["site"], cls[0]["title"]) == (r["site"], r["title"])
    assert (cls[0]["p_plan"], cls[0]["p_birdseye"], cls[0]["p_photo"], cls[0]["by"]) == (1.0, 0.0, 0.0, "hand")


def test_check_staged_three_states(tmp_path, monkeypatch, capsys):
    """The 211 merge states of the --check guard, hermetically (the canonical files pointed at constructed
    temp copies, so the test holds whether or not 211's live merge has run on this checkout):
    (a) the staged row ABSENT from the canonical files (the pre-merge state) - check 0, no join problems,
    evidence PASS; (b) the staged row present with IDENTICAL content (the 211 first-row-wins merge has
    run) - check 0, no join problems: an already-merged row is a no-op, not a clash; (c) the same
    (site, title) key held by a DIFFERENT row - still fails loud (the pre-merge conflict protection),
    naming exactly that key and no other join problem."""
    staged = num._load(num.FILES)
    skey = (staged[0]["site"], staged[0]["title"])

    def write(name, text):
        p = tmp_path / name
        p.write_text(text, encoding="utf-8")
        return str(p)

    # the canonical files with this module's staged row removed: the pre-merge state of ITS key, on any
    # checkout (the other sources' merged rows are untouched, the guard does not care about them)
    files_pre = [json.dumps(r, ensure_ascii=False) for r in num._load(num.FILES_CANONICAL)
                 if (r.get("site"), r.get("title")) != skey]
    staged_line = json.dumps(staged[0], ensure_ascii=False)

    def point(files_rows):
        monkeypatch.setattr(num, "FILES_CANONICAL", write("files.jsonl", "\n".join(files_rows) + "\n"))

    # (a) pre-merge: the staged row is not in the canonical files yet
    point(files_pre)
    code = num.check_staged()
    out = capsys.readouterr().out
    assert code == 0, out
    assert "join:" not in out, out
    assert "evidence: 1 rows, 1 pass, 0 fail, 0 no-tie" in out, out

    # (b) the 211 merge ran: the staged row is in the canonical files with identical content
    point(files_pre + [staged_line])
    code = num.check_staged()
    out = capsys.readouterr().out
    assert code == 0, out
    assert "join:" not in out, out
    assert "evidence: 1 rows, 1 pass, 0 fail, 0 no-tie" in out, out

    # (c) the same (site, title) key held by a DIFFERENT row: the pre-merge conflict protection still fires
    altered = dict(staged[0], year=staged[0]["year"] + 1)  # same key, different content
    point(files_pre + [json.dumps(altered, ensure_ascii=False)])
    code = num.check_staged()
    out = capsys.readouterr().out
    assert code == 1, out
    assert [l for l in out.splitlines() if l.startswith("join:")] == \
        [f"join: staged title already in the canonical files.jsonl: {skey}"], out


def test_evidence_cli_matches_golden():
    """The CLI (fit/evidence.py check) over the staged file row, offline, with the canonical extras.jsonl
    as catalog (the site is a catalog site, not a staged one): exit 0, no stderr, and the printed report
    is byte-for-byte the golden (tests/golden/src_numancia_evidence.txt, written by the module's --golden).
    The caption route never consults the catalog, so the report stays stable after 211's consolidation."""
    p = subprocess.run(
        [sys.executable, "fit/evidence.py", "check",
         "--files", "data/commons/files_numancia.jsonl",
         "--books", "data/books/.no-books",
         "--catalog", "data/catalog/extras.jsonl"],
        cwd=ROOT, capture_output=True, text=True)
    golden = open(os.path.join(ROOT, "tests", "golden", "src_numancia_evidence.txt"), encoding="utf-8").read()
    assert p.stderr == "", p.stderr
    assert p.returncode == 0, (p.returncode, p.stdout)
    assert p.stdout == golden, f"differs from the golden:\n{p.stdout}\n---\n{golden}"


def test_evidence_offline_and_negative_control(tmp_path):
    """fit/evidence.py's check over the staged row, offline (stored fields only): exit 0, zero FAIL. The
    negative control (never written into the staged file) keeps the stored distance in agreement with the
    named place it stores - but names Mons (3.9525, 50.4547) as that place, ~1079 km from the site: the
    name-search trap a live record could store. 200's fail-closed box must report FAIL (the place itself
    is the failure, the distance reproduces) and never keep it; the staged row stays untouched."""
    row = num._load(num.FILES)[0]
    code, text = evidence.check(num.FILES, num.NO_BOOKS, catalog=num.EXTRAS_CANONICAL)
    assert code == 0, text
    assert "evidence: 1 rows, 1 pass, 0 fail, 0 no-tie" in text, text
    assert f"{'PASS':4s} {'caption_coords':15s} numancia|{num.TITLE}" in text, text

    bad = dict(row)
    ev = dict(bad["evidence"])
    ev["place_lon"], ev["place_lat"] = 3.9525, 50.4547  # Mons: the name-search trap
    d = evidence.hav_m(ev["site_lon"], ev["site_lat"], ev["place_lon"], ev["place_lat"])
    ev["dist_m"] = round(d, 1)  # the stored distance reproduces: the failure is the distance itself
    bad["evidence"] = ev
    f = tmp_path / "bad_row.jsonl"
    f.write_text(json.dumps(bad, ensure_ascii=False) + "\n", encoding="utf-8")
    code, text = evidence.check(str(f), num.NO_BOOKS, catalog=num.EXTRAS_CANONICAL)
    assert code == 1, text
    line = next(l for l in text.splitlines() if l.startswith("FAIL"))
    assert f"named place is {d / 1000:.0f} km from the site (the trap), not a tie" in line, line
    assert "evidence: 1 rows, 0 pass, 1 fail, 0 no-tie" in text, text
    assert num._load(num.FILES)[0]["evidence"] == row["evidence"]  # the staged row is untouched


def test_golden_sample_matches_staged_rows():
    """tests/golden/src_numancia_sample.json (written by the module's --golden: the staged rows, keys
    sorted, the checked date normalized - it varies with the staging day) is the staged files exactly -
    the pin the staging is final against; regenerate only for an intended change."""
    golden = json.load(open(os.path.join(ROOT, "tests", "golden", "src_numancia_sample.json"),
                            encoding="utf-8"))
    assert golden["count"] == {"files": 1, "classified": 1}
    assert golden["files"] == num._norm(num._load(num.FILES))
    assert golden["classified"] == num._norm(num._load(num.CLASSIFIED))
    ev = golden["files"][0]["evidence"]  # the evidence specifics, pinned
    assert ev["kind"] == "caption_coords" and ev["named_place"] == "Numancia"
    assert ev["place_qid"] == "Q623407" and ev["place_label"] == "Numantia"
    assert (ev["dist_m"], ev["checked"]) == (26.1, "0000-00-00")
