Status: open
# 211: Consolidate - the new sites and pictures into the page's data
Depends on: 200, 204, 205, 206, 207, 208, 209, 210
Touches: fit/merge.py, data/catalog/extras.jsonl, data/commons/files.jsonl, data/commons/classified.jsonl, data/books/index.jsonl, data/books/validation.json, docs/sources.md, web/data/sites.json, web/data/plans.json, tests/test_merge.py

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
**From 213 (2026-10-11, iteration 39, parent done-claim):** the *_artists* staging files exist and
must be merged into the canonical files by fit/merge.py: data/catalog/extras_artists.jsonl (two NEW
sites: imola-q50195, venice-q641 - both kind "town", aerial-photograph ground, region "Italy"),
data/commons/files_artists.jsonl and data/commons/classified_artists.jsonl (2 rows each; every row
already carries the 200 evidence field - hand-recorded caption_coords, verified by
.venv/bin/python fit/src_artists.py --check, 2/2 PASS). Per-book civitates files also exist and feed
the index.jsonl rebuild: data/books/triage/civitatesorbiste00brau.{A,F}.jsonl (A 292/292, F 118/118,
zero errors), data/books/lists/civitatesorbiste00brau.json (121 figure entries, 7 hand-verified plans)
and .map.json ([]). NOTE: the current books_lists machinery emits an index row only for kind "s";
Liber secundus's bird's-eye VIEWS reach the plan list only after 217 lands its view-as-drawing index
(order 215 -> 216 -> 217). Until then, zero index rows from this book is 217's pending gap, NOT a
211 merge failure - do not invent rows to compensate. 211's Depends omits 213 by design (wave order
2 -> 4 covers it; the merge is idempotent over whatever staging files exist).
