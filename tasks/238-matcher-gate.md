Status: in-progress
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
- [ ] `fit/matchfit.run`: after `judge()` is silent, the document's pairs (the up-to-8
      spread-selected inliers) go through `pipeline/fit_gate.gate` with `transform=None` (the
      gate solves the canonical similarity, as it does when no placement is claimed); the
      document is written only when the verdict is ACCEPT, and its "score" is the gate's
      median residual in ground metres (the batch's own convention, `batch_us.gate_placement`)
      — the raw matcher residual stays in the matcher block for the record.
- [ ] A gate refusal writes no document: the per-candidate result the run reports carries the
      gate's `why` clause verbatim (e.g. "median residual 62 m > 45 m"), the printed line names
      it, and the line's review-item upsert records that reason for the candidate (239
      consumes this result; until then the existing upsert path already records whatever the
      matcher did not place).
- [ ] `docs/gate.md` gains one APPENDED section: the matcher's fit as a gate input (pairs = up
      to 8 spread-selected matcher inliers; no claimed placement — the gate solves the
      canonical similarity, as it does when none is given), the frozen rule applied unchanged,
      and how the two refusal stages divide the failures (the judge: weak or near-line
      consensus; the gate: large median residual, radial gradient — the registered 15% scale
      miss, section 9, is the class only the gate catches). No threshold or rule change
      anywhere else in the file.
- [ ] `tests/test_matchfit_gate.py` (new file; no network: the matcher's `/match` answers come
      from recorded fixtures behind the ephemeral-port stub idiom of `tests/conftest.py`;
      `fit_gate` itself is numpy-only): one candidate that passes the judge but fails a gate
      clause produces no document and the refusal reason; one candidate that passes both
      produces a document whose score is the gate's median; and the 22 golden hand-fit
      documents and all 49 existing matcher documents in the real checkout are byte-unchanged
      after the test.
- [ ] The suite has no new reds against the newest driver loop-start note in PROGRESS.md.

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

(2026-10-14, iteration 201, agent a - measurement session; branch in sync with main at start;
NO code changed, nothing to re-read from a half-done edit)

STATE: iteration 201 = verification + offline measurement only (the prep note's step 3, plus
checking every prep assumption against current main). All of prep tasks/prep/238.md was
re-verified: A1-A7 and A9 hold on current main (fit/matchfit.py 338 L, pipeline/fit_gate.py,
fit/batch_us.gate_placement, the 302f fixture + recorder, docs/gate.md sections 1-9 all as
described). No production file was touched; the only artifact is /tmp/aw238_meas.py (throwaway;
regenerate from this hand-over if lost - it imports tests/fixtures/matchfit_station/record.py
as module `rec`, replays the fixture responses through mf.fit_row/mf.run in a tmp tree from
rec.build_tree, and computes the gate/depiction/synthetic values).

MEASURED (all in this checkout, .venv, offline replay of 302f's recorded badbury responses;
reproducible: the RANSAC is seeded, the replay is deterministic, the checkout surface was
hash-verified unchanged before/after):
- fit_row replay: 22 inliers / 61 matches, rot 3.62 deg, resid_m 3.078 (prints "3 m"), spread
  (0.138, 125.3), why None - the judge is silent, as recorded.
- The 8 spread-selected pairs round to EXACTLY the fixture doc's pairs (norm == fixture doc
  pairs: True). The doc's pairs are stable; 238 changes only score + matcher block + strings.
- gate(pairs, transform=None) on the raw pairs: accept, med 7.08e-10. On the doc's (rounded
  1dp/7dp) pairs: ACCEPT, med 0.009029976684642005, slope_o 4.37e-05, io 8.4e-04.
  => the new doc score = round(med, 1) = **0.0** (not 3.1).
