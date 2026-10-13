Status: open
# 211: Consolidate - the new sites and pictures into the page's data
Depends on: 200, 204, 205, 206, 208, 209, 210, 222, 223, 224, 225, 226, 227, 228
Touches: fit/merge.py, data/catalog/extras.jsonl, data/commons/files.jsonl, data/commons/classified.jsonl, data/merge/, data/books/index.jsonl, data/books/validation.json, data/sites/, docs/sources.md, web/data/sites.json, web/data/sites/, web/data/plans.json, tests/test_merge.py, PITFALLS.md

## Goal
The single point where the per-source staging becomes the canonical data GOAL.md names.
fit/merge.py consolidates every extras_<source>*.jsonl / files_<source>*.jsonl /
classified_<source>*.jsonl (204-210, including subtask variants) into
data/catalog/extras.jsonl, data/commons/files.jsonl and classified.jsonl; rebuilds
data/books/index.jsonl with the existing machinery (it is a generated artifact -
books.py index regenerates it from the per-book files, including the books 207/209
added) together with the shared validation.json; makes sure every new row that reaches
the plan list carries 200's evidence field; builds the new sites (build_catalog.py,
build_site.py) and refreshes web/data/plans.json (export_plans.py) and
web/data/sites.json. Nothing else in the project writes these files; the page renders
the result with no page change (GOAL.md point 5).

## Acceptance criteria
- [x] fit/merge.py consolidates: every staging row is in the canonical files, every
      pre-merge canonical row is still present byte-identical (the files grow, they are
      never rewritten), and the merge is idempotent (a second run changes nothing).
- [x] data/books/index.jsonl is rebuilt from the per-book artifacts of all books (the 8
      original plus whatever 207/209 added); every row that reaches the plan list carries
      the 200 evidence field; fit/evidence.py check passes offline on the merged set.
- [x] Every new site is built: web/data/sites/<id>/ exists for each new site id and
      web/data/sites.json has its entry (at least id/name/lon/lat/corners/size_m/drawings)
      - the served sites.json grows by exactly the new sites; the old 385 entries (the box's
      "384" was the human's estimate; the measured pre-build count is 385 - deviation noted in
      DECISIONS) are unchanged (except fields 212 later owns).
- [x] web/data/plans.json is refreshed with tools/export_plans.py: the new picture rows
      are present, every pre-merge (id, sites[0]) key is still present, and (id, sites[0])
      remains unique (the shared-id case stays one row per (picture, site)).
- [x] docs/sources.md is updated with the per-lead status consolidated from the
      docs/lead_*.md files: what was staged, what was dropped and why, per GOAL.md lead.
      (Section 9, added 2026-10-12: one row per GOAL.md lead 204/205/206/207/208/209/210/213
      with the staged counts and the documented drops with reasons, plus the merge summary;
      purely additive, every number cross-checked against data/merge/log.jsonl and the files.)
- [x] The human's reference is untouched: the 25 hand fits and their 19 sites (000's
      golden test, tests/test_serve.py) still pass after the merge; the test is hermetic
      (port 0, temp tree, no network). (Verified this session: test_hand_fits_are_the_reference
      is green in the suite run and not among the 10 failures; the golden file lists the 19 sites
      and all 19 have web/data/sites/<sid>/depictions.json in this checkout, so the per-site
      depictions check runs for every one; conftest is hermetic - --port 0, temp tree without
      data/raw/ and the .npy/.npz grids, session-scoped server terminated in teardown.)

## Notes
- Row conflicts (the same picture staged by two sources, or a staged row equal to an
  existing canonical row) are resolved by keeping the first and recording the duplicate
  in the merge log - never a silent rewrite of a row that is not byte-identical.
- Building sites is the slow part (DEM fetch, images); it is a working-phase command.
  The test asserts the data-level result (entries, joins, idempotence) on a small fixed
  sample plus the full served-data invariants, not a rebuild.
- The books' triage artifacts that 207/209 left in data/books/ stay as they are; this
  task only reads them and writes the two shared files (index.jsonl, validation.json).

