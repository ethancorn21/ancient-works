"""Task 206 (GOAL.md point 4): the one captionless plan in Mackenzie, The Castles of England (1897) -
page 212, the gap named in the MACKENZIE comment of pipeline/sources.py - is identified by evidence as
Shotwick Castle (Q7502621, Cheshire): the book's county context (the plate sits in Volume 2's Cheshire
section, nineteen leaves before the Lancaster plate), the book's own index and chapter text (the
1600 Randle Holme drawing: a pentagon strengthened by six towers, one drawn as five) and the surviving
ground (the C11 motte ring) all match - docs/lead_mackenzie.md carries the chain. The one staged row and
the platefit doc's record (4 anchors - originally the store file
data/db/platefits/shotwick-castle-q7502621.c_e6e5490609414bb9.json, now the review item's candidate after
the 306a audit removed the store file: the fit is ~2x too big) prove the identification by numbers. The
tests are offline: a socket-blocking fixture makes any network attempt fail loud, so the evidence check
runs from stored fields only (200's fail-closed box) and the gate re-run is docs/gate.md section 4's true
case (the doc's own recorded pairs, the placement solved from them). The gate's ACCEPTING those pairs is
the documented n=3-6 blind spot (4 corners of a 2x ring pass with 2-19 m residuals) - the audit's size
proof is not the gate's. The negative control (a file category that is not the site's P373, no
chain recorded) is reported FAIL, never kept. The golden file (tests/golden/src_mackenzie_sample.json)
pins the staged rows and the doc record; it is regenerated only via the module's --golden flag for an
intended change.
"""
import cmath
import hashlib
import json
import math
import os
import socket
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for d in (os.path.join(ROOT, "fit"), os.path.join(ROOT, "pipeline")):
    if d not in sys.path:
        sys.path.insert(0, d)
import evidence  # noqa: E402  fit/evidence.py, the evidence contract
import fit_gate  # noqa: E402  pipeline/fit_gate.py, the frozen gate of docs/gate.md section 2
import plan_fit  # noqa: E402  pipeline/plan_fit.py, the canonical similarity
import sources  # noqa: E402  pipeline/sources.py, the book's hand-tied tables
import src_mackenzie as mack  # noqa: E402  fit/src_mackenzie.py, the module under test

# Absent on purpose: evidence.check guards os.path.exists(books), so the check runs on the file rows
# only; the default catalog (sites.jsonl) carries the site (the existing-by-QID path).
NO_BOOKS = os.path.join(ROOT, "data", "books", ".no-books")


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """The whole test is offline by contract; make any network attempt in these tests fail loud."""
    def boom(*args, **kwargs):
        raise AssertionError(f"network access attempted: {args} {kwargs}")
    monkeypatch.setattr(socket, "socket", boom)
    monkeypatch.setattr(socket, "create_connection", boom)
    monkeypatch.setattr(socket, "getaddrinfo", boom)


def test_staged_row_and_join():
    """The staging files hold exactly the one row each (file/classified/extras), the row is the book's
    own plate shape (the sources.py mackenzie template plus the 200 evidence field), the site is an
    existing catalog site by QID (never re-staged in extras.jsonl), nothing clashes with the canonical
    files or the hand-tied mackenzie table, and the platefit doc's record (the store file, or the review
    item's candidate after the 306a audit removed it) matches the row (plan id, full-page crop, four
    anchors inside the frame and on the site's own ground)."""
    files = mack._load(mack.FILES)
    cls = mack._load(mack.CLASSIFIED)
    extras = mack._load(mack.EXTRAS)
    assert len(files) == 1 and len(cls) == 1 and len(extras) == 1
    f = files[0]
    assert f["site"] == mack.SITE == "shotwick-castle-q7502621"
    assert f["qid"] == mack.QID == "Q7502621"
    assert f["title"] == mack.TITLE
    assert f["year"] == 1897
    assert f["wd_plan"] is False
    assert f["cat"] == "Shotwick Castle"  # Q7502621's P373 and the file's own category (verified live)
    assert f["name"] == "Shotwick Castle, plan from Mackenzie, The Castles of England (1897)"
    assert f["by"] == "fit/src_mackenzie.py"
    assert (f["w"], f["h"]) == (839, 840)
    assert f["mime"] == "image/jpeg"
    assert f["url"].startswith("https://upload.wikimedia.org/")
    assert f["page"].startswith("https://commons.wikimedia.org/wiki/File:")
    ev = f["evidence"]
    assert ev["rec"] == "evidence/1"
    assert ev["kind"] == "category"
    assert ev["checked"]  # the checked date: live at staging, normalized in the golden
    assert ev["site_cat"] == ev["file_cat"] == "Shotwick Castle"
    assert ev["via"] == []

    sites = {s["id"]: s for s in mack._load(mack.SITES_CANONICAL)}
    assert sites.get(mack.SITE, {}).get("qid") == mack.QID  # the existing-by-QID path
    assert mack.SITE not in {s["id"] for s in mack._load(mack.EXTRAS_CANONICAL)}  # no merge double
    ex = extras[0]
    assert ex["id"] == mack.SITE
    assert ex["aerial_ok"] is True  # the picture is the reason to build the unbuilt site (211)
    assert ex["source"] == "fit/src_mackenzie.py"

    canonical = {(r.get("site"), r.get("title")) for r in mack._load(mack.FILES_CANONICAL)}
    assert (mack.SITE, mack.TITLE) not in canonical
    assert mack.TITLE not in {t for t, _, _, _ in sources.SOURCES["mackenzie"]["rows"]}  # the 26 hand-tied

    c = cls[0]  # the classified row is 1:1 with the file row, a hand-recorded plan
    assert (c["site"], c["title"]) == (mack.SITE, mack.TITLE)
    assert (c["p_plan"], c["p_birdseye"], c["p_photo"], c["by"]) == (1.0, 0.0, 0.0, "hand")

    d = mack.doc_record()
    plan = "c_" + hashlib.sha1(mack.TITLE.encode()).hexdigest()[:16]  # the export_plans rule
    assert d["site"] == mack.SITE and d["plan"] == plan
    assert d["size"] == [839, 840]
    assert d["crop"] == [0, 0, 839, 840]  # the ink spans the whole page: full-frame crop
    assert d["src"] == "commons" and d["model"] == "similarity" and d["label"] == "1897"
    assert len(d["pairs"]) == 4  # >= 4 anchors: with exactly 3 any similar triangle fits to ~0 residual
    if not os.path.exists(mack.DB_DOC):  # the 306a audit removed the store file: the item's record carries it
        assert d.get("why"), "the audit's reason must ride with the item's record"
        assert d["why"].startswith("306a audit"), d["why"]
    s = sites[mack.SITE]
    for u, v, lon, lat in d["pairs"]:
        assert 0 <= u < 839 and 0 <= v < 840
        assert evidence.hav_m(lon, lat, s["lon"], s["lat"]) < 200  # the anchors sit on the site's own ground