- Depiction source line: "...within 1 m (gate score 3.1 m)" -> "...within 1 m (gate score 0.0 m)"
  (the "within 1 m" m = ceil(max residual of the doc-pair similarity) = ceil(0.017) = 1, UNCHANGED;
  source_line's auto branch is keyed on doc["auto"] and doc["score"]).
- 302f confident fixture fields that change when the gate lands (records.json, header.confident):
  doc.score 3.1 -> 0.0; doc.matcher gains "resid_m": 3.1 (the raw matcher residual, box 1);
  depiction.source "(gate score 3.1 m)" -> "(gate score 0.0 m)"; expected_stdout line 6
  "sync ... gate 3.1 m" -> "gate 0.0 m" and line 9 "... synced to the map, gate 3.1 m" ->
  "gate 0.0 m" (site_done prints doc["score"] in both). UNCHANGED: lines 0,2,3,4,5,7,8,10
  (line 2's "residual 3 m" is the raw matcher residual - the FIT line is untouched by box 1;
  line 5's "residuals m [0.0 x8]" is from the doc-pair similarity, pairs unchanged;
  site_entry_equal stays True - the sites.json entry's score 1.45 is the hand fit's, not the doc's),
  spread_pairs, all 15 responses. The UNSURE fixture (records_unsure.json) is UNTOUCHED: the
  judge refuses before the gate (verified: its 8 stdout lines carry no score; the item's why is
  "no model answer", gate_score None). tests/test_matchfit_station.py: one assert changes -
  set(doc["matcher"]) gains "resid_m".
- SYNTHETIC VARIANTS (all built on the 8 doc pairs, transform=None, judge inputs untouched):
  * 4 of 8 anchors' ground points offset +-200 m E (alternating in spread order): REJECT,
    med 96.80919025564799, why "median residual 96.80919025564799 m > 45.0 m" (MEDIAN clause).
  * 2 of 8 anchors +200 m E: REJECT, med 32.9 (below 45!), slope_o 0.22830842459824788, why
    "radial gradient: slope_o 0.22830842459824788 > 0.145" (SLOPE clause).
  * uniform 1.15x scale about the centroid: ACCEPT, med 0.0104 (section 7 limit: a consistent
    global error passes - CONFIRMED, contradicting the task Notes' "natural fails-gate example").
  * RADIAL 15% (1+0.15 rho/rho_max) and 50% scale distortion: both ACCEPT (med 2.27/7.59,
    slope 0.009/0.025). PREP WAS WRONG HERE: prep sec 4 said "tune the 0.15 factor so the
    measured why is the slope clause" - it cannot fire for any scale-shaped distortion, because
    the canonical similarity solve (scale, rotation, 2 translations free) absorbs scale-shaped
    ground errors of every magnitude measured; only anchor-OFFSET patterns produce residuals
    no similarity explains (filed in PITFALLS if you get there; also in the DECISIONS entry).
- Doc inventory (measured): data/db/platefits = 71 docs = 49 by:agent fitter:matcher +
  22 by:hand (NO by:None docs). tests/golden/hand_fit_docs.sha256 = 41 lines = the 22 hand
  docs + 19 hand-fit data/sites/<id>/site.json files (NOT "19 by:None docs" - prep A8 was wrong
  on that; fit/batch_us.write_golden's docstring says so). All 41 hashes match on this tree
  right now. The hermeticity box (box 4) should snapshot exactly these: the 71 platefit JSONs
  (49 matcher + 22 golden hand) and data/review/*.json, before vs after the test runs.

TEST DESIGN (decided; write it into the test docstring):
- Idiom: 302f's ephemeral-port in-process stub (it lives in tests/test_matchfit_station.py -
  _start_stub + the GUARD; tests/conftest.py has NO matcher stub, only the served/copy_web
  helpers; import rec from the fixture dir as that test does). 302f's recorder's _fake_match
  offline replay (never touches a socket at all) is the faster alternative - pick the stub for
  parity with 302f's "no network" proof; both replay by sha256 of the exact request body.
- Candidate 1 (passes both): the recorded badbury answer through mf.run -> doc written;
  assert doc["score"] == round(fit_gate.gate(doc["pairs"], None)[1]["med"], 1) recomputed IN
  THE TEST (expected 0.0); matcher block = 7 old keys + resid_m 3.1; results entry
  {outcome "written", why None}; the FIT stdout line unchanged ("...residual 3 m").
- Candidate 2 (passes judge / fails gate): SYNTHETIC - in-process mf.run with matchfit.fit_row
  wrapped so that after the real fit_row (judge already passed, image-space inputs untouched)
  the returned pairs' ground points get the +-200 m E 4-anchor offset above (label synthetic
  in the docstring; the recorded fixture is not modified). Assert: no doc file; results entry
  {outcome "refused", why == gate's clause verbatim} (byte-compare against a fresh
  fit_gate/batch_us.gate_placement recomputation on the same corrupted pairs); the printed
  line contains the clause + the "[ground x window, rot N]" extra. Do NOT assert any review
  item (the upsert belongs to the line, not to a bare run).
- Candidate 3 (hermeticity): sha256 snapshot of every data/db/platefits/*.json and
  data/review/*.json in the CHECKOUT before the runs, byte-identical after; runs happen in
  rec.build_tree tmp trees (the _checkout_surface/_hash_surface idiom from record.py covers
  the right file set).
- Also assert (cheap, backs docs sec 10): the 1.15x-scaled-anchors variant of the 8 doc pairs
  PASSES the gate (accept, med 0.0104) - the section-7 limit, applied to the matcher.
- NOTE on the task Notes: the "15%-scale-wrong variant ... is the natural fails-gate example"
  is NOT true for transform=None (measured above). The box itself only demands "a candidate
  that passes the judge but fails a gate clause (e.g. 'median residual 62 m > 45 m')" - the
  offset4 construction delivers exactly that clause shape. This needs no ask_human: box 1's
  frozen transform=None design is kept, the Notes example is a suggestion, and docs sec 10
  states the limit honestly (it is a restatement of section 7, not a rule change).

NEXT STEPS (one per session, in order):
1. (refactor-first, AGENTS.md) extract run()'s per-candidate tail (judge-result -> print ->
   write) into a helper, e.g. _settle(root, sid, row, r, kind, dry, results=None), run()
   currently ~47 L and the change adds branches; behaviour-identical; prove with
   tests/test_matchfit_station.py (2 tests, ~56 s, .venv) before AND after; commit the
   refactor ALONE. Suggested shape (settled in the measurement): _settle computes
   pairs = batch_us._norm_pairs(r["pairs"]); gate via batch_us.gate_placement(pairs, None)
   (= fit_gate.gate(pairs, None), the box's named convention) BEFORE the FIT print; on
   refusal r["why"] = the gate's clause verbatim and it prints the same "why" line shape as
   a judge refusal (with the "[ground x window, rot N]" extra) and writes nothing; on accept
   the FIT line prints unchanged, write_doc gets the NORMALIZED pairs and the gate score
   (write_doc re-normalizes idempotently), the matcher block gains "resid_m": round(resid_m,1);
   run() gains a results=None kwarg appending one dict per settled candidate
   {site, plan, outcome written|refused|dry, path (None when refused), why (judge or gate
   clause verbatim, None when written), kind} - site_done calls run(root, [sid]) unchanged,
   239 consumes the kwarg.
2. (feature) the gate in run() per step 1's settled shape; commit.
3. (fixture refresh - 239's declared files, cleared by the Proposed changes section above)
   records.json header.confident: doc.score 0.0, doc.matcher + "resid_m": 3.1,
   depiction.source "(gate score 0.0 m)", expected_stdout lines 6 and 9 "gate 0.0 m";
   test_matchfit_station.py: the matcher-key set gains "resid_m". Commit; re-run the 302f test
   green.
4. (docs) append docs/gate.md "## 10. The matcher's fit as a gate input (238, 2026-10-14)" -
   input (pairs = up to 8 spread-selected matcher inliers; transform=None, the gate solves the
   canonical similarity, the batch's own "true" case of section 4); the two refusal stages
   (judge: weak/rotation/near-line consensus; gate: the doc's own internal consistency - large
   median residual, residual gradient, degeneracy); and the section-7 restatement measured
   this task: with transform=None a CONSISTENT global error passes, including a uniformly 15%
   -scaled answer (the gate re-solves it, med ~ 0) - the scale15 rows of section 9 were caught
   as CLAIMED placements against recorded anchors; the matcher's scale errors are visible to
   the gate only in radial/non-uniform or mutually-inconsistent form; the review queue and the
   human's 18/20 sample remain the scale backstop. No threshold/rule change anywhere else.
5. (test) tests/test_matchfit_gate.py per the TEST DESIGN above; then the FULL suite
   (.venv/bin/python -m pytest tests/ -q -p no:cacheprovider; expect ~177 tests). Baseline:
   the newest driver loop-start note in PROGRESS (2026-10-13: 1 red =
   test_fit_queue placement_gestures) is SUPERSEDED by 307bc's commit note on main (full
   suite 177 passed / 1 skipped / 0 failed, 2026-10-14) - measure the actual baseline at the
   start of the suite session (run the station test + the placement test first, ~2 min) and
   require no NEW reds against that.

PITFALLS candidates (file when you touch those files again; the context limit blocked writing
them this session): (1) the transform=None gate cannot see scale-shaped ground errors of any
measured magnitude (uniform or radial) - the canonical similarity solve absorbs them; only
anchor-offset patterns fail it (med>45 or slope) - Where: pipeline/fit_gate.gate, fit/matchfit
pairs; Symptom: a "15%-scale" fails-gate test case silently passes (accept, med 0.01-7.6). (2)
np.abs(XY - C) with (n,2) rows returns (n,2), not per-row radii - use the complex magnitude
(Z = x+1j*y, RHO = |Z - Z.mean()|); the (n,1)*(n,2) broadcast then silently yields (n,n,2).
(3) tests/golden/hand_fit_docs.sha256 is 22 by:hand docs + 19 data/sites/<id>/site.json, NOT
"22 + 19 by:None docs".
