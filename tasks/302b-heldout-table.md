Status: done
Depends on: 302a
# 302b: The one-shot held-out measurement - 21 hand fits, corner error against the method
Touches: fit/inkfit_heldout.py, data/inkfit/, docs/site_flow.md

## Goal
Measure the ink-fit method against the hand fits as truth, held out (the method never reads the hand
pairs; only the evaluator does), and record the numbers in docs/site_flow.md, good or bad - the
acceptance of the whole task is read off this table. The runner `fit/inkfit_heldout.py` (checkpointing
per site, like autofit.run, so a cut session continues) takes the 21 hand-fit documents (the original
20 of tests/golden/hand_fit_docs.sha256 plus the lead's 21st, maiden-castle-q1232816.c_c20ff6b1f16d173d,
no auto flag on main), runs the frozen method of 302a on each (the method sees only the site, the plate
image and the relief), and for each writes: the corner error in metres (RMS over the 4 full-image
corners mapped to ground, autofit.Site.corner_rms convention) between the method's similarity and the
hand fit's similarity (plan_fit.similarity on the doc's pairs), plus rotation error, scale ratio, the
frozen gate's verdict on the method's own pairs, whether plan_fit.fabrication_pattern is silent on them,
and the search-matched-null margin.

## Acceptance criteria
- [x] BEFORE the run: a committed section in docs/site_flow.md registering the protocol - the frozen
      configuration, the 21 sorted document ids, the corner-error metric, the null recipe, and the
      statement that the method never sees the hand pairs. The run may only happen after this commit.
- [x] The one-shot run completed on all 21 documents (network for DEMs/pictures allowed in the working
      phase; results checkpointed under data/inkfit/heldout/).
- [x] The table in docs/site_flow.md: one row per document with the numbers above, reported verbatim as
      measured (no cherry-picking, no re-tuning of anything on this table except the 302c confidence
      threshold, which box 3 of the parent authorises).
- [x] The fabrication check passes every automatic fit the method produced (every row: fabrication_pattern
      silent). If any row fired, that is recorded here as a method defect, not fixed by editing the table.
- [x] A DECISIONS.md entry: the table summary, which sites fit and which did not, and what that means
      for the 302c threshold.

## Hand-over

(2026-10-11, iteration 83, agent c - session 3. All 5 boxes ticked, Status: done. The run, the
table, the fabrication verdict and the DECISIONS summary are committed and verified; this was
the last session on 302b. The next 302-family work for agent c is 302c (confidence decision +
site_done wiring + e2e test): read the parent's hand-over, then the two 302b DECISIONS entries
- the second carries the threshold guidance 302c sets its value on.)

**State.** Status: done. The one-shot run (started in iteration 82 with the runner commit
e171ec6) finished 21/21 before that session was cut: data/inkfit/heldout/results.json holds
all 21 entries (no "error" keys, reruns=0 everywhere, one fixed at-timestamp
2026-10-11T22:47:37Z stamped on every entry), and run.log the full log (32-219 s per doc).
The table in docs/site_flow.md (the "Measured one-shot" section under the pre-registered
protocol) was committed in the driver's uncommitted-work commit 8296835 after iteration 82;
session 3 verified it byte-identical to `python3 fit/inkfit_heldout.py table` regenerated
from the checkpoint. No footnote: the runner footnotes only exception re-runs, and none
happened.

**Verified in session 3 (fresh eyes, from committed artifacts only - nothing re-run, per
the one-shot discipline):**
- `selfcheck`: all 21 docs 0.0 m corner / 0.0 deg / 1.0 scale against themselves (the metric
  and the size-frame handling hold).
- fit/inkfit.py (frozen at f7dbba6; git log confirms unchanged since): fit() re-runs
  plan_fit.fabrication_pattern on the final mapped pairs, and a firing returns no pairs, no
  doc, gate=None, fabrication=<clause>. Box 4 stands: fabrication=None (silent) on all 20
  rows where a fit was produced (gate accept, 10 pairs each); the only non-silent cell is
  camp-d-attila's "not enough wall ink (2 candidate points, need 4)" - the method's reason
  (1 ink piece -> 2 candidate points < 4), not a pattern firing. No row records a fired
  clause.
- Full test suite green in this checkout: 64 passed, 1 skipped, 0 failed (the test_gate
  failure in the driver's older loop-start notes is fixed on main now).

**Row-10 semantics (for the driver's re-check).** The protocol sentence "a document the
method could not place gets the method's reason in the corner-error cell" covers a doc with
NO placement (placement=None: "no wall ink extracted" / "search found no valid placement").
camp-d-attila is the other case: placement FOUND, fit NOT reported (2 < 4 points) - the
frozen runner's table() renders its placement's real corner/rot/scale numbers with gate
"—" and the reason in the fabrication cell. The table was not edited after the run; it is
the runner's verbatim output, and that is how box 3 is met.

**The numbers (for 302c; full summary in the DECISIONS entry): 20/21 produced fits, all
gate-accept. Corner error 231.2-2203.6 m (median 540.0, mean 755.0); err/size 0.165-1.399:
13 fits within half the site's size, 7 beyond (calleva 1.377, arbor-low 1.399 place the
plate about a site-size away). The null margin does not separate good from bad (best
badbury +0.1871/264.5 m; worst calleva +0.1070/2203.6 m, above castle-rising's +0.0806):
only a threshold in (0.1070, 0.1871] passes exactly the one best doc. 302c's threshold can
therefore only ration the pass rate, and the honest expectation for 302d (Stonehenge) is
"placed nothing" unless the margin clears it - report that plainly.**

**Do NOT touch (frozen by 302b):** data/inkfit/heldout/results.json, run.log, the
"Measured one-shot" section of docs/site_flow.md, fit/inkfit.py,
tests/golden/hand_fit_docs.sha256, the 21 hand-fit docs. 302c sets its threshold from the
DECISIONS entry, never by re-tuning this table. If a test needs the method's pairs for a
site, run inkfit.fit on (site, plate, relief) - the method never reads the hand pairs, so
that is not a held-out violation; what must never happen is rewriting this task's
checkpoint or table.

Re-read: docs/site_flow.md:"Measured one-shot" - regenerate with `python3 fit/inkfit_heldout.py
table` (deterministic from the checkpoint) if the driver re-checks the verbatim claim.
fit/inkfit_heldout.py:measure - the entry schema 302c consumes (placement/gate/fabrication/
confidence; note the checkpoint stores no pairs and no doc).
