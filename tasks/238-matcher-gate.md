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

(2026-10-14, iteration 203, agent a - the gate feature commit is done and committed; branch
agent/a, on top of the driver sync; next session = step 3, the 302f fixture refresh)

STATE: steps 1-2 of the 201 plan are DONE. _settle now runs the frozen 001 gate between the
judge and the write: `accepted, score, gate_why = batch_us.gate_placement(batch_us._norm_pairs(r["pairs"]), None)`
(= fit_gate.gate, transform=None: no claimed placement, the gate solves the canonical
similarity - the batch's own convention). On refusal r = dict(r, why=gate_why) and the EXISTING
refusal print/entry path handles it (one path for judge and gate; the printed line carries the
bracket "[ground x window, rot N]"); no document is written. On accept write_doc gets the
normalized pairs and the gate score, and the matcher block gains "resid_m": round(resid_m, 1).
Docstrings (module trust + final paragraphs, run, _settle) state the passes-both contract. The
dry path is unchanged (returns after the FIT print, before the write).

Re-read: fit/matchfit.py:_settle - the gate block sits after the RoMa resolution and before the
refusal branch; `score` is only referenced in the write_doc call, which is only reached after an
accept. If you touch this again: judge-only refusals must keep today's exact behaviour (they do:
the gate block is skipped when "why" is in r).

MEASURED (iteration 203, throwaway /tmp/aw238_feat.py - 23/23 checks, offline replay of 302f's
recorded responses via rec._fake_match(fixture["responses"]), mf.reachable=False, tmp trees,
checkout surface hash-identical around the runs):
- Confident badbury: doc written; score 0.0 == the gate med 0.009029976684642005 over the doc's
  pairs recomputed in-test; matcher block = the 7 old keys + "resid_m": 3.1; doc pairs
  byte-identical to the fixture's recorded pairs; results entry {outcome written, path, why
  None, kind eloftr}; the FIT stdout line byte-identical to the fixture's ("...residual 3 m" -
  the raw matcher residual, untouched).
- SYNTHETIC fails-gate (judge inputs untouched: wrap fit_row so the RETURNED pairs' ground
  points are perturbed - 4 of 8 anchors +-200 m E in Mercator, alternating in spread order):
  no doc; results entry {outcome refused, why = the gate's clause, byte-compared against a
  fresh batch_us.gate_placement recomputation}; printed line "median residual
  96.81302368864387 m > 45.0 m [six-inch-1st.webp x0.35, rot 4]" (the med differs from 201's
  96.80919... because this perturbs the RAW pairs pre-normalization - 7-dp lat rounding; the
  test byte-compares against the recomputation, so either construction works).
- Unsure fixture: unchanged (the judge refusal happens before the gate; the bare-run line is
  byte-identical to the fixture's recorded line). Dry on the uncovered site: the gate passes,
  the FIT line prints, outcome "dry", nothing written.
- 302f station test (RED on the branch until the refresh - measured the FULL delta by driving
  the test's own _preconditions/_start_stub/_run): stdout differs only on lines 6 and 9 ("gate
  3.1 m" -> "gate 0.0 m"); the doc differs on score 3.1 -> 0.0 and matcher + resid_m 3.1 (all
  other keys incl. the 8 pairs identical); the plan depiction differs only in source
  ("(gate score 3.1 m)" -> "(gate score 0.0 m)"; the "within 1 m" ceil is unchanged); the site
  entry, the review page, all 15 /match responses and the checkout surface are byte-identical.
  The unsure station test still passes.
- Grep: no code outside the station fixture reads a doc's "matcher" block, so resid_m breaks no
  reader; the 49 existing matcher docs are untouched (write_doc never rewrites).

PITFALLS filed this session: (1) the transform=None gate cannot see scale-shaped ground errors
of any measured magnitude (uniform 1.15x med 0.0104; radial 15%/50% med 2.27/7.59 - all
ACCEPT; only anchor-offset patterns fail it); (4) rec._fake_match takes fixture["responses"],
not the whole fixture. Still to file in the test session: (2) np.abs((n,2)-(n,2)) is
per-element, not per-row radii (use the complex magnitude; the (n,1)*(n,2) broadcast silently
yields (n,n,2)); (3) tests/golden/hand_fit_docs.sha256 = 22 by:hand docs + 19
data/sites/<id>/site.json, not "22 + 19 by:None docs".

NEXT STEPS (one per session, in order):
1. DONE (202): the _settle extraction (acbd056).
2. DONE (203): the gate feature commit (this session).
3. (fixture refresh - 239's declared files, cleared by the task's Proposed changes section)
   records.json header.confident: doc.score 0.0; doc.matcher + "resid_m": 3.1;
   depiction.source "(gate score 0.0 m)"; expected_stdout lines 6 and 9 -> "gate 0.0 m".
   test_matchfit_station.py: the matcher-key-set assertion gains "resid_m". Re-run the station
   test green, commit.
4. (docs) append docs/gate.md "## 10. The matcher's fit as a gate input (238, 2026-10-14)" per
   step 4 of the 201 hand-over: input (up to 8 spread-selected matcher inliers; transform=None -
   the gate solves the canonical similarity, the batch's own "true" case of section 4); the two
   refusal stages (judge: weak/rotation/near-line consensus; gate: the doc's own internal
   consistency - large median residual, radial gradient, degeneracy); the section-7 restatement
   measured 201/203: with transform=None a CONSISTENT global error passes, including a uniform
   15% scale (re-solves to med ~ 0) - the matcher's scale errors are visible to the gate only in
   radial/non-uniform or mutually-inconsistent form; the review queue and the human's 18/20
   sample remain the scale backstop. No threshold/rule change anywhere else in the file.
   Re-read docs/gate.md sections 1, 2, 4, 7 and 9 before writing (prep note item 7).
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
