Status: open
# 230: The Roman staging into the canonical data - the 211 consolidation re-run
Depends on: 211, 207a, 207b, 807, 808
Touches: fit/merge.py, data/catalog/extras.jsonl, data/commons/files.jsonl, data/commons/classified.jsonl, data/merge/, data/books/index.jsonl, data/books/validation.json, data/sites/, docs/sources.md, web/data/sites.json, web/data/sites/, web/data/plans.json, tests/test_merge.py

## Goal
211's lead note: the 211 consolidation ran without the Roman books (207 was stopped by
the owner at merge time) and "207a/207b staging, if it ever resumes, goes through a
later re-run of this step." This task is that re-run. Once 211 is done and the Roman
staging (extras_roman.jsonl / files_roman.jsonl / classified_roman.jsonl plus the three
books' per-book lists/triage artifacts) has landed on main, re-run the consolidation:
fold the Roman rows into data/catalog/extras.jsonl, data/commons/files.jsonl and
classified.jsonl; rebuild data/books/index.jsonl and validation.json from ALL books'
per-book artifacts (including the three Roman books) with the existing machinery;
update the Roman row of docs/sources.md section 9; build any new Roman sites (207c's
are mostly new no-QID Scottish forts) and refresh web/data/sites.json and
web/data/plans.json. The page renders the result with no page change (GOAL.md point 5).

If a 207 subtask is dropped before this task runs, edit the Depends on line to the
surviving subtasks and run against the staging that exists (the boxes hold with the
books that landed).

## Acceptance criteria
- [ ] The fit/merge.py re-run: every Roman staging row is in the canonical files; every
      pre-run canonical row is still byte-identical (pure growth); a second run changes
      nothing (idempotent); the run is logged in data/merge/log.jsonl (0 refused, or
      each refusal logged with its reason).
- [ ] data/books/index.jsonl is rebuilt from the per-book files of all books (the
      post-211 set plus the three Roman books); validation.json regenerated; every row
      that reaches the plan list carries the 200 evidence field; fit/evidence.py check
      passes offline on the merged set including the Roman rows.
- [ ] Every new Roman site id has web/data/sites/<id>/; web/data/sites.json grows by
      exactly the new sites and the pre-run entries are unchanged (except the 212-owned
      marker fields); web/data/plans.json: every pre-run (id, sites[0]) key still
      present, (id, sites[0]) still unique, the new Roman picture rows present
      (tools/export_plans.py re-run).
- [ ] docs/sources.md section 9: the Roman lead row records what was staged and what
      was dropped, per book, sourced from docs/lead_roman.md and the merge log
      (replacing the "NONE in this merge" row 211 wrote).
- [ ] The human's reference is untouched: the 25 hand fits and their 19 sites
      (tests/test_serve.py::test_hand_fits_are_the_reference) still pass after the
      re-run; the re-run's tests are hermetic (port 0, temp tree, no network).

## Notes
- Same invariants as 211: row conflicts (a Roman row equal to a canonical row or to a
  row staged by another source) resolve first-wins, recorded in data/merge/log.jsonl -
  never a silent rewrite.
- Building sites is the slow part (DEM fetch, images); it is a working-phase command.
  The test asserts the data-level result (entries, joins, idempotence) on the served
  data, not a full rebuild.
- When this task runs, tests/test_merge.py's frozen pre-merge baseline (the 385
  entries) shifts to the post-211 state (the 499 entries); update the baseline in the
  test for this intended change.

## Hand-over
(2026-10-14, iteration 210, agent a - STEP 2 (book-index rebuild + evidence record/check) DONE ON DISK
but UNCOMMITTED (harness saved it; commit it first this session). Steps 3-6 remain.)

**UNCOMMITTED on disk right now (commit them, task's Touches only, never `git add -A`):**
- data/books/index.jsonl: 1068 -> 1112 rows. The 10 old books in their original row order; then 38
  horsley_britannia_romana_1732 rows (31 kind-s: n0114x2, n0185x5, n0242x2, n0248x3, n0250x2, n0282x4,
  n0284x3, n0236, n0238, n0240, n0244, n0246, n0252, n0254, n0278, n0280, n0286; 7 kind-o list_view
  n0060/n0062/n0256/n0706/n0734/n0832/n0867) and 6 maclauchlan_roman_wall_1858 rows (n0078/n0093/n0111
  s + n0090/n0115/n0129 list_view). Every row carries rec evidence/1.
- data/books/validation.json: 10 -> 12 books. The 10 pre-existing entries are byte-identical to the
  committed file (verified by indent=1 dump diff); horsley + maclauchlan appended (numbers match
  lead_roman.md / the 207b PITFALLS verified values exactly - see DECISIONS it.210).
- Commit message: "230: step 2 - the book-index rebuild lands both roman books (index 1068->1112,
  validation 10->12 books) with the 200 evidence re-recorded on all book rows (check 0 fail) - step 3
  (sources.md) is next". The /tmp driver and baselines are still there: /tmp/230_step2_driver.py,
  /tmp/idx_before_230s2.jsonl, /tmp/val_before_230s2.json.

