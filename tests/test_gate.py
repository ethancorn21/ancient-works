"""The fit gate's one-shot measurement, re-run (docs/gate.md, sections 8-9; task 001, box 4), and
the frozen-set partition semantics (task 218).

The gate was measured once on the held-out hand fits before it was trusted; the measurement is
the frozen record in docs/gate.md section 9. This test re-runs the registered section-6 command
(``.venv/bin/python tools/gate_heldout.py``, here with the test's own interpreter) and checks:

1. the command still prints, byte for byte, the recorded held-out table and the committed dev
   table (tests/golden/gate_heldout.txt: 40 held lines, then 60 dev lines) - so any drift in
   pipeline/fit_gate.py, tools/gate_heldout.py or the 20 hand-fit documents is caught;
2. the section-9 table in docs/gate.md still equals the recorded held-out half - the document
   is the record and the golden file is its mirror; neither may drift from the other;
3. the summary numbers section 9 states (7 of 8 true accepted; 4 of 32 wrong, all scale15;
   0 of 24 moved/rot10/xsite) are what the re-run produces - the result, not just its format;
4. the frozen constants of pipeline/fit_gate.py still equal the section-2 rule verbatim -
   a change there re-tunes the gate on spent data and voids the registration, so it must fail
   here, not silently change the table.

Offline: the tool reads only data/db/platefits/ and web/data/sites.json, writes nothing, uses no
network and no ports (it runs as a subprocess, so even a stray write lands in the checkout the
tool itself is in, and it has none).
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOLDEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "golden", "gate_heldout.txt")
HELD_LINES = 40  # 8 held-out documents x the five section-4 placements


def _run(section):
    """The section-6 command for one set: the committed tool, its stdout as a list of lines."""
    proc = subprocess.run([sys.executable, "tools/gate_heldout.py", "--set", section],
                          cwd=ROOT, capture_output=True, text=True, timeout=300)
    assert proc.returncode == 0, "gate_heldout %s failed: %s" % (section, proc.stderr[-2000:])
    return proc.stdout.splitlines()


def _rows(lines):
    """(doc, case, verdict) per printed line."""
    out = []
    for ln in lines:
        t = ln.split()
        assert len(t) == 7 and t[2].startswith("n=") and t[3].startswith("med=") and \
            t[4].startswith("slope_o=") and t[5].startswith("io=") and t[6] in ("accept", "reject"), \
            "unrecognized gate_heldout line: %r" % ln
        out.append((t[0], t[1], t[6]))
    return out


def _doc_section9_table():
    """The verbatim table in docs/gate.md section 9 (the first fenced block after the heading)."""
    doc = open(os.path.join(ROOT, "docs", "gate.md")).read()
    fence = re.search(r"## 9\..*?```\n(.*?)\n```", doc, re.S)
    assert fence, "docs/gate.md has no section-9 fenced table"
    return fence.group(1).splitlines()


def test_recorded_measurement_reproduces_and_agrees():
    golden = open(GOLDEN).read().splitlines()
    assert len(golden) == HELD_LINES + 60, "golden must hold 40 held + 60 dev lines"

    held = _run("held")
    dev = _run("dev")

    # 1. the section-6 command still prints the recorded tables, byte for byte
    assert held == golden[:HELD_LINES], "held-out table no longer matches tests/golden/gate_heldout.txt"
    assert dev == golden[HELD_LINES:], "dev table no longer matches tests/golden/gate_heldout.txt"

    # 2. the document's section-9 table is the recorded held-out half (doc and golden agree)
    assert _doc_section9_table() == golden[:HELD_LINES], \
        "docs/gate.md section 9 and tests/golden/gate_heldout.txt have drifted apart"

    # 3. the numbers section 9's summary states are what the re-run produces
    rows = _rows(held)
    assert len(rows) == 40
    true = [v for d, c, v in rows if c == "true"]
    wrong = [v for d, c, v in rows if c != "true"]
    by_case = {c: [v for d, cc, v in rows if cc == c] for c in ("moved", "rot10", "scale15", "xsite")}
    assert len(true) == 8 and true.count("accept") == 7, "section 9: 7 of 8 true accepted"
    assert len(wrong) == 32 and wrong.count("accept") == 4, "section 9: 4 of 32 wrong accepted"
    for c in ("moved", "rot10", "xsite"):
        assert by_case[c].count("accept") == 0, "section 9: 0 of 8 %s accepted" % c
    assert by_case["scale15"].count("accept") == 4, "section 9: the 4 wrong accepts are all scale15"

    # and the dev set still shows its section-5 calibration: 10 of 12 true, 2 of 48 wrong
    rows = _rows(dev)
    assert len(rows) == 60
    true = [v for d, c, v in rows if c == "true"]
    wrong = [v for d, c, v in rows if c != "true"]
    assert len(true) == 12 and true.count("accept") == 10, "section 5: 10 of 12 dev true accepted"
    assert len(wrong) == 48 and wrong.count("accept") == 2, "section 5: 2 of 48 dev wrong accepted"


def test_fit_gate_constants_are_the_frozen_section2_rule():
    """A threshold change here would re-tune the spent held-out set; the registration says fail."""
    sys.path.insert(0, os.path.join(ROOT, "pipeline"))
    import fit_gate  # constants only: a config check, not a call through the product
    sys.path.remove(os.path.join(ROOT, "pipeline"))  # keep the path clean for later test files
    assert fit_gate.N_MIN == 3
    assert fit_gate.RHO2_MIN == 1.0
    assert fit_gate.MED_MAX == 45.0
    assert fit_gate.SLOPE_MAX == 0.145
    assert fit_gate.SLOPE_PATTERN == 0.11
    assert fit_gate.IO_MIN == -10.0
    assert (fit_gate.ACCEPT, fit_gate.REJECT) == ("accept", "reject")


def _stub(directory, doc, auto=None):
    """One stub platefit document: partition() reads only the name and the "auto" flag."""
    body = "{}" if auto is None else json.dumps({"auto": auto})
    (directory / (doc + ".json")).write_text(body + "\n")


def _expect_void(module, tree, missing_name):
    """partition() must fail loudly and name the registered document that stopped being non-auto."""
    try:
        module.partition(str(tree))
    except SystemExit as e:
        assert "the registered partition is void" in str(e), str(e)
        assert missing_name in str(e), str(e)
    else:
        raise AssertionError("partition() accepted a tree in which registered doc %s is not a "
                             "non-automatic document" % missing_name)


def test_partition_frozen_set_tolerates_post_registration_docs(tmp_path):
    """(task 218) The frozen set is the 20 names docs/gate.md section 3 registered, not whatever
    is in data/db/platefits/: post-registration documents (the batch's automatic output and new
    hand fits, which stay subject to the production fit gate at fit time) are excluded from the
    one-shot proof, so the derived held/dev equal the registered lists in every state; a
    registered name missing from the non-automatic documents (renamed, deleted, or gained
    "auto": true) voids the registration and fails loudly. Stub documents in a temp directory
    stand for the real ones (partition reads only names and the auto flag); nothing is written
    to the repo tree."""
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import gate_heldout
    sys.path.remove(os.path.join(ROOT, "tools"))  # keep the path clean for later test files
    registered = sorted(gate_heldout.REGISTERED["held"] + gate_heldout.REGISTERED["dev"])
    assert len(registered) == 20, "section 3 registered exactly 20 documents"

    # (a) exactly the registered 20 (plus any number of post-registration documents - new hand
    # fits and batch auto output): the partition is derived over the registered 20 alone, so
    # held/dev come out the registered lists in every state and check_registered passes
    extras = ((),
              ("shotwick-castle-q7502621.c_e6e5490609414bb9",
               "maiden-castle-q1232816.c_c20ff6b1f16d173d",
               "some-roman-site-q1234.c_deadbeefdeadbeef"))
    for i, extra in enumerate(extras):
        tree = tmp_path / ("registered-only" if not extra else "with-post-registration-%d" % i)
        tree.mkdir()
        for doc in registered:
            _stub(tree, doc)
        for doc in extra:
            _stub(tree, doc)
        for doc in ("batch-auto-q1.c_abcd1234abcd1234", "batch-auto-q1.c_9876543298765432"):
            _stub(tree, doc, auto=True)
        names, held, dev = gate_heldout.partition(str(tree))
        assert names == registered, "the derivation is over the 20 registered names in every state"
        assert held == gate_heldout.REGISTERED["held"], "held equals the registered held-out set"
        assert dev == gate_heldout.REGISTERED["dev"], "dev equals the registered dev set"
        gate_heldout.check_registered(held, dev)

    # (b) a registered name missing from the non-automatic documents: fail loudly, naming it.
    # b1: renamed or deleted (19 registered + 1 unknown hand doc); b2: all 20 present, but one
    # gained "auto": true and so dropped out of the non-automatic set.
    broken = tmp_path / "renamed-or-deleted"
    broken.mkdir()
    for doc in registered[:-1]:
        _stub(broken, doc)
    _stub(broken, "shotwick-castle-q7502621.c_e6e5490609414bb9")
    _expect_void(gate_heldout, broken, registered[-1])

    autoflagged = tmp_path / "autoflagged"
    autoflagged.mkdir()
    for doc in registered:
        _stub(autoflagged, doc, auto=(doc == registered[-1]))
    _expect_void(gate_heldout, autoflagged, registered[-1])
