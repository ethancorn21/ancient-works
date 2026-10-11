"""The evidence check and record (task 200, GOAL.md point 4). The check: a fixed in-repo sample of picture rows
with known-good and known-bad ties; it re-verifies every row offline from stored fields only, and its printed
report over the sample matches the golden file (tests/golden/evidence_check.txt, regenerated only for an
intended change). The record: it only extends a row - every existing field keeps its bytes, its order and the
line's terminator, and "evidence" is the only key added, last. No network: the rows and the catalog they verify
against are read from disk; check makes no requests and record without --live makes none."""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_check_over_sample_matches_golden():
    p = subprocess.run(
        [sys.executable, "fit/evidence.py", "check",
         "--files", "tests/evidence_sample/files.jsonl",
         "--books", "tests/evidence_sample/index.jsonl"],
        cwd=ROOT, capture_output=True, text=True)
    golden = open(os.path.join(ROOT, "tests", "golden", "evidence_check.txt"), encoding="utf-8").read()
    assert p.stderr == "", p.stderr
    # the sample deliberately contains 3 rows whose stored record the data no longer supports:
    # check reports them and fails, it does not silently keep them
    assert p.returncode == 1, (p.returncode, p.stdout)
    assert p.stdout == golden, f"differs from the golden:\n{p.stdout}"


def _j(line):
    return json.loads(line)


def _strip_evidence(line):
    r = _j(line)
    r.pop("evidence", None)
    return json.dumps(r, ensure_ascii=False) + "\n"


def test_record_appends_evidence_without_touching_existing_bytes(tmp_path):
    frows = open(os.path.join(ROOT, "data", "commons", "files.jsonl"), encoding="utf-8").readlines()
    brows = open(os.path.join(ROOT, "data", "books", "index.jsonl"), encoding="utf-8").readlines()
    kip = next(l for l in frows if _j(l).get("by") == "pipeline/sources.py kip" and _j(l).get("title"))
    plain = next(l for l in frows if _j(l).get("title") and not _j(l).get("by"))
    sentinel = next(l for l in frows if not _j(l).get("title"))
    files_fixture = tmp_path / "files.jsonl"
    files_fixture.write_text(_strip_evidence(kip) + _strip_evidence(plain) + _strip_evidence(sentinel), encoding="utf-8")
    books_fixture = tmp_path / "books.jsonl"
    books_fixture.write_text(_strip_evidence(brows[0]) + _strip_evidence(brows[1]), encoding="utf-8")
    p = subprocess.run([sys.executable, "fit/evidence.py", "record",
                        "--files", str(files_fixture), "--books", str(books_fixture)],
                       cwd=ROOT, capture_output=True, text=True)
    assert p.returncode == 0 and p.stderr == "", (p.returncode, p.stderr)
    assert p.stdout == "evidence recorded: 1 hand-tied, 2 book, 0 live\n", p.stdout
    out = files_fixture.read_text(encoding="utf-8").splitlines(keepends=True)
    assert len(out) == 3 and all(l.endswith("\n") for l in out), "a line lost its terminator (rows glued)"
    k2, p2, s2 = out
    assert p2 == _strip_evidence(plain) and s2 == _strip_evidence(sentinel), "an unrecorded row was touched"
    assert k2[:-1].startswith(_strip_evidence(kip)[:-2]) and k2.endswith("}}\n"), "existing bytes of the row changed"
    kr, ko = _j(k2), _j(_strip_evidence(kip))
    assert list(kr)[:-1] == list(ko) and kr["evidence"]["kind"] == "hand_tied"
    assert kr["evidence"]["source"] == "pipeline/sources.py kip" and kr["evidence"]["checked"]
    b2 = books_fixture.read_text(encoding="utf-8").splitlines(keepends=True)
    assert len(b2) == 2
    for new, old in zip(b2, (_strip_evidence(brows[0]), _strip_evidence(brows[1]))):
        assert new.endswith("\n") and new[:-1].startswith(old[:-2]), "existing bytes of the book row changed"
        rb, ob = _j(new), _j(old)
        assert list(rb)[:-1] == list(ob) and rb["evidence"]["kind"] in ("caption_coords", "none")
