"""The Van Deventer staging (task 204, GOAL.md point 4): the 56 town plans of c. 1545-1565 staged by
fit/src_van_deventer.py into this task's own files (extras/files/classified _van_deventer.jsonl), from the
hand-checked file -> QID table in the module (every QID verified against its label, its P625 values, its P373
and its enwiki link - a name search alone gives the wrong place). The tests are offline: a socket-blocking
fixture makes any network fetch fail loud, so the evidence check runs from the stored fields only (200's
fail-closed box). The negative controls pin the traps the hand record exists for: a category chain whose last
hop is not the town's P373 category (a hand-typed path the walk never took), and a caption row whose stored
resolution is a ~52 km neighbour (the name-search-style resolution a live record could store) - both must be
reported FAIL, never kept. The golden file (tests/golden/src_van_deventer_sample.json) pins the staged rows
(a sample of the first two towns per evidence kind plus the full counts); it is regenerated only via the
module's --golden flag for an intended change.
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
import src_van_deventer as vd  # noqa: E402  fit/src_van_deventer.py, the module under test

STAGED = 56  # the 56 stageable towns (NL 13 + BE 21 + FR 21 + LU 1) of the 66-town table


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """The check is offline by contract; make any network attempt in this module's tests fail loud."""
    def boom(*args, **kwargs):
        raise AssertionError(f"network access attempted: {args} {kwargs}")
    monkeypatch.setattr(socket, "socket", boom)
    monkeypatch.setattr(socket, "create_connection", boom)
    monkeypatch.setattr(socket, "getaddrinfo", boom)


def test_check_staged_files_join_and_pass(capsys):
    """src_van_deventer --check, offline: the staged files join (every file row names a staged or existing
    site, no staged id/QID pre-exists, the six done towns are not re-staged, every staged site has a picture,
    (site, title) unique, no clash with the canonical files.jsonl, classified rows 1:1) and every staged row
    PASSes the evidence check (54 category chains, 2 caption routes)."""
    code = vd.check_staged()
    out = capsys.readouterr().out
    assert code == 0, out
    assert "join:" not in out, f"join problems:\n{out}"
    assert f"evidence: {STAGED} rows, {STAGED} pass, 0 fail, 0 no-tie" in out, out
    for kind, key in (
            ("category", "aardenburg-q955|File:Aardenburg 1560.jpg"),  # NL, 3-hop chain
            ("category", "mons-q83407|File:Mons (2) - Deventer.jpg"),  # BE, the disambiguated P373 watch item
            ("caption_coords", "brussels-q239|File:Brussels map by Jacob van Deventer, "
                               "Atlas des villes des Pays-Bas, 73 places levées, ca. 1555 (2) 01.png"),
            ("category", "luxembourg-city-q1842|File:Luxemburg 1550 65 v Deventer.jpg")):  # LU, 4-hop chain
        assert f"{'PASS':4s} {kind:15s} {key}" in out, f"missing PASS line for {key}:\n{out}"


def test_table_and_staged_rows():
    """The hand-checked table is complete and the staged files are exactly it: 56 of the 66 towns (the six
    hand-tied in pipeline/sources.py are not re-staged), no staged QID pre-exists in the catalog (no
    duplicate sites), every row carries the full site fields, every year_of lands in the c. 1545-1565 drawing
    window (box 6), and the evidence split is exactly 54 category chains + 2 caption routes (the two capped
    walks)."""
    assert len(vd.TOWNS) == 66
    st = vd.stageable()
    assert len(st) == STAGED
    done = {t for t, d in vd.TOWNS.items() if d.get("done")}
    assert done == {"Gouda", "Zwolle", "Venlo", "Damme", "Binche", "Bergues"}  # the sources.py hand-ties

    known = vd.known_sites()
    extras = vd._load(vd.EXTRAS)
    assert len(extras) == STAGED and len({s["id"] for s in extras}) == STAGED
    assert {s["qid"] for s in extras} == {vd.TOWNS[t]["qid"] for t in st}
    assert not {s["qid"] for s in extras} & set(known)  # no staged QID pre-exists: no duplicate sites
    assert not {s["qid"] for s in extras} & {vd.TOWNS[t]["qid"] for t in done}  # the six done towns absent

    rows_by_id = {s["id"]: s for s in extras}
    town_of_file = {d["file"]: t for t, d in vd.TOWNS.items() if d.get("file")}
    files = vd._load(vd.FILES)
    assert len(files) == STAGED
    assert len({(r["site"], r["title"]) for r in files}) == STAGED  # (site, title) unique
    staged_ids = set(rows_by_id) | set(known.values())
    for r in files:
        tkey = town_of_file[r["title"]]
        t = vd.TOWNS[tkey]
        sid = known.get(t["qid"]) or vd._site_row(tkey, t)["id"]
        assert r["site"] == sid and r["site"] in staged_ids, f"{r['title']}: site {r['site']} not staged/existing"
        assert r["qid"] == t["qid"]
        s = rows_by_id[sid]
        assert s["name"] == tkey, f"{sid}: name {s['name']!r} is not the table key {tkey!r}"
        for k in ("lon", "lat", "region"):
            assert s[k] == t[k], f"{sid}: field {k} differs from the TOWNS table"
        for k in ("place", "wikipedia"):
            assert s.get(k) == t.get(k), f"{sid}: field {k} differs from the TOWNS table"
        assert s["kind"] == "town" and s["aerial_ok"] is True
        assert 1545 <= r["year"] <= 1565, f"{r['title']}: year {r['year']} outside the drawing window"

    kinds = {}
    for r in files:
        kinds[r["evidence"]["kind"]] = kinds.get(r["evidence"]["kind"], 0) + 1
    assert kinds == {"category": 54, "caption_coords": 2}
    cap = {r["site"] for r in files if r["evidence"]["kind"] == "caption_coords"}
    assert cap == {"valkenburg-q100076", "brussels-q239"}  # the two walks that hit the 60-fetch cap

    cls = vd._load(vd.CLASSIFIED)
    assert {(r["site"], r["title"]) for r in cls} == {(r["site"], r["title"]) for r in files}
    for r in cls:
        assert (r["p_plan"], r["by"]) == (1.0, "hand")


