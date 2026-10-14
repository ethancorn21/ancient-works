Status: done
# 238: Every matcher fit goes through the frozen 001 gate
Depends on: 302f, 302g
Touches: fit/matchfit.py, tests/test_matchfit_gate.py, docs/gate.md, tests/fixtures/matchfit_station/records.json, tests/test_matchfit_station.py

## Goal
GOAL point 3 (2026-10-13): "Every matcher fit goes to the gate (point 3)." Today
`fit/matchfit.run` writes a platefit document the moment its own `judge()` is silent, and the
document's "score" is the raw median matcher residual — the frozen 001 gate
(`pipeline/fit_gate.py`, `docs/gate.md` section 2) has never been run on the 49 matcher fits.
This task puts the gate between the judge and the write: a matcher fit is accepted by numbers,
never by the matcher's opinion. The gate is applied exactly as frozen (section 1 forbids
re-tuning; this task adds no threshold, no clause, no exception for the matcher's point style).

## Acceptance criteria
- [x] `fit/matchfit.run`: after `judge()` is silent, the document's pairs (the up-to-8
      spread-selected inliers) go through `pipeline/fit_gate.gate` with `transform=None` (the
      gate solves the canonical similarity, as it does when no placement is claimed); the
      document is written only when the verdict is ACCEPT, and its "score" is the gate's
      median residual in ground metres (the batch's own convention, `batch_us.gate_placement`)
      — the raw matcher residual stays in the matcher block for the record.
- [x] A gate refusal writes no document: the per-candidate result the run reports carries the
      gate's `why` clause verbatim (e.g. "median residual 62 m > 45 m"), the printed line names
      it, and the line's review-item upsert records that reason for the candidate (239
      consumes this result; until then the existing upsert path already records whatever the
      matcher did not place).
- [x] `docs/gate.md` gains one APPENDED section: the matcher's fit as a gate input (pairs = up
      to 8 spread-selected matcher inliers; no claimed placement — the gate solves the
      canonical similarity, as it does when none is given), the frozen rule applied unchanged,
      and how the two refusal stages divide the failures (the judge: weak or near-line
      consensus; the gate: large median residual, radial gradient — the registered 15% scale
      miss, section 9, is the class only the gate catches). No threshold or rule change
      anywhere else in the file.
- [x] `tests/test_matchfit_gate.py` (new file; no network: the matcher's `/match` answers come
      from recorded fixtures behind the ephemeral-port stub idiom of `tests/conftest.py`;
      `fit_gate` itself is numpy-only): one candidate that passes the judge but fails a gate
      clause produces no document and the refusal reason; one candidate that passes both
      produces a document whose score is the gate's median; and the 22 golden hand-fit
      documents and all 49 existing matcher documents in the real checkout are byte-unchanged
      after the test. (Implemented strictly stronger than the stated idiom: the test opens NO
      socket at all - the recorded answers replay through the recorder's `_fake_match` in
      process; `fit_gate` is numpy-only. See the test's docstring.)
- [x] The suite has no new reds against the newest driver loop-start note in PROGRESS.md.
      (Measured this session, box 5: baseline BEFORE the new file 177 passed / 1 skipped /
      0 failed - the 2026-10-13 note's fit_queue red had since been fixed in main, so the
      branch baseline is fully green and matches the 307bc loop-start note; AFTER: 180 passed
      / 1 skipped / 0 failed = baseline + the 3 new tests, zero failures.)

## Notes
- `pipeline/fit_gate.py`: `gate(pairs, transform=None) -> (verdict, stats {n, med, slope_o,
  io})` in ground metres. The batch's adapter `batch_us.gate_placement(pairs, (a, b))` shows
  the existing call shape (its `(a, b)` is the placement the model claimed; the matcher passes
  None).
- The matcher's RANSAC refit (`matchfit.ransac`) is a least squares over its inliers, so the
  gate's canonical solve over the selected up-to-8 pairs is the same placement up to the
  selection's noise — a good fit stays good through the gate.
- The recorded badbury ELoFTR candidate (22 inliers, 3.62 deg, 2.9 m centre;
  `data/matchfit/heldout/results.json`, the 302f fixture source) is the natural passes-both
  example; a 15%-scale-wrong variant of a recorded answer (build it by scaling the ground
  points, label it synthetic) is the natural passes-judge / fails-gate example.

## Proposed changes

239's declared Touches include `tests/fixtures/matchfit_station/records.json` and
`tests/test_matchfit_station.py`. Box 5 (no new reds) makes refreshing both unavoidable in 238's
own window: 238's doc-shape change (score = the gate's median instead of the raw matcher
residual; a `resid_m` key in the matcher block) changes exactly the fields 302f's confident
fixture pins byte-exactly, so the 302f test goes red the moment the gate lands until the fixture
header is refreshed (the 15 recorded /match responses and the whole unsure fixture are
untouched - measured, see hand-over). I added both paths to 238's own Touches line; the refresh
is mechanical (the measured values are in the hand-over and in the 2026-10-14 238 DECISIONS
entry), 239 cannot start before 238 merges (it depends on it), and 239 will re-run/rewrite that
test anyway and must expect the post-238 fixture. If the driver prefers 239 to own the refresh,
238 must instead ship with the 302f test red, which fails box 5.

