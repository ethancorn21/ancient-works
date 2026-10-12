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
(2026-10-12, iteration 185, agent a - BOX 3 TICKED (tests written in the unlogged session, verified 9/9 this session). Merged main per the lead's mid-session instruction (7e61147: full-tree test copies skip the 1.6 GB .npy/.npz grids - the disk was at 1 GB; a "No space left" failure is the disk, not the code). Suites are light now. NEXT: box 5 (docs/sources.md), then box 6, then the claim (gated on 222-228, still open as of this session)).

State:
- BOX 1 DONE (iter 174): live merge - 381 staging rows into the three canonical files, pure growth (byte-identical prefix), idempotent, 0 refused, data/merge/log.jsonl.
- BOX 2 DONE (iter 175, 214c642): data/books/index.jsonl (1068 rows) + validation.json rebuilt; 200 evidence on all book rows; `fit/evidence.py check` 0 fail.
- BOX 3 DONE (builds iter 183; tests+tick iter 185). web/data/sites.json = 499 = 385 pre-build baseline (commit 406562b; deviation: the box's "384" was the human's estimate) + 114 new, all complete. Frozen baseline data/merge/sites_premerge_baseline.jsonl (385). Tests in tests/test_merge.py: test_served_sites_grew_purely (pure growth vs baseline, only 212's marker fields may change), test_new_sites_are_complete (dir + required fields + relief.jpg ⇔ lidar_credit + coverable old-map layer ⇒ depictions.json, the machinery's own covers+MIN_AGE rule), test_new_site_golden_samples (the-hague/ostend/cambrai pinned to their recorded build values). All 3 pass; do NOT test per-sid log lines (build_sites.log lost ~65 lines to killed runs). run_build.py's --force = build_catalog skip-guard only (re-read resolved clean).
- BOX 4 DONE (iter 182): web/data/plans.json = 1168 rows; frozen data/merge/plans_premerge_keys.jsonl (1166) all present; (id, sites[0]) unique; re-running tools/export_plans.py is byte-identical (sha256 852089e0...). main() joins the EXISTING pre-merge data/books/matches.jsonl. NEVER run `pipeline/books.py match` for this task.
- BOX 5 PENDING: docs/sources.md - per-lead status consolidated from docs/lead_*.md (what was staged, what was dropped and why, per GOAL.md lead). Include: 207 stopped by the owner (no roman staging - a later merge re-run picks it up if it resumes; the roman staging files exist in my STAGING list only if 207 resumed - the _tree() helper in test_merge.py already skips missing staging files); 213's view books now indexed (civitates 118 + merian 60 rows, box 2); 114 sites built this phase. Start by reading docs/sources.md and the docs/lead_*.md files it should consolidate.
- BOX 6 PENDING: tests/test_serve.py golden - test_hand_fits_are_the_reference (25 hand fits / 19 sites) is GREEN in this session's suite run; the file is hermetic (conftest: temp copy of the tree, ephemeral port, no network per its docstring). At claim time: re-read it fresh to confirm the 25/19 coverage and hermeticity, then tick.
- CLAIM GATED: 222-228 (7 source-guard fix tasks) still OPEN (re-checked this session: all Status: open). My branch's red set = exactly their 10 source-guard failures (this session's suite: 10 failed / 130 passed / 1 skipped; more passes than iter 183's 124 because main absorbed other tasks' tests; no NEW failures). When 222-228 land on main: driver syncs, re-run the suite (expect fully green; the merge is idempotent - no re-run of fit/merge.py), tick box 5+6, Status: done, claim.

Next session, in order:
1. Re-run the suite (light now: no .npy copies). Expect exactly the 10 source-guard failures if 222-228 still open; if all green, boxes 5-6 can be finished and the claim filed the same session.
2. BOX 5: read docs/sources.md + the docs/lead_*.md files, write the consolidated per-lead status (staged / dropped + why), including the 207-stop note, the 213 books, the 114 sites. docs/sources.md is in my Touches.
3. BOX 6: re-read tests/test_serve.py::test_hand_fits_are_the_reference (25 fits / 19 sites, golden), confirm hermetic (conftest ephemeral port, temp tree, no network), tick.
4. If 222-228 still open: STOP here (gated - they are in Depends on; the driver brings this back). If closed: finish, tick, Status: done, claim.

Open thread: imagecodecs 2026.10.10 is installed in the .venv but NOT pinned in requirements.in/.txt (agent c's in-flight 302a/304 own those files; the AHN sites - incl. the-hague - depend on it). File the pin task once c's requirements work lands (or fold into the claim session).

## Lead note (2026-10-12)
207 (Roman books) is stopped by the owner; this consolidation runs without it. 207a/207b staging, if it ever resumes, goes through a later re-run of this step.
