"""The evidence check (task 200, GOAL.md point 4): a fixed in-repo sample of picture rows with known-good and
known-bad ties; the check re-verifies every row offline from stored fields only, and its printed report over the
sample matches the golden file (tests/golden/evidence_check.txt, regenerated only for an intended change).
No network: the sample rows and the catalog they verify against are read from disk; check makes no requests."""
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
