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

(2026-10-12, iteration 87, agent c - session 3. Re-read verification of fit/surveyfit.py
v0 + one fidelity fix, committed. No tests yet.)

**State.** Status: in-progress. fit/surveyfit.py v0 is COMMITTED (driver commit 3b4c2b2
after session 2; my session-3 fix is this session's commit). The import check was clean.
The MATCHER IS LIVE and re-confirmed this session: `curl -sm 5
http://127.0.0.1:8091/health` -> {"model": "zju-community/matchanything_eloftr",
"device": "NVIDIA GeForce RTX 5060 Ti"}. Pre-registration stands (docs/site_flow.md, my
304 section - agent a also edits that file: only ever touch my 304 section). Suite green
this session: 68 passed, 1 skipped.

**Re-read verification (session 3, all three items - now CLOSED):**
1. Sign convention passes, NO flip: propose._anchor_pairs is z = (m/k)·e^{iθ}·(w−wc)+zc,
   θ = north_angle_deg (positive = arrow deg CLOCKWISE of page-up). A visual (on-screen
   CCW) rotation by φ multiplies the w = x−i y frame by +e^{iφ} (up (0,−1) → left (−1,0)
   at 90°); PIL rotate(+deg) is visual CCW. So rotate_image(panel, +θ) north-up's a plan
   whose arrow is θ, and the composition a_s·a_r·e^{iθ}·fs equals the anchor form.
   rotated_panel_map's R = [[c, s], [−s, c]] is the correct visual-CCW matrix (x right,
   y down). THE SYNTHETIC TEST MUST STILL LOCK THIS (fit(rot=+θ) on a plan drawn with its
   north θ deg CW of page-up must recover the true placement).
2. composite_placement frame separation passes: (a, b) fit on the four FULL-FRAME
   (size-frame) corners; reported corners = the CROP box (size units; _panel_crop:
   map_box fractions × size, or (0,0,w,h) for full-frame docs) through that same
   similarity; the 3-stage composition is an exact similarity so the fit is valid at the
   crop corners. fit()'s size = row.size or [panel.width, panel.height] matches
   inkfit._size_frame.
3. Null phase passes: both null _match_theta calls pass the UNROTATED panel (real or
   scrambled) + the chosen theta; rotation applied inside, same as the fit phase.

