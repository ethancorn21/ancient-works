"""The part and sheet evidence routes (task 801), end to end through the real CLI. The check re-verifies
offline from stored fields: a part_mention row (the printed name is still a documented part of the site
and the stored coordinates still agree with it within 50 km), a sheet_mention row (the stored candidate
must still be derivable from the row's own printed text - a glued run such as "York Castle" out of
"New York. Castle Garden" is not a plain norm substring, so the extractor is re-run - and the distance
guard still holds), and a stored none-with-conflict row (a resolution more than 50 km from the site keeps
failing it, whichever route found it). The three deliberately bad recorded ties must fail the check, never
silently pass. The fixture is a throwaway catalog and rows in the temp dir: no network, no ports. The
printed report matches tests/golden/evidence_801_check.txt (regenerated only for an intended change)."""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "fit"))
import evidence  # noqa: E402  (setup only: hav_m - the same distance the record stored)

CATALOG = [
    {"id": "test-castle", "qid": "Q1", "name": "Test Castle", "lon": 1.0, "lat": 51.0,
     "has_part": [{"qid": "Q2", "name": "Test Tower"}]},
    {"id": "bare-castle", "qid": "Q3", "name": "Bare Castle", "lon": 2.0, "lat": 55.0, "has_part": []},
]


def _mention_ev(kind, named, qid, plon, plat):
    d = evidence.hav_m(1.0, 51.0, plon, plat)
    ev = {"rec": "evidence/1", "kind": kind, "checked": "2026-10-11", "named_place": named,
          "place_qid": qid, "place_label": named, "place_lon": plon, "place_lat": plat,
          "site_lon": 1.0, "site_lat": 51.0, "dist_m": round(d, 1)}
    if kind == "part_mention":
        ev["part_qid"] = qid
    return ev


def _none_ev(route, named, qid, plon, plat, slon, slat):
    return {"rec": "evidence/1", "kind": "none", "checked": "2026-10-11",
            "conflict": {"route": route, "named_place": named, "place_qid": qid,
                         "place_label": named, "place_lon": plon, "place_lat": plat,
                         "site_lon": slon, "site_lat": slat}}


def fixture(tmp_path):
    rows = [
        # 1. part PASS: the title prints a documented part, its coordinates agree with the site (7 m)
        {"site": "test-castle", "title": "A view of Test Castle and its Test Tower",
         "evidence": _mention_ev("part_mention", "Test Tower", "Q2", 1.0001, 51.0)},
        # 2. part FAIL: the stored part is no longer a documented part of the site
        {"site": "test-castle", "title": "A view of Test Castle and its Test Tower",
         "evidence": _mention_ev("part_mention", "Test Tower", "Q9", 1.0001, 51.0)},
        # 3. sheet PASS: the candidate is still derivable (the 2-word pair resolves to nothing; the
        #    single resolves 0.7 km from the site)
        {"site": "test-castle", "title": "File:Testville Testham 1840, sheet by the survey",
         "evidence": _mention_ev("sheet_mention", "Testville", "Q10", 1.01, 51.0)},
        # 4. sheet FAIL: the stored candidate is no longer derivable from the printed text
        {"site": "test-castle", "title": "File:Nowhere Somewhere 1840, sheet by the survey",
         "evidence": _mention_ev("sheet_mention", "Testville", "Q10", 1.01, 51.0)},
        # 5. none + sheet conflict: the first resolved candidate is 334 km from the site - never a pass
        {"site": "bare-castle", "title": "File:Far Sheet 1840, sheet by the survey",
         "evidence": _none_ev("sheet", "Testville", "Q10", 2.0, 52.0, 2.0, 55.0)},
        # 6. none + part conflict: the part's coordinates are 389 km from the site
        {"site": "test-castle", "title": "An old view of Test Castle, the Test Tower",
         "evidence": _none_ev("part", "Test Tower", "Q2", 1.0, 54.5, 1.0, 51.0)},
        # 7. part FAIL (the trap): a documented part more than 50 km from the site is not a tie
        {"site": "test-castle", "title": "A view of Test Castle and its Test Tower",
         "evidence": _mention_ev("part_mention", "Test Tower", "Q2", 1.0, 55.0)},
    ]
    files = tmp_path / "files801.jsonl"
    files.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    catalog = tmp_path / "catalog801.jsonl"
    catalog.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in CATALOG), encoding="utf-8")
    return files, catalog


def test_part_and_sheet_routes_match_golden(tmp_path):
    files, catalog = fixture(tmp_path)
    p = subprocess.run(
        [sys.executable, "fit/evidence.py", "check",
         "--files", str(files), "--books", str(tmp_path / "absent.jsonl"), "--catalog", str(catalog)],
        cwd=ROOT, capture_output=True, text=True)
    golden = open(os.path.join(ROOT, "tests", "golden", "evidence_801_check.txt"), encoding="utf-8").read()
    assert p.stderr == "", p.stderr
    # the fixture deliberately contains 3 recorded ties the stored fields no longer support:
    # check reports them and fails, it does not silently keep them
    assert p.returncode == 1, (p.returncode, p.stdout)
    assert p.stdout == golden, f"differs from the golden:\n{p.stdout}"
