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
- [ ] Every new site is built: web/data/sites/<id>/ exists for each new site id and
      web/data/sites.json has its entry (at least id/name/lon/lat/corners/size_m/drawings)
      - the served sites.json grows by exactly the new sites; the old 384 entries are
      unchanged (except fields 212 later owns).
- [x] web/data/plans.json is refreshed with tools/export_plans.py: the new picture rows
      are present, every pre-merge (id, sites[0]) key is still present, and (id, sites[0])
      remains unique (the shared-id case stays one row per (picture, site)).
- [ ] docs/sources.md is updated with the per-lead status consolidated from the
      docs/lead_*.md files: what was staged, what was dropped and why, per GOAL.md lead.
- [ ] The human's reference is untouched: the 25 hand fits and their 19 sites (000's
      golden test, tests/test_serve.py) still pass after the merge; the test is hermetic
      (port 0, temp tree, no network).

## Notes
- Row conflicts (the same picture staged by two sources, or a staged row equal to an
  existing canonical row) are resolved by keeping the first and recording the duplicate
  in the merge log - never a silent rewrite of a row that is not byte-identical.
- Building sites is the slow part (DEM fetch, images); it is a working-phase command.
  The test asserts the data-level result (entries, joins, idempotence) on a small fixed
  sample plus the full served-data invariants, not a rebuild.
- The books' triage artifacts that 207/209 left in data/books/ stay as they are; this
  task only reads them and writes the two shared files (index.jsonl, validation.json).

