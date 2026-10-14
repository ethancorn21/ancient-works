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

(2026-10-14, iteration 202, agent a - refactor-first step done and committed; branch agent/a,
refactor commit acbd056 on top of the driver sync; next session = the GATE feature commit)

STATE: step 1 of the 201 plan is DONE: fit/matchfit.py's run() now ends each candidate in
`_settle(root, sid, row, r, kind, dry, results)` (extracted, behaviour-identical, proven by the
302f station test before/after: 2 passed, 55.3 s both ways - it pins stdout byte-exact). run()
gained `results=None`; site_done/CLI untouched (grep: site_done.py:83 is the only caller).
Verified the results path by offline replay (rec._fake_match(records["responses"]) - pass the
RESPONSES dict, not the whole fixture, else every /match KeyErrors - and mf.reachable=False):
confident -> {outcome written, path, why None}; unsure -> {outcome refused, why the judge
clause}; dry-on-covered -> nothing (row filtered first). The doc written in that replay is
still the OLD shape (score 3.1, 7-key matcher block): the gate and resid_m land NEXT session.

Re-read: fit/matchfit.py:_settle and run - the gate commit changes exactly the _settle body:
in the ACCEPT branch (after the why-print/continue, before the FIT print) compute
`pairs = batch_us._norm_pairs(r["pairs"])`; `ok, score, why = batch_us.gate_placement(pairs, None)`;
if not ok: print the SAME why-line shape as a judge refusal (`{sid}  {title}: {r['why']}{extra}`
with the "[ground x window, rot N]" extra), record results {outcome refused, path None,
why = the GATE clause} and return None, writing nothing; else print the FIT line unchanged,
`path = batch_us.write_doc(str(root), sid, row, pairs, score)` (normalized pairs, gate score -
write_doc re-normalizes idempotently), and the matcher block gains `"resid_m":
round(r["resid_m"], 1)`. The results entry "why" on gate refusal must be the gate's clause
(the refusal print and the entry both come from the same r). run()'s docstring and the module
docstring's "trust" paragraph get the "passes BOTH the judge and the frozen gate" sentence in
the same commit. The gate runs on the FINAL winner (RoMa when it won) - it does: _settle is
called after run's RoMa pass. Judge-only refusals (the why branch) keep today's exact behaviour.
batch_us.gate_placement IS fit_gate.gate (batch_us.py:126; transform=None -> it solves the
canonical similarity). Do NOT touch the FIT line or the judge branch.

