"""US bird's-eye-view staging, batch 5 (task 241, part of 236; GOAL.md point 5: artists' aerial and
bird's-eye views count as much as surveys): the FINAL FIVE US cities of the 25-city total (16 from
236b + 4 from 240 + 5 here), each a NEW site of its own in this task's own staging files (one
module + one staging file set per batch, so 240 and 241 built in parallel), from the LOC
"Panoramic Maps" collection (about 1,500 US bird's-eye views, 1847-1929, public domain; this
machine cannot reach loc.gov, so the files are fetched from their Wikimedia Commons mirrors - the
236b route, its lead doc). The candidate order (240's lead-doc "Not done yet" pointer, continuing
the 181 candidate list of the 236b lead doc): Omaha (skipped in 236b with no recorded drop reason
- re-run its pool search and record the verdict), Indianapolis, Columbus, Memphis, then whatever
the collection's search order adds to reach five - the task owes FIVE staged cities, not
specifically these, one steepest near-vertical whole-city view each (a city with no usable view
gets a lead-doc note and the next candidate). The tests are offline: a socket-blocking fixture
makes any network fetch fail loud, so the evidence check runs from the stored fields only (200's
fail-closed box). The negative control pins the trap the hand record exists for: a row whose
stored place point is a FOREIGN point (Venice) instead of the site's own point - thousands of km
away, a name-search-style resolution that record --live could store - must be reported FAIL, never
kept (synthetic at module creation; the first city landing rebinds it to the real first staged
row, the 236b/240 pattern). The golden file (tests/golden/src_us_birdseye_batch5_sample.json)
pins the staged rows as a whole; it is regenerated only via the module's --golden flag for an
intended change. The check-staged test covers the merge states of the --check guards hermetically
- pre-merge; the 236c first-row-wins merge already run (an already-merged row is a no-op); and a
same-key different row still failing loud - with the batch-5 new sites held by the site-level
guards (a staged id/QID held by a different site fails; this batch stages NO shared owner-named
cities, so the staged ids are new in every state: 236a's, 236b's and 240's read-only extras
files hold none of them).
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
import src_us_birdseye_batch5  # noqa: E402  fit/src_us_birdseye_batch5.py, the module under test


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """The check is offline by contract; make any network attempt in this module's tests fail loud."""
    def boom(*args, **kwargs):
        raise AssertionError(f"network access attempted: {args} {kwargs}")
    monkeypatch.setattr(socket, "socket", boom)
    monkeypatch.setattr(socket, "create_connection", boom)
    monkeypatch.setattr(socket, "getaddrinfo", boom)


def test_check_staged_files_join_and_pass(capsys):
    """src_us_birdseye_batch5 --check, offline: the staged files join (every file row names an
    existing or staged site - the batch-5 ids via this task's own extras file, never a QID on two
    sites, (site, title) unique, no clash with the canonical files.jsonl, classified rows 1:1,
    every new site has a picture) and every staged row PASSes the evidence check. The key list
    grows one entry per city landing (Omaha first, in the candidate order of the lead doc; none
    at module creation)."""
    code = src_us_birdseye_batch5.check_staged()
    out = capsys.readouterr().out
    assert code == 0, out
    assert "join:" not in out, f"join problems:\n{out}"
    n = len(src_us_birdseye_batch5._load(src_us_birdseye_batch5.FILES_BIRDS))
    assert f"evidence: {n} rows, {n} pass, 0 fail, 0 no-tie" in out, out
    for key in ():  # grows one entry per city landing
        assert f"PASS caption_coords  {key}" in out, f"missing PASS line for {key}:\n{out}"


