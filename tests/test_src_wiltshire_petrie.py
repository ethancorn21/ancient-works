"""The Petrie 1880 Commons leg (task 209c, GOAL point 4): the book is not on IA and the human refused
to download it (ask_human 002, the 001-Hoare pattern: "Just skip it and move on" - iteration 151), so
the leg stands on the two canonical data/commons/files.jsonl rows that 209b visually verified as Petrie
1880 Pl. I/II (stonehenge-q39671, year 1880, the caption_coords tie from the BL Georeferencer
description, machine-classified p_plan 0.94/0.92). fit/src_wiltshire_petrie.py verifies those rows
offline and pins them (the golden sample); it stages nothing (a canonical title is never re-staged)
and keeps no book artifacts. The tests are offline: a socket-blocking fixture makes any network
attempt fail loud, so the evidence check runs from the stored fields only (200's fail-closed box).
They pin the table against the canonical rows (including the BL description's Petrie/1880/shelfmark
facts), the offline --check, the negative controls (a missing canonical title, a re-staged Petrie
title - both written to tmp files only), the absence of book artifacts, the golden sample and the
Petrie section of docs/lead_wiltshire.md (the refusal, the two plates, the n/a recall)."""
import json
import os
import socket
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for d in (os.path.join(ROOT, "fit"), os.path.join(ROOT, "pipeline")):
    if d not in sys.path:
        sys.path.insert(0, d)
import books  # noqa: E402  pipeline/books.py (BOOKS: the petrie book must never be registered)
import src_wiltshire_petrie as src  # noqa: E402  fit/src_wiltshire_petrie.py, the module under test

LEAD = os.path.join(ROOT, "docs", "lead_wiltshire.md")
GOLDEN = os.path.join(ROOT, "tests", "golden", "src_wiltshire_petrie_sample.json")
T47 = "File:47 of 'Stonehenge- plans, descriptions and theories' (11135894643).jpg"
T49 = "File:49 of 'Stonehenge- plans, descriptions and theories' (11133409654).jpg"


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """The verification is offline by contract; make any network attempt in this module's tests fail loud."""
    def boom(*args, **kwargs):
        raise AssertionError(f"network access attempted: {args} {kwargs}")
    monkeypatch.setattr(socket, "socket", boom)
    monkeypatch.setattr(socket, "create_connection", boom)
    monkeypatch.setattr(socket, "getaddrinfo", boom)


def _canonical():
    return {r.get("title"): r for r in src._load(src.FILES_CANONICAL) if r.get("title")}


def test_table_matches_the_canonical_rows():
    """PETRIE_ROWS is the two canonical rows exactly: (title, site, qid, the book's year 1880, size)
    and the caption_coords tie (named place Stonehenge resolving to the site's own point, dist 0.0),
    plus the BL Georeferencer description that names PETRIE / 1880 / shelfmark / page for each - the
    metadata-level proof of the 209b visual identification (W.M.F.P., plate numbers, scales)."""
    canonical = _canonical()
    assert [t for t, *_ in src.PETRIE_ROWS] == [T47, T49]
    pages = {T47: "47", T49: "49"}
    for title, sid, plate, w, h in src.PETRIE_ROWS:
        r = canonical.get(title)
        assert r is not None, f"{title!r} not in the canonical files.jsonl"
        s = src.SITES[sid]
        assert (r["site"], r["qid"], r["year"]) == (sid, s["qid"], src.YEAR), title
        assert (r["w"], r["h"]) == (w, h), title
        ev = r["evidence"]
        assert (ev["kind"], ev["named_place"], ev["place_qid"]) == ("caption_coords", "Stonehenge", s["qid"]), title
        assert ev["dist_m"] == 0.0 and (ev["site_lon"], ev["site_lat"]) == (s["lon"], s["lat"]), title
        for needle in ("PETRIE", "1880", "HMNTS 10352.i.12", "E. Stanford", f"Page : {pages[title]}",
                       "Stonehenge: plans, descriptions and theories"):
            assert needle in r["desc"], f"{title}: the description no longer names {needle!r}"
    cls = {r["title"]: r for r in src._load(src.CLASSIFIED_CANONICAL) if r.get("title") in (T47, T49)}
    assert {T47, T49} <= set(cls)
    assert cls[T47]["p_plan"] > 0.9 and cls[T49]["p_plan"] > 0.9  # the machine call: plans, not views


def test_check_offline(capsys):
    """--check, offline: both canonical rows PASS the evidence check from stored fields alone, the
    (possibly absent) *_wiltshire_c staging files join, and nothing Petrie is re-staged."""
    code = src.check_staged()
    out = capsys.readouterr().out
    assert code == 0, out
    assert "check:" not in out, f"problems:\n{out}"
    for title, _sid, plate, _w, _h in src.PETRIE_ROWS:
        assert f"PASS caption_coords  stonehenge-q39671|{title}  (Pl. {plate}, 1880)" in out, out
    assert "evidence: 2 rows, 2 pass, 0 fail, 0 no-tie" in out, out