MEASURED (iteration 201, offline replay of 302f's recorded badbury responses; deterministic -
RANSAC seeded, replay reproduces the fixture doc's pairs exactly):
- fit_row: 22 inliers / 61 matches, rot 3.62 deg, resid_m 3.078 (prints "3 m"), spread
  (0.138, 125.3), judge silent. The doc's 8 pairs round to the fixture doc's pairs.
- gate(pairs, None): raw pairs med 7.08e-10; the doc's rounded pairs -> ACCEPT, med
  0.009029976684642005, slope_o 4.37e-05, io 8.4e-04 => new doc score = round(med,1) = **0.0**
  (was 3.1).
- Depiction source line: "...within 1 m (gate score 0.0 m)" (the "within 1 m" = ceil(max
  residual of the doc-pair similarity) = 1, UNCHANGED; source_line keys off
  doc["auto"]/doc["score"]).
- 302f fixture delta when the gate lands (records.json header.confident): doc.score 3.1 -> 0.0;
  doc.matcher gains "resid_m": 3.1; depiction.source "(gate score 3.1 m)" -> "(gate score 0.0
  m)"; expected_stdout line 6 "sync ... gate 3.1 m" -> "gate 0.0 m" and line 9 "... synced to
  the map, gate 3.1 m" -> "gate 0.0 m" (site_done prints doc["score"] in both). UNCHANGED:
  lines 0,2,3,4,5,7,8,10 (line 2 "residual 3 m" = raw matcher residual, the FIT line is
  untouched by box 1), site_entry_equal stays True (the sites.json score 1.45 is the HAND
  fit's), spread_pairs, all 15 responses. test_matchfit_station.py: ONE assert changes -
  set(doc["matcher"]) gains "resid_m". The UNSURE fixture (records_unsure.json) is UNTOUCHED:
  its judge refusal (8 inliers) happens before the gate (verified: no score in its 8 stdout
  lines; item why "no model answer").
- SYNTHETIC fails-gate variant (built on the 8 doc pairs, transform=None, judge inputs
  untouched - wrap fit_row so the RETURNED pairs' ground points are perturbed after the real
  fit): 4 of 8 anchors +-200 m E (alternating in spread order) -> REJECT, med
  96.80919025564799, why "median residual 96.80919025564799 m > 45.0 m" (MEDIAN clause - the
  box's example shape). (2 of 8 +200 m E rejects via the SLOPE clause instead, med 32.9.)
  1.15x UNIFORM scale about the centroid -> ACCEPT (med 0.0104) and RADIAL 15%/50% scale ->
  ACCEPT (med 2.27/7.59): with transform=None the canonical similarity solve absorbs EVERY
  scale-shaped distortion measured - a consistent global error re-solves to ~0 (docs/gate.md
  sec 7). The Notes' "15%-scale variant is the natural fails-gate example" is FALSE; the
  offset construction is the test's fails-gate case, and the 1.15x variant is asserted
  PASSING in the same test (backs docs sec 10's limit statement).
- Doc inventory (box 4 hermeticity snapshot): data/db/platefits = 71 JSONs = 49
  fitter:matcher + 22 by:hand (zero by:None); data/review/*.json; tests/golden/
  hand_fit_docs.sha256 = 41 lines = the 22 hand docs + 19 data/sites/<id>/site.json (all
  match on the current tree).

TEST DESIGN (tests/test_matchfit_gate.py, decided 201; write into its docstring):
- Idiom: 302f's ephemeral-port in-process stub (it lives in tests/test_matchfit_station.py -
  _start_stub + the GUARD; tests/conftest.py has NO matcher stub) or the faster recorder
  _fake_match offline replay - pick one and say which (201 leaned stub for no-network parity);
  import rec from tests/fixtures/matchfit_station/record.py as that test does; trees via
  rec.build_tree(tmp, delete_hand_doc=True); mf.reachable -> False (no RoMa here).
- Candidate 1 (passes both): recorded badbury answer through mf.run -> doc written; assert
  doc["score"] == round(fit_gate.gate(doc["pairs"], None)[1]["med"], 1) recomputed IN THE TEST
  (expected 0.0); matcher block = 7 old keys + resid_m 3.1; results entry {outcome written,
  why None}; the FIT stdout line byte-identical ("...residual 3 m").
- Candidate 2 (passes judge / fails gate): SYNTHETIC per the offset4 construction above
  (label synthetic in the docstring; the recorded fixture is not modified). Assert: no doc
  file; results entry {outcome refused, why == the gate's clause verbatim} (byte-compare
  against a fresh fit_gate/batch_us.gate_placement recomputation on the same corrupted pairs);
  the printed line contains the clause + the "[ground x window, rot N]" extra. Do NOT assert
  any review item (the upsert belongs to the site_done line, not a bare run).
- Candidate 3 (hermeticity): sha256 snapshot of every data/db/platefits/*.json and
  data/review/*.json of the CHECKOUT before the runs, byte-identical after
  (rec._checkout_surface/_hash_surface idiom); runs happen only in tmp trees.
- Also assert (cheap, backs docs sec 10): the 1.15x-scaled-anchors variant of the 8 doc pairs
  PASSES the gate (accept, med 0.0104) - the section-7 limit, applied to the matcher.

NEXT STEPS (one per session, in order):
1. DONE (iteration 202): the _settle extraction, committed alone (acbd056).
2. (feature) the gate in _settle exactly as described in Re-read above; commit.
3. (fixture refresh - 239's declared files, cleared by the task's Proposed changes section)
   records.json header.confident: doc.score 0.0, doc.matcher + "resid_m": 3.1,
   depiction.source "(gate score 0.0 m)", expected_stdout lines 6 and 9 "gate 0.0 m";
   test_matchfit_station.py: matcher-key set + "resid_m". Commit; re-run the 302f test green.
4. (docs) append docs/gate.md "## 10. The matcher's fit as a gate input (238, 2026-10-14)":
   input (pairs = up to 8 spread-selected matcher inliers; transform=None, the gate solves the
   canonical similarity - the batch's own "true" case of section 4); the two refusal stages
   (judge: weak/rotation/near-line consensus; gate: the doc's own internal consistency - large
   median residual, residual gradient, degeneracy); the section-7 restatement measured 201:
   with transform=None a CONSISTENT global error passes, including a uniformly 15%-scaled
   answer (the gate re-solves it, med ~ 0) - section 9's scale15 rows were caught as CLAIMED
   placements against recorded anchors; the matcher's scale errors are visible to the gate
   only in radial/non-uniform or mutually-inconsistent form; the review queue and the human's
   18/20 sample remain the scale backstop. No threshold/rule change anywhere else in the file.
5. (test) tests/test_matchfit_gate.py per the TEST DESIGN; then the FULL suite
   (.venv/bin/python -m pytest tests/ -q -p no:cacheprovider; expect ~177 tests). Baseline:
   the newest driver loop-start note in PROGRESS (2026-10-13: 1 red = test_fit_queue
   placement_gestures) is SUPERSEDED by 307bc's commit note on main (full suite 177 passed /
   1 skipped / 0 failed, 2026-10-14) - measure the actual baseline at the start of the suite
   session (run the station test + the placement test first, ~2 min) and require no NEW reds.

PITFALLS candidates (file when you touch those files again; not filed yet):
(1) the transform=None gate cannot see scale-shaped ground errors of any measured magnitude
(uniform or radial) - the canonical similarity solve absorbs them; only anchor-offset
patterns fail it (med>45 or slope) - Where: pipeline/fit_gate.gate, fit/matchfit pairs;
Symptom: a "15%-scale" fails-gate test case silently passes (accept, med 0.01-7.6).
(2) np.abs(XY - C) with (n,2) rows returns (n,2), not per-row radii - use the complex
magnitude (Z = x+1j*y, RHO = |Z - Z.mean()|); the (n,1)*(n,2) broadcast then silently yields
(n,n,2). (3) tests/golden/hand_fit_docs.sha256 is 22 by:hand docs + 19 data/sites/<id>/
site.json, NOT "22 + 19 by:None docs". (4) rec._fake_match takes fixture["responses"], not
the whole fixture - Symptom: "matcher error on <ground> x<f>: '<sha256>'" on every window
and "the matcher found nothing consistent".
