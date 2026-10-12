Status: in-progress
# 304: Fit a drawing against the old survey map, not the ground - the third try at an automatic fit
Depends on: 302b
Touches: fit/surveyfit.py, fit/surveyfit_heldout.py, data/surveyfit/, tests/test_surveyfit.py, docs/site_flow.md, requirements.in, requirements.txt

## Goal
Two automatic fits have failed: the vision model invents its points (301), and drawing ink against LiDAR relief lands
231-2204 m off on the 21 hand fits (302b, data/inkfit/heldout/results.json). The owner (2026-10-11) chose to try
once more while he fits by hand (305). The idea: many sites already have an old survey map placed on the ground
(the OS six-inch 1st edition, Cassini, the Etat-major: kind "map" in the site's depictions.json, already
georeferenced). A survey map and an antiquarian plan are both ink drawings of the same banks and ditches, often from
the same decades, so matching drawing to drawing should be far easier than drawing to relief. Fit the plan to the
survey sheet, then carry the sheet's georeference over.

## Acceptance criteria
- [ ] fit/surveyfit.py: matching points found between the plan and the site's survey sheet from the images
      themselves (features, line structure, any method you choose, GPU optional if a free card is given to you;
      not a model's list of coordinates), a similarity fit through the sheet's georeference, and a confidence score.
- [ ] The 302b protocol, unchanged in spirit: pre-registered in docs/site_flow.md before the one run, the 21 hand
      fits as truth, held out, a search-matched null, one table (corner error m, rotation, scale, confidence) -
      reported as it comes out. Hand fits whose site has no survey sheet are listed as "no sheet", not dropped.
- [ ] The verdict, written plainly next to the table: the method passes only if a confidence threshold exists under
      which every accepted fit is within 60 m of the hand fit and at least 5 of the 21 are accepted. If it passes,
      write 304b (wire it into tools/site_done.py's fit step, confident -> map, unsure -> review with the reason).
      If it fails, say so, and stop: no wiring, no fourth method.

## Notes
- The hand fits and their golden file stay untouched. 302c and 302d are dropped (the ink fit failed its test).
- Do not take any other task; the lead gives the next one.

## Hand-over

(2026-10-12, iteration 90, agent c - session 6. Killed the centroid-bias problem at its root:
8x supersampling DISPROVEN (the bias is a threshold-edge effect; 8x is worse), the stub now
models a good sub-pixel matcher (keypoints at expected positions + +-0.25 px wobble + 0.6 px/deg
jitter; centroids kept for detection only), fixed a real ndi.shift rank bug in the null path,
tightened tolerances to ~2x observed, fixture committed. Suite 7/7, full suite 75 passed 1
skipped. The REAL ELoFTR service now answers at 127.0.0.1:8091.)

**State.** Status: in-progress. All 7 stub tests green:
`.venv/bin/pytest tests/test_surveyfit.py -q` -> 7 passed; full suite 75 passed, 1 skipped.
Observed placement errors (all far inside the new asserts db<1.3 / da<0.006 / corners<1.6):
theta_d=42 rot=42: db 0.624 m, da 0.00273, corners 0.797; theta_d=0 sweep: 0.461 / 0.00137 /
0.460; theta_d=6 sweep: theta recovered exactly 6.0, 0.466 / 0.00230 / 0.597; null run:
fit 0.5278 vs null 0.3923 (margin 0.1355, confidence 0.0715). Fixture
data/surveyfit/fixture_match.json committed (north-42 ideal world: 26 pairs, 14 inliers,
rms 3.6e-12, score 0.538462).

**Changes this session:**
1. tests/test_surveyfit.py: NEW `_wobble(theta, i)` (deterministic +-WOBBLE_PX=0.25 px per
   (theta, i), seed stream separate from `_jitter`); `match_response` now returns plan-side
   keypoints at `_expected(theta, plan_centers)[i]` (the module's own visual-rotation matrix)
   + wobble + angular jitter instead of the measured blob centroid - `matched` still gates
   WHICH glyphs are detected (the sent-image geometry still drives detection, the _take bands,
   the junk set and the response format are all unchanged). Module docstring updated to say
   so. Tolerances tightened to ~2x the observed worst (db 1.3, da 0.006, corners 1.6).
2. fit/surveyfit.py: REAL BUG FIXED - `shift_sheet_image`'s `ndi.shift` got a 2-element shift
   for the RGB (rank-3) sheet image -> "RuntimeError: sequence argument must have length
equal to input rank" on the FIRST null run ever (tests 1-3 use null=False, so it had never
   executed). Now a 3-element shift (0.0 on the channel axis).
3. PITFALLS.md: new `### scipy (1.18.1)` subsection (center_of_mass label-index form returns a
   list of (cy, cx) tuples - the session-5 candidate; ndi.shift shift-sequence rank match) and
   a fit/ entry on the digital-disc centroid bias (0.3-0.8 px, no supersample fixes it, 8x is
   worse; blob centroids = detection only, never sub-pixel truth).
4. The 8x supersample plan (session-5 next step 1-2) is ABANDONED on the evidence in
   DECISIONS.md; `_rasterize` stays at ss=4.

**Acceptance boxes:** still none ticked. Box 1 (method: matching points from the images,
similarity through the georeference, confidence) is tick-able once the NEXT step (the
real-service smoke) proves the pipeline on a real site; the stub suite already proves it
against the API contract. Boxes 2-3 need the one run.

**Next step (session 7):**
(1) REAL-SERVICE SMOKE (the service is UP now: /health -> zju-community/matchanything_eloftr
    on the RTX 5060 Ti): canary `.venv/bin/python fit/surveyfit.py maiden-castle-q1232816
    c_c20ff6b1f16d173d --no-null` (expect a match; the lead's 633 matches / 31 inliers /
    20-35-53 m at the 3 hand points are confirmation ONLY - NEVER tune from them), then
    barnard-castle-q4185811 and avaricum-q281826 (same, --no-null first). Eyeball the reported
    panel corners vs the sheet (they should land on the plan's own ground features). Watch for:
    first real-sheet load (load_sheet), scale-prior band from the catalog (maiden has a scale
    bar? if a band is active it constrains |a| - the note lines say), rotation (prior or
    sweep), runtime (~1 s per match call warm).
(2) Write data/surveyfit/devlog.md (hand-over step 4): the world (400 px sheet, 2 km box at
    (2,50), 7x2 grid pitch 25/30 centred (195,235), SHEET_R 3.5, M_PX 4, JUNK_SEED 304777,
    JITTER_SEED 304778, JITTER 0.6 px/deg, WOBBLE 0.25, HIT_PX 2, ORIENTED_MIN 8), the measured
    fit/null scores + inlier counts per world (numbers above), the per-disc bias table
    (0.33-0.88 px, ss4 vs ss8 vs radius, JPEG/rotation contribution ~0.05 px), corner/placement
    errors, the two scipy 1.18 gotchas, the fixture pin. (It is referenced by the test header,
    docs/site_flow.md:304 and the devlog line the freeze section will cite.)
(3) FREEZE: restate the frozen config in MY section of docs/site_flow.md ("The one-shot
    held-out measurement..." - match params threshold 0.2 / max_side 832, RANSAC 400 iters /
    8 px / min 3 inliers / s_band 1.5, sweep 12 deg coarse + 2 deg fine +-1 coarse step, nulls
    = 302b scramble (SEED 20261012) + half-box sheet shift, score = inlier fraction / (1 +
    rms/8), confidence = score * margin) + the FREEZE COMMIT HASH; commit; the config is
    FROZEN from that commit.
(4) fit/surveyfit_heldout.py (mirror fit/inkfit_heldout.py: the 21 docs from the 302b list,
    both similarities in the doc's size frame, four full-image corners, k0 = aw.ground_scale,
    aerial column camp-d-attila only, per-doc checkpoint to data/surveyfit/heldout/results.json
    + pid lock, selfcheck 0.0 m / 0.0 deg / 1.0 on the synthetic tree before the real run).
(5) THE ONE RUN, then the verbatim table (corner error m, rotation, scale, confidence per
    doc; "no sheet" rows for sheetless hand fits) + plain verdict: PASS iff a confidence
    threshold exists under which every accepted fit is within 60 m and >= 5 of 21 accepted
    (the threshold = the single authorised post-run choice) -> pass: write 304b (wire into
    tools/site_done.py's fit step: confident -> map, unsure -> review with the reason); fail:
    say so and stop - no wiring, no fourth method.

**Never:** read the 21's stored hand pairs during development (the evaluator is the only
reader); tune any parameter from the lead's smoke numbers or from the held-out run; edit
docs/site_flow.md outside my 304 section (agent a owns 305's parts); change the 302b
golden/hand docs; bind fixed network ports in tests (the stub uses port 0; the smoke runs
against 8091 from a script, not a test); write outside the project + the temp dir; `git
merge/rebase/reset/stash` outside a merge request.

**Re-read:** tests/test_surveyfit.py:match_response + _wobble + _jitter - confirm (a) both
wobble streams are seeded per (theta, i) only (a repeated call at the same theta must return
IDENTICAL points - the sweep's first-max tie-break and the duplicate-payload test depend on
it), and (b) the `matched` gate still excludes undetected glyphs from the returned pairs
(detected-but-not-in-_take must never be returned); fit/surveyfit.py:shift_sheet_image -
confirm the shift direction is still half-box NORTH (negative row shift) and half-box EAST
(positive column shift) in image coordinates.
