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

(2026-10-12, iteration 85, agent c - FIRST session on 304. Investigation + pre-registration; no code yet.)

**State.** Status: in-progress. The one-shot run is PRE-REGISTERED in docs/site_flow.md
(section "The one-shot held-out measurement of the survey-sheet fit (task 304...)", appended
at the file's end - agent a also edits this file, so keep future edits to my section only):
matcher = the lead's MatchAnything-ELoFTR service (zju-community/matchanything_eloftr,
Apache-2.0) on the 5060 Ti, `http://127.0.0.1:8091` (POST /match {image0, image1 base64,
threshold 0.2, max_side 832} -> keypoints in original px frames + scores; GET /health;
tunnel down at session end, waiting on the owner's one command): the plan panel (the
doc's crop on the page image, image0) against the site's finest-scale sheet (.webp + its
corners, image1); scale prior from the recorded scale bar (8/21), else the matcher's
scale; rotation prior from a trustworthy north arrow, else a frozen sweep; georeference
carried through the sheet's corners; null = 302b scramble of the panel + 302b half-box
shift of the sheet; verdict = a confidence threshold exists with every accepted fit within
60 m and >=5 of 21 accepted (pass -> 304b, fail -> stop, no fourth method). The 21 docs
are the 302b list, unchanged. The lead's own smoke test on held-out doc 14 (Maiden Castle
DPLA plan vs six-inch-1st): 633 matches / 0.9 s / 31 RANSAC inliers (8 px) / rot 0.0 deg
/ 20-35-53 m at the 3 hand points - evidence of feasibility, NOT a tuning target.
No GPU request was needed: the 5060 Ti runs the matcher, vLLM/clef untouched.

**Investigation facts (verified on this machine 2026-10-12):**
- All 19 held-out sites have a sheet with coverage=1.0, corners, _ink.webp: 15 OS six-inch
  (1:10,560, the finest) + 1-inch; bergues + camp-d-attila Cassini + Etat-major; aztalan
  (topo_1891_62500), cahokia (topo_1888_62500), mound-bottom (topo_1930_62500),
  serpent-mound (topo_1915_48000). camp-d-attila alone has an aerial (fr_ortho1950.webp,
  corners, no ink) - that is the second column.
- Plan panels: 20/21 have web/data/sites/<site>/plan_<id>.webp (+_ink) on disk. Doc 21
  (maiden-castle-q1232816.c_c20ff6b1f16d173d, the DPLA 1806 plan) has NO plan webp - crop
  [165,256,895,663] of its big picture data/raw/commons/big/c_c20ff6b1f16d173d.jpg
  (1280x889) is the panel. Book docs: page data/raw/books/<ia>/full/<file>, size frame +
  crop (avebury: 3367x5050, crop [700,1000,3150,3700]).
- 302b seed records (data/inkfit/heldout/results.json): 8/21 scale-bar docs, 12/21 commons
  coarse anchors (no scale), 1 scale text with unrecorded ppi. So ~13 docs need the matcher
  to supply scale. Catalog size_m/diameter_m are None for these sites.
- Dev sites (sheet + plan, NOT among the 21): avaricum-q281826, barnard-castle-q4185811,
  ... (27 sheet+plan sites built, 19 of them held-out).
- This VM: 6 cores, 15 GB, no GPU (virtual VGA only); the matcher runs remotely on the
  5060 Ti, so no new Python packages are needed (client = requests + numpy, both already
  pinned; no requirements change this session). .venv is rebuilt from the hashed
  requirements.txt before every test run - if a package IS ever needed, pin it with
  hashes in requirements.in first (it is on the Touches line).
- Pre-existing red tests at loop start (not mine): test_batch_eu union tests, test_gate
  recorded-measurement, test_serve platefits_docs_match_sites. My test will be
  tests/test_surveyfit.py (new file, on the Touches line).

**Next step (session 2):**
1. Re-check `curl -m 3 http://127.0.0.1:8091/health` (the tunnel was down at session end,
   waiting on the owner's one command). Build either way, per the lead.
2. fit/surveyfit.py v0 against the API contract: a `match_client` (POST /match, base64,
   timeout + one retry, /health gate), `ransac_similarity(pairs, inlier_px)` (pure numpy:
   4-parameter scale+rotation+translation, a few hundred random 2-pair samples, seeded
   RNG, least squares on inliers), prior application (scale band = recorded bar m/px over
   sheet m/px from the corners; rotation fixed or swept), the two 302b nulls (scramble
   the panel pieces; shift the sheet image half the box), score (inlier fraction
   reweighted by reprojection RMS), confidence (monotone in score + margin), and a JSON
   fit record. CLI: `.venv/bin/python fit/surveyfit.py <site> <plan> [--root DIR]`.
   One job per function.
3. Develop and smoke test against a STUB server implementing the same contract (recorded
   fixture responses) so tests stay hermetic: tests/test_surveyfit.py with a synthetic
   sheet/plan (known transform recovered within tolerance; the scramble scores below the
   true placement; recorded-run reproducibility like test_gate's). When the real tunnel
   answers: reproduce the lead's Maiden Castle smoke numbers (633 matches / 31 inliers /
   20-35-53 m at the 3 hand points) as a canary, then check a NON-held-out sheet+plan
   site (e.g. avaricum-q281826 or barnard-castle-q4185811) by eye via a contact sheet;
   log every choice in data/surveyfit/devlog.md. NEVER read the 21's hand-fit pairs
   during development (only the evaluator may).
4. When the dev-site smoke test is stable: restate the frozen config (threshold 0.2,
   max_side 832, inlier px, rotation-sweep grid, confidence formula, seed convention) in
   the site_flow section with the freeze commit hash; commit that (the freeze commit);
   only then the one run, checkpointed in data/surveyfit/heldout/results.json.
5. fit/surveyfit_heldout.py: the evaluator (reads the hand docs ONLY here, mirrors
   fit/inkfit_heldout.py): per-doc row = corner error (m, the 302b metric), rotation
   (deg), scale ratio (method/hand), score, null, margin, confidence, sheet used, aerial
   column where applicable (camp-d-attila); doc 21's panel is cropped from
   data/raw/commons/big/c_c20ff6b1f16d173d.jpg (crop [165,256,895,663]); after the run:
   paste the measured table into the site_flow section, write the verdict plainly.

**Re-read:** (none yet.)
