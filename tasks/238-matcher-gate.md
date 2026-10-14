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

(2026-10-14, iteration 205, agent a - step 4 done: docs/gate.md section 10 appended (pure append,
boxes 1-3 ticked); next session = step 5, write tests/test_matchfit_gate.py and run the full suite)

STATE: steps 1-4 of the 201 plan DONE, boxes 1-3 ticked. (1) _settle extraction (acbd056).
(2) The gate feature (69470fe): _settle runs the frozen 001 gate (batch_us.gate_placement on the
doc's own pairs, transform=None - no claimed placement, the gate solves the canonical similarity)
between judge and write; a refusal becomes the candidate's refusal (the gate's clause verbatim,
the existing why print/entry path, no document); an accept writes the doc with score = the gate's
median and the matcher block gains "resid_m": round(raw matcher residual, 1); run() takes an
optional results list ({site, plan, outcome written|refused|dry, path, why, kind} per candidate).
(3) The 302f station fixture refresh (8af2d91) - branch suite green again.
(4) This session: docs/gate.md section 10 "The matcher's fit as a gate input (238, 2026-10-14)"
appended (pure append, +45 lines; sections 1-9 byte-identical; no threshold/rule change - the
section-1 registration stands). The section: the input (up-to-8 spread-selected inlier pairs,
transform=None = the section-4 "true" case and the batch's own convention; doc score = the gate's
median, badbury 0.0; resid_m = the raw matcher residual); the two refusal stages (judge:
weak/rotated/near-line consensus; gate: large median residual, radial gradient, degeneracy);
the section-7 restatement (a consistent global error passes, uniform 15% scale included -
measured; the review queue and the 18/20 sample are the backstops).
REMAINING: step 5 ONLY - tests/test_matchfit_gate.py (TEST DESIGN below) + the FULL suite
(box 5: no NEW reds against the newest driver loop-start note in PROGRESS.md - 307bc, 2026-10-14:
177 passed / 1 skipped / 0 failed; measure the actual baseline at session start). If green:
tick boxes 4-5 and set Status: done.

MEASURED (iteration 205, throwaway offline script; reproducible from the fixture's 8 pairs in
records.json header.confident doc.pairs - perturb in Mercator about the centroid of the 8 ground
points, then re-round to 1 dp u/v + 7 dp lon/lat as batch_us._norm_pairs does):
- as-recorded, transform=None: ACCEPT med 0.009029976684642005, slope_o 4.371e-05, io 8.427e-04 -> doc score 0.0.
- uniform 1.15x scale about centroid: ACCEPT med 0.0124 (score 0.0).
- radial (non-uniform) 15% / 50% at the edge (factor 1 + f*rho/rho_max): ACCEPT med 2.274
  (slope_o 0.0093, io −0.67) / 7.593 (slope_o 0.0247, io −2.25) -> scores 2.3 / 7.6.
  (With transform=None the gate cannot see a scale-shaped error at any measured magnitude -
  docs section 10 states this.)
- ALL 8 anchors offset ±200 m E, alternating in spread order: REJECT med 96.8075 (why "median
  residual 96.80754... m > 45.0 m"; slope_o 0.437, io +18.6) - agrees with 201's 96.80919
  (normalized pairs) / 203's 96.81302 (raw pairs pre-normalization) to <0.01 m. The hand-over's
  earlier "4 of 8" phrasing was loose: 4-of-8 variants measure 48.4-60.3 (also med-clause rejects);
  all-8-alternating is the construction that pins 96.8.

TEST DESIGN (tests/test_matchfit_gate.py, decided 201, confirmed 203, refined 205; write into its docstring):
- Idiom: the recorder's OFFLINE replay - rec._fake_match(fixture["responses"]) (NOT the whole
  fixture - PITFALLS fit/) + patching mf.reachable -> False (no RoMa). Import the recorder like
  test_matchfit_station.py does (importlib spec_from_file_location; rec.SID/PLAN/DOCID; its
  build_tree(tmp, delete_hand_doc=True) builds the badbury tmp tree - site, plan row, grounds).
  No network at all (never touches a socket - stronger than the ephemeral-port stub, say so in
  the docstring), no subprocess, no fixed ports, nothing written outside the tmp trees.
- Candidate 1 (passes both): the recorded badbury ELoFTR answer through mf.run(tree, [SID],
  results=[...]) -> doc written; doc["score"] == round(fit_gate.gate(doc["pairs"], None)[1]["med"], 1)
  recomputed IN the test (0.0); doc["matcher"] = the 7 old keys + resid_m 3.1; results entry
  {outcome "written", path, why None, kind "eloftr"}; the FIT stdout line (capture stdout around
  the in-process run) byte-identical to the FIT line in records.json header.confident
  expected_stdout (the "FIT (eloftr) 22/61 ..." line - extract it from the fixture, don't hard-code).
- Candidate 2 (passes judge / fails gate): SYNTHETIC (labelled synthetic in the docstring; the
  recorded fixture is untouched): wrap mf.fit_row and perturb the RETURNED pairs' ground points
  (lon/lat) - all 8, ±200 m E alternating in spread order, Mercator about their centroid, re-round
  as _norm_pairs - then run as candidate 1. Assert: no doc file; results entry {outcome "refused",
  path None, why == the gate's clause}; byte-compare why against a fresh
  batch_us.gate_placement(perturbed pairs normalized, None) recomputation in the test; the printed
  line contains that clause and the "[six-inch-1st.webp x0.35, rot 4]" bracket. Do NOT assert any
  review item (the upsert belongs to the site_done line, not a bare run). The perturbation cannot
  change the judge's verdict: in fit_row every judge input (inliers, rot, spread, resid_m) is
  computed from the /match response + RANSAC on image px BEFORE pairs is assembled, and the judge
  runs on best inside fit_row (verified 205, removed the re-read item).
- Candidate 3 (hermeticity): sha256 every data/db/platefits/*.json and data/review/*.json of the
  CHECKOUT before the runs and assert byte-identical after (rec._checkout_surface/_hash_surface
  idiom or a plain {path: sha256} dict; covers the 49 matcher docs + the 22 golden hand docs;
  all runs happen in the tmp trees). Also assert the checkout's web/data/sites/ is untouched.
- Candidate 4 (backs docs section 10's limit statement): the 8 doc pairs scaled 1.15x uniformly
  about their centroid (Mercator) PASS the gate: fit_gate.gate(pairs, None) == ACCEPT, med ~0.012
  (recompute in-test; do not hard-code the float beyond a tolerance).
- Expected runtime: a few seconds (pure in-process replay).
- After writing: run the new test, then the FULL suite (.venv/bin/python -m pytest tests/ -q
  -p no:cacheprovider). Box 5 = no NEW reds against the 307bc baseline (the driver's loop-start
  note in PROGRESS.md may list known reds - compare against it, not against a green ideal).

PITFALLS relevant here (all filed under fit/; search PITFALLS.md): _fake_match takes
fixture["responses"]; np.abs on an (n,2) point array is per-element - use the complex magnitude
(and (n,1)*(n,2) broadcasts to (n,n,2)); hand_fit_docs.sha256 = 22 by:hand docs + 19
data/sites/<id>/site.json (the store is 71 = 22 hand + 49 agent + 0 unmarked, so the golden does
NOT cover the matcher docs - candidate 3's own snapshot does).

