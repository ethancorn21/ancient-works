Status: open
# 211: Consolidate - the new sites and pictures into the page's data
Depends on: 200, 204, 205, 206, 208, 209, 210
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
- [ ] fit/merge.py consolidates: every staging row is in the canonical files, every
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
(2026-10-12, iteration 173, agent a - merged main; the 211 pair now works; all six boxes still unticked)

State:
- fit/merge.py verified correct: append-only growth (old bytes byte-identical, written through a
  temp file), key = id (catalog) / (site, title) (commons), first row wins, conflicts and
  missing/kind-none evidence rows are refused and logged in data/merge/log.jsonl (no timestamps;
  a no-op rerun rewrites it byte-identical). rc 0 = no refusals, rc 1 = any refusal.
- tests/test_merge.py: 3/3 pass hermetic (temp tree via --root, sockets blocked). Full suite:
  134 passed, 1 skipped. The LIVE canonical files are NOT yet merged - data/merge/ does not exist
  in the repo (tests never write there).
- Real staging inventory: extras = artists(2), kip, limes, mackenzie, van_deventer; files and
  classified additionally have numancia, wiltshire_b; NO roman staging (207 stopped by the owner -
  see Lead note; the merge is idempotent, a later rerun picks it up). Checked: 0 staging rows
  fail the evidence gate, 0 cross-source/canonical conflicts.

Remaining work = the six acceptance boxes, in this order:
1. Live run: `.venv/bin/python fit/merge.py merge` in this repo. Creates data/merge/log.jsonl and
   appends staging rows into data/catalog/extras.jsonl, data/commons/files.jsonl, classified.jsonl.
   Verify: git diff shows only growth; second run produces zero further diff.
2. Rebuild data/books/index.jsonl + validation.json with the existing books machinery (8 original
   books; 213's civitates per-book files feed it). Every row reaching the plan list carries the 200
   evidence field; fit/evidence.py check passes offline on the merged set. NOTE: Liber secundus'
   bird's-eye VIEWS land only after 217 (order 215 -> 216 -> 217) - zero index rows from that book
   is 217's gap, NOT a 211 failure; do not invent rows.
3. Build the new sites (build_catalog.py / build_site.py - the slow working-phase part: DEM fetch +
   images) -> web/data/sites/<id>/ for each new site id; web/data/sites.json grows by exactly the
   new sites, old 384 entries unchanged (except fields 212 later owns).
4. Refresh web/data/plans.json (tools/export_plans.py): new picture rows present, every pre-merge
   (id, sites[0]) key still present, (id, sites[0]) stays unique.
5. docs/sources.md: per-lead status consolidated from docs/lead_*.md (staged vs dropped and why).
6. Human's reference untouched: tests/test_serve.py golden (25 hand fits / 19 sites) still green
   after the merge (it is in the suite; re-verify at claim time).

Next step (new session): box 1 - run the live merge, verify the git-diff is pure growth + idempotent
rerun, commit.

Re-read: fit/merge.py:run_target - the evidence gate applies to files.jsonl rows with a title ONLY;
classified rows are not gated (the plan-list gate is on the files rows) - check that reading before
changing the gate.

## Lead note (2026-10-12)
207 (Roman books) is stopped by the owner; this consolidation runs without it. 207a/207b staging, if it ever resumes, goes through a later re-run of this step.
