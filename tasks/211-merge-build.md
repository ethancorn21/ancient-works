Status: open
# 211: Consolidate - the new sites and pictures into the page's data
Depends on: 200, 204, 205, 206, 208, 209, 210, 222, 223, 224, 225, 226, 227, 228
Touches: fit/merge.py, data/catalog/extras.jsonl, data/commons/files.jsonl, data/commons/classified.jsonl, data/merge/, data/books/index.jsonl, data/books/validation.json, data/sites/, docs/sources.md, web/data/sites.json, web/data/sites/, web/data/plans.json, tests/test_merge.py

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
207 (Roman books) is stopped by the owner; this consolidation runs without it. 207a/207b staging, if it ever resumes, goes through a later re-run of this step. (NOTE 2026-10-12 iter 186: 207 has since resumed as 207a/207b/207c - agent c is working it; 207c is blocked; its staging is on agent c's branch, not main yet.)

## Hand-over
(2026-10-12, iteration 187, agent a - GATE STILL OPEN: all seven of 222-228 are
`Status: open` and main has moved nothing since the 186 sync (branch tip 6ad8570
contains main tip 7e61147; only driver bookkeeping in between). The done-claim
stays gated; nothing was re-run (the merge is idempotent; the red set is
unchanged and the driver re-checks the suite at claim time). This session's
step: the imagecodecs open thread is now task 229 - filed, dependency-gated,
no open thread left on this task.)

State (unchanged since 186; details in the 183-186 DECISIONS entries):
- BOXES 1-4 DONE: box 1 the live merge (381 staging rows -> the 3 canonical
  files, pure growth, idempotent, 0 refused, log in data/merge/log.jsonl);
  box 2 data/books/index.jsonl 1068 rows + validation.json (200 evidence on
  all book rows; `fit/evidence.py check` 0 fail); box 3 the 114 new sites
  built, web/data/sites.json 385 -> 499 vs the frozen 385-entry baseline,
  tests/test_merge.py 9/9; box 4 web/data/plans.json = 1168 (the 1166 pre-
  merge keys all present, (id, sites[0]) unique, tools/export_plans.py re-run
  byte-identical, sha256 852089e0...). NEVER run `pipeline/books.py match`
  for this task.
- BOX 5 DONE (iter 186): docs/sources.md section 9 - one row per GOAL.md lead
  (staged counts + documented drops, per lead doc + merge log) plus the merge
  summary; purely additive.
- BOX 6 DONE (iter 186): 000's golden reference re-verified - the 19 sites
  (all with depictions.json in this checkout), hermetic conftest (--port 0,
  temp tree minus raw/grids, terminated in teardown), green in the run.
- SUITE (iter 186, still current): 10 failed / 130 passed / 1 skipped in
  234 s; the 10 are exactly the 222-228 source-guard set (their
  check_staged/join assertions see their staged rows in the canonical files -
  the live merge's by-design effect; the fix tasks own the post-merge check
  semantics). No new failures; test_serve/test_gate/test_merge green.
  Gotcha: no `--timeout` flag (pytest-timeout not in the .venv) - run
  `pytest tests/ -q`, nohup + pidfile.
- 229 FILED (iter 187): tasks/229-imagecodecs-pin.md (Depends on: 302a, 304;
  Touches: requirements.in, requirements.txt, PITFALLS.md) pins the ad-hoc
  imagecodecs 2026.10.10 the AHN builds need (PITFALLS pillow entry now
  points at it). It is dependency-gated on c's in-flight requirements work
  and NOT on this task's Depends-on list - it does not block the 211 claim
  (the driver's in-place .venv rebuild keeps the package until it lands).

Next session, in order:
1. Check 222-228 statuses (head -1 of each task file). If any is still
   `Status: open` (or in-progress/blocked/split without a recorded drop):
   STOP (gated; the driver brings this back). Nothing else remains on 211
   while they are open (229 is queued, dependency-gated).
2. If none is open anymore (all done, or dropped with a recorded reason):
   re-run the suite (`pytest tests/ -q`; expect fully green; the merge is
   idempotent - do NOT re-run fit/merge.py; a "No space left" failure is the
   disk, see 7e61147), then set Status: done and file the done claim. Cite:
   all six boxes; the 381-row merge (0 refused / 0 conflicts); 114 new sites
   (385 -> 499); the 1,068-row books index; the 19-site golden reference;
   that the red set of 10 was 222-228's source-guard set (now fixed by them);
   and that the imagecodecs pin is 229 (check its status line: landed or
   still queued).
