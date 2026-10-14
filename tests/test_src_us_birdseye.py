"""The US bird's-eye-view staging (task 236b, GOAL.md point 5: artists' aerial and bird's-eye views
count as much as surveys): the eleven views of the four owner-named cities from the LOC "Panoramic
Maps" collection, staged by fit/src_us_birdseye.py onto 236a's shared site ids (never a second site
for a QID) - New York: the 1874 Bachmann, the 1879 Will L. Taylor and the 1907 Ohman metro-wide view;
Washington DC: the 1883 Sachse, the 1886 B.H. Warner & Co. and the 1921 Olsen views; San Francisco:
the 1854 Henry Bill (the oldest staged view of the city), the 1868 Goddard, the 1878 Parsons/
Currier & Ives and the 1914 C. Merriman Peter views; Nashville: the 1897 Tennessee Centennial
Exposition view - plus batches 1, 2 and 3 of the new cities, each a NEW site in this task's own
extras file (one steepest view per city): batch 1: Boston the 1902 Walker, Philadelphia the 1872
Davis/Harper's Weekly, Baltimore the 1880 Parsons, Pittsburgh the 1902 Fowler and Cincinnati the 1900
Trout views; batch 2: Louisville the 1883 Clarke/Levyau sheet (the International Exposition two-panel
composite), St. Louis the 1858 Palmatary (the steepest and oldest view staged for the city), Chicago
the 1892 Peter Roy, Detroit the 1889 Calvert and Milwaukee the 1872 Bailey views; batch 3: Kansas
City the 1869 Ruger view (the only whole-city view of the city through the gate) - into this task's
own files (files/classified _us_birdseye.jsonl; extras _us_birdseye.jsonl holds the eleven new-cities
site rows). The tests are offline: a socket-blocking fixture makes any network fetch fail loud, so
the evidence check runs from the stored fields only (200's fail-closed box). The negative control
pins the trap the hand record exists for: a staged row with a foreign place point (Venice) instead
of the site's own point - ~6681 km away, a name-search-style resolution that record --live could
store - must be reported FAIL, never kept. The golden file
(tests/golden/src_us_birdseye_sample.json) pins the staged rows as a whole; it is regenerated only
via the module's --golden flag for an intended change. The check-staged test covers the merge states
of the --check guards hermetically - pre-merge; the 236c first-row-wins merge already run (an
already-merged row is a no-op); and a same-key different row still failing loud - with the batch-1
new sites held by the site-level guards (a staged id/QID held by a different site fails).
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
import src_us_birdseye  # noqa: E402  fit/src_us_birdseye.py, the module under test


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """The check is offline by contract; make any network attempt in this module's tests fail loud."""
    def boom(*args, **kwargs):
        raise AssertionError(f"network access attempted: {args} {kwargs}")
    monkeypatch.setattr(socket, "socket", boom)
    monkeypatch.setattr(socket, "create_connection", boom)
    monkeypatch.setattr(socket, "getaddrinfo", boom)


