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

(2026-10-12, iteration 86, agent c - session 2. fit/surveyfit.py v0 BUILT on disk (UNCOMMITTED,
harness-saved); matcher went LIVE mid-session (lead message); no tests written yet, nothing run.)

**State.** Status: in-progress. Pre-registration stands (docs/site_flow.md end section, mine -
agent a also edits that file: only ever touch my 304 section). THE MATCHER IS NOW LIVE:
`curl -sm 5 http://127.0.0.1:8091/health` -> {"model": "zju-community/matchanything_eloftr",
"device": "NVIDIA GeForce RTX 5060 Ti"} (lead confirmed 2026-10-12, mid-session 86).

**On disk now (UNCOMMITTED - read before changing):** fit/surveyfit.py v0, complete but
UNTESTED: MatchClient (POST /match base64 PNG, 30 s timeout + one retry, /health gate;
SurveyFitError = method-level reason), ransac (seeded 2-pair samples, LS refinement, s_band
scale-prior rejection), score = inlier_frac/(1+rms/INLIER_PX), confidence = score*margin floored
0 (PROVISIONAL - restated at the freeze commit), priors() (302b anchor via propose.propose_for:
bar/ratio scale prior only; trustworthy arrow = north_angle_deg a number + north_arrow True +
|deg|<=60, same rule as propose._rotation), 302b nulls (scramble_image = pixel-exact 302b piece
transform over autowalls keep-mask pieces, one rng, seed 20261012, (-length,idx) order;
shift_sheet_image = ndi.shift(-h/2 rows, +w/2 cols) cval 255), sheet_similarity (corners
TL TR BR BL vs pixel-grid corners, rectilinear, Web Mercator) + sheet_m_px,
composite_placement (size frame -> rotated panel px -> sheet px -> merc; 4-point LS, no hand
algebra; full-frame corners for (a,b), crop corners for the reported panel corners), fit()
(panel via inkfit.load_panel - the 302b rule: row map_box or full image; thetas = [rot_fixed]
or [rot] or _sweep 30+13 calls; SurveyFitError caught in the match and null phases -> reason),
CLI (site plan --root --matcher --no-null). Provisional frozen constants at top: MATCHER_URL
127.0.0.1:8091, timeout 30, MATCH_THRESHOLD 0.2, MAX_SIDE 832, SEED 20261012, RANSAC_ITERS 400,
INLIER_PX 8, SCALE_TOL 1.5, SWEEP 12 deg coarse / 2 deg fine, SHIFTS 0.5/0.5, SHEET_FILL 255.

**CRITICAL sign convention (verified against propose._anchor_pairs; do NOT flip):** a visual
(on-screen CCW) rotation by phi of an image multiplies its w = x - i y frame by **+e^{i phi}**.
A drawn plan whose north offset is theta (302b convention: the anchor similarity factor is
e^{i theta}; a north arrow theta deg CLOCKWISE of page-up has theta = +theta) is brought back
north-up by rotating the image by **+theta** (PIL rotate(+theta) = CCW on screen). So
_match_theta does rotate_image(panel, +theta) and rotated_panel_map uses R = [[c, s], [-s, c]].
THE SYNTHETIC TEST MUST LOCK THIS (a rotated synthetic plan recovers the identity placement
when fit(rot=+theta)).

**Doc 21 panel - deviation from the session-1 note (recorded in DECISIONS):** the method does
NOT use the hand doc's crop [165,256,895,663] (that was the lead's smoke-test crop): the
protocol says the method never opens a platefit document, and the 302b-consistent uniform rule
is inkfit.load_panel (row map_box or full image). Doc 21 (DPLA 1280x889) therefore uses the
FULL image as panel. The lead's smoke (633 matches / 31 inliers / 20-35-53 m at the 3 hand
points, held-out doc 21 itself) is feasibility evidence ONLY - no parameter tuned from it.

**Data availability (verified this session - the one run is possible locally once frozen):**
all 22 page images on disk (21 docs' book full/ pages + commons big/ jpgs incl. doc 21's);
ALL 19 held-out sites have their sheets on disk (depictions.json + webp, none missing, no
site without a sheet). Panel rule per doc: 9 book docs have a map_box (panel = recorded crop);
12 commons docs (incl. doc 21) use the full image.

**Next step (session 3) - in order:**
1. Import/syntax-check the uncommitted file: `.venv/bin/python -c "import sys; sys.path
   .insert(0,'fit'); import surveyfit"` (expect small breakages; fix), then COMMIT it:
   "304: fit/surveyfit.py v0 - ELoFTR client + RANSAC similarity + 302b nulls".
