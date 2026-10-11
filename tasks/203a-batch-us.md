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
Session 4h (iteration 43). Status: in-progress, HELD on the dependency: tasks 802 and 803
are still `Status: open`, unassigned, and NOT in main (main is at bb3140f, a full ancestor
of my branch; no driver sync since iteration 40's 02b09b9). The 4g hand-over expected the
driver to bring this task back only after 802/803 merged; the driver handed it back before
that, so this session re-verified the held state (no edits; all values below unchanged
since 4g):
- Full suite: 4 failed / 34 passed = exactly 802's test_recorded_measurement_reproduces_
  agrees and 803's three review tests (export_cli "88 open of 89"; page list; save
  KeyError 'map_box'). My 5/5 tests/test_batch_us.py green (full suite and in isolation).
- Golden: sha256sum -c tests/golden/hand_fit_docs.sha256 = 39/39 OK.
- 802's invariant holds live: 36 platefit docs = 16 "auto": true + 20 without, and the 20
  non-auto names are set-equal to the golden's 20 hand-fit names -> a partition() derived
  over non-auto names reproduces the registered 20-name table byte for byte here, and
  automatic docs only add names, so also on a pre-batch checkout.
- 803's premise holds live: 89 review items, all raw resolved=null; alligator's item
  carries candidate c_618a6be74dfaff32 whose auto doc exists -> 201's export derives it
  resolved -> 88 open, as 803's spec says (pre-batch it reduces to 2 open of 2).
Why the suite is red at all: the 4 failures are hardcoded pre-batch population pins in
tests owned by 001/201 (full root-cause evidence in the 4g DECISIONS entry; 802/803 specs
carry the fix, both re-filed in 4g with `Depends on: 001`/`201` = done, so both are
assignable now). Queue note: PROGRESS.md's "Next open tasks" lists 215/216/217 ahead of
802/803 - benign if the queue is numerical (800/801 were also 8xx and got handed out);
if 802/803 stay unassigned after 215-217 are out, or the driver keeps handing me this
task with the same 4 red, ask_human (recommendation: hand 802/803 to idle agents, or let
this task's holder implement them - I wrote both specs; each is one session's work).

NEXT SESSION:
1. First check `head -2 tasks/802-*.md tasks/803-*.md` and whether main advanced past
   bb3140f into my branch.
2. If both are merged into main (or otherwise in my branch): run `.venv/bin/python -m
   pytest -q` (expect GREEN, 38+) and `sha256sum -c tests/golden/hand_fit_docs.sha256`
   (= 39/39). Then set `Status: done` and re-file the claim - all 6 boxes were ticked
   and verified in 4e/4f. If a failure is in a file of MY Touches (fit/batch_us.py,
   tests/test_batch_us.py, data/db/platefits/, data/review/, docs/batch_us.md, the
   golden) fix it; if it is in someone else's file, record it in DECISIONS and leave it.
3. If 802/803 are still open: re-run the two checks above (they must still be exactly
   4/34 and 39/39), record in DECISIONS, keep this hand-over, commit, stop - do NOT
   implement their specs (their files are not on my Touches) and do NOT ask_human yet
   (one more hold round; then the escalation above). Never re-run the batch, never
   touch the 20 hand-fit documents, never edit tests/test_gate.py or tests/test_review.py.

For 203b (imports run_sites/write_report from fit/batch_us.py): site list = region != "US"
plus the 6 region-less sites; keep is_pre_fit's site.json["plate"]["fit"] branch (the
region-less hand fits live there); report docs/batch_eu.md; shared SEED 20261010; the
feature-presence check degrades to a no-op on aerial ground (texture everywhere) - documented
in the module docstring, acceptable (gate + human sample remain). The 802/803 fallout is
US-specific in shape but 203b's run will extend data/review/ and data/db/platefits/ again:
803's re-baseline must derive from the repo state (it is designed to) and 802's non-auto
filter already covers 203b's future auto docs.
