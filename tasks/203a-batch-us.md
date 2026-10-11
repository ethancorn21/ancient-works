Status: blocked
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
Session 4i (iteration 44). Status: BLOCKED - the escalation the 4h hand-over set has
fired. Third consecutive iteration (42/43/44) the driver handed me this task with the
same 4 red; the held state was re-verified a third time and is unchanged since 4h.
WAITING ON: human request 002 (`.agent/asks/002.md`, blocking) - who implements
802/803; my named recommendation is that I do; a 120-minute timeout auto-answers
with the recommendation. Do not wait or poll for it.
- main still at bb3140f (full ancestor of my branch; no 802/803 in it); both task files
  still `Status: open`, unassigned; 215/216/217 still listed "next open" ahead of them.
- Suite: 4 failed / 34 passed = exactly 802's test_recorded_measurement_reproduces_
  agrees (20-name precondition vs 36 docs) and 803's three pre-batch pins
  (test_export_cli "88 open of 89" vs 90; test_page_shows_the_review_list; 
  test_save_resolves_the_item KeyError 'map_box'). My 5/5 tests/test_batch_us.py green.
- Golden: sha256sum -c tests/golden/hand_fit_docs.sha256 = 39/39 OK.
- 802's live invariant: 36 docs = 16 "auto": true + 20 non-auto; the 20 non-auto names
  are set-equal to the golden's 20 hand-fit names.
- 803's live premise: 89 review items, all raw resolved=null; alligator's item carries
  candidate c_618a6be74dfaff32 whose auto doc exists -> 201's export derives 88 open.
  (data/review also holds a README.md - that is the 90th directory entry, not an item.)
Per the stuck rule (3rd failed attempt at the 802/803 blocker: 4e filed them with an
inversion, 4g re-filed them assignable, 4h waited a round - no assignment in any round)
and the 4h policy ("one more hold round; then the escalation above"), this session
filed ask_human request 002 and set Status: blocked while that request is open. The request:
who implements 802/803 - MY RECOMMENDATION: let me (the 203a holder) implement them
(I wrote both specs from the root-cause analysis on the live data; each is ~one
session; it unblocks the only red in the repo); ALTERNATIVE: assign them to an idle
agent (none visible: agent a is on 204, 215-217 still open). A timeout auto-answers
with my recommendation.

NEXT SESSION (after the request resolves - human answer or the loop's 120-minute
auto-answer, which goes with the recommendation):
- If the answer is IMPLEMENT (or the auto-answer with the recommendation):
  1. Set Status: in-progress. Add the three source paths to the Touches line:
     tools/gate_heldout.py, tests/test_gate.py, tests/test_review.py (the team rule
     "add a path there first" + the human's yes to my recommendation).
  2. Implement 802 (spec: tasks/802-gate-holdout-auto-docs.md): partition() derives the
     held-out name list over the NON-auto docs instead of hardcoding 20; the test pins
     become derived. Two-state bar: pre-batch (20 docs) must byte-reproduce the
     registered 20-name table and post-batch (36) must hold. Commit alone.
  3. Implement 803 (spec: tasks/803-review-queue-rebaseline.md): the three test pins
     derive from the repo items through 201's own export derivation (export counts,
     page list, save document built from the plans.json ROW - all of map_box/size/ia/
     file/label/book/cite are plans.json columns; stored entry fields stay a fallback
     for rows absent from the build). Two-state bar: pre-batch reduces to the pinned
     values (2 open of 2; [alligator, bibracte]; Review (2)/rvn 2/stats) word for word;
     post-batch holds (88 open of 89; alligator derived-resolved via its auto doc).
     Commit alone.
  4. `.venv/bin/python -m pytest -q` (expect ~38/38 green) and
     `sha256sum -c tests/golden/hand_fit_docs.sha256` (39/39). Set 802 and 803 done
     (my own specs: tick each box as I verify it; record in DECISIONS), then set 203a
     to Status: done and file the claim - all 6 of my boxes were ticked and verified in
     4e/4f and nothing of mine has changed since.
- If the answer is ASSIGN (another agent takes 802/803): set Status: in-progress,
  keep `Depends on: 802, 803`, and resume the 4h hold procedure: each time I am
  handed the task, re-verify 4/34 + 39/39 (or the merged state: suite green -> claim).
- If the answer text is ambiguous: interpret it in light of the recommendation, say
  what I understood in DECISIONS, and proceed.
Protect: never re-run the batch, never touch the 20 hand-fit documents or the golden
file, keep 802/803 state-agnostic (the two-state reduction is their correctness bar).

For 203b (imports run_sites/write_report from fit/batch_us.py): site list = region != "US"
plus the 6 region-less sites; keep is_pre_fit's site.json["plate"]["fit"] branch (the
region-less hand fits live there); report docs/batch_eu.md; shared SEED 20261010; the
feature-presence check degrades to a no-op on aerial ground (texture everywhere) - documented
in the module docstring, acceptable (gate + human sample remain). The 802/803 fallout is
US-specific in shape but 203b's run will extend data/review/ and data/db/platefits/ again:
803's re-baseline must derive from the repo state (it is designed to) and 802's non-auto
filter already covers 203b's future auto docs.
