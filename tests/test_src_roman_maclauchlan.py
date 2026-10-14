"""The Maclauchlan staging (task 207b, GOAL.md point 4): the one legible site plan of the 1858 original
(n0093, Fig. 4, the plan of Carlisle) staged by fit/src_roman_maclauchlan.py into the shared roman staging
files (files_roman/classified_roman.jsonl + the new site luguvallium-q71551754 in extras_roman.jsonl - the
other kind-s plates are blank in this copy, the per-leaf verdicts in the Maclauchlan section of
docs/lead_roman.md). The tests are offline: a socket-blocking fixture makes any network attempt fail loud,
so stage() and the evidence check run from the committed per-book artifacts only (the 200 fail-closed box),
no LLM, no fixed ports - the module's staging-file path constants are monkeypatched to temp files, so the
committed staging files are never touched. The negative controls pin the traps the stored evidence exists
for: a stored distance that does not reproduce from the stored coordinates, and a caption that does not
name the place - both must be reported FAIL, never kept. The golden file (tests/golden/
src_roman_maclauchlan_sample.json) pins the staged rows; it is regenerated only via the module's --golden
flag for an intended change.
"""
import json
import os
import socket
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for d in (os.path.join(ROOT, "fit"), os.path.join(ROOT, "pipeline")):
    if d not in sys.path:
        sys.path.insert(0, d)
import evidence  # noqa: E402  fit/evidence.py
import src_roman_maclauchlan as sm  # noqa: E402  fit/src_roman_maclauchlan.py, the module under test


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """The staging and the check are offline by contract; make any network attempt in these tests fail loud."""
    def boom(*args, **kwargs):
        raise AssertionError(f"network access attempted: {args} {kwargs}")
    monkeypatch.setattr(socket, "socket", boom)
    monkeypatch.setattr(socket, "create_connection", boom)
    monkeypatch.setattr(socket, "getaddrinfo", boom)


def _stage_into(tmp_path, monkeypatch):
    """Point the module's staging-file constants at temp files and run stage() once - the committed roman
    staging files are never touched."""
    paths = {}
    for name in ("FILES_ROMAN", "EXTRAS_ROMAN", "CLASSIFIED_ROMAN"):
        p = tmp_path / (name.lower() + ".jsonl")
        monkeypatch.setattr(sm, name, str(p))
        paths[name] = str(p)
    sm.stage()
    return paths


def test_stage_writes_one_row_per_file_and_is_idempotent(tmp_path, monkeypatch, capsys):
    """stage() (offline, no LLM) writes exactly one row into each of the three roman staging files: the new
    site luguvallium-q71551754 (Q71551754, kind roman fort, region england, the location_check cross-check),
    the n0093 picture row (w/h from the committed stage-B row, the caption_coords evidence with the stored
    324.1 m distance) and its hand "plan" classified row. A second run writes no byte (idempotent on
    (site, title) and site id)."""
    paths = _stage_into(tmp_path, monkeypatch)
    out = capsys.readouterr().out
    assert out.count("appended 1 row") == 3, out

    sites = sm._load(paths["EXTRAS_ROMAN"])
    files = sm._load(paths["FILES_ROMAN"])
    cls = sm._load(paths["CLASSIFIED_ROMAN"])
    s = sites[0]
    assert (s["id"], s["qid"], s["name"]) == ("luguvallium-q71551754", "Q71551754", "Luguvallium (Carlisle)")
    assert (s["lon"], s["lat"], s["region"], s["kind"]) == (-2.94077, 54.896187, "england", "roman fort")
    assert s["aerial_ok"] is True and s["source"] == sm.MODULE
    assert s["location_check"]["status"] == "confirmed" and "324 m" in s["location_check"]["note"]

    f = files[0]
    assert (f["site"], f["qid"], f["title"], f["year"], f["date"], f["artist"]) == \
        ("luguvallium-q71551754", "Q71551754", sm.FILE_TITLE, 1858, "1858", "Henry Maclauchlan")
    assert (f["w"], f["h"]) == (964, 1400)  # read from the committed stage-B row
    assert f["url"] == f"https://archive.org/download/{sm.IA}/page/n0093.jpg"
    ev = f["evidence"]
    assert (ev["rec"], ev["kind"], ev["named_place"], ev["place_qid"]) == \
        ("evidence/1", "caption_coords", "Carlisle", "Q192896")
    assert (ev["place_lon"], ev["place_lat"]) == (-2.936388889, 54.894722222)
    assert (ev["site_lon"], ev["site_lat"]) == (-2.94077, 54.896187)
    assert ev["dist_m"] == 324.1

    c = cls[0]
    assert (c["site"], c["title"], c["p_plan"], c["p_birdseye"], c["p_photo"], c["by"]) == \
        ("luguvallium-q71551754", sm.FILE_TITLE, 1.0, 0.0, 0.0, "hand")

    before = [open(p, encoding="utf-8").read() for p in paths.values()]
    sm.stage()
    out = capsys.readouterr().out
    assert out.count("row already present (skipped, nothing written)") == 3, out
    assert [open(p, encoding="utf-8").read() for p in paths.values()] == before  # a second run changes no byte


