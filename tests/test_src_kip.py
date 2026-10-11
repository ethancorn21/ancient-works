"""The Kip bird's-eye-view inventory (task 205, GOAL.md point 4): fit/src_kip.py holds the 132-file verdict
table for the lead Commons categories (Johannes Kip root + its 5 subcategories; Britannia Illustrata) - the
source of docs/lead_kip.md §1 and §3 - and stages the large scans (long edge >= 1000 px) of UK country
houses and their formal gardens into this task's own staging files (11 new `garden` sites, 12 picture rows
with the evidence kind caption_coords, hand classified p_birdseye 1.0); 211 consolidates and builds. The
tests are offline: a socket-blocking fixture makes any network attempt fail loud, so the evidence check runs
from the stored fields only (200's fail-closed box). They pin the inventory's own rules (the 1000 px
threshold, the verdict tally, the six hand-tied titles that must never be re-staged), the SITES table against
the staged extras rows, the lead-doc mirror (§2's verified-site tables, §3 row for row, §1 headline
numbers), the offline --check (join + the evidence pass on every staged row), the age recorded on every
staged row (the date overrides, the AIC title-year row, the two raw QS-suffixed dates), the negative control
(the Hutton Hall trap: the row with the Derbyshire Q5951058 point, 116 km away, must be reported FAIL,
never kept; it is written to a tmp file only) and the golden sample (regenerated only via --golden, for an
intended change)."""
import json
import os
import socket
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for d in (os.path.join(ROOT, "fit"), os.path.join(ROOT, "pipeline")):
    if d not in sys.path:
        sys.path.insert(0, d)
import evidence  # noqa: E402  fit/evidence.py (the offline check over the staged rows)
import sources  # noqa: E402  pipeline/sources.py (the KIP table the six hand-tied titles must equal)
import src_kip  # noqa: E402  fit/src_kip.py, the module under test

LEAD = os.path.join(ROOT, "docs", "lead_kip.md")
FILES = os.path.join(ROOT, "data", "commons", "files.jsonl")
GOLDEN = os.path.join(ROOT, "tests", "golden", "src_kip_sample.json")
TALLIES = {  # the §3 tally, in the document's order
    "staged": 12, "hand-tied": 6, "drop: review-queue": 4, "drop: duplicate impression": 11,
    "drop: not a house": 18, "drop: church": 7, "drop: foreign": 19, "drop: city prospect": 11,
    "drop: photo": 8, "drop: too small": 36,
}


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """The inventory work is offline by contract; make any network attempt in this module's tests fail loud."""
    def boom(*args, **kwargs):
        raise AssertionError(f"network access attempted: {args} {kwargs}")
    monkeypatch.setattr(socket, "socket", boom)
    monkeypatch.setattr(socket, "create_connection", boom)
    monkeypatch.setattr(socket, "getaddrinfo", boom)


def _bare(t):
    assert t.startswith("File:")
    return t[5:]


def test_inventory_thresholds_and_tally():
    """The 132-row verdict table is complete and consistent with the 1000 px threshold rule (the §1 claim):
    every staged view is fit-sized, every 'too small' drop is not, nothing 'too small' falls in the
    900-1000 band, and the tally per verdict group is the §3 one (so box 1 is machine-checkable)."""
    rows = src_kip.INVENTORY
    assert len(rows) == 132 and len({r[0] for r in rows}) == 132
    assert all(len(r) == 5 and isinstance(r[1], int) and isinstance(r[2], int) and r[1] > 0 and r[2] > 0
               and r[4].strip() for r in rows)
    assert all(r[3] in TALLIES for r in rows)
    tally = {}
    for r in rows:
        tally[r[3]] = tally.get(r[3], 0) + 1
    assert tally == TALLIES
    staged = [r for r in rows if r[3] == "staged"]
    too_small = [r for r in rows if r[3] == "drop: too small"]
    assert all(max(r[1], r[2]) >= src_kip.MIN_EDGE for r in staged)
    assert all(max(r[1], r[2]) < src_kip.MIN_EDGE for r in too_small)
    assert min(max(r[1], r[2]) for r in staged) == 1375  # Kingsweston, the smallest staged view
    assert max(max(r[1], r[2]) for r in too_small) == 822  # Siston Court, the largest drop
    band = [r for r in rows if 900 <= max(r[1], r[2]) < 1000]
    # the threshold needs no exception list: the three files in the band drop for their own reasons
    assert {r[3] for r in band} == {"drop: foreign", "drop: duplicate impression", "drop: church"}
    assert len([r for r in rows if max(r[1], r[2]) >= 1000]) == 92


