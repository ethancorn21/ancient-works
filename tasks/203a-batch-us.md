Status: in-progress
# 203a: The batch, US - the 90 US built sites
Depends on: 001, 200, 201, 202, 802, 803
Touches: fit/batch_us.py, data/db/platefits/, data/review/, docs/batch_us.md, tests/test_batch_us.py, tests/golden/hand_fit_docs.sha256, tasks/802-gate-holdout-auto-docs.md, tasks/803-review-queue-rebaseline.md

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
- [x] In the full working-phase run (all 90 US sites, recorded in the report), every US site
      ends with at least one automatic document or an open review item - or an existing hand
      fit.
- [x] After the run the 20 hand-fit documents and the 19 site files are byte-identical to the
      golden hashes; the batch added files, it rewrote none.
- [x] docs/batch_us.md: counts (automatic fit / review item / already hand-fitted / no picture
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
Session 4g (iteration 42). Status: in-progress. The driver REJECTED the 4f done claim
(reopened the task) because the suite failed on exactly the 4 cross-task failures 4f had
predicted and recorded: tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees
and tests/test_review.py::test_export_cli / test_page_shows_the_review_list /
test_save_resolves_the_item. All 6 boxes of THIS task remain verified: 4g re-ran the full
suite (4 failed / 34 passed - the 4 exactly as listed, my 5/5 test_batch_us green) and the
golden (sha256sum -c tests/golden/hand_fit_docs.sha256 = 39/39). The data from the 4e run
(16 auto docs, 89 item files, docs/batch_us.md) is committed and untouched.

The block is a DEPENDENCY INVERSION that 4f itself created, and 4g resolved it:

- Root cause of each of the 4 (evidence in the 4g DECISIONS entry): all four are
  hardcoded PRE-batch population pins in tests owned by 001/201. 802's: gate_heldout
  partition() expects exactly 20 docs, finds 36. 803's: pinned "2 open of 2" stdout, the
  [alligator, bibracte] open list, the Review (2)/rvn==2 page pins, and test_save reading
  map_box/size/ia/file/label/book/cite from the ITEM ENTRY. The last is a TEST artifact,
  not a data defect: web/review.js rvResolveRow resolves the candidate's row from
  web/data/plans.json by (plan, site) FIRST and only falls back to stored entry fields
  (missing map_box tolerated: openPlan falls back to the full frame) for rows absent from
  the build. My upserted 203a-shape entries are product-fine; NO repair of my item files
  and NO fit/review.py change is needed for it.
- The fix is state-agnostic in both filings: 802 derives its name list over NON-auto
  documents - identical to the original 20 names before and after any batch (no hand-fit
  doc ever gains "auto"); 803 derives every expectation from the repo's data/review/ items
  through 201's own rules and must reduce EXACTLY to the currently pinned values on the
  pre-batch population (2 open of 2; save pick lands on alligator n0214_2 - the only open
  site with a book row carrying map_box+size). Both were therefore re-filed with
  `Depends on: 001` / `Depends on: 201` (both done) instead of 203a, so an implementer on
  ANY main-based branch (with or without 203a's data) lands green, and their merge keeps
  main green in both orders. 4g also added both to THIS task's `Depends on:` line (001,
  200, 201, 202, 802, 803) so the driver holds 203a until both are merged, and added their
  paths to my `Touches:` (I authored those filings in 4f and maintain them until they are
  handed out - recorded in DECISIONS).

NEXT SESSION on this task (the driver should bring it back after 802 and 803 have merged
into main and main has been merged into my branch):
1. `.venv/bin/python -m pytest -q`: expect GREEN (38+ tests). If still red: if a failure
   is in a file of MY Touches (fit/batch_us.py, tests/test_batch_us.py, data/db/platefits/,
   data/review/, docs/batch_us.md, tests/golden/hand_fit_docs.sha256) fix it; if it is in
   someone else's file, record it in DECISIONS and leave it - do not edit other tasks'
   files.
2. Re-confirm `sha256sum -c tests/golden/hand_fit_docs.sha256` = 39/39 (my data files have
   not moved since the run; they must not).
3. Set `Status: done` (all 6 boxes are already ticked and verified in 4e/4f) and re-file
   the claim; note the outcome in this section. Do NOT re-run the batch, touch the 20
   hand-fit documents, or edit tests/test_gate.py or tests/test_review.py (802/803 own
   those).

For 203b (imports run_sites/write_report from fit/batch_us.py): site list = region != "US"
plus the 6 region-less sites; keep is_pre_fit's site.json["plate"]["fit"] branch (the
region-less hand fits live there); report docs/batch_eu.md; shared SEED 20261010; the
feature-presence check degrades to a no-op on aerial ground (texture everywhere) - documented
in the module docstring, acceptable (gate + human sample remain). The 802/803 fallout is
US-specific in shape but 203b's run will extend data/review/ and data/db/platefits/ again:
803's re-baseline must derive from the repo state (it is designed to) and 802's non-auto
filter already covers 203b's future auto docs.
