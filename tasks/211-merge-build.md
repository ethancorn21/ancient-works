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
- [ ] data/books/index.jsonl is rebuilt from the per-book artifacts of all books (the 8
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
(2026-10-12, iteration 174, agent a - box 1 done and committed; 211 now waits on 222-228)

State:
- BOX 1 DONE (committed on this branch): first live run of `.venv/bin/python fit/merge.py merge`
  on the real repo -> +115 extras.jsonl, +133 files.jsonl, +133 classified.jsonl (381 staging
  rows; 0 refused; rc 0); data/merge/log.jsonl created (381 "merged" entries, 0 conflicts).
  Verified: all three canonical files are pure growth (HEAD bytes a byte-identical prefix);
  every staging row present; a second run is a complete no-op (0 added, all four files
  byte-identical, log re-written byte-identical).
- The live merge turned 10 tests red in 7 source modules (all owned by DONE tasks 204/205/206/
  208/210/209b/213 - not files I may edit in this session): every module's check/stage guard
  asserts its staged rows are NOT in the canonical files, and after the merge they ARE
  (identically - the merge's own success). Red: test_src_artists::test_check_staged_files_join_
  and_pass; test_src_kip::test_check_staged_offline; test_src_limes::test_check_staged_files_
  join_and_pass; test_src_mackenzie::test_staged_row_and_join; test_src_numancia::test_check_
  staged_files_join_and_pass; test_src_van_deventer::test_check_staged_files_join_and_pass +
  test_table_and_staged_rows; test_src_wiltshire_stukeley::test_stage_offline (SystemExit) +
  test_check_staged_offline + test_book_rows_staged_in_files_b (asserts the pre-merge invariant
  itself). Systemic, not a merge bug; the only new reds (full run: 10 failed / 117 passed; the
  8 deselected batch_eu reds are 203b's own, pre-existing). Full list + fix spec below in the
  filed tasks.
- FILED 222-228 (one module + its test each, in lead order: 222 van_deventer/204, 223 kip/205,
  224 mackenzie/206, 225 limes/208, 226 numancia/210, 227 stukeley/209b, 228 artists/213): a
  staged row identical to its canonical twin (merge's norm(): sort-keys JSON) is an already-
  merged no-op; a different row with the same key still fails loud; known-site self-references
  (artists, van_deventer: known_sites() reads the now-merged canonical extras) are a problem
  only when the id/QID resolves to a DIFFERENT site; tests cover all three states hermetically.
  Added to my Depends on; 211 is scheduled after they merge. Main stays green meanwhile (its
  pre-merge state passes the new guards); when they land and main merges into my branch, my
  branch's suite goes green without re-running the merge (it is idempotent).
- No roman staging exists (207 stopped) - a later rerun of the merge picks it up.

Remaining boxes, in order (next 211 session, once 222-228 are on main):
2. Rebuild data/books/index.jsonl + validation.json with the books machinery (8 original books;
   213's civitates per-book files feed it). PITFALLS (book machinery): the rebuild DROPS the 200
   evidence field - re-record it (fit/evidence.py record) after the rebuild so every plan-list row
   carries it; byte-diff against `git show HEAD:data/books/index.jsonl`, never a /tmp snapshot.
   NOTE: Liber secundus' bird's-eye VIEWS land only after 217 (order 215 -> 216 -> 217) - zero
   index rows from that book is 217's gap, NOT a 211 failure; do not invent rows.
3. Build the new sites (build_catalog.py / build_site.py - the slow working-phase part: DEM fetch +
   images) -> web/data/sites/<id>/ for each new site id; web/data/sites.json grows by exactly the
   new sites, old 384 entries unchanged (except fields 212 later owns).
4. Refresh web/data/plans.json (tools/export_plans.py): new picture rows present, every pre-merge
   (id, sites[0]) key still present, (id, sites[0]) stays unique.
5. docs/sources.md: per-lead status consolidated from docs/lead_*.md (staged vs dropped and why).
6. Human's reference untouched: tests/test_serve.py golden (25 hand fits / 19 sites) still green
   after the merge (it is in the suite; re-verify at claim time).

Next step (new session, after 222-228 merge): box 2 (books index rebuild + evidence re-record).

Re-read: fit/merge.py:run_target - the evidence gate applies to files.jsonl rows with a title ONLY;
classified rows are not gated (the plan-list gate is on the files rows) - check that reading before
changing the gate.

## Lead note (2026-10-12)
207 (Roman books) is stopped by the owner; this consolidation runs without it. 207a/207b staging, if it ever resumes, goes through a later re-run of this step.