def test_evidence_offline_and_negative_control(tmp_path):
    """fit/evidence.py's check over the staged row, offline (stored fields only): exit 0, the exact PASS
    line. The negative control (never written into the staged file) is a copy with a file category that
    is not the site's P373 and no subcategory chain recorded: 200's fail-closed box must report FAIL
    (a tie broken after staging is a failure, not a pass), and the staged row must stay untouched."""
    row = mack._load(mack.FILES)[0]
    code, text = evidence.check(mack.FILES, NO_BOOKS)
    assert code == 0, text
    assert "evidence: 1 rows, 1 pass, 0 fail, 0 no-tie" in text, text
    assert f"{'PASS':4s} {'category':15s} {mack.SITE}|{mack.TITLE}" in text, text

    bad = dict(row)
    bad["evidence"] = dict(bad["evidence"], file_cat="Not the Castle's Category")
    f = tmp_path / "bad_row.jsonl"
    f.write_text(json.dumps(bad, ensure_ascii=False) + "\n", encoding="utf-8")
    code, text = evidence.check(str(f), NO_BOOKS)
    assert code == 1, text
    line = next(l for l in text.splitlines() if l.startswith("FAIL"))
    assert "differs from the site's with no recorded chain" in line, line
    assert "evidence: 1 rows, 0 pass, 1 fail, 0 no-tie" in text, text
    assert mack._load(mack.FILES)[0]["evidence"] == row["evidence"]  # the staged row is untouched


def test_gate_accepts_the_committed_doc():
    """docs/gate.md section 4, the true case: the doc's own recorded pairs (the review item's candidate
    after the 306a audit removed the store file) checked against the placement solved from them
    (transform=None, exactly plan_fit.similarity) - the recorded fit's own residual is the claim.
    The frozen gate (section 2) still accepts these pairs - that acceptance is exactly the documented
    n=3-6 blind spot that let the ~2x fit onto the map - and the numbers stay pinned."""
    doc = mack.doc_record()
    verdict, stats = fit_gate.gate(doc["pairs"])
    assert verdict == fit_gate.ACCEPT
    assert stats["n"] == 4
    assert stats["med"] == pytest.approx(15.81, abs=0.01)
    assert stats["slope_o"] == pytest.approx(0.1385, abs=0.001)  # the 0.11-0.145 "usable, must be said" band
    assert stats["io"] == pytest.approx(-7.04, abs=0.01)
    a, b, resid, k = plan_fit.similarity(doc["pairs"])
    assert all(math.isfinite(r) for r in resid)
    assert float(resid.max()) < 45  # the worst anchor well inside MED_MAX
    # north-up: the solved rotation is ~0 deg; the printed compass arrow points page-left and is 90 deg
    # off (docs/lead_mackenzie.md section 2)
    assert math.degrees(cmath.phase(a)) == pytest.approx(-0.2, abs=0.05)


def test_golden_sample_matches_staged():
    """tests/golden/src_mackenzie_sample.json (written by the module's --golden: the staged rows and the
    doc record, checked/date_commons/at normalized) is the staged files and record exactly - the pin the
    staging is final against; regenerate only for an intended change."""
    golden = json.load(open(os.path.join(ROOT, "tests", "golden", "src_mackenzie_sample.json"),
                            encoding="utf-8"))
    assert golden["files"] == mack._norm(mack._load(mack.FILES))
    assert golden["classified"] == mack._norm(mack._load(mack.CLASSIFIED))
    assert golden["extras"] == mack._norm(mack._load(mack.EXTRAS))
    assert golden["doc"] == dict(mack.doc_record(), at="0000-00-00T00:00:00+00:00")