def test_check_staged_files_join_and_pass(capsys):
    """src_us_birdseye --check, offline: the staged files join (every file row names an existing site
    - the four shared ids via 236a's read-only extras file, the new-cities ids (batches 1-3) via
    this task's own extras file - no site re-used under two ids, (site, title) unique, no clash with the
    canonical files.jsonl, classified rows 1:1, every new-cities site has a picture) and every staged
    row PASSes the evidence
    check."""
    code = src_us_birdseye.check_staged()
    out = capsys.readouterr().out
    assert code == 0, out
    assert "join:" not in out, f"join problems:\n{out}"
    n = len(src_us_birdseye._load(src_us_birdseye.FILES_BIRDS))
    assert f"evidence: {n} rows, {n} pass, 0 fail, 0 no-tie" in out, out
    for key in ("new-york-q60|File:New York - drawn by J. Bachmann ; print by G. Schlegel, 97 William St. N.Y. LCCN98508526.jpg",
                "new-york-q60|File:The city of New York. LOC 75694818.jpg",
                "new-york-q60|File:View of the city of New York and vicinity LOC 78692903.jpg",
                "washington-q61|File:The national capital, Washington City, D.C. LOC 75694904.jpg",
                "washington-q61|File:B.H. Warner & Co.'s Map showing a bird's-eye view of the city of Washington and suburbs - locating the public buildings and places of interest LOC 87693417.jpg",
                "washington-q61|File:Washington, the beautiful capital of the nation LOC 78695113.jpg",
                "san-francisco-q62|File:San Francisco. 1854 (published for the History of the world) - DPLA - Original.jpg",
                "san-francisco-q62|File:(Bird's eye view of San Francisco) LOC 75693101.jpg",
                "san-francisco-q62|File:The city of San Francisco. Birds eye view from the bay looking south-west. LOC 75693104.jpg",
                "san-francisco-q62|File:1914 San Francisco Birds Eye Map by Peter.jpg",
                "nashville-q23197|File:Tennessee Centennial Exposition, Nashville, Tennessee, 1897. LOC 77696328.jpg",
                "boston-q100|File:Bird's eye view of Boston. LOC 75694559.jpg",
                "philadelphia-q1345|File:Bird's eye view of Philadelphia. LOC 75694509.jpg",
                "baltimore-q5092|File:The City of Baltimore - sketched and drawn by C.R. Parsons. LCCN90715972.jpg",
                "pittsburgh-q1342|File:Pittsburgh, Pennsylvania 1902. LOC 75696521.jpg",
                "cincinnati-q43196|File:Panoramic view, city of Cincinnati, U.S.A. 1900. LOC 75694914.jpg",
                "kansas-city-q41819|File:Bird's eye view of Kansas City, Missouri. Jan'y. 1869. LOC 73693480.jpg"):
        assert f"PASS caption_coords  {key}" in out, f"missing PASS line for {key}:\n{out}"


def test_check_staged_three_states(tmp_path, monkeypatch, capsys):
    """The 236c merge states of the --check guards, hermetically (temp copies of the canonical files,
    so the test holds whether or not 236c's live merge has run on this checkout): (a) staged rows
    ABSENT from the canonical files (the pre-merge state) - check 0, no join problems, evidence all
    PASS; (b) staged rows present with IDENTICAL content (the 236c first-row-wins merge has run) -
    check 0, no join problems: an already-merged row is a no-op; (c) the same (site, title) key held
    by a DIFFERENT row - still fails loud, naming exactly that problem and no other. The four shared
    city ids stay known in every state via 236a's read-only extras file (the monkeypatched canonical
    files never held them; 236c's real merge adds them there too, which the guard treats as a no-op
    self reference, as in 236a's test). The new-cities' sites (batches 1-3) sit in this task's own
    extras file: the site-level guards (a staged id/QID held by a different site) apply to them, as in
    236a's test."""
    staged_files = src_us_birdseye._load(src_us_birdseye.FILES_BIRDS)
    staged_sites = src_us_birdseye._load(src_us_birdseye.EXTRAS_BIRDS)
    skeys = {(r.get("site"), r.get("title")) for r in staged_files}
    sids = {s["id"] for s in staged_sites}

    def write(name, text):
        p = tmp_path / name
        p.write_text(text, encoding="utf-8")
        return str(p)

    # the canonical files with this module's staged rows removed: the pre-merge state of ITS keys/sites
    # on any checkout (the other sources' merged rows are untouched, the guards do not care about them)
    files_pre = [json.dumps(r, ensure_ascii=False) for r in src_us_birdseye._load(src_us_birdseye.FILES_CANONICAL)
                 if (r.get("site"), r.get("title")) not in skeys]
    extras_pre = [json.dumps(r, ensure_ascii=False) for r in src_us_birdseye._load(src_us_birdseye.EXTRAS)
                  if r.get("id") not in sids]
    web = json.load(open(src_us_birdseye.WEB_SITES, encoding="utf-8"))
    monkeypatch.setattr(src_us_birdseye, "WEB_SITES",
                        write("sites.json", json.dumps(dict(web, sites=[s for s in web["sites"]
                                                               if s.get("id") not in sids]),
                                                       ensure_ascii=False)))
    sites = tmp_path / "sites.jsonl"
    sites.write_text(open(src_us_birdseye.SITES_JSONL, encoding="utf-8").read(), encoding="utf-8")
    monkeypatch.setattr(src_us_birdseye, "SITES_JSONL", str(sites))

    def point(files_rows, extras_rows):
        monkeypatch.setattr(src_us_birdseye, "FILES_CANONICAL",
                            write("files.jsonl", "\n".join(files_rows) + "\n"))
        monkeypatch.setattr(src_us_birdseye, "EXTRAS", write("extras.jsonl", "\n".join(extras_rows) + "\n"))

    staged_file_lines = [json.dumps(r, ensure_ascii=False) for r in staged_files]
    staged_site_lines = [json.dumps(s, ensure_ascii=False) for s in staged_sites]
    evidence_line = f"evidence: {len(staged_files)} rows, {len(staged_files)} pass, 0 fail, 0 no-tie"

    # (a) pre-merge: the staged rows are not in the canonical files yet
    point(files_pre, extras_pre)
    code = src_us_birdseye.check_staged()
    out = capsys.readouterr().out
    assert code == 0, out
    assert "join:" not in out, out
    assert evidence_line in out, out

    # (b) the 236c merge ran: every staged row is in the canonical files with identical content
    point(files_pre + staged_file_lines, extras_pre + staged_site_lines)
    code = src_us_birdseye.check_staged()
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
    code = src_us_birdseye.check_staged()
    out = capsys.readouterr().out
    assert code == 1, out
    join = [l for l in out.splitlines() if l.startswith("join:")]
    assert join == [f"join: staged title already in the canonical files.jsonl: {k}"], join
    assert evidence_line in out, out