## Hand-over

(2026-10-14, iteration 206, agent a - DONE: all five boxes ticked, Status: done; the driver
re-checks (boxes ticked + suite green). If reopened: re-run
`.venv/bin/python -m pytest tests/test_matchfit_gate.py tests/test_matchfit_station.py -q -p no:cacheprovider`;
the station test is the fixture drift sentinel (its _drift vs records.json input_hashes).

WHAT IS SHIPPED (all merged into this branch, one commit per step, see git log):
- fit/matchfit.py: _settle runs the frozen 001 gate (batch_us.gate_placement on the doc's own
  normalized pairs, transform=None) between judge and write. Refusal -> no document, the
  candidate's refusal carries the gate's clause verbatim (why print + results entry); accept ->
  doc score = the gate's median residual, matcher block gains resid_m (the raw matcher
  residual). run(results=None) appends one {site, plan, outcome written|refused|dry, path, why,
  kind} entry per candidate (239 consumes this).
- docs/gate.md section 10 (pure append; section 1's registration and section 2's rule unchanged):
  the input, the two refusal stages' division of failures, the section-7 limit measured for
  this input (a uniform 15% scale re-solves and PASSES; only mutually-inconsistent anchors
  fail, med 96.8 > 45).
- tests/fixtures/matchfit_station/records.json refreshed (8af2d91) for the doc-shape change
  (score 0.0, resid_m, the two 'gate 0.0 m' lines, depiction source); the 15 recorded /match
  responses, records_unsure.json and the input hashes are untouched.