def test_missing_canonical_title_fails_loud(tmp_path, monkeypatch, capsys):
    """If either Petrie file disappears from the canonical files.jsonl (renamed on Commons), the
    Commons leg is broken: --check exits 1 and names the row. The tmp file carries the other row
    only; the real file is never touched."""
    keep = next(r for r in src._load(src.FILES_CANONICAL) if r.get("title") == T47)
    f = tmp_path / "files.jsonl"
    f.write_text(json.dumps(keep, ensure_ascii=False) + "\n", encoding="utf-8")
    monkeypatch.setattr(src, "FILES_CANONICAL", str(f))
    code = src.check_staged()
    out = capsys.readouterr().out
    assert code == 1, out
    assert f"no longer in the canonical files.jsonl: the Commons leg is broken" in out, out
    assert T49 in out, out
    assert "evidence: 2 rows, 1 pass, 1 fail, 0 no-tie" in out, out


def test_re_staged_petrie_title_fails_loud(tmp_path, monkeypatch, capsys):
    """A *_wiltshire_c staging row carrying a Petrie title is a hard fail (a canonical title is never
    re-staged - the 209b canonical-title-clash guard's case, owned here): --check exits 1 and names
    it. Both rows stay canonical (they keep passing); only the tmp staging files are written."""
    r47 = next(r for r in src._load(src.FILES_CANONICAL) if r.get("title") == T47)
    fc = tmp_path / "files_wiltshire_c.jsonl"
    fc.write_text(json.dumps(r47, ensure_ascii=False) + "\n", encoding="utf-8")
    cc = tmp_path / "classified_wiltshire_c.jsonl"
    cc.write_text(json.dumps({"site": r47["site"], "title": T47, "p_plan": 1.0,
                              "p_birdseye": 0.0, "p_photo": 0.0, "by": "hand"}) + "\n", encoding="utf-8")
    monkeypatch.setattr(src, "FILES_C", str(fc))
    monkeypatch.setattr(src, "CLASSIFIED_C", str(cc))
    code = src.check_staged()
    out = capsys.readouterr().out
    assert code == 1, out
    assert "re-stages the canonical Petrie title" in out and T47 in out, out
    assert "evidence: 2 rows, 2 pass, 0 fail, 0 no-tie" in out, out  # the rows themselves still pass


def test_no_book_artifacts():
    """The book leg was refused, not built: no petrie book is registered, no triage or lists artifact
    exists, and no human-downloaded copy sits in the repo (the 209a-style wrap would be added only if
    a complete copy ever lands in data/raw/books/petrie1880/)."""
    assert not any("petrie" in k.lower() for k in books.BOOKS)
    for d in (os.path.join(ROOT, "data", "books", "triage"), os.path.join(ROOT, "data", "books", "lists")):
        if os.path.isdir(d):
            assert not [n for n in os.listdir(d) if "petrie" in n.lower()], d
    assert not os.path.exists(os.path.join(ROOT, "data", "raw", "books", "petrie1880"))


def test_golden_matches_the_canonical_rows():
    """tests/golden/src_wiltshire_petrie_sample.json (written by --golden: the two canonical file rows
    and their machine-classified rows, checked normalized, keys sorted) is the current canonical state
    exactly - the pin the Commons leg is final against; regenerate only via --golden for an intended
    change."""
    golden = json.load(open(GOLDEN, encoding="utf-8"))
    canonical = _canonical()
    files = [canonical[t] for t, *_ in src.PETRIE_ROWS]
    cls = [r for r in src._load(src.CLASSIFIED_CANONICAL) if r.get("title") in {t for t, *_ in src.PETRIE_ROWS}]
    want = {"files": src._norm(files), "classified": cls}
    assert golden == want, "the canonical rows differ from the golden sample - an intended change needs --golden"


def test_lead_doc_records_the_outcome():
    """The Petrie section of docs/lead_wiltshire.md records the final state: the refusal (ask_human 002,
    the human does not download books), the two plates and their canonical disposition, the undelivered
    rest of the book, and the stage-A/B recall as n/a (no book). A doc edit that drifts fails loud."""
    text = open(LEAD, encoding="utf-8").read()
    sec = text.split("## Petrie,", 1)
    assert len(sec) == 2, "the lead doc has no Petrie section"
    sec = sec[1].split("\n## ", 1)[0]
    for needle in ("ask_human 002", "skip it", "Pl. I", "Pl. II", "W.M.F.P.", "1880", "stonehenge-q39671",
                   "HMNTS 10352.i.12", "not re-staged", "n/a", "undelivered"):
        assert needle in sec, f"missing in the Petrie section: {needle!r}"