2. tests/test_surveyfit.py (hermetic: stub HTTP server on 127.0.0.1 PORT 0 - never a fixed
   port; recorded responses; synthetic world: 400x400 sheet with ~14 feature glyphs, corners
   from aw.site_bbox/aw.corners at a synthetic (lon,lat,size_m) site, 320x320 plan = sheet
   features under a known transform, plus junk pairs for outlier rejection; the stub callback
   decodes the sent images and builds responses - for the sweep, degrade pairs at wrong theta
   to simulate the matcher's orientation sensitivity). Tests: (a) recovery of the known
   transform through the corners (corner error vs an independently composed (a,b) < ~1 m;
   rotated variant locks the sign convention); (b) scramble null < fit score; (c)
   shifted-sheet null < fit score; (d) recorded-run reproducibility against a committed
   fixture (generate data/surveyfit/fixture_match.json once from the module's own ransac +
   score output; test asserts exact reproduction - the test_gate pattern); (e) /health 500 ->
   reason "matcher unavailable", no crash.
3. Run `.venv/bin/pytest tests/test_surveyfit.py -x -q` until green (the suite's pre-existing
   reds are NOT mine: test_batch_eu union, test_gate recorded-measurement, test_serve
   platefits_docs_match_sites). Create data/surveyfit/devlog.md; log dev facts.
4. REAL-SERVICE smoke (matcher is LIVE): `.venv/bin/python fit/surveyfit.py
   maiden-castle-q1232816 c_c20ff6b1f16d173d --no-null` (the lead's canary doc; reproducing
   633/31/20-53 m is allowed ONLY as a canary, never as tuning) AND non-held-out
   barnard-castle-q4185811 / avaricum-q281826; eyeball the placement's panel corners against
   the site lon/lat (they should sit on the site). Log in devlog.md.
5. FREEZE: restate in MY site_flow 304 section the exact frozen config as of the code + the
   freeze commit hash (the constants list, score formula, confidence formula, sweep grid,
   panel rule, doc-21-full-image deviation, SEED). Commit = THE FREEZE COMMIT. No parameter
   change after this without amending that same section (the pre-registration allows amending
   at the freeze and at the run only).
6. fit/surveyfit_heldout.py (mirror fit/inkfit_heldout.py: the 21 doc ids from
   tests/golden/hand_fit_docs.sha256 + MAIDEN; precheck (golden sha256, no auto flag, site +
   row resolve); per-doc measure = surveyfit.fit + hand_similarity (the ONLY reader of the
   stored pairs) + corner_metrics (both similarities in the doc's size frame, four
   full-image corners, k0 = aw.ground_scale(lat0)); rows: corner error m, drot deg, scale
   ratio, objective {fit,scramble,shifted}, null, margin, confidence, sheet used, aerial
   column for camp-d-attila only (kinds=("aerial",)); "no sheet" rows if any (none expected);
   checkpoint data/surveyfit/heldout/results.json per doc, pid lock, one re-run only on an
   exception; `table` and `selfcheck` subcommands - selfcheck must give 0.0 m / 0.0 deg /
   1.0 for all 21 BEFORE the run (it reads hand fits: allowed for the evaluator, never the
   method). Run selfcheck now that data are in place.
7. THE ONE RUN: re-check /health; `.venv/bin/python fit/surveyfit_heldout.py run`. Paste the
   table verbatim into my site_flow section + the verdict plainly: PASS iff a confidence
   threshold exists with every accepted fit within 60 m AND >=5 of 21 accepted (the threshold
   is the pass criterion itself, as in 302b - scan thresholds, report which docs pass at
   each). Pass -> create task 304b (next free number in 800-1099, Depends on: 304, Touches:
   one module: wire into tools/site_done.py's fit step: confident -> map, unsure -> review
   with the reason). Fail -> say so in the section, stop: no wiring, no fourth method.

**Never:** read the 21's stored hand pairs during development (evaluator only); tune any
parameter from the lead's held-out smoke numbers or from the run (the threshold choice is the
single authorised choice, made after the run on the measured table); edit docs/site_flow.md
outside my 304 section; change the 302b golden file or the hand docs.

**Re-read:** fit/surveyfit.py:rotated_panel_map + _match_theta - re-verify the +theta sign
against propose._anchor_pairs before trusting any rotated-panel result; fit/surveyfit.py:
composite_placement - confirm the size-frame vs crop-frame separation; the null phase of
fit() (both _match_theta calls pass the UNROTATED panel + the chosen theta).


