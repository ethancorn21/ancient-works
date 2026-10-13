Status: done
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
(2026-10-12, iteration 199, agent a - DONE: the 222-228 gate opened (all
seven `Status: done`), the full suite re-run is green (150 passed,
1 skipped, 248.96s, run with `.venv/bin/python`) and all six boxes were
verified intact on the merged tree -> Status: done, done claim filed
(DECISIONS, same date). Nothing further remains on 211; the follow-ups
are owned by 229 and 230.)

State at claim time (my branch tip 9940b56 = main's tip 643dfa1 + 3
driver commits; my merge commit 09a9472 is already ON main, so the
driver's acceptance merge of this branch is a fast-forward. The 222-228
commits touched only their own fit/src_*.py + tests/test_src_*.py +
tests/conftest.py + tests/test_fit_queue.py - never 211's outputs; the
six shared files were audited against my 09a9472 this session):
- BOX 1: the live merge (09a9472): 381 staging rows ->
  data/catalog/extras.jsonl (193), data/commons/files.jsonl (1623),
  classified.jsonl (930); pure growth, idempotent, 0 refused / 0
  conflicts; log in data/merge/log.jsonl. The three canonical files are
  byte-identical to the merge commit (git diff, this session).
- BOX 2: data/books/index.jsonl 1068 rows + validation.json (214c642);
  every row that reaches the plan list carries 200's evidence;
  `fit/evidence.py check` passes offline (0 fail).
- BOX 3: the 114 new sites built; web/data/sites.json = 499 unique-id
  entries vs the frozen 385-entry pre-build baseline (0 removed / 0
  changed; the box's "384" was the human's estimate, measured 385 -
  deviation in DECISIONS).
- BOX 4: web/data/plans.json 1168 rows / 13 cols; 574 rows carry a
  non-empty sites list (col index 8) and all 574 (id, sites[0]) pairs
  are unique; all pre-merge (id, sites[0]) keys present;
  tools/export_plans.py re-run byte-identical.
- BOX 5: docs/sources.md section 9 (0c33b8b): one row per GOAL.md lead
  (staged counts + documented drops) + the merge summary.
- BOX 6: 000's golden reference (25 hand fits / 19 sites) green in this
  session's suite run (test_serve.py; hermetic: port 0, temp tree, no
  network).
- Suite this session: `.venv/bin/python -m pytest tests/ -q` ->
  150 passed, 1 skipped in 248.96s (the former 10 reds were exactly
  222-228's source-guard failures; each fixed by making its own
  check/staged treat its already-merged rows as no-ops; the 1 skip is
  the standing baseline).
- Origin: still c063314 (fetch found no new commits) -> the 188 union
  audit stands (origin holds none of my outputs; only sites.json
  overlaps, disjoint on both sides; platefits/goldens byte-identical).
  New fact this session: c063314 is NOT an ancestor of main (the driver
  has not pulled the human's push) - the origin union is the driver's
  job at push/merge time and remains safe for all six boxes per 188.

Follow-ups (other tasks, not 211): 229 (imagecodecs pin) still open,
gated on 302a/304 (agent c in flight; they hold requirements.in/.txt -
do NOT touch those files for 229); the ad-hoc .venv imagecodecs install
is alive (the driver's in-place rebuild keeps it). 230 (Roman merge
re-run) open, gated on 211 [now done] + 207a/207b/207c (the Roman
staging exists on agent c's branch only - verified absent from main in
189).

If this task ever reopens: the merge is idempotent - re-run
`fit/merge.py` only if a new source stages rows (that is 230's job for
the Roman staging); re-run the suite with `.venv/bin/python -m pytest
tests/ -q`, never bare `pytest` (system python3 has no numpy/PIL -
PITFALLS "This codebase"); do NOT run `pipeline/books.py match`.
