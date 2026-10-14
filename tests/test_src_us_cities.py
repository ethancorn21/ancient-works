"""The US city plans staging (task 236a, GOAL.md point 5): the four old plans of New York - the 1660 Castello
plan, the 1767 Ratzer map, the 1811 Commissioners' Plan (bird's-eye) and the 1865 Viele map - staged by
fit/src_us_cities.py into this task's own files (extras/files/classified _us_cities.jsonl), plus the
hand-verified QID table (New York City Q60; Washington DC, San Francisco and Nashville follow in later
sessions, 236c consolidates). The tests are offline: a socket-blocking fixture makes any network fetch fail
loud, so the evidence check runs from the stored fields only (200's fail-closed box). The negative control
pins the trap the hand record exists for: a staged row with a foreign place point (Venice) instead of the
site's own point - ~10408 km away, a name-search-style resolution that record --live could store - must be
reported FAIL, never kept. The golden file (tests/golden/src_us_cities_sample.json) pins the staged rows as
a whole; it is regenerated only via the module's --golden flag for an intended change. The
check-staged test covers the three merge states of the --check guards hermetically - pre-merge; the
236c first-row-wins merge already run (the module's own rows a no-op, the known-site guards stop
self-triggering); and a same-key different row, or a staged QID/site id held by a different site, still
failing loud.
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
import src_us_cities  # noqa: E402  fit/src_us_cities.py, the module under test


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """The check is offline by contract; make any network attempt in this module's tests fail loud."""
    def boom(*args, **kwargs):
        raise AssertionError(f"network access attempted: {args} {kwargs}")
    monkeypatch.setattr(socket, "socket", boom)
    monkeypatch.setattr(socket, "create_connection", boom)
    monkeypatch.setattr(socket, "getaddrinfo", boom)


def test_check_staged_files_join_and_pass(capsys):
    """src_us_cities --check, offline: the staged files join (every file row names a staged or existing
    site, no staged id/QID pre-exists, every staged site has a picture, (site, title) unique, no clash with
    the canonical files.jsonl, classified rows 1:1) and every staged row PASSes the evidence check."""
    code = src_us_cities.check_staged()
    out = capsys.readouterr().out
    assert code == 0, out
    assert "join:" not in out, f"join problems:\n{out}"
    assert "evidence: 4 rows, 4 pass, 0 fail, 0 no-tie" in out, out
    for key in ("new-york-q60|File:Afbeeldinge van de Stadt Amsterdam in Nieuw Neederlandt (NYPL Hades-118555-54682).tif",
                "new-york-q60|File:Plan of the City of New York by Bernard Ratzer, 1767.jpg",
                "new-york-q60|File:Commissioners' Plan of 1811 by John Randel published in 1821.jpg",
                "new-york-q60|File:Viele Map (Topographical map of the City of New York), 1865.jpg"):
        assert f"PASS caption_coords  {key}" in out, f"missing PASS line for {key}:\n{out}"


