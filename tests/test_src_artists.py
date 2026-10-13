"""The artists' views staging (task 213/213b, GOAL.md point 5): Leonardo's 1502 aerial plan of Imola (a new
site, aerial-photograph ground - no open LiDAR here) and Jacopo de' Barbari's 1500 view of Venice, staged by
fit/src_artists.py into this task's own files (extras/files/classified _artists.jsonl), plus the hand-verified
QID table the book towns go through (the seven towns of Civitates Liber secundus; 216/217 take the QIDs and
cite strings from it and from docs/lead_artists.md). The tests are offline: a socket-blocking fixture makes any
network fetch fail loud, so the evidence check runs from the stored fields only (200's fail-closed box). The
negative control pins the trap the hand record exists for: the Imola row with the Cervia point
(44.245 N, 12.367 E) instead of the site's own point - ~54 km away, a name-search-style resolution that record
--live could store - must be reported FAIL, never kept. The golden file (tests/golden/src_artists_sample.json)
pins the staged rows as a whole; it is regenerated only via the module's --golden flag for an intended change.
Task 228 (211's live merge puts the module's own staged rows into the canonical files) extends the check-staged
test: test_check_staged_three_states covers the three merge states of the --check guards hermetically -
pre-merge; the 211 first-row-wins merge already run (the module's own rows a no-op, the known-site guards stop
self-triggering); and a same-key different row, or a staged QID/site id held by a different site, still failing
loud.
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
import src_artists  # noqa: E402  fit/src_artists.py, the module under test


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """The check is offline by contract; make any network attempt in this module's tests fail loud."""
    def boom(*args, **kwargs):
        raise AssertionError(f"network access attempted: {args} {kwargs}")
    monkeypatch.setattr(socket, "socket", boom)
    monkeypatch.setattr(socket, "create_connection", boom)
    monkeypatch.setattr(socket, "getaddrinfo", boom)


def test_check_staged_files_join_and_pass(capsys):
    """src_artists --check, offline: the staged files join (every file row names a staged or existing site, no
    staged id/QID pre-exists, every staged site has a picture, (site, title) unique, no clash with the
    canonical files.jsonl, classified rows 1:1) and every staged row PASSes the evidence check."""
    code = src_artists.check_staged()
    out = capsys.readouterr().out
    assert code == 0, out
    assert "join:" not in out, f"join problems:\n{out}"
    assert "evidence: 2 rows, 2 pass, 0 fail, 0 no-tie" in out, out
    for key in ("imola-q50195|File:Leonardo da Vinci - RCIN 912284, A map of Imola 1502.jpg",
                "venice-q641|File:(Venice) View of Venice by Jacopo de' Barbari - Museo Correr.jpg"):
        assert f"PASS caption_coords  {key}" in out, f"missing PASS line for {key}:\n{out}"