**State of the tests when last run (test_merge.py, it.210):** 9 passed / 1 failed in 22 s - the one red
is the EXPECTED open build gate (test_new_sites_are_complete: "no new sites: the build phase produced
nothing"), closing at step 4. test_index_and_plan_list_rows_carry_evidence PASSES (every index row +
every titled files row has rec; the offline check in-test returns rc 0 / " 0 fail").

**Remaining steps (in order):**
3. docs/sources.md section 9 (box 4): replace the "**none in this merge**" Roman lead row with per-book
   staged/dropped, sourced from docs/lead_roman.md + data/merge/log.jsonl (all 45 rows "merged", 0
   refused; horsley 17 kind-s staged / 7 kind-o indexed-only, maclauchlan 1 of 3 staged - n0078/n0111
   blank in this copy, n0093 staged; 207c dropped). Note in the row: the index rebuild recorded the 200
   evidence on all 1112 book rows (checked date 2026-10-14; pre-roman rows content-identical to the
   2026-10-12 record - the 211 precedent updates the date on rebuild) and the matcher's one-pair rule
   tied 6 roman rows (4 questionable: n0244_1 'Whitehouse'->Whitehouse Camp Wiltshire, n0248_1 'MAGNA'
   -> Brimstone Hill via alias token, n0286_1 'Mill'->Mill Mount, n0185_5 GLANNIBANTA->Glannoventa via
   the catalog's own alias) - see DECISIONS it.210; the rest are reported NONE, never silently kept.
4. Build the 9 new Roman sites (box 3, the slow part): OPEN QUESTION - what DEM/LiDAR source
   build_catalog.py has for UK sites (pipeline/dem_sources.py source_for / lidar_scot.py for
   Scotland). Precedent: the four no-QID Antonine Wall camps (bar-hill-fort, inchtuthil, raedykes,
   rough-castle-fort) already in extras.jsonl - inspect their web/data/sites/ dirs (relief.jpg?
   lidar_credit?) to see what a UK build produces (aerial-only is a valid outcome; the test checks
   self-consistency: relief.jpg iff the entry credits LiDAR). Then `nohup .venv/bin/python
   data/merge/run_build.py luguvallium-q71551754 ardoch virosidum cilurni petriana congavata
   tunnocelum kirkintilloch carriden &` (check `ps` first - PITFALLS run_build entry; log
   data/merge/build_sites.log; "NOT BUILT" = no LiDAR and no old map or bad id; one site per child;
   kill leaves a clean boundary).
5. `tools/export_plans.py` re-run: pure growth over the 1510-key baseline (test asserts); the roman
   picture rows for the QID sites + the new no-QID sites appear.
6. Full suite `.venv/bin/python -m pytest -p no:cacheprovider`: expect ALL green (the open gate
   closes at step 4). Then tick all 5 boxes, Status: done, done claim.

**Commit hygiene (team mode):** never `git add -A`; commit only this task's files (its `Touches:`
list). If docs/site_flow/307d_*.png go dirty after a full-suite run (suite side-effect churn,
PITFALLS 307d-PNG entry), restore main's bytes (`git checkout main -- docs/site_flow/307d_*.png`)
and leave them out of the commit.

Re-read: data/merge/run_build.py - the per-site loop and its log lines (read at iteration 209; one
process per site, "NOT BUILT" semantics); pipeline/dem_sources.py:source_for - the OPEN QUESTION
for UK sites (which source build_catalog gets for the 9 roman ids, Scotland vs England) before
starting step 4. Also read docs/sources.md section 9's current Roman row before rewriting it.

**State on disk now (committed; tree clean apart from this file + DECISIONS.md at commit time):**
- data/catalog/extras.jsonl 202 (was 193), data/commons/files.jsonl 1748 (was 1730), data/commons/classified.jsonl
  1055 (was 1037). Pure growth verified: first 193/1730/1037 lines byte-identical to the pre-run copies. Second
  run was a byte-identical no-op (rc 0) - idempotent.
