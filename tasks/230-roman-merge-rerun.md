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
(2026-10-14, iteration 211, agent a - STEP 3 (docs/sources.md section 9 Roman row) DONE and committed.
Next session: STEP 4 - run the 9 Roman site builds (no open questions left; all facts probed this session).)

**Done (committed):**
- Steps 1-2 (it.208-210): the scoped merge (45 roman rows into the 3 canonical files, 0 refused,
  idempotent) + the book-index rebuild (index 1068 -> 1112, validation 12 books, 200 evidence re-recorded
  on all 1112 rows, check rc 0). The driver committed them (37edbfb).
- Step 3 (this session): docs/sources.md section 9 - the Roman lead row now reads "Horsley (1732) and
  Maclauchlan (1858); Roy (1793) dropped" (207a/207b, both fit modules, lead_roman.md) and records per
  book: staged = 45 rows all merged / 0 refused (the log is that run's snapshot; Horsley 17 kind-s =
  100% of the list, 8 new no-QID extras rows, Maclauchlan 1 of 3 kind-s -> new luguvallium-q71551754 row;
  every row caption_coords); dropped = n0078/n0111 blank in this copy, 10 kind-o leaves indexed-only,
  Horsley's ~121 inscription plates deferred, Roy DROPPED (owner, ask 008). The row also records the
  evidence re-record on all 1,112 book rows and the matcher's 6 one-pair ties (2 genuine / 4
  questionable, never silently kept). The section intro line notes the 2026-10-14 re-run (230).
  test_merge.py: 9 passed / 1 failed - the one red is the EXPECTED open build gate
  (test_new_sites_are_complete: "no new sites: the build phase produced nothing"), closing at step 4.
- Corrections logged in DECISIONS it.211: the it.210 hand-over's tie counties were wrong -
  whitehouse-camp-q17678709 is HEREFORDSHIRE (Michaelchurch Escley), mill-mount-q24661439 is SUFFOLK
  (Redisham); sources.md records the catalog's counties.

**STEP 4 (next session) - build the 9 new Roman sites (box 3). Open question RESOLVED (probes, it.211):**
1. Check `ps aux | grep run_build` first (PITFALLS: only one run_build at a time).
2. `nohup .venv/bin/python data/merge/run_build.py luguvallium-q71551754 ardoch virosidum cilurni
   petriana congavata tunnocelum kirkintilloch carriden &` - one process per site, appends to
   data/merge/build_sites.log; a kill leaves a clean boundary at the last finished site (build_catalog
   skips already-built ids; --force rebuilds a half-built one). Expect web/data/sites.json 499 -> 508.
3. What each site gets (probed):
   - 6 ENGLISH (luguvallium, virosidum, cilurni, petriana, congavata, tunnocelum): source "ea"
     (Environment Agency composite DTM, EPSG 27700) - reachable from this VM (cilurni probe: finite data
     in 1.0 s) -> relief.jpg + lidar_credit.
   - 3 SCOTTISH (ardoch, kirkintilloch, carriden): main ORDER -> None; the STATIC fallback picks "scot"
     (pipeline/lidar_scot.py - a local S3 mirror of the Scottish national LiDAR, no service/key).
     ardoch (Gask Ridge) throws aw.NoLidar "no Scottish LiDAR tiles on this box" (the mirror holds
     selected tiles only) -> it builds AERIAL-ONLY + the NLS 1747-55 military-survey overlay
     (depictions.json present, no relief.jpg - the test's self-consistency holds). Before starting,
     probe the other two the same way (5 s each): `.venv/bin/python -c` with sys.path pipeline,
     `import lidar_scot, aw; lidar_scot.read_dem(aw.site_bbox(lon,lat,60,60),24,24,lon,lat)` on the
     kirkintilloch and carriden coords from extras.jsonl (carriden is near Bo'ness - same region as the
     four built Antonine Wall camps, which carry scot-6-first.webp; kirkintilloch (Badenoch) probably has
     no tiles). nls.covers() is True for all 3 Scottish sites (and all 9), so NONE can end up
     "NOT BUILT" (that needs no LiDAR AND no old map).
4. If a session is cut mid-build: `ps` for run_build, kill it, commit what finished, resume the remaining
   ids next session (the runner and build_catalog are both idempotent per site).

**Then (same or later sessions):**
5. `tools/export_plans.py` re-run: plans.json (1,510 baseline keys) pure growth - the roman picture rows
   (17 horsley + 1 maclauchlan; the files/classified rows for the 1510-era catalog QID sites included)
   appear; test_merge.py asserts pure growth + uniqueness.
6. Full suite `.venv/bin/python -m pytest -p no:cacheprovider` - expect ALL green (the open gate closes).
   If docs/site_flow/307d_*.png go dirty from suite churn (PITFALLS 307d-PNG), restore main's bytes
   (`git checkout main -- docs/site_flow/307d_*.png`) and leave them out of the commit. Then tick all 5
   boxes, Status: done, done claim.

**Commit hygiene (team mode):** never `git add -A`; commit only this task's Touches files
(fit/merge.py, the 3 canonical data files, data/merge/, data/books/index.jsonl, data/books/validation.json,
data/sites/, docs/sources.md, web/data/sites.json, web/data/sites/, web/data/plans.json, tests/test_merge.py).

Re-read: data/merge/run_build.py:main - what it does after build_catalog per site (set_drawings marks
refresh; --marks-only mode) if a build misbehaves; pipeline/nls.py:covers - the exact coverage ring, if a
Scot site unexpectedly lands "NOT BUILT".