def test_check_staged_three_states(tmp_path, monkeypatch, capsys):
    """The 236c merge states of the --check guards, hermetically (temp copies of the canonical
    files, so the test holds whether or not 236c's live merge has run on this checkout): (a)
    staged rows ABSENT from the canonical files (the pre-merge state) - check 0, no join problems,
    evidence all PASS; (b) staged rows present with IDENTICAL content (the 236c first-row-wins
    merge has run) - check 0, no join problems: an already-merged row is a no-op; (c) the same
    (site, title) key held by a DIFFERENT row - still fails loud, naming exactly that problem and
    no other (the batch-4/236b pattern; a no-op at module creation, re-enabled by the first city
    landing). This batch stages NO shared (owner-named) cities, so every staged id is NEW in every
    state: known_sites() is built from the real catalog/extras + 236a's + 236b's + 240's extras
    files and the temp web file, none holding a batch-5 id (236a's four owner cities, 236b's
    sixteen and 240's four stay known as other sites, never colliding - the QID-unique guards are
    what make that true)."""
    staged_files = src_us_birdseye_batch5._load(src_us_birdseye_batch5.FILES_BIRDS)
    staged_sites = src_us_birdseye_batch5._load(src_us_birdseye_batch5.EXTRAS_BIRDS)
    skeys = {(r.get("site"), r.get("title")) for r in staged_files}
    sids = {s["id"] for s in staged_sites}

    def write(name, text):
        p = tmp_path / name
        p.write_text(text, encoding="utf-8")
        return str(p)

    # the canonical files with this module's staged rows removed: the pre-merge state of ITS keys/sites
    # on any checkout (the other sources' merged rows are untouched, the guards do not care about them)
    files_pre = [json.dumps(r, ensure_ascii=False) for r in src_us_birdseye_batch5._load(src_us_birdseye_batch5.FILES_CANONICAL)
                 if (r.get("site"), r.get("title")) not in skeys]
    extras_pre = [json.dumps(r, ensure_ascii=False) for r in src_us_birdseye_batch5._load(src_us_birdseye_batch5.EXTRAS)
                  if r.get("id") not in sids]
    web = json.load(open(src_us_birdseye_batch5.WEB_SITES, encoding="utf-8"))
    monkeypatch.setattr(src_us_birdseye_batch5, "WEB_SITES",
                        write("sites.json", json.dumps(dict(web, sites=[s for s in web["sites"]
                                                               if s.get("id") not in sids]),
                                                       ensure_ascii=False)))
    sites = tmp_path / "sites.jsonl"
    sites.write_text(open(src_us_birdseye_batch5.SITES_JSONL, encoding="utf-8").read(), encoding="utf-8")
    monkeypatch.setattr(src_us_birdseye_batch5, "SITES_JSONL", str(sites))

    def point(files_rows, extras_rows):
        monkeypatch.setattr(src_us_birdseye_batch5, "FILES_CANONICAL",
                            write("files.jsonl", "\n".join(files_rows) + "\n"))
        monkeypatch.setattr(src_us_birdseye_batch5, "EXTRAS", write("extras.jsonl", "\n".join(extras_rows) + "\n"))

    staged_file_lines = [json.dumps(r, ensure_ascii=False) for r in staged_files]
    staged_site_lines = [json.dumps(s, ensure_ascii=False) for s in staged_sites]
    evidence_line = f"evidence: {len(staged_files)} rows, {len(staged_files)} pass, 0 fail, 0 no-tie"

    # (a) pre-merge: the staged rows are not in the canonical files yet
    point(files_pre, extras_pre)
    code = src_us_birdseye_batch5.check_staged()
    out = capsys.readouterr().out
    assert code == 0, out
    assert "join:" not in out, out
    assert evidence_line in out, out

    # (b) the 236c merge ran: every staged row is in the canonical files with identical content
    point(files_pre + staged_file_lines, extras_pre + staged_site_lines)
    code = src_us_birdseye_batch5.check_staged()
    out = capsys.readouterr().out
    assert code == 0, out
    assert "join:" not in out, out
    assert evidence_line in out, out

    # (c) the same (site, title) key held by a DIFFERENT row: the pre-merge conflict protection
    # still fires (only once a staged row exists - the batch-4/236b pattern, re-enabled by the
    # first city landing)
    if staged_files:
        victim = staged_files[0]
        k = (victim["site"], victim["title"])
        other = dict(victim, name="a different row holds this key")
        lines = [json.dumps(other, ensure_ascii=False) if (r.get("site"), r.get("title")) == k
                 else json.dumps(r, ensure_ascii=False) for r in staged_files]
        point(files_pre + lines, extras_pre + staged_site_lines)
        code = src_us_birdseye_batch5.check_staged()
        out = capsys.readouterr().out
        assert code == 1, out
        join = [l for l in out.splitlines() if l.startswith("join:")]
        assert join == [f"join: staged title already in the canonical files.jsonl: {k}"], join
        assert evidence_line in out, out


def test_sites_table_and_staged_rows():
    """The hand-checked tables and the staged rows are exactly them: batch 5 stages NO shared
    (owner-named) cities - 236a's four owner cities are tied to their 236a site ids by 236b's
    module (its tests) - so this task's extras file has NO owner-city rows at all: it is EXACTLY
    the SITES set, one new site per city (region "United States", kind "town", aerial_ok true)
    and one steepest view each; the staged file rows are exactly the module's source rows: each
    pick's page date matches the drawing (a Zwolle-style swap lands as date=... only if a later
    sheet needs one, the page value kept as date_commons), and every row's evidence point is the
    site's own point (the city's verified P625) with the short caption name. The tables grow one
    entry per city landing (empty at module creation; the candidate order: Omaha, Indianapolis,
    Columbus, Memphis, then the collection's search order)."""
    # the hand-verified SITES table (slug rule, P625 points, aerial ground) - grows one entry per
    # city landing (five at close)
    assert {qid: s["id"] for qid, s in src_us_birdseye_batch5.SITES.items()} == {}
    for s in src_us_birdseye_batch5.SITES.values():
        assert s["region"] == "United States" and s["kind"] == "town" and s["named"]
        assert s["note"]  # the staged view's apparent angle, for 236c/the matcher's fit order
    extras = src_us_birdseye_batch5._load(src_us_birdseye_batch5.EXTRAS_BIRDS)
    assert {s["id"]: s["qid"] for s in extras} == {
        s["id"]: qid for qid, s in src_us_birdseye_batch5.SITES.items()}
    assert all(s["region"] == "United States" and s["kind"] == "town" and s["aerial_ok"] is True
               for s in extras)

    files = src_us_birdseye_batch5._load(src_us_birdseye_batch5.FILES_BIRDS)
    want = {(r[0], r[1]) for src in src_us_birdseye_batch5.SOURCES.values() for r in src["rows"]}
    assert {(r["title"], r["qid"]) for r in files} == want
    assert len(files) == len(src_us_birdseye_batch5.SITES)  # one view per city
    years = {}
    points = {}
    named_by_qid = {}
    for r in files:
        assert r["year"] == years[r["title"]]
        assert r["site"] in points and r["qid"] in named_by_qid
        assert r.get("evidence") and r["evidence"]["kind"] == "caption_coords"
        assert r["evidence"]["named_place"] == named_by_qid[r["qid"]]
        assert (r["evidence"]["site_lon"], r["evidence"]["site_lat"]) == points[r["site"]]
        assert (r["evidence"]["place_lon"], r["evidence"]["place_lat"]) == points[r["site"]]
        assert r["evidence"]["dist_m"] == 0.0
        assert r["license"] == "Public domain"  # the collection is public domain, per-file verified