## Lead note (2026-10-12)
207 (Roman books) is stopped by the owner; this consolidation runs without it. 207a/207b staging, if it ever resumes, goes through a later re-run of this step. (NOTE 2026-10-12 iter 186: 207 has since resumed as 207a/207b/207c - agent c is working it; 207c is blocked; its staging is on agent c's branch, not main yet.) (NOTE 2026-10-12 iter 189: the "later re-run" is now filed as tasks/230-roman-merge-rerun.md - Depends on: 211, 207a, 207b, 207c; it re-runs this consolidation over the canonical files once the Roman staging lands.)

## Hand-over
(2026-10-12, iteration 191, agent a - GATE STILL OPEN: all seven of 222-228
`Status: open` (each `Depends on: none` - NOT circularly gated on 211, just
un-dispatched: the driver's "Next open tasks" lists 207a/207b/221 and
222-228 queue behind them; each touches only its own fit/src_*.py + tests,
no overlap with my Touches, so nothing I can do unblocks them). Local main
still 7e61147; `git fetch origin` found ZERO new commits (origin/main still
c063314, so the 188 union audit stands). Fresh state sanity this session:
all of 211's outputs intact and exactly as expected (counts below). No
re-run (merge idempotent; red set unchanged; the driver re-checks the suite
at claim time). Nothing else remains on 211 while the gate is open.)

State (unchanged since 186; 187-191 were filing/audit/sanity sessions; full
details in the 183-191 DECISIONS entries):
- BOXES 1-6 ALL TICKED: box 1 the live merge (09a9472; 381 staging rows ->
  the 3 canonical files, pure growth, idempotent, 0 refused, log in
  data/merge/log.jsonl); box 2 data/books/index.jsonl 1068 rows +
  validation.json (200 evidence on all book rows; `fit/evidence.py check` 0
  fail); box 3 the 114 new sites built, web/data/sites.json 385 -> 499 vs
  the frozen 385-entry baseline, tests/test_merge.py 9/9; box 4
  web/data/plans.json = 1168 rows (the 1166 pre-merge (id, sites[0]) keys all
  present, (id, sites[0]) unique, tools/export_plans.py re-run
  byte-identical); box 5 docs/sources.md section 9 (one row per GOAL.md lead
  - staged counts + documented drops - plus the merge summary); box 6 000's
  golden reference (25 hand fits / 19 sites; hermetic conftest: --port 0,
  temp tree minus raw/grids, terminated in teardown). NEVER run
  `pipeline/books.py match` for this task.
- SUITE (last run 186, still current): 10 failed / 130 passed / 1 skipped;
  the 10 are exactly the 222-228 source-guard set, and main has not moved
  since (7e61147). Gotchas: no `--timeout` flag - run `pytest tests/ -q`
  with nohup + pidfile; a "No space left" failure is the disk (see 7e61147),
  not the tests.
- 229 (imagecodecs pin) still `Status: open`, dependency-gated on 302a/304
  (agent c is working both per this session's prompt; they hold
  requirements.in/.txt in flight - do NOT touch those files for 229). NOT a
  211 blocker (the driver's in-place .venv rebuild keeps the ad-hoc package
  until 229 lands).
- 230 (Roman merge re-run) still `Status: open`, gated on 211 +
  207a/207b/207c (207a/207b agent c in flight; 207c BLOCKED; the Roman
  staging files exist on agent c's branch only - verified absent on main).
- Origin audit (188; fetches in 189 and 190 found no new commits, so it
  stands): tip c063314; fork point with my branch 4ca9e2c (8 min BEFORE my
  merge commit 09a9472) -> origin holds none of my 211 outputs. Union:
  canonical files / index / validation / plans.json / sources.md /
  test_merge.py take mine (origin unchanged since the fork); sites.json
  differs on both sides but disjoint (my 114 new entries vs the human's
  marker-field updates on the old 385 = test_merge's MARKERS, the fields
  212 owns) -> box 3 tolerates exactly that (a textual conflict resolves as:
  my 114 entries + their marker values); platefits + golden files
  byte-identical on both sides -> box 6 survives; review.json takes
  origin's (not my file). Full audit: the 188 DECISIONS entry.
- Data-shape gotcha (new in 190; filed in PITFALLS under This codebase, and
  PITFALLS.md was added to my Touches line for it): web/data/sites.json is
  a top-level dict {"sites": [499 entries, unique ids]}; web/data/plans.json
  is a dict {"cols": [13], "rows": [1168]} - 574 rows carry a non-empty sites
  list and all 574 (id, sites[0]) pairs are unique (box 3/4 invariants hold
  in the live files). A bare `len(json.load(...))` reads 1/2, not the entry
  count.

Next session, in order:
1. Check 222-228 statuses (head -1 of each task file). If any is still
   `Status: open` (or in-progress/blocked/split without a recorded drop):
   STOP (gated; the driver brings this back). Cheap freshness checks are
   fine: `git fetch origin` (expect origin/main still c063314 unless the
   human pushed again - if it moved, re-run the 188 union audit against the
   new commits) + the row-count sanity below (expect 193/1623/930/1068,
   499 sites, 1168 plan rows). Nothing else remains on 211 while they are
   open (229 is queued, gated on 302a/304; the Roman re-run is 230, gated on
   211 + 207a/b/c).
2. If none is open anymore (all done, or dropped with a recorded reason):
   re-run the suite (`pytest tests/ -q`, nohup + pidfile; expect fully
   green; the merge is idempotent - do NOT re-run fit/merge.py). If anything
   is red, the first things to look at are web/data/sites.json (the human's
   marker-field updates on the old 385) or web/data/review.json (not my
   file - 306x / agent c). Then set Status: done and file the done claim.
   Cite: all six boxes; the 381-row merge (0 refused / 0 conflicts); the 114
   new sites (385 -> 499); the 1,068-row books index; the 19-site golden
   reference; that the red set of 10 was 222-228's source-guard set (now
   fixed by them); that the imagecodecs pin is task 229 (check its status
   line: landed or still queued); that the Roman re-run is filed as task
   230; and that the human's origin push (c063314, fork 4ca9e2c) was audited
   safe for all six boxes (188 hand-over / DECISIONS).