def test_shared_table_and_staged_rows():
    """The hand-checked tables and the staged rows are exactly them: the four owner cities use
    236a's site ids (new-york-q60, washington-q61, san-francisco-q62, nashville-q23197) - never a
    second site for a QID - and _shared_site resolves each against 236a's read-only staged file
    (a drift fails loud, offline); batches 1-3 of the new cities each stage one NEW site
    (boston-q100, philadelphia-q1345, baltimore-q5092, pittsburgh-q1342, cincinnati-q43196,
    louisville-q43668, st-louis-q38022, chicago-q1297, detroit-q12439, milwaukee-q37836,
    kansas-city-q41819 - region "United States", kind "town", aerial_ok true) and one steepest view
    each; the staged file rows are
    exactly the module's source rows: the known drawing/publication dates are on the rows where the
    file page lost them or printed the copyright year (the 1897 Centennial view: page 1896 kept as
    date_commons; the 1854 Bill view: the page is undated, the year from the title), and every row's
    evidence point is the site's own point (236a's verified values for the shared cities, the city's
    P625 for the new-cities ones) with the short caption name."""
    assert src_us_birdseye.SHARED_SITES == {
        "Q60": ("new-york-q60", "New York"),
        "Q61": ("washington-q61", "Washington"),
        "Q62": ("san-francisco-q62", "San Francisco"),
        "Q23197": ("nashville-q23197", "Nashville"),
    }
    # batches 1 and 2 of the new cities: the hand-verified SITES table (slug rule, P625 points, aerial
    # ground)
    assert {qid: s["id"] for qid, s in src_us_birdseye.SITES.items()} == {
        "Q100": "boston-q100", "Q1345": "philadelphia-q1345", "Q5092": "baltimore-q5092",
        "Q1342": "pittsburgh-q1342", "Q43196": "cincinnati-q43196",
        "Q43668": "louisville-q43668", "Q38022": "st-louis-q38022", "Q1297": "chicago-q1297",
        "Q12439": "detroit-q12439", "Q37836": "milwaukee-q37836", "Q41819": "kansas-city-q41819"}
    for s in src_us_birdseye.SITES.values():
        assert s["region"] == "United States" and s["kind"] == "town" and s["named"]
        assert s["note"]  # the staged view's apparent angle, for 236c/the matcher's fit order
    # _shared_site cross-checks 236a's staged file (read-only) and fails loud on drift:
    for qid, (sid, named) in src_us_birdseye.SHARED_SITES.items():
        s = src_us_birdseye._shared_site(qid)
        assert s["id"] == sid and s["named"] == named and s["qid"] == qid
        assert s.get("name") and s.get("place") and s.get("wikipedia")
        assert isinstance(s["lon"], float) and isinstance(s["lat"], float)

    extras = src_us_birdseye._load(src_us_birdseye.EXTRAS_BIRDS)
    assert {s["id"]: s["qid"] for s in extras} == {
        "boston-q100": "Q100", "philadelphia-q1345": "Q1345", "baltimore-q5092": "Q5092",
        "pittsburgh-q1342": "Q1342", "cincinnati-q43196": "Q43196",
        "louisville-q43668": "Q43668", "st-louis-q38022": "Q38022", "chicago-q1297": "Q1297",
        "detroit-q12439": "Q12439", "milwaukee-q37836": "Q37836", "kansas-city-q41819": "Q41819"}  # the four owner cities' sites come from 236a's file, not this task's
    assert all(s["region"] == "United States" and s["kind"] == "town" and s["aerial_ok"] is True for s in extras)

    files = src_us_birdseye._load(src_us_birdseye.FILES_BIRDS)
    want = {(r[0], r[1]) for src in src_us_birdseye.SOURCES.values() for r in src["rows"]}
    assert {(r["title"], r["qid"]) for r in files} == want
    assert len(files) == 22
    years = {"File:New York - drawn by J. Bachmann ; print by G. Schlegel, 97 William St. N.Y. "
             "LCCN98508526.jpg": 1874,
             "File:The city of New York. LOC 75694818.jpg": 1879,
             "File:View of the city of New York and vicinity LOC 78692903.jpg": 1907,
             "File:The national capital, Washington City, D.C. LOC 75694904.jpg": 1883,
             "File:B.H. Warner & Co.'s Map showing a bird's-eye view of the city of Washington and "
             "suburbs - locating the public buildings and places of interest LOC 87693417.jpg": 1886,
             "File:Washington, the beautiful capital of the nation LOC 78695113.jpg": 1921,
             "File:San Francisco. 1854 (published for the History of the world) - DPLA - Original.jpg": 1854,
             "File:(Bird's eye view of San Francisco) LOC 75693101.jpg": 1868,
             "File:The city of San Francisco. Birds eye view from the bay looking south-west. "
             "LOC 75693104.jpg": 1878,
             "File:1914 San Francisco Birds Eye Map by Peter.jpg": 1914,
             "File:Tennessee Centennial Exposition, Nashville, Tennessee, 1897. LOC 77696328.jpg": 1897,
             "File:Bird's eye view of Boston. LOC 75694559.jpg": 1902,
             "File:Bird's eye view of Philadelphia. LOC 75694509.jpg": 1872,
             "File:The City of Baltimore - sketched and drawn by C.R. Parsons. LCCN90715972.jpg": 1880,
             "File:Pittsburgh, Pennsylvania 1902. LOC 75696521.jpg": 1902,
             "File:Panoramic view, city of Cincinnati, U.S.A. 1900. LOC 75694914.jpg": 1900,
             "File:Birds-eye view of Louisville from the river front and Southern Exposition, 1883. LOC 75693235.jpg": 1883,
             "File:Bird's-Eye View of St. Louis, MO. (full view).jpg": 1858,
             "File:Bird's eye view of Chicago, 1892. LOC 75693206.jpg": 1892,
             "File:Birds eye view-showing about three miles square-of the central portion of the city of Detroit, Michigan. LOC 76693077.jpg": 1889,
             "File:Milwaukee, Wis. LOC 76693067.jpg": 1872,
             "File:Bird's eye view of Kansas City, Missouri. Jan'y. 1869. LOC 73693480.jpg": 1869}
    # the 236a site points (verified there) and the new-cities' P625s (verified here): the stored
    # evidence point must be the site's own point
    points = {"new-york-q60": (-74.006111, 40.712778), "washington-q61": (-77.036667, 38.895),
              "san-francisco-q62": (-122.40289, 37.79213), "nashville-q23197": (-86.78152, 36.16529),
              "boston-q100": (-71.057778, 42.360278), "philadelphia-q1345": (-75.163611, 39.952778),
              "baltimore-q5092": (-76.615, 39.286389), "pittsburgh-q1342": (-80.0, 40.441667),
              "cincinnati-q43196": (-84.5125, 39.1),
              "louisville-q43668": (-85.751389, 38.256111), "st-louis-q38022": (-90.199444, 38.626389),
              "chicago-q1297": (-87.627778, 41.881944), "detroit-q12439": (-83.0475, 42.331667),
              "milwaukee-q37836": (-87.95, 43.05), "kansas-city-q41819": (-94.583333, 39.05)}
    named_by_qid = {"Q60": "New York", "Q61": "Washington", "Q62": "San Francisco", "Q23197": "Nashville",
                    "Q100": "Boston", "Q1345": "Philadelphia", "Q5092": "Baltimore",
                    "Q1342": "Pittsburgh", "Q43196": "Cincinnati",
                    "Q43668": "Louisville", "Q38022": "St. Louis", "Q1297": "Chicago",
                    "Q12439": "Detroit", "Q37836": "Milwaukee", "Q41819": "Kansas City"}
    for r in files:
        assert r["year"] == years[r["title"]]
        assert r["site"] in points and r["qid"] in named_by_qid
        assert r.get("evidence") and r["evidence"]["kind"] == "caption_coords"
        assert r["evidence"]["named_place"] == named_by_qid[r["qid"]]
        assert (r["evidence"]["site_lon"], r["evidence"]["site_lat"]) == points[r["site"]]
        assert (r["evidence"]["place_lon"], r["evidence"]["place_lat"]) == points[r["site"]]
        assert r["evidence"]["dist_m"] == 0.0
    by_title = {r["title"]: r for r in files}
    # the known-drawing-date swap (the Zwolle precedent): the page value kept as date_commons
    cent = by_title["File:Tennessee Centennial Exposition, Nashville, Tennessee, 1897. LOC 77696328.jpg"]
    assert cent["date"] == "1897" and cent["date_commons"] == "1896"
    # the 1854 Bill sheet: the file page is undated (the drawing's year comes from the title)
    bill = by_title["File:San Francisco. 1854 (published for the History of the world) - DPLA - Original.jpg"]
    assert bill["date"] == "" and bill["year"] == 1854
    for r in files:
        assert r["license"] == "Public domain"  # the collection is public domain, per-file verified