def test_evidence_offline_and_negative_control(tmp_path):
    """fit/evidence.py's check over the staged rows, offline: exit 0, zero FAIL, every row PASS
    caption_coords. The negative control (never written into the staged files) is reported FAIL:
    a row whose stored place point is a FOREIGN point (Venice) instead of the site's own point -
    ~5615 km away, a name-search-style resolution a live record could store - fails the stored-
    distance reproduction (200's fails-closed box). Synthetic at module creation (no staged row to
    copy yet); the first city landing rebinds the control to the real first staged row (the
    236b/240 pattern, the Denver row with the Venice point)."""
    code, text = evidence.check(src_us_birdseye_batch5.FILES_BIRDS, src_us_birdseye_batch5.NO_BOOKS,
                                catalog=src_us_birdseye_batch5.EXTRAS_BIRDS)
    assert code == 0, text
    n = len(src_us_birdseye_batch5._load(src_us_birdseye_batch5.FILES_BIRDS))
    assert f"evidence: {n} rows, {n} pass, 0 fail, 0 no-tie" in text, text

    site_lon, site_lat = -95.933889, 41.256944  # a midwest US point (the synthetic site's own point)
    place_lon, place_lat = 12.33, 45.44  # Venice: the foreign point a name search could store
    bad = {"site": "batch5-skeleton", "qid": "Q0",
           "title": "File:Bird's eye view of Batchville, 1900. LOC 00000000.jpg",
           "desc": "", "year": 1900, "wd_plan": False, "cat": None, "license": "Public domain",
           "evidence": {"rec": "evidence/1", "kind": "caption_coords", "checked": "0000-00-00",
                        "named_place": "Batchville", "place_qid": "Q0", "place_label": "Batchville",
                        "place_lon": place_lon, "place_lat": place_lat,
                        "site_lon": site_lon, "site_lat": site_lat, "dist_m": 0.0}}
    f = tmp_path / "bad_skeleton.jsonl"
    f.write_text(json.dumps(bad, ensure_ascii=False) + "\n", encoding="utf-8")
    code, text = evidence.check(str(f), src_us_birdseye_batch5.NO_BOOKS,
                                catalog=src_us_birdseye_batch5.EXTRAS_BIRDS)
    assert code == 1, text
    d = evidence.hav_m(site_lon, site_lat, place_lon, place_lat)
    line = next(l for l in text.splitlines() if l.startswith("FAIL"))
    assert "batch5-skeleton" in line and f"does not reproduce ({d:.0f} m)" in line, line
    assert "evidence: 1 rows, 0 pass, 1 fail, 0 no-tie" in text, text


def test_golden_sample_matches_staged_rows():
    """tests/golden/src_us_birdseye_batch5_sample.json (written by the module's --golden, keys
    sorted, checked/date_commons normalized) is the staged rows exactly - the pin the staging
    files are final against (empty at module creation; --golden only for an intended change)."""
    golden = json.load(open(os.path.join(ROOT, "tests", "golden", "src_us_birdseye_batch5_sample.json"),
                            encoding="utf-8"))
    want = {"extras": src_us_birdseye_batch5._norm(src_us_birdseye_batch5._load(src_us_birdseye_batch5.EXTRAS_BIRDS)),
            "files": src_us_birdseye_batch5._norm(src_us_birdseye_batch5._load(src_us_birdseye_batch5.FILES_BIRDS)),
            "classified": src_us_birdseye_batch5._norm(
                src_us_birdseye_batch5._load(src_us_birdseye_batch5.CLASSIFIED_BIRDS))}
    assert golden == want, "the staged rows differ from the golden sample - an intended change needs --golden"
