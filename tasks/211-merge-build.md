Status: open
# 211: Consolidate - the new sites and pictures into the page's data
Depends on: 200, 204, 205, 206, 208, 209, 210, 222, 223, 224, 225, 226, 227, 228
Touches: fit/merge.py, data/catalog/extras.jsonl, data/commons/files.jsonl, data/commons/classified.jsonl, data/merge/, data/books/index.jsonl, data/books/validation.json, docs/sources.md, web/data/sites.json, web/data/plans.json, tests/test_merge.py

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
- [ ] web/data/plans.json is refreshed with tools/export_plans.py: the new picture rows
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
(2026-10-12, iteration 175, agent a - boxes 1+2 DONE and COMMITTED as 214c642; boxes 3-6 remain and are independent of 222-228; next session starts at box 3)

State:
- BOX 1 DONE (iteration 174): live merge - 381 staging rows into the three canonical files, pure growth
  (byte-identical prefix), idempotent, 0 refused, data/merge/log.jsonl written.
- BOX 2 DONE (iteration 175, committed in 214c642): rebuilt data/books/index.jsonl + data/books/
  validation.json with the machinery (`pipeline/books.py index` / `validate`), re-recorded the 200
  evidence on all 1068 book rows (`fit/evidence.py record`, offline), `fit/evidence.py check` passes
  offline (2582 rows: 1385 pass, 0 fail, 1197 no-tie). Tests extended in tests/test_merge.py (5/5 pass).
  Full details in the DECISIONS entry. Numbers: index = 8 originals (counts unchanged
  145/115/197/88/55/18/235/37) + civitates_liber2 118 (217's hand-list views: 107 added, 11 old qwen rows
  updated with the hand list) + merian_helvete00zeil 60 (the 216/217 book); the 5 untriaged view books
  contribute 0 rows (217's follow-on scope - never invent). validation.json: civitates figures stats
  filled, merian entry added. The 890 book rows that reach plans.json all carry the field (135
  caption_coords / 755 none - the none is 200's fail-closed end state; tie-coverage improvement is 801's
  job). The 264 files NONE rows: 0 reach plans.json.
- 222-228 are still OPEN on main as of this session (checked: no such commits; the modules here still
  carry the old "staged title already in canonical" guards). They stay in my Depends on and gate the
  CLAIM (the driver re-checks the suite when I set done; my branch must be green then). They do NOT gate
  boxes 3-6: those touch only files mine (web/data/*, docs/sources.md) and my branch's red set is exactly
  the 10 source-guard reds before and after any of them.
- Suite on this branch: 10 failed / 124 passed / 1 skipped, identical to the pre-work baseline (verified
  by diffing the FAILED lists; the 10 = the 222-228 set). tests/test_serve.py (the human's golden: 25
  hand fits / 19 sites) passes in that run.

Remaining boxes, in order (all independent of 222-228; claim after they land):
3. Build the new sites - the slow working-phase part. `pipeline/build_catalog.py` (NOT fit/: the task
   file's names are pipeline/build_catalog.py + pipeline/build_site.py) turns extras.jsonl sites into
   data/sites/<id>/ (LiDAR relief + block via build_site.py, old maps, summary) and build_site.py writes
   web/data/sites/<id>/ + the sites.json entry. Scope: the 115 new site ids from the merged extras.jsonl
   (extras has 193 rows total; 12,603 Wikidata sites in sites.jsonl are already handled by earlier
   waves). web/data/sites.json must grow by exactly the new sites: the current HEAD set is 385 entries
   (the task text's "old 384" predates 301/Maiden Castle landing) - diff against `git show HEAD:web/data/
   sites.json`, never a /tmp snapshot. DEM fetch = live national services (network, archive.org-grade
   allowed); budget a session or two. Sites without LiDAR coverage are skipped and listed (build_catalog
   does that itself) - do not force them.
4. Refresh web/data/plans.json with tools/export_plans.py: new picture rows present (the 167 new index
   rows with a local full image + any new commons rows), every pre-merge (id, sites[0]) key still present,
   (id, sites[0]) stays unique. DO NOT re-run `pipeline/books.py match` for this: export_plans joins the
   existing data/books/matches.jsonl, and re-matching against the grown extras catalog could re-point
   pre-merge (id, sites[0]) keys, which the box forbids. (Re-read item below.)
5. docs/sources.md: per-lead status consolidated from docs/lead_*.md (what was staged, what was dropped
   and why, per GOAL.md lead). Include: 207 stopped by the owner (no roman staging, no books - a later
   re-run of the merge picks it up if it resumes); 213's view books now indexed (118 + 60 rows).
6. Human's reference: tests/test_serve.py golden (25 hand fits / 19 sites) - re-verify at claim time
   (green in this session's run; the test is hermetic: port 0, temp tree, no network).

Claim order: when 222-228 are on main and the driver's main-sync merges them in (my branch goes fully
  green - the merge is idempotent, no re-run needed), finish boxes 3-6, tick, and set Status: done.

Re-read: tools/export_plans.py:main - before running box 4, confirm with the consuming page code whether
 the plans.json "sites" column is expected to track the grown catalog or to stay the stable pre-merge join
 (the box wording "every pre-merge (id, sites[0]) key is still present" points to stable; the page's
 consumers are web/ - grep for plans.json there).
(The earlier re-read on fit/merge.py:run_target's evidence gate was resolved in iteration 175: the gate
applies to files.jsonl titled rows only, classified rows are not gated, book-index rows are never merge-
gated - confirmed by re-reading the module; no change made. See the DECISIONS entry.)

## Lead note (2026-10-12)
207 (Roman books) is stopped by the owner; this consolidation runs without it. 207a/207b staging, if it ever resumes, goes through a later re-run of this step.