def test_hand_tied_is_the_sources_kip_table_and_never_re_staged():
    """The six 'hand-tied' verdicts are exactly pipeline/sources.py's KIP table, and exactly the six
    canonical files.jsonl rows it produced (kind hand_tied) - they are the views that must never be
    re-staged (their evidence kind stays 'hand-tied QID')."""
    kip = sources.SOURCES["kip"]["rows"]
    assert len(kip) == 6
    hand_tied = {r[0] for r in src_kip.INVENTORY if r[3] == "hand-tied"}
    assert hand_tied == {r[0] for r in kip}
    assert {r[1] for r in kip} == {"Q1443802", "Q1070927", "Q5049456", "Q1074877", "Q17530246", "Q225471"}
    canonical = [json.loads(l) for l in open(FILES, encoding="utf-8") if l.strip()]
    rows = [r for r in canonical if r.get("by") == "pipeline/sources.py kip"]
    assert {r["title"] for r in rows} == hand_tied
    assert all(r["evidence"]["kind"] == "hand_tied" for r in rows)
    for p in (src_kip.FILES_KIP, src_kip.CLASSIFIED_KIP):  # the six never land in the staging files
        for r in src_kip._load(p):
            assert r["title"] not in hand_tied, f"{p}: {r['title']} re-stages a hand-tied view"


def test_sites_table_and_staged_site_rows():
    """SITES is complete and the staged extras rows are exactly it: eleven `garden` sites (eight QID-bearing,
    all distinct; three without any Wikidata item - qid None, which the model handles) and every row
    complete (lon/lat on the landmark that carries the fit, region, kind, aerial_ok, place, wikipedia,
    note); every STAGED view names a SITES site."""
    sites = src_kip.SITES
    assert len(sites) == 11
    assert {sid for sid, s in sites.items() if s["qid"] is None} == \
        {"kings-weston-house", "stoke-house", "burford-house-windsor"}
    qids = [s["qid"] for s in sites.values() if s["qid"]]
    assert len(qids) == 8 and len(set(qids)) == 8
    for sid, s in sites.items():
        for k in ("qid", "name", "lon", "lat", "place", "region", "kind", "wikipedia", "note"):
            assert k in s, f"{sid} missing {k}"
        assert s["kind"] == "garden" and s["region"] == "england"
    extras = src_kip._load(src_kip.EXTRAS_KIP)
    assert {s["id"] for s in extras} == set(sites)
    for s in extras:
        t = sites[s["id"]]
        for k in ("qid", "name", "lon", "lat", "region", "kind", "place", "wikipedia", "note"):
            assert s[k] == t[k], f"{s['id']}: field {k} differs from the SITES table"
        assert s["aerial_ok"] is True and s["source"] == "fit/src_kip.py"
    assert {sid for _, sid, _, _ in src_kip.STAGED} <= set(sites)


def test_lead_doc_section2_mirrors_sites():
    """docs/lead_kip.md §2's verified-site tables mirror SITES (offline, from the document and the table):
    the eight QID-bearing rows (id, QID, the landmark point, P625 Δ 0.00 km for every one, the enwiki title,
    the Hutton Hall name-search trap named in words) and the three no-QID rows (id, landmark point) - a doc
    edit that drifts from the table fails loud."""
    text = open(LEAD, encoding="utf-8").read()
    sec2 = text.split("## 2.", 1)[1].split("## 3.", 1)[0]
    t1 = [[c.strip() for c in line.split("|")[1:-1]] for line in sec2.splitlines()
          if line.startswith("|") and line.count("|") == 10]
    data = [r for r in t1 if r[0] != "id" and not set(r[0]) <= {"-"}]
    assert len(data) == 8
    for id_, qid, _label, landmark, delta, _p373, _p131, enwiki, hit in data:
        s = src_kip.SITES[id_]
        assert qid == s["qid"], id_
        lon, lat = (float(x) for x in landmark.split(","))
        assert (lon, lat) == (s["lon"], s["lat"]), id_
        assert delta == "0.00 km", id_
        slug = s["wikipedia"].rsplit("/", 1)[1].replace("%27", "'").replace("_", " ")
        assert enwiki == slug, f"{id_}: enwiki {enwiki!r} != the title of {s['wikipedia']}"
        if id_ == "hutton-hall-q5951100":  # the one live name-search trap
            assert "Q5951058" in hit and "116 km" in hit, hit
    assert {r[0] for r in data} == {sid for sid, s in src_kip.SITES.items() if s["qid"]}
    t2 = [[c.strip() for c in line.split("|")[1:-1]] for line in sec2.splitlines()
          if line.startswith("|") and line.count("|") == 4]
    data2 = [r for r in t2 if r[0] != "id" and not set(r[0]) <= {"-"}]
    assert [r[0] for r in data2] == ["kings-weston-house", "stoke-house", "burford-house-windsor"]
    for id_, landmark, _src in data2:
        s = src_kip.SITES[id_]
        lon, lat = (float(x) for x in landmark.split(","))
        assert (lon, lat) == (s["lon"], s["lat"]), id_