def test_check_staged_joins_and_passes(tmp_path, monkeypatch, capsys):
    """--check, offline: (a) the pre-merge state on this branch (the roman staging not yet in the canonical
    files) joins clean and the row PASSes the evidence check; (b) after the 211 merge (the staged site row
    in the canonical extras, identical) it still joins clean - a merged row is a no-op; (c) the same id
    held by a DIFFERENT canonical row fails loud (the pre-merge conflict protection). The canonical path
    constants are monkeypatched to temp copies, so the test holds whether or not 211's live merge has run."""
    _stage_into(tmp_path, monkeypatch)
    staged_sites = sm._load(sm.EXTRAS_ROMAN)
    assert len(staged_sites) == 1

    # (a) pre-merge: the canonical files are the real ones (the roman id/QID is in neither)
    code = sm.check_staged()
    out = capsys.readouterr().out
    assert code == 0, out
    assert "join:" not in out, out
    assert "evidence: 1 rows, 1 pass, 0 fail, 0 no-tie" in out, out
    line = next(l for l in out.splitlines() if l.startswith("PASS"))
    assert "caption_coords" in line and "luguvallium-q71551754" in line and sm.FILE_TITLE in line, line

    real_sites = open(sm.SITES_CATALOG).read()   # captured before the monkeypatch re-points the constants
    real_extras = open(sm.EXTRAS_CANONICAL).read()
    monkeypatch.setattr(sm, "SITES_CATALOG", str(tmp_path / "sites_catalog.jsonl"))
    monkeypatch.setattr(sm, "EXTRAS_CANONICAL", str(tmp_path / "extras_catalog.jsonl"))
    (tmp_path / "sites_catalog.jsonl").write_text(real_sites, encoding="utf-8")

    # (b) the 211 merge ran: the staged site row is in the canonical extras with identical content
    (tmp_path / "extras_catalog.jsonl").write_text(
        real_extras + json.dumps(staged_sites[0], ensure_ascii=False) + "\n", encoding="utf-8")
    code = sm.check_staged()
    out = capsys.readouterr().out
    assert code == 0, out
    assert "join:" not in out, out
    assert "evidence: 1 rows, 1 pass, 0 fail, 0 no-tie" in out, out

    # (c) the same id held by a DIFFERENT row: the pre-merge conflict protection fires
    altered = dict(staged_sites[0], qid="Q99999999")  # same id, different content
    (tmp_path / "extras_catalog.jsonl").write_text(
        real_extras + json.dumps(altered, ensure_ascii=False) + "\n", encoding="utf-8")
    code = sm.check_staged()
    out = capsys.readouterr().out
    assert code == 1, out
    join = [l for l in out.splitlines() if l.startswith("join:")]
    assert join == ["join: staged site luguvallium-q71551754 differs from its canonical row in "
                    "extras_catalog.jsonl"], join


def test_evidence_offline_and_negative_control(tmp_path, monkeypatch, capsys):
    """fit/evidence.py's check over the staged row, offline: exit 0, the one row PASSes from stored fields
    only. The negative controls (never written into the staged files) are reported FAIL: a stored distance
    that does not reproduce from the stored coordinates, and a caption that does not name the place - the
    traps a live record could store. Both fail 200's fail-closed box; the staged row stays untouched."""
    _stage_into(tmp_path, monkeypatch)
    r = sm._load(sm.FILES_ROMAN)[0]

    code, text = evidence.check(sm.FILES_ROMAN, sm.NO_BOOKS, catalog=sm.SITES_CATALOG)
    assert code == 0, text
    assert "evidence: 1 rows, 1 pass, 0 fail, 0 no-tie" in text, text

    bad_dist = dict(r)
    ev = dict(r["evidence"])
    ev["dist_m"] = 48000  # does not reproduce: the stored distance must match the stored coordinates
    bad_dist["evidence"] = ev
    bad_name = dict(r)
    bad_name["title"] = "THE WALL AND THE YALLUM."  # no "Carlisle" anywhere in the row's printed text
    bad_name["desc"] = ""

    f = tmp_path / "bad_rows.jsonl"
    f.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in (bad_dist, bad_name)) + "\n",
                 encoding="utf-8")
    code, text = evidence.check(str(f), sm.NO_BOOKS, catalog=sm.SITES_CATALOG)
    assert code == 1, text
    line = next(l for l in text.splitlines() if l.startswith("FAIL") and "48000" in l)
    assert "stored distance 48000 m does not reproduce (324 m)" in line, line
    line = next(l for l in text.splitlines() if l.startswith("FAIL") and l.endswith("does not name 'Carlisle'"))
    assert line, text
    assert "evidence: 2 rows, 0 pass, 2 fail, 0 no-tie" in text, text
    assert sm._load(sm.FILES_ROMAN)[0] == r  # the staged row is untouched by the controls


def test_golden_matches_staged_rows():
    """tests/golden/src_roman_maclauchlan_sample.json (written by the module's --golden: this book's staged
    rows - the one picture, its new site, its classified row - plus the per-file counts, dates normalized,
    keys sorted) is the committed staged rows exactly - the pin the staging files are final against."""
    golden = json.load(open(os.path.join(ROOT, "tests", "golden", "src_roman_maclauchlan_sample.json"),
                            encoding="utf-8"))
    files = [r for r in sm._load(sm.FILES_ROMAN) if r.get("by") == sm.MODULE]
    sites = [s for s in sm._load(sm.EXTRAS_ROMAN) if s.get("source") == sm.MODULE]
    keys = {(r["site"], r["title"]) for r in files}
    cls = [c for c in sm._load(sm.CLASSIFIED_ROMAN) if (c.get("site"), c.get("title")) in keys]
    assert golden["count"] == {"extras": 1, "files": 1, "classified": 1}
    assert golden["extras"] == sm._norm(sites)
    assert golden["files"] == sm._norm(files)
    assert golden["classified"] == sm._norm(cls)