def test_evidence_offline_and_negative_control(tmp_path):
    """fit/evidence.py's check over the staged rows, offline: exit 0, zero FAIL. The negative controls (never
    written into the staged files) are reported FAIL: the Aardenburg chain with a last hop that is not the
    town's P373 category (a path the walk never took), and the Brussels caption row with a ~52 km neighbour
    (Mons) as its stored resolution instead of the verified site point - the name-search trap a live record
    could store. Both fail 200's fail-closed box; the staged rows themselves stay untouched."""
    code, text = evidence.check(vd.FILES, vd.NO_BOOKS, catalog=vd.EXTRAS)
    assert code == 0, text
    assert f"evidence: {STAGED} rows, {STAGED} pass, 0 fail, 0 no-tie" in text, text

    files = vd._load(vd.FILES)
    aar = next(r for r in files if r["site"] == "aardenburg-q955")
    bad_chain = dict(aar)
    ev = dict(aar["evidence"])
    via = list(ev["via"])
    via[-1] = "Wrong Top Category"  # a hand-typed chain that never reaches the town's P373
    bad_chain["evidence"] = {**ev, "via": via}

    bru = next(r for r in files if r["site"] == "brussels-q239")
    bad_cap = dict(bru)
    ev = dict(bru["evidence"])
    ev["place_lon"], ev["place_lat"] = 3.9525, 50.4547  # Mons, ~52 km away: the name-search trap
    bad_cap["evidence"] = ev
    d = evidence.hav_m(bru["evidence"]["site_lon"], bru["evidence"]["site_lat"], 3.9525, 50.4547)

    f = tmp_path / "bad_rows.jsonl"
    f.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in (bad_chain, bad_cap)) + "\n",
                 encoding="utf-8")
    code, text = evidence.check(str(f), vd.NO_BOOKS, catalog=vd.EXTRAS)
    assert code == 1, text
    line = next(l for l in text.splitlines() if l.startswith("FAIL") and "aardenburg" in l)
    assert "does not run from the file's category to the site's" in line, line
    line = next(l for l in text.splitlines() if l.startswith("FAIL") and "brussels" in l)
    assert f"stored distance 0.0 m does not reproduce ({d:.0f} m)" in line, line
    assert "evidence: 2 rows, 0 pass, 2 fail, 0 no-tie" in text, text
    aar2 = next(r for r in vd._load(vd.FILES) if r["site"] == "aardenburg-q955")
    assert aar2["evidence"] == aar["evidence"]  # the staged row is untouched by the control


def test_golden_sample_matches_staged_rows():
    """tests/golden/src_van_deventer_sample.json (written by the module's --golden: the first two towns per
    evidence kind in the TOWNS order - Aardenburg and Alkmaar (category), Valkenburg and Brussels (caption) -
    plus the full staged counts, keys sorted, checked/date_commons normalized) is the staged rows exactly -
    the pin the staging files are final against."""
    golden = json.load(open(os.path.join(ROOT, "tests", "golden", "src_van_deventer_sample.json"),
                            encoding="utf-8"))
    files = vd._load(vd.FILES)
    sites = vd._load(vd.EXTRAS)
    cls = vd._load(vd.CLASSIFIED)
    assert golden["count"] == {"extras": STAGED, "files": STAGED, "classified": STAGED}

    row_of = {r["title"]: r for r in files}
    picks = [vd.TOWNS[t]["file"] for t in vd.stageable()
             if row_of[vd.TOWNS[t]["file"]]["evidence"]["kind"] == "category"][:2]  # Aardenburg, Alkmaar
    picks += [vd.TOWNS[t]["file"] for t in vd.stageable()
              if row_of[vd.TOWNS[t]["file"]]["evidence"]["kind"] == "caption_coords"][:2]  # Valkenburg, Brussels
    want_files = [vd._norm([r])[0] for r in files if r["title"] in picks]
    assert [r["title"] for r in golden["files"]] == picks
    assert golden["files"] == want_files

    town_of_file = {d["file"]: t for t, d in vd.TOWNS.items() if d.get("file")}
    known = vd.known_sites()
    ids = [known.get(vd.TOWNS[town_of_file[p]]["qid"]) or vd._site_row(town_of_file[p], vd.TOWNS[town_of_file[p]])["id"]
           for p in picks]
    assert golden["extras"] == [vd._norm([s])[0] for s in sites if s["id"] in ids]
    want_cls = [vd._norm([c])[0] for c in cls
                if (c["site"], c["title"]) in {(r["site"], r["title"]) for r in golden["files"]}]
    assert golden["classified"] == want_cls
