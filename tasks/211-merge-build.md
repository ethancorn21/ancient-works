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
(2026-10-12, iteration 188, agent a - GATE STILL OPEN: all seven of 222-228
`Status: open` and the driver's local main is unmoved (tip 7e61147, as in
186/187; my branch tip 22036f9 contains it). No re-run (merge idempotent; red
set unchanged; the driver re-checks the suite at claim time). NEW this
session: the human's GitHub main (origin) was pushed (now c063314, today
13:34); its fork point with my branch is 4ca9e2c (today 13:21, "306a: done")
- 8 minutes BEFORE my merge commit 09a9472 (13:29) - so origin holds none of
my 211 outputs. I audited the union (my branch ∪ origin) against every box:
all six survive, no blocking conflict, nothing for me to do (merging is the
driver's). Details below.)

State (unchanged since 186/187; details in the 183-188 DECISIONS entries):
- BOXES 1-4 DONE: box 1 the live merge (09a9472; 381 staging rows -> the 3
  canonical files, pure growth, idempotent, 0 refused, log in
  data/merge/log.jsonl); box 2 data/books/index.jsonl 1068 rows +
  validation.json (200 evidence on all book rows; `fit/evidence.py check` 0
  fail); box 3 the 114 new sites built, web/data/sites.json 385 -> 499 vs
  the frozen 385-entry baseline, tests/test_merge.py 9/9; box 4
  web/data/plans.json = 1168 rows (the 1166 pre-merge (id, sites[0]) keys all
  present, (id, sites[0]) unique, tools/export_plans.py re-run
  byte-identical). NEVER run `pipeline/books.py match` for this task.
- BOX 5 DONE (186): docs/sources.md section 9 - one row per GOAL.md lead
  (staged counts + documented drops) plus the merge summary.
- BOX 6 DONE (186): 000's golden reference re-verified (19 sites, hermetic
  conftest: --port 0, temp tree minus raw/grids, terminated in teardown).
- SUITE (186, still current): 10 failed / 130 passed / 1 skipped; the 10 are
  exactly the 222-228 source-guard set. No new failures; test_serve/
  test_gate/test_merge green. Gotcha: no `--timeout` flag (pytest-timeout
  not in the .venv) - run `pytest tests/ -q`, nohup + pidfile.
- 229 (imagecodecs pin) still `Status: open`, dependency-gated on 302a/304
  (agent c is working both per this session's prompt). NOT a blocker for the
  211 claim (the driver's in-place .venv rebuild keeps the ad-hoc package
  until 229 lands).

NEW (188) - the human's origin/main moved; the union is audited safe:
- The remote-tracking ref was stale at 984b1b4 (yesterday 15:28 - GitHub had
  not been pushed since before the matchfit/302 era). `git fetch origin`
  (read-only; I may not merge) moved it to c063314 (today 13:34): the
  human's Mac work - map UI (d939bd2/6fb2b61 base maps, 76feacb marker
  clicks, 503c978 ?base=), Stonehenge site_done sync 2e41a6c (sites.json
  drawings 0->7 + review queue), the Maiden Castle hand-fit copy cd104ca,
  the 301 Argentoratum line f0d8c0b, [lead] 302 2eb60f2, [lead] 304/305
  b7a708c, the 303 provenance commits.
- Fork point 4ca9e2c (today 13:21) predates my merge (13:29) -> origin's
  files are the pre-merge world: extras 78 / files 1490 / classified 797 /
  index 901 / sites 385 / sources.md without section 9; no data/merge/*, no
  tests/test_merge.py, no tasks/222-229 (filed on my side after the fork).
- Union audit, per file: canonical files / index / validation / plans.json
  (content-identical to mine apart from a trailing newline) / sources.md /
  test_merge.py - origin side unchanged since the fork -> the union takes
  mine, no conflict (boxes 1/2/4/5 hold). sites.json - both sides differ
  but disjoint: my side only adds the 114 new entries; the origin side only
  touches the four marker fields (drawings/score/oldest/overlays =
  test_merge's MARKERS, the fields 212 owns) on the 385 old entries -> box 3
  tolerates exactly that (a textual conflict there resolves as: my 114
  entries + their marker values). platefits - origin made ZERO changes since
  the fork and the golden files are byte-identical on both sides -> box 6's
  25 hand fits / 19 sites survive. review.json - origin differs, my side
  unchanged -> the union takes origin's; not my file (306x / agent c), no
  test of mine reads it. Net: the incoming origin merge cannot break any of
  my six boxes nor the driver's claim-time suite check.

Next session, in order:
1. Check 222-228 statuses (head -1 of each task file). If any is still
   `Status: open` (or in-progress/blocked/split without a recorded drop):
   STOP (gated; the driver brings this back). Nothing else remains on 211
   while they are open (229 is queued, dependency-gated on 302a/304).
2. If none is open anymore (all done, or dropped with a recorded reason):
   re-run the suite (`pytest tests/ -q`; expect fully green; the merge is
   idempotent - do NOT re-run fit/merge.py; a "No space left" failure is the
   disk, see 7e61147). If main has absorbed the origin merge by then, the
   audit above says my tests stay green; the one thing to look at first if
   anything is red is sites.json (their marker updates) or review.json
   (not mine). Then set Status: done and file the done claim. Cite: all six
   boxes; the 381-row merge (0 refused / 0 conflicts); 114 new sites (385 ->
   499); the 1,068-row books index; the 19-site golden reference; that the
   red set of 10 was 222-228's source-guard set (now fixed by them); that
   the imagecodecs pin is 229 (check its status line: landed or still
   queued); and that the human's origin push (c063314, fork 4ca9e2c) was
   audited safe for all six boxes (this hand-over).
