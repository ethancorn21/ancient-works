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

(2026-10-12, iteration 88, agent c - session 4. Wrote tests/test_surveyfit.py (complete,
7 tests + fixture emitter) - NOT YET RUN. Matcher was live at session start. The file is
uncommitted on disk (harness kept it); commit it with the first green state.)

**State.** Status: in-progress. fit/surveyfit.py v0 committed (ee36213 + driver 3b4c2b2).
NEW this session: tests/test_surveyfit.py - hermetic stub-server suite (port 0, OS-
assigned), 7 tests: (1) fixed-rotation recovery θ_d=42 (sign-convention lock), (2) sweep
θ_d=0 (wrap: best coarse 0 -> fine 348..12; asserts 30<=calls<=43 and >=2 duplicate
payloads), (3) sweep refinement θ_d=6 (final theta in {4,6,8}, not a multiple of 12),
(4) scramble null < fit, (5) shifted-sheet null < fit, (6) fixture pin
(data/surveyfit/fixture_match.json - NOT YET GENERATED), (7) /health 500 ->
"matcher unavailable". Suite has NEVER been run: expect first-run friction (below).

**Sign convention - VERIFIED BY CODE this session (closes the session-3 re-read item's
last "must still lock"):** PIL rotate(+90) sends marker (90,50) -> (50,10) (right->up =
visual CCW); rotated_panel_map(90) agrees (matrix R=[[c,s],[-s,c]] IS visual CCW in
x-right/y-down); a visual CCW rotation by φ sends a point's w = x - i y coordinate to
e^{+iφ}·w (checked numerically for both basis vectors - my earlier hand derivation of
e^{-iφ} was an arithmetic slip, the module is right). COROLLARY (derived, untested in
code): the true pairs must satisfy a_r = (a_true/a_s)·e^{-iθ_sent} and the module's
composition a_s·a_r·e^{iθ} then gives a_total = a_true for ANY θ_sent - rotation is
absorbed by the fit, so the sweep discriminates only through the matcher's match
quality (which the stub simulates via its degradation rule).

**Stub design (in the test file):** world = 400x400 sheet (corners = real aw.corners of
a 2000m box at (2.0,50.0); a_s exactly real ~7.7786) with 14 glyph discs (7x2 grid
x=30+50i, y in {250,310}; the 8 with x<=199 survive the half-box shift to (x+200,
y-200)) + 320x320 plan = the same glyphs under z = a_true·w + b_true (a_true =
(M_PX/k0)e^{iθ_d}, M_PX=4.0, b_true centres the plan on the site) + 4 junk glyphs at
the corners (>=25px from true ones; rigid rotation keeps them unmatchable) + 12 junk
pairs seed 304777. Handler: sheet classified by 3x3 ink windows at original/shifted
centres (real >=12 orig; shifted == all 8 survivors); plan rotation resolved from
connected-component centroids vs 180 candidates (multiples of 2deg), hit window 2.0px,
oriented iff >=8 of 14 hit (blob radii 4.375px; plan-centre radii 43-200px make 2deg
discrimination binary); degradation by |wrap180(θ_sent-θ_d)|: <=3 all survivors,
<=15 first 6, else none. Expected score order: 14-true ~0.53 > 6-true ~0.30 > junk-
only ~0.19; shifted null ~0.34 < fit. Tolerances as written: corners <2m, |db| <2m,
|da| <0.1 m/px - recalibrate to observed values (est. jitter 0.2-0.5px from JPEG q95 +
bicubic + 4x supersample) and log the measured numbers.

**Next step (session 5):** (1) KNOWN BUG TO FIX FIRST: _resolve_theta crashes on a
zero-centroid image (ndi.label n=0 -> cents shape (0,2) -> d.min(axis=0) ValueError):
guard `if cents.shape[0] == 0: return None, {}` - reachable if the scrambled panel has
no ink after autowalls.extract. Also tidy `__import__("io").BytesIO` in the handler to
a top-level `import io`. (2) `.venv/bin/pytest tests/test_surveyfit.py -x -q`. Likely
friction, in order of probability: junk-only RANSAC model scoring above the 6-true
level (~0.30) - change JUNK_SEED (304778, 304779...) until junk-only < 6-true <
14-true; tolerance recalibration (tighten if observed corner errors << 2m); scramble
image coincidentally oriented (deterministic - see it in the logs, adjust world
layout). (3) When green: `.venv/bin/python tests/test_surveyfit.py --emit-fixture`
writes data/surveyfit/fixture_match.json (ideal true pairs of the θ_d=42 world + junk;
full-precision floats; re-running ransac must equal it exactly). (4) Write
data/surveyfit/devlog.md: world params, JUNK_SEED, measured fit/scramble/shifted
scores + inlier counts per world, corner errors, panel_pieces piece count on the
synthetic panel, breakage hit. (5) Full suite `.venv/bin/pytest -q` (was 68 passed, 1
skipped; mine adds 7). (6) Re-check `curl -sm 5 http://127.0.0.1:8091/health` for the
real-service smoke (next session): canary `fit/surveyfit.py maiden-castle-q1232816
c_c20ff6b1f16d173d --no-null` (lead's numbers 633/31/20-35-53m = confirmation ONLY,
never tune) + barnard-castle-q4185811 / avaricum-q281826 non-held-out; eyeball corners
on site; log in devlog. (7) Then FREEZE (restate frozen config in MY site_flow 304
section + freeze commit hash) -> fit/surveyfit_heldout.py (mirror fit/inkfit_heldout.py:
21 docs, both similarities in the doc's size frame, four full-image corners, k0 =
aw.ground_scale(lat0), aerial column camp-d-attila only, checkpoint + pid lock,
selfcheck 0.0m/0.0deg/1.0 before the run) -> THE ONE RUN -> verbatim table + plain
verdict (PASS iff a confidence threshold exists: every accepted within 60m AND >=5 of
21; threshold = the single authorised post-run choice) -> pass: task 304b (lowest free
number in 800-1099, Depends on: 304, one-module Touches: wire tools/site_done.py fit
step: confident->map, unsure->review with reason); fail: say so, stop.

**Acceptance boxes:** none ticked yet. Box 1 (method: matching points from images,
similarity through the georeference, confidence) becomes tick-able once tests 1-5 are
green. Boxes 2-3 need the real run.

**Never:** read the 21's stored hand pairs during development (evaluator only); tune
any parameter from the lead's smoke numbers or the held-out run; edit docs/site_flow.md
outside my 304 section (agent a owns 305's parts); change the 302b golden/hand docs;
bind fixed network ports in tests; write outside the project + temp dir.

**Re-read (new):** tests/test_surveyfit.py:match_response + _resolve_theta - confirm
the sheet-state thresholds (real >=12 of 14, shifted == all 8) are right for the
webp-decoded sheet (lossy edges: a 7px disc through 3x3 window); and test 3's final
theta assumption (argmax keeps the FIRST max: coarse 0, then first fine 0.54-level is
4) - if observed theta differs, check the degradation band edges (<=3 / <=15) and the
junk-only score, not the assertion.