def test_check_staged_three_states(tmp_path, monkeypatch, capsys):
    """The 236c merge states of the --check guards, hermetically (temp copies of the canonical files, so
    the test holds whether or not 236c's live merge has run on this checkout): (a) staged rows ABSENT from
    the canonical files (the pre-merge state) - check 0, no join problems, evidence all PASS; (b) staged
    rows present with IDENTICAL content (the 236c first-row-wins merge has run) - check 0, no join
    problems: an already-merged row is a no-op and the known-site checks stop self-triggering on the
    module's own rows; (c) the same (site, title) key, or a staged QID or site id, held by a DIFFERENT row
    or site - still fails loud, naming exactly that problem and no other. This task stages one site so
    far; the test scales when the other cities are added."""
    staged_files = src_us_cities._load(src_us_cities.FILES_US_CITIES)
    staged_sites = src_us_cities._load(src_us_cities.EXTRAS_US_CITIES)
    skeys = {(r.get("site"), r.get("title")) for r in staged_files}
    sids = {s["id"] for s in staged_sites}

    def write(name, text):
        p = tmp_path / name
        p.write_text(text, encoding="utf-8")
        return str(p)

    # the canonical files with this module's staged rows removed: the pre-merge state of ITS keys/sites on
    # any checkout (the other sources' merged rows are untouched, the guards do not care about them)
    files_pre = [json.dumps(r, ensure_ascii=False) for r in src_us_cities._load(src_us_cities.FILES_CANONICAL)
                 if (r.get("site"), r.get("title")) not in skeys]
    extras_pre = [json.dumps(r, ensure_ascii=False) for r in src_us_cities._load(src_us_cities.EXTRAS)
                  if r.get("id") not in sids]
    web = json.load(open(src_us_cities.WEB_SITES, encoding="utf-8"))
    monkeypatch.setattr(src_us_cities, "WEB_SITES",
                        write("sites.json", json.dumps(dict(web, sites=[s for s in web["sites"]
                                                               if s.get("id") not in sids]),
                                                       ensure_ascii=False)))
    sites = tmp_path / "sites.jsonl"
    sites.write_text(open(src_us_cities.SITES_JSONL, encoding="utf-8").read(), encoding="utf-8")
    monkeypatch.setattr(src_us_cities, "SITES_JSONL", str(sites))

    def point(files_rows, extras_rows):
        monkeypatch.setattr(src_us_cities, "FILES_CANONICAL",
                            write("files.jsonl", "\n".join(files_rows) + "\n"))
        monkeypatch.setattr(src_us_cities, "EXTRAS", write("extras.jsonl", "\n".join(extras_rows) + "\n"))

    staged_file_lines = [json.dumps(r, ensure_ascii=False) for r in staged_files]
    staged_site_lines = [json.dumps(s, ensure_ascii=False) for s in staged_sites]
    evidence_line = f"evidence: {len(staged_files)} rows, {len(staged_files)} pass, 0 fail, 0 no-tie"

    # (a) pre-merge: the staged rows are not in the canonical files yet
    point(files_pre, extras_pre)
    code = src_us_cities.check_staged()
    out = capsys.readouterr().out
    assert code == 0, out
    assert "join:" not in out, out
    assert evidence_line in out, out

    # (b) the 236c merge ran: every staged row is in the canonical files with identical content
    point(files_pre + staged_file_lines, extras_pre + staged_site_lines)
    code = src_us_cities.check_staged()
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
    code = src_us_cities.check_staged()
    out = capsys.readouterr().out
    assert code == 1, out
    join = [l for l in out.splitlines() if l.startswith("join:")]
    assert join == [f"join: staged title already in the canonical files.jsonl: {k}"], join
    assert evidence_line in out, out

    # (c2) a staged site's QID held by a DIFFERENT site: the pre-merge QID protection still fires
    ny = next(s for s in staged_sites if s["qid"] == "Q60")
    other_site = dict(ny, id="new-york-harbor-q60")  # same QID, a different site
    point(files_pre, extras_pre + [json.dumps(other_site, ensure_ascii=False)])
    code = src_us_cities.check_staged()
    out = capsys.readouterr().out
    assert code == 1, out
    join = [l for l in out.splitlines() if l.startswith("join:")]
    assert join == [f"join: staged site {ny['id']} re-uses existing QID {ny['qid']} (new-york-harbor-q60)"], join
    assert evidence_line in out, out

    # (c3) a staged site's id held by a DIFFERENT site (a different QID): the pre-merge id protection
    # still fires
    other_site = dict(ny, qid="Q30492")  # same id, a different QID (Q30492 is the NUMBER "483")
    point(files_pre, extras_pre + [json.dumps(other_site, ensure_ascii=False)])
    code = src_us_cities.check_staged()
    out = capsys.readouterr().out
    assert code == 1, out
    join = [l for l in out.splitlines() if l.startswith("join:")]
    assert join == [f"join: staged site ids collide with existing sites: [{ny['id']!r}]"], join
    assert evidence_line in out, out


