Status: in-progress
# 301: Argentoratum (Strasbourg), finished on the map - the second site through the line
Depends on: 300
Touches: web/data/sites.json, web/data/sites/argentoratum-q2361353/, web/data/sites/stonehenge-q39671/, web/data/review.json, data/review/, docs/site_flow.md, docs/site_flow/, tools/site_done.py, pipeline/plan_fit.py, pipeline/build_site.py, tests/test_site_done.py

## Goal
One site at a time, all the way to the map (owner, 2026-10-11). Stonehenge went through first and left the line
as one command (docs/site_flow.md). Argentoratum is next: the batch left 8 automatic fit documents for it
(data/db/platefits/argentoratum-q2361353.*.json, best gate 8.7 m). Take it all the way with the line, and look at
the result the way a visitor does before calling it done.

## Acceptance criteria
- [ ] `tools/site_done.py argentoratum-q2361353` run; every picture of the site is synced to the map or an open
      review item, and its entry in web/data/sites.json counts the synced drawings.
- [ ] Checked in a browser: each synced drawing opened over the ground. A drawing that is visibly in the wrong place
      (streets/walls of the drawing not on the real ones) goes to the review queue with the reason, even if its gate
      passed: a gate of 0.0 m means the points were not checked, not that the fit is right. Screenshot of the best
      drawing at docs/site_flow/argentoratum.png with one line on what it shows.
- [ ] Anything that broke in the line on this site is fixed in the line (not by hand for this site), with a test,
      and one line under "What broke" in docs/site_flow.md. The full suite passes.

## Notes
- The 20 hand fits and their golden file stay untouched.
- Do not start 207 or any other task: the lead gives the next site when this one is done.

## Hand-over
(iteration 68, agent c - NO code changed this session; the fabrication-pattern check is CALIBRATED
but not yet written into pipeline/plan_fit.py. Tests last run iteration 66: 60 passed, green.
Order unchanged: the line's fix -> run it on Stonehenge -> Argentoratum.)

**The lead's redirect stands (DECISIONS 2026-10-11 301, first two entries):** all 7 Stonehenge auto
docs are fabricated (identity maps / corner-to-corner / diagonal ladders), none sits on the sarsens,
all 13 of the site's candidates end in the review item, the site shows 0 drawings until a human fits
one. The gate passed them by construction (gate.md s.7 blind spot) and stays frozen (test_gate pins
its constants); the fix belongs in the line.

**Calibration done (scratch /tmp/calib.py - re-create if lost; every number below was run, not
guessed, with .venv/bin/python). The PREVIOUS hand-over's tolerances are wrong - do not use them
as-is.** The provisional tolerances (1.5/0.67 gaps, 20 px shared-coordinate grouping, C window
25%/[0.7,1.4]) fire on 6 of the 20 hand fits (the golden reference) - a hard failure of the
validation requirement:
- A (2D lattice): fires hand-fit maiden-castle n0124 (u margins 1.381/0.943, v 1.046/0.954 both
  inside 1.5/0.67).
- B (1D ladder, 20 px grouping): fires castle-rising (v=484 x3, u line [269,696,981], gap margins
  1.199/0.801) and old-sarum c_8192 (u values 614,626,633 = 19 px spread, v line [210,484,768],
  margins 1.018/0.982; and v values 484,491,491, u line [363,614,889], margins 1.046/0.954).
- C (frame-identity alone): fires 4 hand fits that are LEGITIMATE "the drawing covers the site
  box" maps: avebury n0581 (full 3367x5050 frame -> 1000 m box: d=(-22.8,-46.6) m, rx=0.781,
  ry=1.133), bergues c_4bbca7 (rx=1.281, ry=1.234, box 2000), calleva n0360 (rx=1.388, ry=1.172,
  box 1600), camp-d c_6a912845 (d=(274,99.8) m, rx=1.097, ry=0.918, box 1600). Rotation CANNOT
  separate them (tested: old book maps are north-up - calleva 0.21 deg, camp-d 2.30 deg, avebury
  2.41 deg off axis, vs stonehenge fakes at 0.0-1.9 deg). Dead end.

**The real signature: grid-round coordinates.** Fraction of DISTINCT anchor page-px values that
are multiples of 10 (+-0.5): ALL 15 auto docs (7 stonehenge + 8 argentoratum) are >= 0.9 - 14 are
exactly 1.0; stonehenge c_098c is 9/10 (v=648 x3 is its only non-multiple). ALL 20 hand docs are
<= ~0.5 (worst: castle-rising 12 of 24 coordinates; hand pairs carry 1-dp positions like 614.3,
484.7 - the page tool records drag positions, the model reads grid labels). The batch's own pilots
(llm_model docstring, gate.md s.7) document this fabrication class; this check is independent of
the batch's three pre-gate checks (stated-scale cross-check, feature-presence texture, range
clipping).

**Design decision (next agent, ONE of two - then implement `fabrication_pattern(pairs, crop,
size, box)` in pipeline/plan_fit.py as a pure numpy function, no network; box = the site's
ground-metre box from web/data/sites.json corners x aw.ground_scale(lat) - data/sites/<sid>/
site.json has NO corners, the previous hand-over's "box from site.json" was wrong there; both
site entries EXIST in web/data/sites.json now with drawings 0 - the "entry MISSING" caution is
STALE, verified this session):**
- (a) 2D lattice, TIGHTENED: >=3 distinct u AND >=3 distinct v, >=4 anchors, consecutive gaps
  near-arithmetic on both axes with max/median <= 1.3 (NOT 1.5) and min/median >= 0.67. hi=1.3
  excludes maiden (1.381), whitley (1.307), arbor-low (1.316), cahokia (1.335), hembury-v (1.305)
  - margins 0.007-0.08, thin but the docs are golden-pinned; fires c_098c (1.091/0.909 u,
  1.125/0.893 v), c_83b4 (1.048/0.952 u, 1.2/0.8 v), argentoratum c_cd8109 (perfect 1.0/1.0 both).