## Hand-over
(2026-10-12, iteration 183, agent a - BOX 3 BUILD PHASE COMPLETE and verified: all 114 new sites built to completion against the 385-entry pre-build baseline (0 removed, 0 changed). This session: ran run 3 to its end, the runner died on ENOSPC, added --force to run_build.py and resumed the 3 remaining, then found + rebuilt the-hague (orphaned half-built since run 2's kill). Code change (run_build.py) + build output are UNCOMMITTED (harness holds them). NEXT: box 3's tests + tick, then boxes 5-6, then claim (gated on 222-228, still open))

State:
- BOX 1 DONE (iter 174): live merge - 381 staging rows into the three canonical files, pure growth (byte-identical prefix), idempotent, 0 refused, data/merge/log.jsonl.
- BOX 2 DONE (iter 175, committed 214c642): data/books/index.jsonl (1068 rows: 8 originals + civitates_liber2 118 + merian_helvete00zeil 60) + validation.json rebuilt with the machinery; 200 evidence re-recorded on all book rows; `fit/evidence.py check` passes offline (0 fail); tests/test_merge.py extended.
- BOX 4 DONE (iter 182): web/data/plans.json = 1168 rows (890 book rows + 278 commons; the 2 NEW commons rows are shotwick-castle-q7502621 and numancia; the 167 newly indexed book rows have no local full pages and are correctly absent). Refresh already done in unlogged sessions 176-179; re-running tools/export_plans.py is byte-identical (sha256 852089e0...); frozen data/merge/plans_premerge_keys.jsonl (1166 keys) is a subset of the current keys; (id, sites[0]) unique; tests 6/6. Re-read resolved: main() joins the EXISTING pre-merge data/books/matches.jsonl (no re-matching). NEVER run `pipeline/books.py match` for this task.
- BOX 3: BUILD PHASE DONE (iter 183). FINAL STATE (verified this session; worktree not yet committed - run_build.py + build_sites.log + web/data/sites.json + 10 new data/sites/ dirs are pending, the harness holds them):
  - web/data/sites.json = 499 entries = 385 pre-build baseline (commit 406562b, iteration 137 - the last commit BEFORE 211's first build; all 385 present and object-identical: 0 removed, 0 changed) + 114 new sites, ALL complete.
  - The box's "old 384" is the human's estimate; the MEASURED pre-build count is 385 (deviation noted in DECISIONS; set tests to the measured value).
  - The 114 = UK houses (temple-newsam ... kings-weston-house, badminton-house), NL (12: alkmaar amsterdam enkhuizen goes groningen haarlem reimerswaal rotterdam sluis the-hague utrecht valkenburg), BE (aardenburg bruges brussels ghent kortrijk mechelen ostend + more), ~38 German Limes forts, FR/LU towns (arras ath ... vieil-hesdin, incl. beaumont oudenaarde soignies luxembourg-city lille), IT (imola venice).
  - "Complete" = web/data/sites/<id>/ exists; relief.jpg ⇔ lidar_credit field; a coverable old-map layer (depict.LAYERS: `depict.covers(L, lon, lat) and L["year"] <= time.gmtime().tm_year - depict.MIN_AGE_YEARS`) ⇒ depictions.json exists. Aerial-only sites (no coverable layer, e.g. ostend, conde) correctly have no depictions.json. Entries carry id/name/lon/lat/corners/size_m/drawings (drawings=0 is normal: no placed drawings yet).
  - This session's builds: run 3 finished 23/23 by ~22:05Z but the runner DIED on therouanne (OSError ENOSPC - the shared 48G disk filled; agent c's /tmp/loop-ancient-works.c had hit 3.5G - and run_build's log() then raised on write, killing the process mid-line: truncated `=== therouanne-q261399 FAILED ==`). Added `--force` to data/merge/run_build.py (forwarded to build_catalog; its ONLY effect is the `sid in built and not a.force` skip guard - without it a half-built site already in sites.json is skipped FOREVER) and resumed the 3 remaining with it (ok by 22:16Z: therouanne rebuilt in place score 1.01/overlays 2/oldest 1780; valenciennes; vieil-hesdin). Then found the-hague-q36600 half-built SINCE RUN 2's 20:27Z kill (unlogged sessions: child killed mid LiDAR-load, completion lines lost, the later third invocation at 20:40Z - utrecht + ostend/mons/saint-ghislain/tournai - never included it, sessions 178-182 missed it): rebuilt with --force, ok 22:22Z (score 0.91, overlays 1, oldest 1850, tmk1850 100%).
  - Verification scripts used (re-runnable): baseline diff = `git show 406562b:web/data/sites.json` vs web/data/sites.json (per-id object equality; expect 385 ⊆ 499, 0 removed, 0 changed); completeness audit = import pipeline/depict and apply the covers+MIN_AGE rule above to all 114. Both clean. PITFALLS entry filed in the data/merge/ section (ENOSPC kill + --force + audit recipe).
  - LOG CAVEAT (matters for the test design): data/merge/build_sites.log (890 lines) LOST per-site lines when past runs were killed (~65 of the 114 have no `build rc=`/`ok` line; the 7 run-1 AHN `NOT BUILT` lines were all superseded by later successful builds). Do NOT base a test on per-sid terminal log lines - base it on the data (baseline diff + completeness audit).
  - Disk: recovered to ~6G free (87%) after the ENOSPC spike; agent c's /tmp growth is the main shared-disk pressure.
- BOX 5 PENDING: docs/sources.md - per-lead status consolidated from docs/lead_*.md (what was staged, what was dropped and why, per GOAL.md lead). Include: 207 stopped by the owner (no roman staging - a later merge re-run picks it up if it resumes); 213's view books now indexed (civitates 118 + merian 60 rows, box 2); 114 sites built this phase.
- BOX 6 PENDING: tests/test_serve.py golden (25 hand fits / 19 sites; hermetic: port 0, temp tree, no network) - re-verify at claim time.
- CLAIM GATED: 222-228 (7 source-guard fix tasks) still OPEN (re-checked iter 183; no fix commits on main; branch in sync with main tip 23ed8b0 which has 306b done). My branch's red set = exactly their 10 source-guard failures (10 failed / 124 passed / 1 skipped; unchanged by this session's script-only edit). When they land: re-run the suite (expect fully green; the merge is idempotent - no re-run of it), finish boxes, tick, Status: done.

Next session, in order:
1. Re-read first: data/merge/run_build.py:run/main - fresh eyes on the --force change (must only affect build_catalog's skip guard; --marks-only path unchanged; docstring accurate). Then re-run the suite (expect the same 10 source-guard failures, nothing else).
2. BOX 3 tests + tick. Extend tests/test_merge.py (hermetic: read-only on data, no rebuild, no network, no fixed ports):
   (a) freeze data/merge/sites_premerge_baseline.jsonl = the 385 baseline entries extracted from `git show 406562b:web/data/sites.json` (commit it; like plans_premerge_keys.jsonl);
   (b) test: every baseline entry present in web/data/sites.json, object-identical, nothing removed (pure growth vs the frozen baseline);
   (c) test: every non-baseline entry has web/data/sites/<id>/; required fields (id/name/lon/lat/corners/size_m/drawings); relief.jpg ⇔ lidar_credit; coverable old-map layer ⇒ depictions.json (the audit logic above);
   (d) small fixed sample per the Notes: the-hague-q36600 (AHN + tmk1850: oldest=1850, overlays=1, score=0.91), ostend-q12996 (aerial-only BE LiDAR: relief present, no depictions.json), cambrai-q181285 (IGN + 2 maps: oldest=1780, overlays=2, score=1.01) - assert those concrete values;
   (e) optionally a weak log assertion only if robust; prefer (b)+(c)+(d) as the real invariants. Then tick box 3.
3. BOX 5, then 6, then the claim as above.

Open thread: imagecodecs 2026.10.10 is installed in the .venv but NOT pinned in requirements.in/.txt (agent c's in-flight 302a/304 own those files; the AHN sites - incl. today's the-hague rebuild - depend on it). File the pin task once c's requirements work lands (or fold into the claim session).

## Lead note (2026-10-12)
207 (Roman books) is stopped by the owner; this consolidation runs without it. 207a/207b staging, if it ever resumes, goes through a later re-run of this step.
