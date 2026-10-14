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

(2026-10-14, iteration 204, agent a - step 3 done: the 302f fixture is refreshed for the gate and
the station test is green again; next session = step 4, append docs/gate.md section 10)

STATE: steps 1-3 of the 201 plan are DONE. (1) _settle extraction (acbd056). (2) The gate feature
(69470fe): _settle runs the frozen 001 gate (batch_us.gate_placement on the doc's own pairs,
transform=None - no claimed placement, the gate solves the canonical similarity) between judge and
write; a refusal becomes the candidate's refusal (the gate's clause verbatim, the existing why
print/entry path, no document); an accept writes the doc with score = the gate's median and the
matcher block gains "resid_m": round(raw matcher residual, 1). (3) This session: the 302f station
fixture refresh - records.json header.confident records the post-gate values (doc score 0.0;
matcher block + "resid_m": 3.1 after rot_deg; expected_stdout lines 6/9 "gate 3.1 m" -> "gate 0.0
m"; depiction source "(gate score 3.1 m)" -> "(gate score 0.0 m)"), plus one header "refreshed"
provenance line (mechanical 238 refresh by deterministic offline replay, NOT a live re-recording:
the 15 /match responses, the unsure fixture and every input hash are untouched);
test_matchfit_station.py's matcher key-set assertion gained "resid_m". Station test: 2 passed,
55.58 s (it had been 1 failed / 1 passed on the branch since the feature commit). The task's
"Proposed changes" (driver may 238 to touch 239's two declared files) resolved as option (a): both
paths are in 238's Touches line.

RE-READ (for the test session): fit/matchfit.py:fit_row - the synthetic fails-gate case wraps
fit_row and perturbs the RETURNED pairs' ground points (lon/lat); verify the judge's inputs
(inliers, rot, spread from image px; resid_m vs the raw matched keypoints) are all computed before
pairs are assembled, so the perturbation cannot change the judge's verdict (203 measurement: it
doesn't - 22 inliers, rot 3.62, spread (0.138, 125.3) all come from the /match response + RANSAC on
image px; the gate is the only thing that sees the corrupted lon/lat).

MEASURED (iteration 204, throwaway /tmp/aw238_verify.py - offline replay via
rec._fake_match(fixture["responses"]) + mf.reachable=False, tmp tree; the station test then
re-verified the whole subprocess flow):
- doc score 0.0 == round(fit_gate.gate(doc pairs, None) med 0.009029976684642005, 1); slope_o
  4.37e-05, io 8.4e-04 -> accept; matcher block = the 7 old keys + "resid_m": 3.1; doc pairs and
  the FIT stdout line byte-identical to the fixture's recorded values; results entry
  {outcome written, path, why None, kind eloftr}.
- The only fixture deltas were those four value groups (score, matcher, two "gate X m" lines,
  depiction source); the "within 1 m" ceil is unchanged; the header's input_hashes record repo
  inputs only (site dir, pages, jsonl rows - fit/matchfit.py is NOT among them), so the test's
  _drift check is unaffected by the 238 code change (confirmed by the passing run).

PITFALLS still to file in the test session: (2) np.abs((n,2)-(n,2)) is per-element, not per-row
radii (use the complex magnitude; the (n,1)*(n,2) broadcast silently yields (n,n,2)); (3)
tests/golden/hand_fit_docs.sha256 = 22 by:hand docs + 19 data/sites/<id>/site.json, not "22 + 19
by:None docs". Already filed (203): (1) the transform=None gate cannot see scale-shaped ground
errors of any measured magnitude (uniform 1.15x med 0.0104; radial 15%/50% med 2.27/7.59 - all
ACCEPT; only anchor-offset patterns fail it); (4) rec._fake_match takes fixture["responses"], not
the whole fixture.

NEXT STEPS (one per session, in order):
4. (docs) append docs/gate.md "## 10. The matcher's fit as a gate input (238, 2026-10-14)" per
   step 4 of the 201 plan: input (up to 8 spread-selected matcher inliers; transform=None - the
   gate solves the canonical similarity, the batch's own "true" case of section 4); the two
   refusal stages (judge: weak/rotation/near-line consensus; gate: the doc's own internal
   consistency - large median residual, radial gradient, degeneracy); the section-7 restatement
   measured 201/203: with transform=None a CONSISTENT global error passes, including a uniform
   15% scale (re-solves to med ~ 0) - the matcher's scale errors are visible to the gate only in
   radial/non-uniform or mutually-inconsistent form; the review queue and the human's 18/20
   sample remain the scale backstop. No threshold/rule change anywhere else in the file. Re-read
   docs/gate.md sections 1, 2, 4, 7 and 9 before writing (prep note item 7).
5. (test) tests/test_matchfit_gate.py per the TEST DESIGN below; then the FULL suite
   (.venv/bin/python -m pytest tests/ -q -p no:cacheprovider; the 307bc note on main says
   177 passed / 1 skipped / 0 failed, 2026-10-14 - measure the actual baseline at the start of
   that session and require no NEW reds).

TEST DESIGN (tests/test_matchfit_gate.py, decided 201, confirmed 203; write into its docstring):
- Idiom: the recorder's _fake_match OFFLINE replay (tests/fixtures/matchfit_station/record.py -
  pass fixture["responses"], NOT the whole fixture; PITFALLS filed) + mf.reachable -> False
  (no RoMa). Trees via rec.build_tree(tmp, delete_hand_doc=True). No network at all, no
  subprocess.
- Candidate 1 (passes both): the recorded badbury ELoFTR answer through mf.run (results kwarg)
  -> doc written; doc["score"] == round(fit_gate.gate(doc["pairs"], None)[1]["med"], 1)
  recomputed IN the test (expected 0.0); matcher block = the 7 old keys + resid_m 3.1;
  results entry {outcome written, path, why None, kind eloftr}; the FIT stdout line
  byte-identical to records.json header.confident expected_stdout's FIT line.
- Candidate 2 (passes judge / fails gate): SYNTHETIC per the 203 measurement (wrap fit_row,
  perturb the returned pairs' ground points, 4 of 8 +-200 m E in Mercator, alternating in
  spread order; labelled synthetic in the docstring; the recorded fixture is untouched).
  Assert: no doc; results entry {outcome refused, why == the gate's clause, byte-compared
  against a fresh batch_us.gate_placement recomputation on the same corrupted pairs}; the
  printed line contains the clause + the "[ground x window, rot N]" bracket. Do NOT assert
  any review item (the upsert belongs to the site_done line, not a bare run).
- Candidate 3 (hermeticity): sha256 snapshot of every data/db/platefits/*.json and
  data/review/*.json of the CHECKOUT (rec._checkout_surface/_hash_surface) before and after
  the runs - byte-identical (covers the 49 matcher docs + the 22 golden hand docs; the runs
  happen only in the tmp trees).
- Candidate 4 (cheap, backs docs sec 10's limit statement): the 8 doc pairs scaled 1.15x
  uniformly about their centroid (Mercator) PASS the gate (accept, med ~ 0.0104) - the
  section-7 limit applied to the matcher.
- Expected runtime: a few seconds (pure in-process replay).

