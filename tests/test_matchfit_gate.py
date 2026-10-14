"""The matcher's fit through the frozen 001 gate (task 238), hermetically: no network at all.

Since 238, fit/matchfit.run writes a platefit document only when a candidate passes BOTH the
matcher's judge and the frozen gate of docs/gate.md section 2 (pipeline/fit_gate.gate, no claimed
placement: the gate solves the canonical similarity from the document's own up-to-8 spread-selected
inlier pairs, and its median residual is the document's score). This test drives the real run()
in-process with the 302f recorded ELoFTR fixture (tests/fixtures/matchfit_station/records.json):
the matcher's /match answers come from the recorder's _fake_match, keyed by the sha256 of the
exact request body - the ephemeral-port stub idiom of tests/conftest.py with the socket removed,
which is the stronger form of its no-network proof (this test never opens a connection at all).

  passes both    the recorded badbury-rings-q798831 ELoFTR answer (22 inliers, 3.6 deg) passes
                 judge and gate: the document is written, its score is the gate's median
                 residual recomputed here from the document's own pairs (0.0; the raw matcher
                 residual 3.1 m stays in the matcher block as resid_m), its printed FIT line is
                 byte-identical to the fixture's, the results entry says written.
  passes judge,   a SYNTHETIC variant (the recorded fixture is untouched): the fit's returned
  fails gate      pairs are corrupted after the judge has seen them - all 8 anchors offset 200 m
                 east, alternating in spread order, in Mercator about their centroid: a strong
                 consensus whose anchors are mutually inconsistent. The judge's verdict cannot
                 change (fit/matchfit.fit_row computes all of its inputs - inliers, rotation,
                 spread, matcher residual - from the /match response and its RANSAC refit before
                 it assembles the pairs); the gate refuses by its median clause: no document is
                 written, and the results entry and the printed line carry the gate's clause
                 verbatim (byte-compared against a fresh gate_placement recomputation on the same
                 corrupted pairs).
  the limit      docs/gate.md section 10 (the section-7 limit applied to this input): with
                 transform = None the placement is solved from the same pairs, so a consistent
                 global scale error passes - the 8 recorded pairs scaled 15% about their centroid
                 re-solve and accept (med ~0.01 m, score 0.0). The review queue and the human's
                 sample are the backstops for that class, not the gate.

Hermeticity: every run happens on a throwaway tree (the recorder's build_tree, the hand document
deleted in its copy), and the checkout's document store (the 22 golden hand documents and all 49
existing matcher documents), its review queue, its per-site web data for the run's site and its
site/plans/review JSON are sha256-pinned before and after each run - nothing a run can write
outside its own tree.
"""
import contextlib
import importlib.util
import io
import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIX = ROOT / "tests" / "fixtures" / "matchfit_station"

sys.path.insert(0, str(ROOT / "fit"))
sys.path.insert(0, str(ROOT / "pipeline"))
import aw  # noqa: E402
import batch_us  # noqa: E402
import fit_gate  # noqa: E402
import matchfit as mf  # noqa: E402


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# The recorder (working-phase tool, import-safe: no live work at import): its constants, the tmp-
# tree builder it shares with tests/test_matchfit_station.py, and the offline replay.
rec = _load(FIX / "record.py", "matchfit_station_recorder_gate")
SID, PLAN, DOCID = rec.SID, rec.PLAN, rec.DOCID


def _fixture():
    return json.loads((FIX / "records.json").read_text())


def _fit_line(fixture):
    """The fixture's recorded FIT stdout line (extracted, never re-typed): the printed line of a
    passing run must be byte-identical to it."""
    return next(l for l in fixture["header"]["confident"]["expected_stdout"]
                if ": FIT (eloftr)" in l)


def _run_offline(fixture, tree, fit_row=None):
    """matchfit.run on the tree with the recorded ELoFTR answers replayed in-process: mf.match is
    the recorder's _fake_match (the fixture's responses, keyed by the sha256 of the exact request
    body) and reachable is forced down (no RoMa second pass). No socket is opened: every /match
    the run builds is answered from the fixture by its body hash. -> (results, written, stdout,
    stderr)."""
    orig = (mf.match, mf.reachable, mf.fit_row)
    mf.match = rec._fake_match(fixture["responses"])
    mf.reachable = lambda url=None: False
    if fit_row is not None:
        mf.fit_row = fit_row
    results = []
    out, err = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            written = mf.run(str(tree), [SID], results=results)
    finally:
        (mf.match, mf.reachable, mf.fit_row) = orig
    return results, written, out.getvalue(), err.getvalue()


def _perturbed_fit_row(holder):
    """The judge's fit, corrupted after the judge: the returned pairs' ground points offset 200 m
    east, alternating in spread order, in Mercator about their centroid, re-rounded the doc's way.
    The judge cannot see it (its inputs are computed before the pairs exist); the gate, scoring
    the document's own internal consistency, must. `holder` receives the corrupted pairs for the
    test's fresh recomputation."""
    orig = mf.fit_row

    def perturb(pairs):
        xy = [aw.to_merc(p[2], p[3]) for p in pairs]
        cx = sum(x for x, _ in xy) / len(xy)
        cy = sum(y for _, y in xy) / len(xy)
        out = []
        for i, (p, (x, y)) in enumerate(zip(pairs, xy)):
            x += 200.0 if i % 2 == 0 else -200.0
            out.append([p[0], p[1], *aw.to_lonlat(x, y)])
        holder["pairs"] = out
        return out

    def fit_row(root, site, row, url=None, kind="eloftr"):
        r = orig(root, site, row, url, kind)
        if "pairs" in r:
            r["pairs"] = perturb(r["pairs"])
        return r

    return fit_row


