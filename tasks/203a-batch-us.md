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
Session 4c (2026-10-11, iteration 38). Step done: the A/B pilot of the 4b `llm_model` on the 5
4a-fabrication candidates (tunnel re-verified UP: qwen3.8-27b on 127.0.0.1:8080 AND :8081; run with
AW_LLM_URL=http://127.0.0.1:8081/v1/chat/completions). Result: 3 of 5 route to items exactly as
designed (poverty-point: honest 0-pair answer; serpent n0636_1: diagonal ladder dropped to 1 pair
by the range validate; cahokia: corner answer, stated 1.639 vs implied 3.333 -> cross-check trimmed
to 3). TWO auto-passed and were eyeballed (overlay: model points red, seed-mapped same features
green; throwaway scripts /tmp/pilot_llm.py, /tmp/eyecheck.py, /tmp/quant.py, /tmp/calibrate{,2,3}.py
still on disk; sheets /tmp/fit_*.jpg, overlays /tmp/eye_*.jpg; raw answers /tmp/llm_raw_4c.txt):
- pyramid-mound n0134_1 (stated 0.57 vs seed 0.8806, gate med 24 m): model+seed points coincide
  (24-320 m, inside the 460 m box span) ON the visible C-embankment and square-mound pit -> a REAL
  fit; the auto doc is right.
- tremper c_75950f29c23bf033 (stated 1.3245 = the seed scale ECHOED verbatim, gate med 0.6 m): model
  and seed points 120 m apart (inside that seed's 500 m no-map_box uncertainty - seed agreement alone
  cannot discriminate) and BOTH on featureless ground; the site's real ring is unused; 2 of the 4
  points on the modern highway -> a docs/gate.md section-7 consistent global error (correct scale,
  wrong translation) that the gate, the range validate and the scale cross-check all miss. The
current code would write a garbage auto doc, so the full run needs one more batch-side
counterweight before it runs.
DECIDED (calibrated on all 20 hand fits + the 2 model answers, /tmp/calibrate3.py margin grid,
local std R=12 px box vs same-image fixed-seed null): a FEATURE-PRESENCE check in the llm_model
closure (routing-only; the gate stays frozen): count model points whose local std of the site's own
ground image (fitkit.ground, grayscale, 1 m/px) at a 24 m box is >= the median of a 400-point
null (seed 20261011, distinct from the report SEED 20261010); the answer passes only if >= half
the points are above. Numbers: tremper 1/4 above -> reject (0.27-0.65x on every variant tried);
pyramid 3/4 -> pass (1.00-1.57x); hand fits over-refuse only serpent 0/3, mayburgh 1/3,
little-solsbury 2/5 - genuinely faint features, a deliberate strict-gate cost (the pairs still ride
to the item as leads). The edge-distance variant was tested and dropped: it passes all hand fits
but lets tremper through (its highway points are near edges). KNOWN residual (document in the
docstring): a fabrication anchored on strong ground texture (road network, field boundaries) passes
this check AND the scale check; docs/gate.md section 7's human 18/20 sample remains the backstop.
The check only ever routes to review - it never loosens the gate.
BUG FOUND (fix pending): the 4b scale cross-check does `implied = abs(float(a)) * k` but `a` from
plan_fit.similarity is COMPLEX (pipeline/plan_fit.py L35-45); float(a) drops the imaginary part, so
for a ROTATED fit implied = |s*cos(theta)| (60 deg -> 50% low) and can misfire "not trusted" on a
true answer. Fix: `implied = abs(a) * k`. fit/batch_us.py is UNMODIFIED this session (everything
above is /tmp throwaway; no checkout file touched, no tests run; last state: tests/test_batch_us.py
5/5, full suite 34/34, after 4b's commit bff2b3e).
NEXT (session 4d), in order, all in fit/batch_us.py (the task's only code file):
1. Fix the scale cross-check to `implied = abs(a) * k` (keep the NaN guard as is).
2. Add `_feature_present(site, pts_ll, gpath)` after `_parse_answer`: grayscale array of the ground
   image (PIL convert("L") /255); R=12 box std per point (px clamped to [R, W-R-1], inverse of
   _ground_lonlat through site corners + aw.to_merc); null = 400 boxes at np default_rng(20261011);
   med = null median -> return (frac >= 0.5, frac); ANY read failure -> (True, None) (no evidence
   never blocks a fit; the gate and the human are still downstream).
3. In the `llm_model` closure, after the scale cross-check, when len(pairs) >= 4: ok, frac =
   _feature_present(site, [(p[2], p[3]) for p in pairs], fitkit.ground(site["id"])); if not ok:
   append note "only %d%% of the recorded points sit on more textured ground than a typical region
   of this site: the features are not visible where claimed - not trusted" and trim pairs, feats
   to 3 (run_sites' <4 branch routes it to the item, like the scale branch).
4. Docstrings: module (third batch-side counterweight + the road-texture residual, section-7
   backstop) and llm_model (4c finding: correct-scale wrong-translation fabrications caught here;
   faint-feature over-refusal is deliberate). Keep the header comment one sentence (CODEMAP).
5. Re-run /tmp/pilot_llm.py: expect tremper -> could-not-fit item with the new note, pyramid still
   AUTO, the other three unchanged.
6. .venv/bin/python -m pytest -q (expect 5/5 + 34/34; tests bypass llm_model by design).
THEN (session 4e, its own): full run `AW_LLM_URL=http://127.0.0.1:8081/v1/chat/completions
.venv/bin/python fit/batch_us.py --working` (58 candidates, 10-40 min, long timeout; re-verify the
tunnel first; all 58 images local, all 18 sites have relief.jpg, sheets in /tmp) -> verify
`sha256sum -c tests/golden/hand_fit_docs.sha256` (39 OK -> box 4) and the report's error bucket
empty with counts summing to 90 (box 3) -> tick boxes 3/4/5 -> commit docs + items +
docs/batch_us.md (the alligator-effigy item is MERGED by the upsert; its file is NOT in the
golden). EXPECT a LOW auto-doc rate (box 3 is fit OR ready item; the human's drag is the authority,
the report's 18/20 sample the backstop). Do NOT weaken the gate or the tests to raise the auto
rate. For 203b (later): import run_sites/write_report; site list = region != "US" plus the 6
region-less sites (keep the site.json["plate"]["fit"] branch of is_pre_fit, R9); report
docs/batch_eu.md; shared SEED 20261010; the feature-presence check is US-relief-oriented (aerial
photos are textured everywhere, so it degrades to a no-op there - acceptable, note it for 203b).

State of this checkout: boxes 1, 2, 6 ticked; 3, 4, 5 pending the working run. data/db/platefits/
still exactly the 20 pre-batch docs; data/review/ has the alligator + bibracte items.