- tests/test_matchfit_gate.py (this session, 3 tests, 38 s, zero sockets):
  1. passes-both: the recorded badbury ELoFTR answer replayed in-process (rec._fake_match(
     fixture["responses"]) - the RESPONSES dict, not the fixture; mf.reachable =
     lambda url=None: False) through the real mf.run on the recorder's tmp tree: the doc is
     written, {k:v | k != at} byte-equal to the 302f fixture doc, score recomputed in-test as
     fit_gate.gate(doc["pairs"], None) (accept, med 0.009029976684642005 -> 0.0), resid_m 3.1,
     results entry {written, why None, kind eloftr}, stdout byte-identical to the fixture's
     FIT line.
  2. passes-judge / fails-gate (SYNTHETIC, recorded fixture untouched): wrap mf.fit_row and
     perturb the RETURNED pairs' ground points - all 8, +/-200 m east alternating in spread
     order, Mercator about their centroid. The judge cannot see it (its inputs are computed
     before the pairs exist, fit_row; verified 205). The gate refuses: no document, why
     "median residual 96.81302368864387 m > 45.0 m" byte-compared against a fresh
     batch_us.gate_placement(_norm_pairs(perturbed), None) recomputation (score 96.8 >
     MED_MAX), printed line carries the clause + "[six-inch-1st.webp x0.35, rot 4]".
  3. the documented limit (docs sec 10): the 8 recorded pairs scaled 1.15x uniformly about
     their centroid -> ACCEPT, med 0.012385761943715991 (score 0.0): a consistent global
     scale error is invisible to a transform=None gate; the review queue and the 18/20 sample
     are the backstops.
  Hermeticity (a fixture over both run tests): rec._checkout_surface() (the WHOLE
  data/db/platefits - all 71 docs = the 22 golden hand docs + all 49 matcher docs; the review
  queue; the real badbury site dir behind the checkout's symlink; the site/plans/review JSON)
  sha256-pinned before and after each run: byte-identical. No fixed ports (no sockets at all -
  the conftest stub idiom minus the network), no writes outside the tmp trees.
- PITFALLS filed: patching matchfit.reachable for an offline replay needs a lambda returning
  False - a bare False (the 202/205 hand-over shorthand) raises TypeError: 'bool' object is
  not callable, because run() calls reachable(roma) WITH the argument.

VERIFIED (measured this session): my 3 tests 3 passed / 38.2 s; full suite baseline BEFORE the
new file 177 passed / 1 skipped / 0 failed (493.9 s; the 2026-10-13 loop-start note's
fit_queue::test_placement_gestures red is absent - fixed in main by the 307 work, so the
measured baseline equals the 307bc note's 177/1/0); full suite AFTER 180 passed / 1 skipped /
0 failed (530.7 s) = baseline + the 3 new tests, zero failures. Box 5 holds.

UNCOMMITTED (the harness saved the working tree; commit it first thing next session):
- tests/test_matchfit_gate.py - NEW FILE, FINAL form. Verified this session: 3 passed / 38.8 s
  standalone (that run is AFTER the last edit, which only removed an unused import; the 180-passed
  full-suite run used the identical logic). The full suite has not been re-run with the final
  bytes - trivially equivalent (unused import), but if cheap for the driver, a re-run settles it.
- PITFALLS.md - one entry appended under fit/: the reachable-lambda patch trap (bare False ->
  TypeError: 'bool' object is not callable, because run() calls reachable(roma) WITH the argument).

EXACT NEXT STEP (one small session, or the head of the 239 session - 239 may not start before
238 merges, so the commit must land first): commit the two uncommitted files, e.g.
`git add tests/test_matchfit_gate.py PITFALLS.md && git commit -m "238: tests/test_matchfit_gate.py -
the matcher's fit through the frozen gate, hermetic (zero sockets): the recorded fit passes both
(judge then gate, doc score = the gate's median 0.0), a synthetic judge-passing/gate-failing fit
writes no document with the gate's clause, the transform=None scale limit, the checkout pinned"`
then stop. The task is done (all boxes ticked, Status: done) and awaits the driver's re-check
(boxes ticked + suite green). If the driver rejects the done claim, the reasons will be in
DECISIONS.md / the task file - act on those, do not re-derive. No other work remains in 238.

PITFALLS relevant here (all under fit/ in PITFALLS.md): _fake_match takes fixture["responses"]
(the flat sha->response dict, not the fixture); patching mf.reachable needs a lambda returning
False, not a bare False (new this session); np.abs on an (n,2) array is per-element; the
data/db/platefits store is 71 = 22 by:hand + 49 agent + 0 unmarked (the golden does NOT cover the
matcher docs - this test's hermeticity fixture snapshots all 71); the per-site web/data/sites
dirs are mostly symlinks into the shared store (382 of them) - hash the recorder's checkout
surface, never the whole web/data/sites tree.

