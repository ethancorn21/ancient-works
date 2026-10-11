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
Session 3 (2026-10-11): `tests/test_batch_us.py` is GREEN (5/5, 15.4 s) and committed; full suite
34/34 in .venv (53 s). All three session-2 failures were in the TEST file - fit/batch_us.py never
needed a change:
(1) `/` and `%` are same-precedence, left-associative: the format strings needed parentheses in
    both `_check_doc` and `_check_doc_stub` (PITFALLS has the family);
(2) `_table` needed the report's exact header "## Sample of automatically accepted fits (for the
    human's 18/20 check)";
(3) NOT state pollution: `fit_gate.gate` is a pure function of (pairs, transform) plus frozen
    module constants (verified by reading pipeline/fit_gate.py), and within the same test the
    batch's own in-process gate calls had already ACCEPTed all 15 serpent proposals. The real bug:
    `pre_docs` matches any `<site>.*.json` in data/db/platefits - including the automatic docs the
    run itself just wrote - so the test's post-run "pre" snapshot swallowed the batch's output and
    the expected set came out empty ({15} != set()). Fix: snapshot pre_docs/is_pre_fit BEFORE
    run_sites (pre_docs_before / pre_fit_before).

State of this checkout:
- Boxes 1, 2, 6 ticked. 3, 4, 5 all say "after the full working-phase run" - they wait for it.
- tests/test_batch_us.py: 5 hermetic tests (the no_network fixture monkeypatches
  socket.connect/create_connection to raise - no network, no port at all: the batch is a file
  loop, and the page's view of results is 212's). The `tree` fixture copies web/ + data/ minus
  data/raw/ (~29+39 MB, ~0.2 s) to tmp_path. Fixed sample: serpent-mound-q968802 (16 candidates,
  1 pre; 15 pinned 202 proposals -> automatic docs, gate med 0.001-0.022), cahokia-q333661
  (two-pair x3 + no-answer x1 -> one item), mound-bottom-q14710093 (only its pre doc -> nothing
  written), the first zero-candidate US site (aberdeen-mound-q4666953 -> no-picture item). The
  stub tests use the first US site with >= 2 non-pre candidates, no pre-fit and no existing item
  (angel-mounds-q4530064).
- data/db/platefits/ here still has exactly the 20 pre-batch docs (the batch has never written
  into this checkout). data/review/ has alligator-effigy-mound-q4732645 (region US, 2 candidates,
  201's seed - the working run's upsert will MERGE into that file: same-plan entries replaced,
  `resolved` never cleared) and the bibracte item (France, never touched by 203a). Expect the
  alligator file to change in the working-phase commit; it is NOT part of the golden.
- The golden (fe84152) is checked by test 4 against the temp copy; after the working run re-verify
  against THIS checkout: `sha256sum -c tests/golden/hand_fit_docs.sha256` (all 39 must be OK).

NEXT (session 4) - the WORKING phase (network allowed, .venv):
1. Check the AI-box tunnel is up before running (pipeline/llm.py - its base URL). If it is down
   and you cannot bring it up yourself, ask_human (the machine side) - everything else of this
   task is done.
2. `.venv/bin/python fit/batch_us.py --working` (all 90 US sites; fetches missing
   pictures/aerials as needed; writes docs + items + docs/batch_us.md).
3. Re-read: fit/batch_us.py llm_model - the prompt has never seen the model. On the first run,
   check a few real Qwen answers against the parsing (JSON shape, u/v in plan-px, lon/lat via
   _ground_lonlat) and adjust the prompt/parsing if needed (my file).
4. Then verify: the golden `sha256sum -c`; the report's "error (no outcome)" bucket empty and the
   counts sum to 90 (box 3: every US site ends auto-doc OR item OR pre-fit); tick 3, 4, 5; commit
   the docs + items + docs/batch_us.md.

For 203b (when it starts): import run_sites/write_report from fit.batch_us; its site list =
region != "US" plus the 6 region-less sites (they include the old-style fudge/hopeton/newark/
marietta/forthill/highbank - keep the site.json["plate"]["fit"] branch of is_pre_fit, R9); report
to docs/batch_eu.md; the SEED 20261010 is shared (both reports sample from it).
