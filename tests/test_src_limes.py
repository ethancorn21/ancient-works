"""The German Limes staging (task 208, GOAL.md point 4): 56 named fort plans of 43 ORL forts staged by
fit/src_limes.py into this task's own files (extras_limes/files_limes/classified_limes.jsonl) - 45
de.wikipedia plates of the Abt B monographs, 9 disjoint Commons plates, and the two plan plates of the
1895 Internet Archive scan of Band IV Nr. 40 (Osterburken). Every row is hand-recorded caption+coordinates
evidence (the P373 category route is dead for this set; the two item-less forts, 64 Schirenhof and 67 Buch,
stage on name+coordinates per the task Notes) and re-verifies offline from the stored fields only
(200's fail-closed box). The negative control pins the trap the hand record exists for: the Heddesdorf row
re-pointed at a different fort's coordinates must be reported FAIL, never kept. The golden file
(tests/golden/src_limes_sample.json) pins one staged row per source plus their extras and classified rows;
it is regenerated only via the module's --golden flag for an intended change.
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
import src_limes  # noqa: E402  fit/src_limes.py, the module under test

GOLDEN = os.path.join(ROOT, "tests", "golden", "src_limes_sample.json")


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """The check is offline by contract; make any network attempt in this module's tests fail loud."""
    def boom(*args, **kwargs):
        raise AssertionError(f"network access attempted: {args} {kwargs}")
    monkeypatch.setattr(socket, "socket", boom)
    monkeypatch.setattr(socket, "create_connection", boom)
    monkeypatch.setattr(socket, "getaddrinfo", boom)


def test_check_staged_files_join_and_pass(capsys):
    """src_limes --check, offline: the staged files join (every file row names a staged extras row, every
    staged site has a picture, (site, title) unique, no staged id/QID pre-exists in the catalog, no clash
    with the canonical files.jsonl, classified rows 1:1) and every staged row PASSes the evidence check."""
    code = src_limes.check_staged()
    out = capsys.readouterr().out
    assert code == 0, out
    assert "join:" not in out, f"join problems:\n{out}"
    assert "evidence: 56 rows, 56 pass, 0 fail, 0 no-tie" in out, out
    for key in ("osterburken-q1243550|Das Kastell Osterburken, Tafel III - Situationskarte (1895)",
                "heddesdorf-q1735373|File:ORL_01_tab_03_pic_01_Grundriss_Kastellbad.jpg",
                "heddesdorf-q1735373|File:ORL 01 tab 01 pic 01 Lageplan.jpg"):
        assert f"PASS caption_coords  {key}" in out, f"missing PASS line for {key}:\n{out}"


def test_forts_table_and_staged_rows():
    """The hand-checked table is complete (45 staging forts: 42 ORL numbers, 42 and 45 each split into two
    fort items, plus the Anhausen fortlet; 64/67 have no Wikidata item) and the staged rows are exactly it:
    45 complete extras rows matching the table, 56 file rows matching the module's FILES table field for
    field (monograph years 1894-1915, all <= 1925), 56 classified rows 1:1 with p_plan 1.0 by hand."""
    forts = src_limes.FORTS
    assert len(forts) == 45
    assert forts["64"]["qid"] is None and forts["67"]["qid"] is None  # name+coords, recorded as such
    assert "no Wikidata item" in forts["64"]["note"] and "no Wikidata item" in forts["67"]["note"]
    assert {k for k, f in forts.items() if f["qid"] is None} == {"64", "67"}
    years = {k: f["year"] for k, f in forts.items()}
    assert years["01"] == 1903 and years["40"] == 1895 and years["42w"] == years["42o"] == 1897
    assert years["33"] == 1914 and years["67"] == 1896 and years["Anhausen"] == 1915
    assert all(1894 <= y <= 1925 for y in years.values())

    id_to_key = {src_limes.fort_id(k): k for k in forts}
    extras = src_limes._load(src_limes.EXTRAS_LIMES)
    assert len(extras) == 45
    assert {s["id"] for s in extras} == set(id_to_key)
    for s in extras:
        f = forts[id_to_key[s["id"]]]
        for k in ("name", "lon", "lat", "place", "wikipedia"):
            assert s[k] == f[k], f"{s['id']}: field {k} differs from the FORTS table"
        assert s["qid"] == f["qid"]
        assert s["region"] == "germany" and s["kind"] == "roman fort" and s["aerial_ok"] is True
        assert s["source"] == "fit/src_limes.py" and s.get("note")

    files = src_limes._load(src_limes.FILES_LIMES)
    assert len(files) == 56
    table = {e["title"]: e for e in src_limes.FILES}
    assert {r["title"] for r in files} == set(table)
    for r in files:
        want = src_limes.file_row(table[r["title"]])
        for k in ("site", "qid", "title", "year", "wd_plan", "cat", "name", "by", "url", "thumb",
                  "w", "h", "mime", "date", "desc", "artist", "license", "page"):
            assert r.get(k) == want[k], f"{r['title']}: field {k} differs from the FILES table"
        assert r.get("date_commons") == want.get("date_commons")
        assert r["date"] == str(r["year"])
        ev, wev = r["evidence"], want["evidence"]
        for k in ("rec", "kind", "named_place", "place_qid", "place_label", "place_lon",
                  "place_lat", "site_lon", "site_lat", "dist_m"):
            assert ev[k] == wev[k], f"{r['title']}: evidence {k} differs"
        assert ev["kind"] == "caption_coords" and ev["dist_m"] == 0.0  # place point = site point

    cls = src_limes._load(src_limes.CLASSIFIED_LIMES)
    assert {(c["site"], c["title"]) for c in cls} == {(r["site"], r["title"]) for r in files}
    assert all(c["p_plan"] == 1.0 and c["p_birdseye"] == 0.0 and c["p_photo"] == 0.0 and c["by"] == "hand"
               for c in cls)