- (b) 1D ladder, TIGHTENED: >=3 anchors sharing one coordinate with spread <= 2 px (the model's
  ladders are exactly 0: 640,640,640) with near-arithmetic spacing on the other axis
  max/median <= 1.5 AND min/median >= 0.9. Excludes castle-rising (0.801 < 0.9) and old-sarum
  (19 px / 7 px spread > 2); fires c_0226 (u=640, v gaps 400/400 -> 1.0/1.0), c_098c (two groups:
  1.004/0.996 and 1.0/1.0), argentoratum c_0a0173 (v=480, u gaps 400/400). STILL RE-VERIFY all 20
  hand docs against exactly these B params before cutting (only the two named above were checked).
- (c) THE DECISION: grid-roundness as a STANDALONE clause (>=4 anchors and >= 90% of DISTINCT
  anchor coordinates within 0.5 of a multiple of 10) vs the previous hand-over's frame-identity
  PLUS the roundness requirement. Standalone fires on ALL 8 argentoratum docs (all 1.0 round) ->
  the site ends 0 drawings, all 8 wait for the human's drag; it also fires all 7 stonehenge (so
  (c) alone would already satisfy the validation). Frame-identity+round fires only 5 of 8
  argentoratum (c_139946, c_1cb316, c_751f93, c_cd8109, c_0a0173) and leaves c_5bfb04 (gate 0.0
  m, octagon ring), c_6ba6bb (gate 8.7 m - the BEST of the 8) and c_7e281c (40.1 m) to the
  browser check. I viewed composites of c_5bfb04 and c_6ba6bb over relief.jpg (regen recipe in
  the DECISIONS third entry; /tmp/arg_*.png may be wiped): both frames plausibly match the real
  old-town block (the canal ring is visible in the relief) but the 8 anchor rings sit on nothing
  visible - no canal line, no street corner; looks fabricated, less starkly than Stonehenge.
  c_7e281c/c_0a0173/c_cd8109 composites were generated but NOT viewed. My recommendation:
  standalone-round - the strict gate is the project's stated direction (gate.md: "a strict gate
  that over-refuses is fine"), the human's drag is the last word and the pairs ride to the item
  as a lead, and c_6ba6bb's 8.7 m is the weakest kind of evidence the lead already flagged.
  Note all 7 stonehenge docs fire (a) or (b) as well, so the reason string should name which
  clause(s) fired.

**Then, unchanged from the previous hand-over:**
- site_done._sync: run the check BEFORE any download; on a hit skip the build, prune any
  existing overlay (plan_fit.prune), upsert the review candidate (plan/title/url/pairs/
  gate_score/why "line check: fabricated anchor pattern - <which>; the gate's X m measures
  internal consistency of the anchors, not their truth"), include it in the review step and the
  per-picture summary; _entry/_review recompute (stonehenge: drawings 7 -> 0, item 6 -> 13);
  idempotent re-run; then RUN `.venv/bin/python tools/site_done.py stonehenge-q39671` (no
  --model: all 13 candidates covered -> no batch run, no network).
- Docs: correct docs/site_flow.md's Stonehenge paragraph ("its circles and stones sit on the real
  sarsens" is false), replace docs/site_flow/stonehenge.png (shoot the new state with
  server/serve.py + tools/shot.mjs, true one-line caption), add the entry under "What broke".
- Test: extend tests/test_site_done.py's hermetic harness (socket-dead child, tmp copy):
  (i) the check fires on all 7 stonehenge docs and none of the 20 hand docs; (ii) the line run on
  the copied site: exit 0, 0 plan webp (pruned), depictions = the 2 maps, sites.json drawings 0,
  item 13 candidates (7 with the pattern reason), review.json republished, second run
  idempotent. The existing test's goldens pin the OLD (wrong) 7-synced state - rewrite them.
- Then ARGENTORATUM: `.venv/bin/python tools/site_done.py argentoratum-q2361353` - 8 auto docs
  (c_0a0173 19.9, c_139946 25.7, c_1cb316 25.7, c_5bfb04 0.0, c_6ba6bb 8.7, c_751f93 32.4,
  c_7e281c 40.1, c_cd8109 0.0; all similarity, all src commons); whatever passes the check goes
  on the map, the rest to the queue with the reason; browser-check every synced drawing;
  screenshot the best to docs/site_flow/argentoratum.png + one line; add anything that broke in
  the line to "What broke".

**Re-read:**
- Re-read: fit/batch_us.py:llm_model + _parse_answer + _feature_present - confirm the new line
  check is independent of (not a copy of) those three pre-gate checks, and that the 7 docs are
  the ones the pre-gate checks let through (not the 6 in the item).
- Re-read: pipeline/plan_fit.py:prune - exactly what it removes (webp, ink, depiction entry,
  count refresh) so the line's prune path leaves no stale files or stale depiction rows.
- Re-read: tools/site_done.py:_fit - `need_fit` for a site whose docs all pattern-reject (they
  still cover their candidates via pre_docs, so no batch run; confirm the covered count and the
  summary still hold when a doc is both in pre_docs and (newly) in the item).

**Environment:** system python3 has NO numpy - use .venv/bin/python for anything importing
pipeline/ or fit/. The driver's ".venv could not be built" note (2026-10-10, PROGRESS.md) is
STALE: task 800 pinned requirements.txt and the venv builds; the suite ran green (60 passed) at
iteration 66. Do not run git merge/rebase/reset/stash/branch switches. Agent a works on 206 in
its own checkout; 207 waits on the human - neither is yours.