**Bug found + fixed (this session's commit):** panel_pieces kept every autowalls keep
label, but the 302b reference inkfit.template_pieces drops labels with zero of
extract's 1-in-step sampled points (deterministic seed-0 subsample, step=2); a kept-but-
unsampled label would consume (th, dx, dy) draws from the single seeded RNG and shift
every later piece's transform in the scrambled null. Fixed: select labels through the
sampled points, exactly as template_pieces does. Verified: identical (idx, length)
piece lists and first scramble draw on a synthetic panel; scramble_image valid (white
bg, ink present); ransac recovers a planted exact similarity (|Δa| ~1e-16);
sheet_similarity gives |a| = 10 / 0 deg for a known 10-merc-m/px sheet.

**Data availability (session 2, unchanged):** all 22 page images on disk; all 19
held-out sites have their sheets (depictions.json + webp). Panel rule: book docs with a
map_box -> crop; 12 commons docs (incl. doc 21, DPLA 1280x889) -> full image (the
doc-21-full-image deviation, recorded in the pre-registration).

**Next step (session 4) - write tests/test_surveyfit.py (hermetic), in this order:**
1. Stub HTTP server on 127.0.0.1, **port 0** (the OS picks a free port; NEVER a fixed
   port - other agents' checkouts run tests at the same time). Endpoints: /health (200
   with a JSON body, or 500 for test (e)); /match (POST, JSON body: image0/image1 base64
   PNG, threshold, max_side). The handler decodes both PNGs and builds the response:
   the SYNTHETIC WORLD is a 400x400 sheet with ~14 feature glyphs (circles/arcs/lines
   drawn at known sheet-px positions) and a 320x320 plan = the same glyphs under a known
   transform T (scale, rotation, translation; plus a few junk glyphs in the plan that
   have no sheet counterpart, for outlier rejection). The handler finds which glyphs
   appear in both sent images (by pixel proximity of glyph centres after undoing the
   panel's rotation) and returns their keypoints (in the ORIGINAL pixel frames) +
   scores + junk pairs; to simulate the matcher's orientation sensitivity for the sweep
   test, degrade the returned pairs when the sent panel is visibly rotated (e.g. a
   few junk pairs instead of the true ones).
2. Synthetic ground truth: a site (lon, lat) with its sheet corners from
   aw.site_bbox/aw.corners at a known size_m; the sheet's a_s, b_s come from
   surveyfit.sheet_similarity itself; the plan's true placement = a known similarity
   z = a_true·w + b_true expressed via a True (a, b) built independently of the module
   (e.g. a_true = (plan_m_px/k0)·e^{iθ_true} with k0 = aw.ground_scale(lat)).
3. The five tests: (a) recovery of the known transform through the reported corners
   (corner error vs the independently composed (a, b) < ~1 m; the ROTATED variant -
   plan drawn with north θ deg CW, fit(rot=+θ) - must recover the SAME true placement:
   this locks the sign convention); (b) scramble null score < fit score; (c)
   shifted-sheet null score < fit score; (d) recorded-run reproducibility: generate
   data/surveyfit/fixture_match.json ONCE (commit it) from the module's own ransac +
   score output on a fixed synthetic /match response, and assert exact reproduction
   (the test_gate pattern); (e) /health 500 -> result["reason"] starts with
   "matcher unavailable", no exception.
4. Run `.venv/bin/pytest tests/test_surveyfit.py -x -q` until green; create
   data/surveyfit/devlog.md and log the dev facts (world params, glyph count, junk
   count, any breakage hit).

**After the tests (sessions 5+), in order:** real-service smoke (matcher is LIVE):
`.venv/bin/python fit/surveyfit.py maiden-castle-q1232816 c_c20ff6b1f16d173d
--no-null` (the lead's canary doc: 633 matches / 31 inliers / 20-35-53 m at the 3 hand
points; reproducing it is canary confirmation ONLY - never tune from it) AND
non-held-out barnard-castle-q4185811 / avaricum-q281826; eyeball the placement's panel
corners against the site lon/lat (they should sit on the site); log in devlog.md.
Then FREEZE (restate in MY site_flow 304 section the exact frozen config as of the
code + the freeze commit hash: constants, score formula, confidence formula, sweep
grid, panel rule, doc-21-full-image deviation, SEED; commit = THE FREEZE COMMIT; no
parameter change after without amending that section). Then fit/surveyfit_heldout.py
(mirror fit/inkfit_heldout.py: 21 doc ids from tests/golden/hand_fit_docs.sha256 +
MAIDEN; precheck golden sha256/no-auto/site+row-resolve; per-doc measure =
surveyfit.fit + hand_similarity (the ONLY reader of the stored pairs) +
corner_metrics, both similarities in the doc's size frame, four full-image corners,
k0 = aw.ground_scale(lat0); rows: corner error m, drot deg, scale ratio, objective
{fit, scramble, shifted}, null, margin, confidence, sheet used, aerial column for
camp-d-attila only (kinds=("aerial",)); "no sheet" rows if any (none expected);
checkpoint data/surveyfit/heldout/results.json per doc; pid lock; one re-run only on an
exception; run/table/selfcheck subcommands; selfcheck must give 0.0 m / 0.0 deg / 1.0
for all 21 BEFORE the run - it reads hand fits: allowed for the evaluator, never the
method). Then THE ONE RUN: re-check /health; `.venv/bin/python
fit/surveyfit_heldout.py run`; paste the table verbatim into my site_flow section +
the verdict plainly (PASS iff a confidence threshold exists under which every
accepted fit is within 60 m AND >=5 of 21 accepted; the threshold choice is the single
authorised post-run choice, as in 302b). Pass -> create task 304b (next free number in
800-1099, with `Depends on: 304` and a one-module `Touches:` line: wire into
tools/site_done.py's fit step: confident -> map, unsure -> review with the reason).
Fail -> say so in the section, stop: no wiring, no fourth method.

**Never:** read the 21's stored hand pairs during development (evaluator only); tune
any parameter from the lead's held-out smoke numbers or from the run (after the run
the ONLY authorised choice is the confidence threshold); edit docs/site_flow.md
outside my 304 section; change the 302b golden file or the hand docs; bind fixed
network ports in tests.

**Re-read (new):** fit/surveyfit.py:_sweep - before the stub test, note the fine grid
wraps (best=0 -> fine values 348..12 via `round(th % 360, 1)`); a fine theta can equal
a coarse theta (0), so the stub may see the same image sent twice - assert at most
30 + 13 calls, never exactly 43; and check the dedup is within the fine list only.