def test_check_staged_three_states(tmp_path, monkeypatch, capsys):
    """The 211 merge states of the --check guards, hermetically (temp copies of the canonical files, so the
    test holds whether or not 211's live merge has run on this checkout): (a) staged rows ABSENT from the
    canonical files (the pre-merge state) - check 0, no join problems, evidence all PASS; (b) staged rows
    present with IDENTICAL content (the 211 first-row-wins merge has run) - check 0, no join problems: an
    already-merged row is a no-op and the known-site checks stop self-triggering on the module's own rows;
    (c) the same (site, title) key, or a staged QID or site id, held by a DIFFERENT row or site - still fails
    loud, naming exactly that problem and no other."""
    staged_files = src_artists._load(src_artists.FILES_ARTISTS)
    staged_sites = src_artists._load(src_artists.EXTRAS_ARTISTS)
    skeys = {(r.get("site"), r.get("title")) for r in staged_files}
    sids = {s["id"] for s in staged_sites}

    def write(name, text):
        p = tmp_path / name
        p.write_text(text, encoding="utf-8")
        return str(p)

    # the canonical files with this module's staged rows removed: the pre-merge state of ITS keys/sites on
    # any checkout (the other sources' merged rows are untouched, the guards do not care about them)
    files_pre = [json.dumps(r, ensure_ascii=False) for r in src_artists._load(src_artists.FILES_CANONICAL)
                 if (r.get("site"), r.get("title")) not in skeys]
    extras_pre = [json.dumps(r, ensure_ascii=False) for r in src_artists._load(src_artists.EXTRAS)
                  if r.get("id") not in sids]
    web = json.load(open(src_artists.WEB_SITES, encoding="utf-8"))
    monkeypatch.setattr(src_artists, "WEB_SITES",
                        write("sites.json", json.dumps(dict(web, sites=[s for s in web["sites"]
                                                               if s.get("id") not in sids]),
                                                       ensure_ascii=False)))
    sites = tmp_path / "sites.jsonl"
    sites.write_text(open(src_artists.SITES_JSONL, encoding="utf-8").read(), encoding="utf-8")
    monkeypatch.setattr(src_artists, "SITES_JSONL", str(sites))

    def point(files_rows, extras_rows):
        monkeypatch.setattr(src_artists, "FILES_CANONICAL",
                            write("files.jsonl", "\n".join(files_rows) + "\n"))
        monkeypatch.setattr(src_artists, "EXTRAS", write("extras.jsonl", "\n".join(extras_rows) + "\n"))

    staged_file_lines = [json.dumps(r, ensure_ascii=False) for r in staged_files]
    staged_site_lines = [json.dumps(s, ensure_ascii=False) for s in staged_sites]
    evidence_line = f"evidence: {len(staged_files)} rows, {len(staged_files)} pass, 0 fail, 0 no-tie"

    # (a) pre-merge: the staged rows are not in the canonical files yet
    point(files_pre, extras_pre)
    code = src_artists.check_staged()
    out = capsys.readouterr().out
    assert code == 0, out
    assert "join:" not in out, out
    assert evidence_line in out, out

    # (b) the 211 merge ran: every staged row is in the canonical files with identical content
    point(files_pre + staged_file_lines, extras_pre + staged_site_lines)
    code = src_artists.check_staged()
    out = capsys.readouterr().out
    assert code == 0, out
    assert "join:" not in out, out
    assert evidence_line in out, out

    # (c1) the same (site, title) key held by a DIFFERENT row: the pre-merge conflict protection still fires
    victim = staged_files[0]
    k = (victim["site"], victim["title"])
    other = dict(victim, name="a different row holds this key")
    lines = [json.dumps(other, ensure_ascii=False) if (r.get("site"), r.get("title")) == k
             else json.dumps(r, ensure_ascii=False) for r in staged_files]
    point(files_pre + lines, extras_pre + staged_site_lines)
    code = src_artists.check_staged()
    out = capsys.readouterr().out
    assert code == 1, out
    join = [l for l in out.splitlines() if l.startswith("join:")]
    assert join == [f"join: staged title already in the canonical files.jsonl: {k}"], join
    assert evidence_line in out, out

    # (c2) a staged site's QID held by a DIFFERENT site: the pre-merge QID protection still fires
    venice = next(s for s in staged_sites if s["qid"] == "Q641")
    other_site = dict(venice, id="venice-lagoon-q641")  # same QID, a different site
    point(files_pre, extras_pre + [json.dumps(other_site, ensure_ascii=False)])
    code = src_artists.check_staged()
    out = capsys.readouterr().out
    assert code == 1, out
    join = [l for l in out.splitlines() if l.startswith("join:")]
    assert join == [f"join: staged site {venice['id']} re-uses existing QID {venice['qid']} "
                    f"(venice-lagoon-q641)"], join
    assert evidence_line in out, out

    # (c3) a staged site's id held by a DIFFERENT site (a different QID): the pre-merge id protection
    # still fires
    imola = next(s for s in staged_sites if s["qid"] == "Q50195")
    other_site = dict(imola, qid="Q773853")  # same id, a different QID
    point(files_pre, extras_pre + [json.dumps(other_site, ensure_ascii=False)])
    code = src_artists.check_staged()
    out = capsys.readouterr().out
    assert code == 1, out
    join = [l for l in out.splitlines() if l.startswith("join:")]
    assert join == [f"join: staged site ids collide with existing sites: [{imola['id']!r}]"], join
    assert evidence_line in out, out


