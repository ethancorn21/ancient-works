Status: in-progress
# 230: The Roman staging into the canonical data - the 211 consolidation re-run
Depends on: 211, 207a, 207b, 807, 808, 242, 810, 812, 813, 814
Touches: fit/merge.py, fit/src_roman_maclauchlan.py, pipeline/commons.py, data/catalog/extras.jsonl, data/commons/files.jsonl, data/commons/classified.jsonl, data/merge/, data/books/index.jsonl, data/books/validation.json, data/books/matches.jsonl, data/sites/, docs/sources.md, web/data/sites.json, web/data/sites/, web/data/plans.json, tests/test_merge.py, tests/test_matchfit_station.py, tests/fixtures/matchfit_station/, PITFALLS.md

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

(2026-10-15, iteration 237, agent a - I hold the WHOLE CYCLE (230/242/810/811/812/813/814; inter-deps
count as met, build them together on this branch). STATE: DONE AND CLAIMED THIS SESSION - full suite
run 2 on the fixed content: 184 passed / 1 skipped / 0 failed in 573.83 s
(/tmp/loop-ancient-works.a/fullsuite-237b.log); Status flipped to done; the driver re-checks (every
box ticked + suite green on this branch) and, on acceptance, merges this branch - 230 lands with
everything else on it (245's page fix, the 814/816 recipe file, the maclachlan date fix) - and the
cycle's remaining tasks come back next.)

**This session (it.237):**
1. Finished the it.236 housekeeping item (a): PITFALLS web/ entry "saveFit's one-shot sites.json fetch
   could land in the ~119 ms depiction->re-score gap..." (Where/Symptom/Why + the 245 fix + measured
   evidence). Items (b)/(c) were already committed by the driver sweep a3003b03 (245/810/812/813/814
   hand-overs all carry their it.236 updates).
2. Full suite run 1 (branch as it stood): 1 failed / 183 passed / 1 skipped in 585.97 s
   (/tmp/loop-ancient-works.a/fullsuite-237.log). The four a423d19 reds all green (matchfit 2/2,
   owner_check pair green, merge/data/serve all green). The ONE new red:
   test_src_roman_maclauchlan.py::test_check_staged_joins_and_passes at step (a) -
   "join: staged site luguvallium-q71551754 differs from its canonical row in extras.jsonl".
3. Root cause (measured): fit/src_roman_maclauchlan.py stage() stamps now() (the RUN date) into
   location_check.checked and evidence.checked. The committed staging rows AND the canonical rows 230
   merged from them carry 2026-10-14 = the day the LIVE verification ran (P625 cross-check; the note
   hard-codes "sitelinks checked 2026-10-14"). A re-stage on any later day re-stamps to that day, the
   full-content join (same norm as fit/merge.py) sees the two date fields differ -> false "differs" ->
   exit 1. The test passed in a423d19 only because that run was on 2026-10-14, the same day as the
   merge. Date-bomb: it reds on every later day, so waiting is not a fix. Verified by walking the
   fresh-vs-canonical row: ONLY the two checked fields differ.
4. Fix (fit/src_roman_maclauchlan.py added to this task's Touches - the it.216 "caused by my own
   change fixes itself" absorption; my merge made the row canonical, which exposed the re-stamp):
   CHECKED = "2026-10-14" stored constant replaces now() (function + time import dropped; _norm
   docstring corrected). Committed staging/canonical rows UNCHANGED (already 2026-10-14; stage() is
   idempotent, writes no byte on a populated file). The test file was NOT touched. Verified:
   test_src_roman_maclauchlan 4/4 in 4.2 s (offline, socket-blocked, temp trees); the module's --check
   CLI exits 0 on the real post-merge tree. No other file imports the module.
5. Flagged, NOT fixed (agent c's 809 lane, see the DECISIONS entry): fit/src_roman_horsley.py has the
   IDENTICAL trap (now() at 536 evidence.checked and 588 location_check.checked; all 8 horsley rows
   checked 2026-10-14, all canonical since the 230 merge) - 809's new offline --check will hit the
   same false "differs" on any run after 2026-10-14 unless it stores the verification date.
   src_mackenzie.py also stamps now() (line 369) but its tests are green - awareness only.
6. Full suite run 2 (the claim gate, fixed content): 184 passed / 1 skipped / 0 failed in 573.83 s
   (log /tmp/loop-ancient-works.a/fullsuite-237b.log) - exactly run 1's 185 tests with the one red
   turned green, nothing else moved. The merge was deliberately NOT re-run this session (its index
   rebuild re-stamps evidence.checked - the it.215 trap that needed the it.216 fixture re-record; the
   data files stand exactly as it.215/it.216 left them and the suite re-verifies them as-is).

**NEXT SESSION (only if the driver REOPENS 230 - otherwise the remaining cycle work below is next on
this branch):**
1. If reopened: the reason is in DECISIONS.md (the driver's note on the rejected claim names the reds).

**What happens next on this branch (the driver hands the remaining cycle tasks back after 230
merges):** the 812/813 rebuild (double-shot assert + AW_OWNER_REFRESH regime) on top of the 816 recipe
- the it.235 build survives verbatim at `git show 3579c22b:tests/test_owner_check.py` (rebase its parts
onto the current file, keeping c's settle/subpixel); then 811 (one-time refresh + pinned PNGs + docs
note + PITFALLS rewrite); then the 810/242 verification passes. See those files' hand-overs.

**Standing discipline (applies to every owner_check work on this branch):** the pair always runs in ONE
invocation (A then B - B cannot run alone); after ANY owner_check run, restore the ten
docs/site_flow/307d_*.png to committed bytes before committing (git restore docs/site_flow/; R5) -
813's refresh flag is not in the branch file yet, so unflagged runs re-copy all ten (run 2 re-encoded 9
of the 10; B_1-card always byte-identical); NEVER git add -A over them. The probe logs of a green run
die with the session - read them from $TMPDIR/pytest-of-agent/pytest-<N>/owner{A,B}0/owner_probe.log
with retention (`-o tmp_path_retention_policy=all`; NOTE: `--tmp-retention-policy` is NOT a valid pytest
9.1.1 CLI flag, use the `-o` override; retention_count=1 in pytest.ini keeps only the latest run - copy
a run's PNGs out before the next one if you need a cross-run compare). If 230 is ever REOPENED: the
reason is the driver's note in DECISIONS.md; triage per the run-2 red taxonomy (tier check = 245's
defect, old ratio step = the 816 defect, roman date-stamp = check the checked dates, horsley = agent
c's 809 not mine, anything else = cross-lane: log, do not absorb, do not claim).