@pytest.fixture
def checkout_untouched():
    """The checkout files a run must never touch, sha256-pinned for the test's duration: the whole
    document store (the 22 golden hand documents and all 49 existing matcher documents), the
    review queue, the run's site directory (the real one behind the checkout's symlink) and the
    site/plans/review JSON."""
    before = rec._hash_surface(rec._checkout_surface())
    yield
    after = rec._hash_surface(rec._checkout_surface())
    changed = {p: (b, a) for p, b in before.items() if after.get(p) != b}
    assert not changed, "the run wrote outside its tmp tree: %r" % changed
    assert not (after.keys() ^ before.keys()), "files appeared or vanished in the checkout"


def test_gate_accepts_the_recorded_fit(tmp_path, checkout_untouched):
    """A candidate that passes both the judge and the gate becomes a document whose score is the
    gate's median residual over its own pairs - not the matcher's residual."""
    fixture = _fixture()
    tree = rec.build_tree(tmp_path / "tree", delete_hand_doc=True)
    results, written, out, err = _run_offline(fixture, tree)
    assert err == "", err  # a drifted fixture would surface as per-window replay errors here

    doc_path = tree / "data" / "db" / "platefits" / (DOCID + ".json")
    assert written == [str(doc_path)] and doc_path.is_file()
    doc = json.loads(doc_path.read_text())
    assert "at" in doc
    assert {k: v for k, v in doc.items() if k != "at"} == fixture["header"]["confident"]["doc"]

    # the score is the gate's median residual, recomputed here from the document's own pairs with
    # no claimed placement; the raw matcher residual stays in the matcher block as resid_m
    verdict, stats = fit_gate.gate(doc["pairs"], None)
    assert verdict == fit_gate.ACCEPT
    assert doc["score"] == round(stats["med"], 1) == 0.0
    assert doc["matcher"]["resid_m"] == 3.1

    assert results == [{"site": SID, "plan": PLAN, "outcome": "written",
                        "path": str(doc_path), "why": None, "kind": "eloftr"}]
    assert out.splitlines() == [_fit_line(fixture)]


def test_gate_refuses_before_the_write(tmp_path, checkout_untouched):
    """A candidate that passes the judge but fails a gate clause writes no document: the refusal
    the run reports carries the gate's own clause."""
    fixture = _fixture()
    fit_line = _fit_line(fixture)
    title = fit_line.split(SID + "  ")[1].split(":")[0]

    holder = {}
    tree = rec.build_tree(tmp_path / "tree", delete_hand_doc=True)
    results, written, out, err = _run_offline(fixture, tree, fit_row=_perturbed_fit_row(holder))
    assert err == "", err
    assert "pairs" in holder  # the replay produced the fit the corruption wraps

    assert written == []
    assert not (tree / "data" / "db" / "platefits" / (DOCID + ".json")).is_file()

    # the refusal is the gate's median clause, byte-compared against a fresh recomputation on the
    # same corrupted pairs (normalized exactly as the run normalizes them)
    accepted, score, why = batch_us.gate_placement(batch_us._norm_pairs(holder["pairs"]), None)
    assert not accepted and why is not None
    assert score > fit_gate.MED_MAX  # the clause that refused: the median over the frozen limit
    entry = results[0]
    assert entry == {"site": SID, "plan": PLAN, "outcome": "refused", "path": None,
                     "why": why, "kind": "eloftr"}
    assert out.splitlines() == ["%s  %s: %s [six-inch-1st.webp x0.35, rot 4]" % (SID, title, why)]


def test_uniform_scale_passes_the_gate():
    """The documented limit of this input (docs/gate.md section 10): a consistent global scale
    error re-solves to near-zero residuals and passes - the 8 recorded pairs scaled 15% about
    their centroid accept, med ~0.01 m, score 0.0."""
    pairs = [list(p) for p in _fixture()["header"]["confident"]["doc"]["pairs"]]
    xy = [aw.to_merc(p[2], p[3]) for p in pairs]
    cx = sum(x for x, _ in xy) / len(xy)
    cy = sum(y for _, y in xy) / len(xy)
    scaled = [[p[0], p[1], *aw.to_lonlat(cx + 1.15 * (x - cx), cy + 1.15 * (y - cy))]
              for p, (x, y) in zip(pairs, xy)]
    verdict, stats = fit_gate.gate(batch_us._norm_pairs(scaled), None)
    assert verdict == fit_gate.ACCEPT
    assert stats["med"] < 0.05  # the gate's median, recomputed here: the score rounds to 0.0
    assert round(stats["med"], 1) == 0.0