def test_check_staged_offline(capsys):
    """src_kip --check, offline: the staged files join (every file row names a staged or existing site, no
    staged id or QID pre-exists, every staged site has a picture, (site, title) unique, none of the six
    hand-tied titles re-staged, no title clash with the canonical files.jsonl, classified rows 1:1) and every
    staged row PASSes the evidence check from stored fields alone."""
    code = src_kip.check_staged()
    out = capsys.readouterr().out
    assert code == 0, out
    assert "join:" not in out, f"join problems:\n{out}"
    assert "evidence: 12 rows, 12 pass, 0 fail, 0 no-tie" in out, out
    rows = src_kip._load(src_kip.FILES_KIP)
    assert len(rows) == 12
    for r in rows:
        assert f"PASS caption_coords  {r['site']}|{r['title']}" in out, \
            f"missing PASS line for {r['site']}|{r['title']}:\n{out}"


def test_staged_rows_record_the_plate_dates():
    """The age of every staged view is recorded on the row (views are exempt from the 150-year rule,
    recorded anyway): the dump's date where it is already the plate's date, the known plate date (the Yale
    records, Britannia Illustrata, the Atkyns edition) where the dump has only a life-dates boilerplate or
    no date - the raw dump value kept in date_commons whenever the override changes it, and no date_commons
    on the raw rows. Pinned row for row so a re-stage cannot silently change them."""
    want = {
        "File:Landgoed Badminton, RP-P-1949-371.jpg": ("1709", None, 1709),
        "File:Gott Collection at Hepworth Gallery (112a).JPG":
            ("between 1707 and 1709",
             "between 1680 and 1722 date QS:P,+1500-00-00T00:00:00Z/6,P1319,+1680-00-00T00:00:00Z/9,"
             "P1326,+1722-00-00T00:00:00Z/9",
             1707),  # override: the dump date is Kip's life dates, boilerplate
        "File:Hutton Hall Kip.jpg":
            ("by 1709 date QS:P,+1709-00-00T00:00:00Z/7,P1326,+1709-00-00T00:00:00Z/9", None, 1709),  # raw, with its QS suffix
        "File:Gezicht op Stanway, RP-P-1949-369.jpg": ("1709", None, 1709),
        "File:Gezicht op Stoke Bishop, RP-P-1949-367.jpg": ("1709", None, 1709),
        "File:Jan Kip - A Prospect of the House at Windsor, Belonging to his Grace Charles Beauclerck"
        " - B2017.35.1 - Yale Center for British Art.jpg": ("1707", None, 1707),
        "File:Jan Kip - St James^s House, Le Palais Royal de St James - B2017.35.3"
        " - Yale Center for British Art.jpg": ("1707", None, 1707),
        "File:Jan Kip - The Palace and Park of St James's - B1977.14.18146 - Yale Center for British Art.jpg":
            ("1707", "", 1707),  # override: the dump date was empty
        "File:Jan Kip - Lambeth, His Grace the Lord Archbishop of Canterbury Palace - B1977.14.17372"
        " - Yale Center for British Art.jpg": ("1711-12", "", 1711),  # override: the dump date was empty
        "File:Jan Kip - Somerset House - B1977.14.18272 - Yale Center for British Art.jpg":
            ("1707", "", 1707),  # override: the dump date was empty
        "File:Jan kip per david mortier, hampton court (da leonard mortier), dalla britannia illustrata,"
        " 1707.jpg": ("2016-10-26 20:13:11", None, 1707),
        # the AIC impression: the dump's 2016 photo date kept raw, no override - year_of's title-year
        # idiom (an upload timestamp with a <=1925 year in the title) already returns 1707
        "File:Kingsweston Kip.jpg": ("1710", None, 1710),
    }
    files = src_kip._load(src_kip.FILES_KIP)
    assert {r["title"] for r in files} == set(want)
    for r in files:
        date, dc, year = want[r["title"]]
        assert r["date"] == date, r["title"]
        assert r.get("date_commons") == dc, r["title"]  # absent key == None, an empty string stays ""
        assert r["year"] == year, r["title"]


