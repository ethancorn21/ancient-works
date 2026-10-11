Status: open
# 203a: The batch, US - the 90 US built sites
Depends on: 001, 200, 201, 202
Touches: fit/batch_us.py, data/db/platefits/, data/review/, docs/batch_us.md, tests/test_batch_us.py, tests/golden/hand_fit_docs.sha256

## Goal
GOAL.md point 2: the local model does the fitting itself, the way the 25 hand fits were made. For
every US built site in web/data/sites.json (region "US", 90 of 384): candidates = the plans.json
rows whose "sites" contains the site (with 200's evidence field where present). For each candidate
picture: build the fitkit sheet (`tools/fitkit.py sheet` - the picture's crop next to the site's
ground, relief or the aerial photograph where there is no LiDAR, both gridded) and let the local
vision model (`pipeline/llm.py`) read the grid labels, find the same features on both sides (wall
corners, gate gaps, bastion tips, road junctions, church footprints, river crossings), and record at
least four point pairs (202's seed is its starting point where one exists; a
code/north/centre-only placement is never the fit). The pairs go through the existing `plan_fit`
similarity solver and then the gate (001): accepted fits become automatic platefit documents in
data/db/platefits/ with the gate's score and an "auto" mark; a gate refusal, or a picture the model
could not fit (fewer than four pairs), becomes a review item in data/review/ in 201's format
carrying those pairs; a site with no candidate at all gets an item marked "no picture found"
(point 1: fit or item). The 20 existing hand-fit documents are never touched. 203b (the rest of
the world) reuses this module's loop.

## Acceptance criteria
- [x] Before the first batch write: tests/golden/hand_fit_docs.sha256 is committed, listing all
      20 pre-batch platefit documents (file name + sha256) and the 19 hand-fit sites'
      data/sites/<id>/site.json files.
- [x] fit/batch_us.py runs the loop for a set of US sites: for each site, every candidate picture
      goes fitkit sheet -> model (>= 4 matched-feature pairs, 202's seed as starting point) -> fit
      -> gate; the accepted ones write automatic platefit documents (existing format + score +
      "auto" mark) and the rest become review items (the model's pairs where it made any); a site
      with no candidate at all gets an item marked "no picture found". The loop is a function 203b
      can import and point at its own site list, with the model step injectable.
- [ ] In the full working-phase run (all 90 US sites, recorded in the report), every US site
      ends with at least one automatic document or an open review item - or an existing hand
      fit.
- [ ] After the run the 20 hand-fit documents and the 19 site files are byte-identical to the
      golden hashes; the batch added files, it rewrote none.
- [ ] docs/batch_us.md: counts (automatic fit / review item / already hand-fitted / no picture
      found), the recorded seed, and the seeded sample of automatically accepted fits (20 where
      there are at least 20; a page URL each) for the human's 18/20 check.
- [x] Test (no network, port 0, no model-server call): the loop run on a fixed sample of US sites
      with in-repo ground, the model step supplied a fixed recorded answer, produces, per site, a
      document or an item in the right format; the hand-fit files are byte-identical; the report's
      sample is reproducible from the recorded seed.

## Notes
- Ground: the in-repo images (web/data/sites/<id>/) carry the test fits (fitkit convention:
  relief where there is, aerial otherwise). The full run uses the same convention per site;
  fetches happen only in the working phase, never in tests.
- The page-facing sync (overlays, drawings counts) is NOT this task's job: the documents sit
  in data/db/platefits/ and 212 syncs them to the page in one pass.
- The golden hashes cover the pre-batch state of THIS checkout; regenerate them if the batch
  has already been partially run, but never edit them to make a failure pass.
- The model call is injectable by design: the working phase calls `pipeline/llm.py` on the fitkit
  sheet; tests supply a fixed recorded answer so no test touches the model server (GOAL: what the
  model says is a lead to check, not a fact — the gate is the check).

## Hand-over
Session 4d (2026-10-11, iteration 39). Step done: the two pending 4c code items are in fit/batch_us.py
(the task's only code file; the rest of the checkout is untouched):
1. SCALE CROSS-CHECK BUG FIX: `implied = abs(a) * k` (was `abs(float(a)) * k`): `a` from
   plan_fit.similarity is COMPLEX (scale + rotation); float() drops the imaginary part, so for a
   rotated fit implied = |s*cos(theta)|*k. Measured on a real hand fit (mound-bottom) rotated 60
   deg: old 0.5243 vs true 1.0597 m/px - a 2.02x ratio that would misfire "not trusted" on a TRUE
   answer; the fix gives exactly 1.000. NaN guard unchanged.
2. FEATURE-PRESENCE CHECK `_feature_present(site, pts_ll, gpath)` (the 4c decision, now code;
   after _parse_answer): grayscale of the site's own ground image (PIL "L"/255); each answer
   ground point scored by the std of a 24 m box (R=12 px at 1 m/px; centre clamped to
   [R, W-R-1]; inverse of _ground_lonlat through site corners + aw.to_merc); null = 400 boxes at
   np.random.default_rng(20261011) (distinct from the report SEED 20261010); pass iff >= half the
   points score >= the null median; ANY read failure -> (True, None) (no evidence never blocks a
   fit). Wired into the llm_model closure after the scale cross-check, when len(pairs) >= 4: on
   failure the note "only %d%% of the recorded points sit on more textured ground than a typical
   region of this site: the features are not visible where claimed - not trusted" is appended and
   pairs trimmed to 3 (the <4 branch routes the picture to the review item). Module + llm_model
   docstrings document the check, its deliberate faint-feature over-refusal, and the known
   residual (a fabrication anchored on strong texture - road network, field boundaries - passes
   it and the scale check; docs/gate.md section 7's human 18/20 sample remains the backstop).
Verified (offline): _feature_present reproduces 4c's calibration on the recorded 4c points -
tremper 1/4 -> (False, 0.25); pyramid 3/4 -> (True, 0.75); hand-fit over-refusals serpent 0/3,
mayburgh 1/3, little-solsbury 2/5 (deliberate strict-gate cost; the pairs still ride to the item).
tests/test_batch_us.py 5/5 (recorded answers bypass llm_model by design) and the full suite 34/34
in .venv.
Pilot re-run (tunnel re-verified UP on 8080/8081; /tmp/pilot_llm.py; raw answers now
/tmp/llm_raw_4c.txt - this run overwrote 4c's; the answers were IDENTICAL to 4c, the model is
deterministic at this temperature):
- tremper c_75950f29c23bf033 -> could-not-fit ITEM carrying the new note (25% of points) - the
  FIFTH fabrication class (correct scale, wrong translation, points on structureless ground) is
  now handled.
- pyramid-mound n0134_1 -> AUTO DOC (gate med 24 m; the real fit, unchanged).
- poverty-point -> honest 0 pairs -> item; serpent n0636_1 -> range-validate drops the diagonal
  ladder to 1 pair -> item; cahokia -> scale cross-check (stated 1.639 vs implied 3.333) trims to
  3 -> item. Exactly the expected routing, no regression.
State of this checkout: boxes 1, 2, 6 ticked; 3, 4, 5 pending the working run. data/db/platefits/
still exactly the 20 pre-batch docs (tests/golden/hand_fit_docs.sha256 intact); data/review/ has
the alligator-effigy + bibracte items; docs/batch_us.md does not exist yet. data/raw is a symlink
to the shared store /home/agent/projects/ancient-works/data/raw: all 58 candidate images are
already local (37 book pages under books/<ia>/full/, 21 commons thumbs under commons/<site>/), and
all 18 candidate sites have web/data/sites/<id>/relief.jpg, so fitkit.ground returns the relief
and the full run needs no fetches at all - its only network is the LLM tunnel. fitkit sheets go
to $FITKIT_OUT (default /tmp): outside the checkout, safe for the parallel team checkouts.
NEXT (session 4e, its own), the full run:
1. Re-verify the tunnel (127.0.0.1:8080 and :8081 both vLLM qwen3.8-27b; the harness env has
   LLM_URL=http://127.0.0.1:8081).
2. Run: `AW_LLM_URL=http://127.0.0.1:8081/v1/chat/completions .venv/bin/python
   fit/batch_us.py --working` (18 sites, 58 candidates, ~10-40 min - use a long bash timeout,
   say 3600 s; it prints the per-site counts and writes docs/batch_us.md itself).
3. Verify: `sha256sum -c tests/golden/hand_fit_docs.sha256` -> all 39 lines OK (20 docs + 19
   site.json) -> tick box 4; the report's error bucket empty and the four counts sum to 90 ->
   tick box 3.
4. Read docs/batch_us.md (counts, seed 20261010, the 20-or-fewer sample with page URLs) -> tick
   box 5.
5. Commit: `git add -A && git commit -m "203a: the full US batch run - <a> automatic / <b> review
   items / <c> already hand-fitted / <d> no picture found; all 90 US sites covered"`.
   The alligator-effigy item file is MERGED by the upsert (201's one-item-per-site rule) and its
   hash is deliberately NOT in the golden - do not regenerate the golden to make a failure pass.
EXPECT A LOW AUTO-DOC RATE (box 3 is fit OR ready item; the human's drag and the report's 18/20
sample are the authority and the backstop). Do NOT loosen the gate or the counterweights to
raise the auto rate. For 203b (later; imports run_sites/write_report, does not rewrite them):
site list = region != "US" plus the 6 region-less sites (they must not be skipped); keep the
site.json["plate"]["fit"] branch of is_pre_fit (R9); report docs/batch_eu.md; shared SEED
20261010; note for 203b: the feature-presence check is US-relief-oriented - aerial photos are
textured everywhere, so it degrades to a no-op there (acceptable: the gate and the human sample
remain).