def test_qid_table_and_staged_rows():
    """The hand-checked table is complete and the staged rows are exactly it: New York City (Q60) staged
    this session - Washington DC (Q61), San Francisco (Q62) and Nashville (Q23197) follow in later
    sessions (the trap note: the prep's first New York memory, Q30492, is the NUMBER "483") - every staged
    extras row is complete (id/qid/name/lon/lat/region/kind/wikipedia/aerial_ok) and matches its table
    entry; the staged file rows are exactly the module's source rows with the known drawing dates (the
    1811 plan and the 1660 Castello survey, whose file page lost the date, swapped in)."""
    table = src_us_cities.SITES
    assert set(table) == {"Q60"}
    s = table["Q60"]
    assert s["id"] == "new-york-q60"
    for k in ("name", "named", "lon", "lat", "place", "wikipedia", "note"):
        assert s.get(k), f"Q60 missing {k}"
    assert s["region"] == "United States" and s["kind"] == "town"

    extras = src_us_cities._load(src_us_cities.EXTRAS_US_CITIES)
    assert [x["id"] for x in extras] == ["new-york-q60"]
    for x in extras:
        t = table[x["qid"]]
        for k in ("name", "lon", "lat", "place", "wikipedia"):
            assert x[k] == t[k], f"{x['id']}: field {k} differs from the SITES table"
        assert x["region"] == "United States" and x["kind"] == "town" and x["aerial_ok"] is True
        assert x.get("note")  # the aerial-ground / fit-scale note 212 reads

    files = src_us_cities._load(src_us_cities.FILES_US_CITIES)
    want = {(r[0], r[1]) for src in src_us_cities.SOURCES.values() for r in src["rows"]}
    assert {(r["title"], r["qid"]) for r in files} == want
    years = {"File:Afbeeldinge van de Stadt Amsterdam in Nieuw Neederlandt (NYPL Hades-118555-54682).tif": 1660,
             "File:Plan of the City of New York by Bernard Ratzer, 1767.jpg": 1767,
             "File:Commissioners' Plan of 1811 by John Randel published in 1821.jpg": 1811,
             "File:Viele Map (Topographical map of the City of New York), 1865.jpg": 1865}
    for r in files:
        assert r["year"] == years[r["title"]]
        assert r.get("evidence") and r["evidence"]["kind"] == "caption_coords"
        assert r["evidence"]["named_place"] == "New York"
    by_title = {r["title"]: r for r in files}
    # the known-drawing-date swaps: the page value kept as date_commons (the Zwolle precedent)
    assert by_title[years and "File:Afbeeldinge van de Stadt Amsterdam in Nieuw Neederlandt (NYPL Hades-118555-54682).tif"]["date"] == "1660"
    assert by_title["File:Afbeeldinge van de Stadt Amsterdam in Nieuw Neederlandt (NYPL Hades-118555-54682).tif"]["date_commons"] == "[Date not available]"
    assert by_title["File:Commissioners' Plan of 1811 by John Randel published in 1821.jpg"]["date"] == "1811"
    assert by_title["File:Commissioners' Plan of 1811 by John Randel published in 1821.jpg"]["date_commons"] == "1821"


def test_evidence_offline_and_negative_control(tmp_path):
    """fit/evidence.py's check over the staged rows, offline: exit 0, zero FAIL, every row PASS
    caption_coords. The negative control (never written into the staged files) is reported FAIL: the
    Castello row with the Venice point instead of the site's own point - ~10408 km away, a
    name-search-style resolution a live record could store - fails both the stored-distance reproduction
    and the 50 km tolerance (200's fails-closed box)."""
    code, text = evidence.check(src_us_cities.FILES_US_CITIES, src_us_cities.NO_BOOKS,
                                catalog=src_us_cities.EXTRAS_US_CITIES)
    assert code == 0, text
    assert "evidence: 4 rows, 4 pass, 0 fail, 0 no-tie" in text, text

    castello = next(r for r in src_us_cities._load(src_us_cities.FILES_US_CITIES)
                    if r["title"].startswith("File:Afbeeldinge"))
    bad = dict(castello)
    bad["evidence"] = dict(castello["evidence"], place_lon=12.33, place_lat=45.44, dist_m=0.0)  # Venice
    f = tmp_path / "bad_new_york.jsonl"
    f.write_text(json.dumps(bad, ensure_ascii=False) + "\n", encoding="utf-8")
    code, text = evidence.check(str(f), src_us_cities.NO_BOOKS, catalog=src_us_cities.EXTRAS_US_CITIES)
    assert code == 1, text
    line = next(l for l in text.splitlines() if l.startswith("FAIL"))
    assert "new-york-q60" in line and "does not reproduce (10407617 m)" in line, line
    assert "evidence: 1 rows, 0 pass, 1 fail, 0 no-tie" in text, text
    assert castello["evidence"]["place_lon"] == -74.006111  # the staged row is untouched by the control


def test_golden_sample_matches_staged_rows():
    """tests/golden/src_us_cities_sample.json (written by the module's --golden, keys sorted, checked/
    date_commons normalized) is the staged rows exactly - the pin the staging files are final against."""
    golden = json.load(open(os.path.join(ROOT, "tests", "golden", "src_us_cities_sample.json"), encoding="utf-8"))
    want = {"extras": src_us_cities._norm(src_us_cities._load(src_us_cities.EXTRAS_US_CITIES)),
            "files": src_us_cities._norm(src_us_cities._load(src_us_cities.FILES_US_CITIES)),
            "classified": src_us_cities._norm(src_us_cities._load(src_us_cities.CLASSIFIED_US_CITIES))}
    assert golden == want, "the staged rows differ from the golden sample - an intended change needs --golden"
