Status: in-progress
# 230: The Roman staging into the canonical data - the 211 consolidation re-run
Depends on: 211, 207a, 207b, 807, 808, 242, 810, 812, 813
Touches: fit/merge.py, pipeline/commons.py, data/catalog/extras.jsonl, data/commons/files.jsonl, data/commons/classified.jsonl, data/merge/, data/books/index.jsonl, data/books/validation.json, data/books/matches.jsonl, data/sites/, docs/sources.md, web/data/sites.json, web/data/sites/, web/data/plans.json, tests/test_merge.py, tests/test_matchfit_station.py, tests/fixtures/matchfit_station/, PITFALLS.md

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
- [x] The fit/merge.py re-run: every Roman staging row is in the canonical files; every
      pre-run canonical row is still byte-identical (pure growth); a second run changes
      nothing (idempotent); the run is logged in data/merge/log.jsonl (0 refused, or
      each refusal logged with its reason).
- [x] data/books/index.jsonl is rebuilt from the per-book files of all books (the
      post-211 set plus the three Roman books); validation.json regenerated; every row
      that reaches the plan list carries the 200 evidence field; fit/evidence.py check
      passes offline on the merged set including the Roman rows.
- [x] Every new Roman site id has web/data/sites/<id>/; web/data/sites.json grows by
      exactly the new sites and the pre-run entries are unchanged (except the 212-owned
      marker fields); web/data/plans.json: every pre-run (id, sites[0]) key still
      present, (id, sites[0]) still unique, the new Roman picture rows present
      (tools/export_plans.py re-run).
- [x] docs/sources.md section 9: the Roman lead row records what was staged and what
      was dropped, per book, sourced from docs/lead_roman.md and the merge log
      (replacing the "NONE in this merge" row 211 wrote).
- [x] The human's reference is untouched: the 25 hand fits and their 19 sites
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

(2026-10-14, iteration 216, agent a - the 5 acceptance boxes were ticked in it.215 and
committed (170066f); the driver's rejection (a423d19) named 4 new reds. THIS SESSION:
2 of the 4 (test_matchfit_station x2) FIXED - they were caused by 230's own step-2 index
rebuild, so 243 (the re-record task, "Depends on: 230" - a deadlock: the driver will never
accept 230 while 243's tests are red) was ABSORBED into 230: its two paths added to the
Touches line, record.py run against the live ELoFTR (127.0.0.1:8091, matchanything_eloftr
on the RTX 5060 Ti), both fixtures re-recorded, 243 dropped. Verified: test_matchfit_station
2/2 (55 s); fixture diff minimal (recorded_at re-stamp, index_row 4c7be2d0 -> 003d1d77, the
unsure section's evidence.checked 2026-10-12 -> 2026-10-14, non-reproducible `seconds`;
238's hand-written `refreshed` note dropped - record.py regenerates the header, git keeps
it, the test doesn't read it; 0 frozen-heldout discrepancies, replay identical, both
in-process branches rc=0). The other 2 (test_owner_check x2) went RED AGAIN this session,
3rd consecutive time on this checkout, at the SAME probe step as it.214/it.215: A fails
"RESULT FAIL: toolbar scale and turn change the drawing on screen" (pick
richard-s-castle-q17650937 / earthworkenglan01allcgoog_n0453_1), B fails as the designed
consequence (itemBytes never recorded). it.215 proved every relevant file byte-identical
across this checkout, agent c's and main, so the flake is machine state (render-timing
mid-transition; hypothesis: GPU contention from the parallel agents' concurrent test runs
- 242's own measurement: same-tree runs an hour apart differ 28.6-33.6% of pixels on the
saved/reload views). Per the TEAM MODE rule, the done-claim's green-suite gate cannot
complete until that test is stable, so "Depends on:" now carries 242 (open; its 307d dep
is merged) and 207c was trimmed (dropped, per the task's own instruction). THE DRIVER
HOLDS 230 until 242 merges, then returns it. Data level: nothing changed this session
outside the fixtures - the it.215 numbers stand (merge idempotent +0/+0/+0, evidence
1456 pass/0 fail, sites 508, plans 1572 sha256 dee768f2db7c..., test_merge 10/10,
test_data 3/3, hand-fits reference 1/1).

Next session (230 returned after 242 merged):
1. `.venv/bin/python -m pytest tests/test_matchfit_station.py -p no:cacheprovider` - expect
   green; if 242 or another task re-stamped index evidence since, re-record first:
   `.venv/bin/python tests/fixtures/matchfit_station/record.py` (live ELoFTR 8091).
2. Run the owner_check PAIR in ONE invocation: `.venv/bin/python -m pytest
   tests/test_owner_check.py -p no:cacheprovider` (A then B, the 306d way) - with 242
   merged (settle-before-shooting) it should be green; B cannot run in isolation.
3. Both green -> one full-suite run, then re-claim done (all 5 boxes were ticked in
   it.215; the driver re-checks the suite and already reopened once on exactly these 4
   tests, so do NOT claim while the pair is red). If the pair is STILL red after 242
   merged, that is a 242 defect in its owner lane - do NOT absorb it: log the exact
   failure step in DECISIONS and ask_human pointing at 242.
After ANY owner_check run, restore the re-rendered docs/site_flow/307d_*.png to the
committed bytes (`git show HEAD:docs/site_flow/<name>.png > docs/site_flow/<name>.png`)
before committing - the ten PNGs must stay byte-identical (6af207b precedent; never
git add -A).