def test_qid_table_and_staged_rows():
    """The hand-checked table is complete and the staged rows are exactly it: two SITES sites (Imola, Venice)
    plus the seven book towns of Liber secundus (eight unique QIDs, never a name-search-only one); every staged
    extras row is complete (id/qid/name/lon/lat/region/kind/wikipedia/aerial_ok) and matches its table entry;
    the staged file rows are exactly the module's source rows with the known drawing dates (1502/1500)."""
    table = src_artists.table_sites()
    assert set(table) == {"Q239", "Q490", "Q641", "Q12892", "Q1741", "Q2044", "Q220", "Q50195"}
    assert set(src_artists.SITES) == {"Q50195", "Q641"}  # the two image-level sources
    assert list(src_artists.BOOKS["civitates"]["sites"]) == ["Q239", "Q12892", "Q1741", "Q490", "Q641",
                                                             "Q2044", "Q220"]  # the book's plate order
    for qid, s in table.items():
        for k in ("name", "lon", "lat", "place", "wikipedia", "cat"):
            assert s.get(k), f"{qid} missing {k}"

    extras = src_artists._load(src_artists.EXTRAS_ARTISTS)
    assert [s["id"] for s in extras] == ["imola-q50195", "venice-q641"]
    for s in extras:
        t = src_artists.SITES[s["qid"]]
        for k in ("name", "lon", "lat", "place", "wikipedia"):
            assert s[k] == t[k], f"{s['id']}: field {k} differs from the SITES table"
        assert s["region"] == "Italy" and s["kind"] == "town" and s["aerial_ok"] is True
        assert s.get("note")  # the no-open-LiDAR / fit-scale notes 212 reads

    files = src_artists._load(src_artists.FILES_ARTISTS)
    want = {(r[0], r[1]) for src in src_artists.SOURCES.values() for r in src["rows"]}
    assert {(r["title"], r["qid"]) for r in files} == want
    years = {"File:Leonardo da Vinci - RCIN 912284, A map of Imola 1502.jpg": 1502,  # known drawing date, the file page has none
             "File:(Venice) View of Venice by Jacopo de' Barbari - Museo Correr.jpg": 1500}  # DateTimeOriginal
    for r in files:
        assert r["year"] == years[r["title"]]
        assert r.get("evidence") and r["evidence"]["kind"] == "caption_coords"


def test_evidence_offline_and_negative_control(tmp_path):
    """fit/evidence.py's check over the staged rows, offline: exit 0, zero FAIL, every row PASS
    caption_coords. The negative control (never written into the staged files) is reported FAIL: the Imola row
    with the Cervia point instead of the site's own point - the ~54 km name-search trap a live record could
    store - fails both the stored-distance reproduction and the 50 km tolerance (200's fails-closed box)."""
    code, text = evidence.check(src_artists.FILES_ARTISTS, src_artists.NO_BOOKS, catalog=src_artists.EXTRAS_ARTISTS)
    assert code == 0, text
    assert "evidence: 2 rows, 2 pass, 0 fail, 0 no-tie" in text, text

    imola = next(r for r in src_artists._load(src_artists.FILES_ARTISTS) if r["site"] == "imola-q50195")
    bad = dict(imola)
    bad["evidence"] = dict(imola["evidence"], place_lon=12.367, place_lat=44.245, dist_m=0.0)  # Cervia, 44.245 N 12.367 E
    f = tmp_path / "bad_imola.jsonl"
    f.write_text(json.dumps(bad, ensure_ascii=False) + "\n", encoding="utf-8")
    code, text = evidence.check(str(f), src_artists.NO_BOOKS, catalog=src_artists.EXTRAS_ARTISTS)
    assert code == 1, text
    line = next(l for l in text.splitlines() if l.startswith("FAIL"))
    assert "imola-q50195" in line and "does not reproduce (53566 m)" in line, line
    assert "evidence: 1 rows, 0 pass, 1 fail, 0 no-tie" in text, text
    assert imola["evidence"]["place_lon"] == 11.7112  # the staged row is untouched by the control


def test_golden_sample_matches_staged_rows():
    """tests/golden/src_artists_sample.json (written by the module's --golden, keys sorted, checked/
    date_commons normalized) is the staged rows exactly - the pin the staging files are final against."""
    golden = json.load(open(os.path.join(ROOT, "tests", "golden", "src_artists_sample.json"), encoding="utf-8"))
    want = {"extras": src_artists._norm(src_artists._load(src_artists.EXTRAS_ARTISTS)),
            "files": src_artists._norm(src_artists._load(src_artists.FILES_ARTISTS)),
            "classified": src_artists._norm(src_artists._load(src_artists.CLASSIFIED_ARTISTS))}
    assert golden == want, "the staged rows differ from the golden sample - an intended change needs --golden"