- data/merge/log.jsonl = 45 rows, all action "merged", source "roman" (9 extras / 18 files / 18 classified).
  It REPLACED 211's 381-row snapshot (that one is in git history).
- web/data/sites.json still 499 entries, web/data/plans.json still 1510 rows - the new Roman sites are NOT built
  yet; tests/test_merge.py is 9/10 with test_new_sites_are_complete the expected red open gate (the 499
  baseline == all served sites, so "new sites" is empty until the builds land).
- The 9 new site ids (luguvallium-q71551754, ardoch, virosidum, cilurni, petriana, congavata, tunnocelum,
  kirkintilloch, carriden) are in extras.jsonl now. files_roman/classified_roman also carry rows for EXISTING
  catalog QID sites (castrum-segedunum-q637958 x2, rudchester-..., haltonchesters-..., birdoswald-...,
  aesica-...) - those merged into the files and will appear in plans.json, but build no new site.
- 207c is DROPPED (owner, ask 008); the re-run covers the two landed books (Horsley, Maclauchlan). 207a/207b
  staging is all on main - the Depends on line stays as-is (no edit needed; the driver's note in the task file
  covers the dropped case).

**Remaining steps (in order):**
2. Book-index rebuild (box 2): in-process driver - `import fit.src_roman_horsley as h;
   import fit.src_roman_maclauchlan as m; h.register(); m.register()` then
   `pipeline.books_lists.cmd_index(None)` and `cmd_validate(None)` (they iterate BOOKS, which the register()
   calls extend; all offline). Verify data/books/index.jsonl grows from 1068 by the roman rows, validation.json
   regenerated, every index row + every titled files row carries rec "evidence/1" (test
   test_index_and_plan_list_rows_carry_evidence asserts). Then `.venv/bin/python fit/evidence.py record` (book
   rows record offline via the matcher; existing rows stay byte-identical) and `fit/evidence.py check` -> rc 0 /
   " 0 fail". books_match reads data/catalog/sites.jsonl ONLY, so book rows of the NEW roman extras sites record
   kind "none" (reported, never a failure) - do NOT extend the matcher for this task.
3. docs/sources.md section 9 (box 4): replace the "**none in this merge**" Roman lead row with per-book
   staged/dropped, sourced from docs/lead_roman.md + data/merge/log.jsonl.
4. Build the 9 new Roman sites (box 3, the slow part): OPEN QUESTION to resolve first - what DEM/LiDAR source
   build_catalog.py has for UK sites (pipeline/dem_sources.py source_for / lidar_scot.py for Scotland).
   Precedent: the four no-QID Antonine Wall camps (bar-hill-fort, inchtuthil, raedykes, rough-castle-fort) are
   already in extras.jsonl - inspect their web/data/sites/ dirs (relief.jpg? lidar_credit?) to see what a UK
   build produces (aerial-only is a valid outcome; the test checks self-consistency: relief.jpg iff the entry
   credits LiDAR). Then `nohup .venv/bin/python data/merge/run_build.py luguvallium-q71551754 ardoch virosidum
   cilurni petriana congavata tunnocelum kirkintilloch carriden &` (check `ps` first - PITFALLS run_build entry;
   log data/merge/build_sites.log; "NOT BUILT" = no LiDAR and no old map or bad id; one site per child; kill
   leaves a clean boundary).
5. `tools/export_plans.py` re-run: pure growth over the 1510-key baseline (test asserts); the roman picture
   rows for the QID sites + the new no-QID sites appear.
6. Full suite `.venv/bin/python -m pytest -p no:cacheprovider`: expect ALL green (the open gate closes at
   step 4). Then tick all 5 boxes, Status: done, done claim.

**Commit hygiene (team mode):** never `git add -A`; commit only this task's files (its `Touches:` list). If
docs/site_flow/307d_*.png go dirty after a full-suite run (suite side-effect churn, PITFALLS 307d-PNG entry),
restore main's bytes (`git checkout main -- docs/site_flow/307d_*.png`) and leave them out of the commit.

Re-read: data/merge/run_build.py - the per-site loop and its log lines (read at iteration 209; one process per
site, "NOT BUILT" semantics); pipeline/dem_sources.py:source_for - the OPEN QUESTION for UK sites (which source
build_catalog gets for the 9 roman ids, Scotland vs England) before starting step 4.