def test_evidence_offline_and_negative_control(tmp_path):
    """fit/evidence.py's check over the staged rows, offline: exit 0, zero FAIL, every row PASS
    caption_coords. The negative control (never written into the staged files) is reported FAIL: the
    Bachmann row with the Venice point instead of the site's own point - ~6681 km away, a
    name-search-style resolution a live record could store - fails both the stored-distance
    reproduction and the 50 km tolerance (200's fails-closed box)."""
    code, text = evidence.check(src_us_birdseye.FILES_BIRDS, src_us_birdseye.NO_BOOKS,
                                catalog=src_us_birdseye.EXTRAS_BIRDS)
    assert code == 0, text
    n = len(src_us_birdseye._load(src_us_birdseye.FILES_BIRDS))
    assert f"evidence: {n} rows, {n} pass, 0 fail, 0 no-tie" in text, text

    bachmann = next(r for r in src_us_birdseye._load(src_us_birdseye.FILES_BIRDS)
                    if r["title"].startswith("File:New York - drawn by J. Bachmann"))
    bad = dict(bachmann)
    bad["evidence"] = dict(bachmann["evidence"], place_lon=12.33, place_lat=45.44, dist_m=0.0)  # Venice
    f = tmp_path / "bad_new_york.jsonl"
    f.write_text(json.dumps(bad, ensure_ascii=False) + "\n", encoding="utf-8")
    code, text = evidence.check(str(f), src_us_birdseye.NO_BOOKS, catalog=src_us_birdseye.EXTRAS_BIRDS)
    assert code == 1, text
    line = next(l for l in text.splitlines() if l.startswith("FAIL"))
    assert "new-york-q60" in line and "does not reproduce (6680986 m)" in line, line
    assert "evidence: 1 rows, 0 pass, 1 fail, 0 no-tie" in text, text
    assert bachmann["evidence"]["place_lon"] == -74.006111  # the staged row is untouched by the control


def test_golden_sample_matches_staged_rows():
    """tests/golden/src_us_birdseye_sample.json (written by the module's --golden, keys sorted,
    checked/date_commons normalized) is the staged rows exactly - the pin the staging files are final
    against."""
    golden = json.load(open(os.path.join(ROOT, "tests", "golden", "src_us_birdseye_sample.json"), encoding="utf-8"))
    want = {"extras": src_us_birdseye._norm(src_us_birdseye._load(src_us_birdseye.EXTRAS_BIRDS)),
            "files": src_us_birdseye._norm(src_us_birdseye._load(src_us_birdseye.FILES_BIRDS)),
            "classified": src_us_birdseye._norm(src_us_birdseye._load(src_us_birdseye.CLASSIFIED_BIRDS))}
    assert golden == want, "the staged rows differ from the golden sample - an intended change needs --golden"