def test_box3_counts_from_staged_rows():
    """The task's box 3, from the staged rows: at least 10 fort plans from at least 2 sources - here 56
    distinct plans from 3 distinct sources (de.wikipedia, Commons, Internet Archive)."""
    files = src_limes._load(src_limes.FILES_LIMES)
    plans = {(r["site"], r["title"]) for r in files}
    sources = {r["by"].rsplit(" ", 1)[1] for r in files}
    assert len(plans) >= 10 and len(sources) >= 2
    assert len(plans) == 56
    assert sources == {"dewiki-orl", "commons-orl", "ia-1895"}


def test_evidence_offline_and_negative_control(tmp_path):
    """fit/evidence.py's check over a copy of the staged rows, offline: a Heddesdorf row re-pointed at the
    neighbouring fort (wrong fort in the named place, ~15 km off the site) and the same row with its place
    point shifted ~10 km (the name-search trap a live record could store) are both reported FAIL - never
    written into the staged files, which stay untouched."""
    files = src_limes._load(src_limes.FILES_LIMES)
    row = next(r for r in files if r["title"] == "File:ORL_01_tab_03_pic_01_Grundriss_Kastellbad.jpg")
    bad1 = dict(row)
    bad1["evidence"] = dict(row["evidence"], named_place="Niederberg", place_qid="Q1670400",
                            place_label="Niederberg", place_lon=7.62734, place_lat=50.3689, dist_m=0.0)
    bad2 = dict(row)
    bad2["evidence"] = dict(row["evidence"], place_lon=7.57, place_lat=50.40, dist_m=0.0)
    f = tmp_path / "bad_limes.jsonl"
    f.write_text(json.dumps(bad1, ensure_ascii=False) + "\n" + json.dumps(bad2, ensure_ascii=False) + "\n",
                 encoding="utf-8")
    code, text = evidence.check(str(f), src_limes.NO_BOOKS, catalog=src_limes.EXTRAS_LIMES)
    assert code == 1, text
    fail = [l for l in text.splitlines() if l.startswith("FAIL")]
    assert len(fail) == 2, text
    assert "does not name 'Niederberg'" in fail[0], fail[0]
    assert "does not reproduce" in fail[1], fail[1]
    assert "evidence: 2 rows, 0 pass, 2 fail, 0 no-tie" in text, text
    staged = next(r for r in src_limes._load(src_limes.FILES_LIMES) if r["title"] == row["title"])
    assert staged["evidence"]["named_place"] == "Heddesdorf"
    assert staged["evidence"]["place_lon"] == 7.46931


def test_golden_sample_matches_staged_rows():
    """tests/golden/src_limes_sample.json (written by the module's --golden, keys sorted, checked/
    date_commons normalized) is one staged row per source plus their extras and classified rows - the pin
    the staging files are final against."""
    golden = json.load(open(GOLDEN, encoding="utf-8"))
    files = [r for r in src_limes._load(src_limes.FILES_LIMES) if r["title"] in src_limes.GOLDEN_ROWS]
    assert len(files) == len(src_limes.GOLDEN_ROWS)
    sites = {r["site"] for r in files}
    want = {"extras": src_limes._norm([s for s in src_limes._load(src_limes.EXTRAS_LIMES) if s["id"] in sites]),
            "files": src_limes._norm(files),
            "classified": src_limes._norm([c for c in src_limes._load(src_limes.CLASSIFIED_LIMES)
                                           if (c["site"], c["title"]) in {(r["site"], r["title"]) for r in files}])}
    assert golden == want, "the staged rows differ from the golden sample - an intended change needs --golden"