def test_evidence_negative_control(tmp_path):
    """The name-search trap, never written into the staged files: the Hutton Hall row with the Derbyshire
    'Hutton Hall' point (Q5951058, -1.0757, 54.5222 - the first live name-search hit, 116 km from the
    Cumbrian Fletcher seat) instead of its own verified landmark must be reported FAIL by the evidence
    check (the stored distance does not reproduce and the place is beyond the 50 km tolerance - 200's
    fails-closed box); the staged file stays untouched."""
    hutton = next(r for r in src_kip._load(src_kip.FILES_KIP) if r["site"] == "hutton-hall-q5951100")
    bad = dict(hutton)
    bad["evidence"] = dict(hutton["evidence"], place_lon=-1.0757, place_lat=54.5222, dist_m=0.0)
    f = tmp_path / "bad_hutton.jsonl"
    f.write_text(json.dumps(bad, ensure_ascii=False) + "\n", encoding="utf-8")
    code, text = evidence.check(str(f), src_kip.NO_BOOKS, catalog=src_kip.EXTRAS_KIP)
    assert code == 1, text
    line = next(l for l in text.splitlines() if l.startswith("FAIL"))
    assert "hutton-hall-q5951100" in line and "does not reproduce (115512 m)" in line, line
    assert "evidence: 1 rows, 0 pass, 1 fail, 0 no-tie" in text, text
    assert hutton["evidence"]["place_lon"] == -2.839  # the staged row is untouched by the control


def test_golden_sample_matches_staged_rows():
    """tests/golden/src_kip_sample.json (written by the module's --golden: the three GOLDEN_TITLES file
    rows - one per evidence flavour, a QID row, a qid=None row, the desc-carries-the-caption row - with
    their extras and classified rows, keys sorted, checked/date_commons normalized) is the staged rows
    exactly - the pin the staging files are final against; regenerate only via --golden for an intended
    change."""
    golden = json.load(open(GOLDEN, encoding="utf-8"))
    files = [r for r in src_kip._load(src_kip.FILES_KIP) if r.get("title") in src_kip.GOLDEN_TITLES]
    assert len(files) == 3
    sids = {r["site"] for r in files}
    keyed = {(r["site"], r["title"]) for r in files}
    sites = [s for s in src_kip._load(src_kip.EXTRAS_KIP) if s["id"] in sids]
    cls = [r for r in src_kip._load(src_kip.CLASSIFIED_KIP) if (r.get("site"), r.get("title")) in keyed]
    want = {"extras": src_kip._norm(sites), "files": src_kip._norm(files), "classified": src_kip._norm(cls)}
    assert golden == want, "the staged rows differ from the golden sample - an intended change needs --golden"


def test_lead_doc_mirrors_the_inventory():
    """docs/lead_kip.md §3 is the INVENTORY table row for row (size, verdict, reason; the date column is
    dump-derived and not pinned here), and §1's headline numbers (category counts, the 1000 px threshold,
    the 92/40 split, the 822/1375 extremes, the out-of-scope siblings, the six hand-tied with their QIDs)
    match the module - a doc edit that drifts from the inventory fails loud."""
    text = open(LEAD, encoding="utf-8").read()
    sec3 = text.split("## 3. ", 1)[1].split("\n## 4.", 1)[0]
    rows = [[c.strip() for c in line.split("|")[1:-1]] for line in sec3.splitlines()
            if line.startswith("|") and line.count("|") == 6]
    data = [r for r in rows if r[0].strip() != "File" and not set(r[0].strip()) <= {"-"}]
    assert len(data) == 132  # the 132 inventory rows (header and --- separator skipped by name, not index)
    inv = {}
    for t, w, h, v, reason in src_kip.INVENTORY:
        assert _bare(t) not in inv
        inv[_bare(t)] = (f"{w} × {h}", v, reason)
    for bare, size, _date, verdict, reason in data:
        assert bare in inv, f"doc row not in the inventory: {bare[:60]}"
        assert (size, verdict, reason) == inv[bare], f"doc drift for {bare[:60]}"
    assert {d[0] for d in data} == set(inv)
    tally_line = next(l for l in sec3.splitlines() if l.startswith("Tally:"))
    for v, n in TALLIES.items():
        assert f"{v} {n}" in tally_line, tally_line
    # §1 headline numbers
    sec1 = text.split("## 1.", 1)[1].split("## 2.", 1)[0]
    for needle in (
        "| `Johannes Kip` (root) | 65 |",
        "| **distinct** | **132** | **92** |",
        "long edge ≥ 1000 px",
        "92 of the 132 files are fit-sized, 40 are under 1000 px",
        'largest file dropped as "too small" is 822 px',
        "smallest staged view is 1375 px",
        "`Category:Jan Kip` = 5 files",
        "`Category:History of Kent` = 29 files",
    ):
        assert needle in sec1, f"missing in §1: {needle}"
    for t, qid, *_ in sources.SOURCES["kip"]["rows"]:
        assert f"{_bare(t)} | " in sec1 and qid in sec1, f"hand-tied {t[:40]} missing from §1"
