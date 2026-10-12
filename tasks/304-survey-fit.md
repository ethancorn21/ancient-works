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

(2026-10-12, iteration 89, agent c - session 5. Redesigned the synthetic world, added the
match-quality jitter, fixed two first-run crashes; the suite now runs end to end. UNCOMMITTED
on disk: tests/test_surveyfit.py only - fit/surveyfit.py unchanged this session.)

**State.** Status: in-progress. Last run: `.venv/bin/pytest tests/test_surveyfit.py -x -q`
-> test 1 (fixed rotation theta_d=42) fails `db < 2.0` with 2.958 m (= 0.74 plan-px); tests
2-7 not reached. Everything before that in the run path now works (stub, world, sweep).

**Changes this session (all in tests/test_surveyfit.py):**
1. Zero-centroid guard in `_resolve_theta` (`cents.shape[0] == 0 -> (None, {})`) +
   `__import__("io")` -> top-level `import io` (the session-4 known bug: DONE).
2. NEW CRASH FIXED: scipy 1.18.1 `ndi.center_of_mass(ink, lab, np.arange(1,n+1))` returns a
   LIST OF (cy, cx) TUPLES, not (cy_arr, cx_arr) - `cy, cx = ...` raises "too many values to
   unpack" for n != 2. `_centroids` rewritten: `[(c[1], c[0]) for c in com]`. NOTE: the
   single-mask form `ndi.center_of_mass(m)` (fit/surveyfit.py:344 panel_pieces) still returns
   a (cy, cx) tuple - no change needed there. PITFALLS candidate (scipy 1.18.1).
3. WORLD REDESIGNED (old grid 30+50i x {250,310} was 375 plan-px wide in the 320 frame and
   off-centre: a junk corner sat 9-21 px from true glyphs at theta_d=0/6). New grid: 7 cols
   `120+25*i` x rows {220,250} (25/30 px pitch, centred (195,235)). Verified numerically:
   8 half-box-shift survivors (4 cols <=198 x 2 rows >=202); all 14 glyphs in-frame at
   theta_d in {0,6,42}; min junk gap 35-93 px; sweep deterministic: at sent=theta_d the stub
   resolves the true theta uniquely (14 hits; adjacent 2-deg candidates get only 4); at
   sent=theta_d+/-2 it resolves the SENT value (14 hits), delta 2. Score landscape (JITTER
   _PX_PER_DEG=0.6, per-glyph wobble seeded per (theta,i), JITTER_SEED=304778): delta0 ~0.52
   (14 pairs, amp 0) > delta2 ~0.48 (14 pairs, amp 1.2) >> delta4-15 ~0.15-0.19 (6 pairs) ~
   junk-only ~0.15. So theta_d=0 sweep -> unique max at 0 (358/2 lose to the jitter; fine-0
   duplicate ties and keeps the coarse first); theta_d=6 -> unique max at fine 6.
4. match_response now adds `_jitter(theta, i, delta)` to the plan-side true-pair points.

**Current hypothesis (why db = 2.96 m at theta_d=42):** my 4x-supersample rasterizer biases
EACH disc's measured centroid 0.3-0.7 px (coverage quantisation: 16 ss-cells, threshold 0.3
makes the effective ink boundary asymmetric w.r.t. the sub-pixel centre). Measured per disc
(no JPEG, raw): base 0.44-0.66 px; after 42 deg PIL bicubic: 0.34-0.77 px. The 14 biases
share a common component -> b_r off ~0.7 plan-px -> 2.9 m. An 8x supersample should cut this
to ~0.1 px.

**Next step (session 6):**
(1) Rerun the 8x-supersample experiment (throwaway script; last run crashed at
`cents(imj)[0]` IndexError size 0 - one single-disc case came back with ZERO components
after the JPEG q95 roundtrip: print per point and guard empties before concluding; if a real
7-px disc genuinely vanishes under JPEG q95, enlarge the glyph radii instead - SHEET_R 3.5
-> 5 and let the plan radius derive, keep the pitch).
(2) Bump `_rasterize` from ss=4 to ss=8 (sheet and plan), rerun the suite.
(3) Recalibrate the test tolerances (db<2m, da<0.1 m/px, corners<2m) to ~2x the OBSERVED
worst values and LOG the measured numbers (devlog below).
(4) When green: `.venv/bin/python tests/test_surveyfit.py --emit-fixture` writes
data/surveyfit/fixture_match.json (theta_d=42 ideal world + junk; re-running ransac must
equal it exactly); then write data/surveyfit/devlog.md (world params incl. the new grid,
JUNK_SEED/JITTER_SEED, measured fit/scramble/shifted scores + inlier counts per world,
corner/placement errors, panel_pieces piece count on the synthetic panel, the scipy 1.18
center_of_mass gotcha, raster jitter numbers).
(5) Full suite `.venv/bin/pytest -q` (was 68 passed 1 skipped; mine adds 7).
(6) Real-service smoke (if `curl -sm 5 http://127.0.0.1:8091/health` answers): canary
`fit/surveyfit.py maiden-castle-q1232816 c_c20ff6b1f16d173d --no-null` (lead's 633/31/
20-35-53m = confirmation ONLY, never tune) + barnard-castle-q4185811 / avaricum-q281826;
eyeball corners; log in devlog.
(7) FREEZE (restate frozen config in MY site_flow 304 section + freeze commit hash) ->
fit/surveyfit_heldout.py (mirror fit/inkfit_heldout.py: 21 docs, both similarities in the
doc's size frame, four full-image corners, k0 = aw.ground_scale(lat0), aerial column
camp-d-attila only, checkpoint + pid lock, selfcheck 0.0m/0.0deg/1.0 before the run) ->
THE ONE RUN -> verbatim table + plain verdict (PASS iff a confidence threshold exists:
every accepted within 60m AND >=5 of 21; the threshold = the single authorised post-run
choice) -> pass: task 304b (lowest free number in 800-1099, Depends on: 304, one-module
Touches: wire tools/site_done.py fit step: confident->map, unsure->review with reason);
fail: say so, stop.

**Acceptance boxes:** none ticked yet. Box 1 (method: matching points from images, similarity
through the georeference, confidence) becomes tick-able once tests 1-7 are green + fixture
committed. Boxes 2-3 need the real one run.

**Never:** read the 21's stored hand pairs during development (evaluator only); tune any
parameter from the lead's smoke numbers or the held-out run; edit docs/site_flow.md outside
my 304 section (agent a owns 305's parts); change the 302b golden/hand docs; bind fixed
network ports in tests (the stub uses port 0); write outside the project + temp dir.

**Re-read:** tests/test_surveyfit.py:match_response + _jitter - confirm the jitter is seeded
per (theta, i) only (a repeated call at the same theta must return IDENTICAL points - the
sweep's first-max tie-break and the duplicate-payload test depend on it); and _take's bands
(<=3 all / <=15 first 6 / else none) still match the docstring after the grid change.
