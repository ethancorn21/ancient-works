Status: done
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

(2026-10-15, iteration 238, agent a - I hold the WHOLE CYCLE (230/242/810/811/812/813/814; inter-deps
count as met, built together on this branch). STATE: RE-CLAIMED DONE THIS SESSION (Status: done
above). The driver's it.237 rejection was a pure branch conflict with main, not the work: the merge
is done (f3b39f5b; the single conflict was this file - resolved as the union of both sides: main's
extended Depends chain + my maclachlan Touches entry + my hand-over). The claim-gate suite is green
on the driver's exact command: 194 passed / 1 skipped / 0 failed, 606.10 s, 195 collected
(/tmp/loop-ancient-works.a/fullsuite-238.log) - all three reds on main (owner-check pair x2, the
maclauchlan date skew) are fixed on this branch, and main's new tests (809's horsley 5, 241's batch5
5) all pass on my tree. If the driver accepts, the WHOLE branch lands on main (245's page fix, the
816 recipe in test_owner_check.py, the maclachlan fix, plus my copies of main's 809/batch5/815/817/818
files) and the remaining cycle comes back in chain order: 814 -> 812 -> 813 -> 810 -> 811 -> 242.)

**This session (it.238):**
1. `git merge main` (f3b39f5b). One conflict (this file): Depends = main's 10-item chain (the
   242-split bookkeeping; satisfied here since I hold the cycle), Touches = mine (+
   fit/src_roman_maclauchlan.py), hand-over = mine. Merged in from main: 809 DONE (final horsley
   module + 5 tests + golden + PITFALLS checked-date entry), task files 815/817/818, agent c's
   IN-PROGRESS 241 batch5 files (not mine - do not touch; byte-identical to main).
2. Suite (the driver's exact `.venv/bin/python -m pytest -q`; 900 s timeout budgeted - test_gate is
   only 2.24 s): 194/1/0 in 606.10 s. 195 = it.237's 185 + the 10 new main tests, all green.
   The owner-check pair is the 6th consecutive green run in this branch's lineage (it.236 x3,
   it.237 x2, it.238 x1) - the 816 recipe (settle+subpixel) + 245's page fix (tier race) hold.
   The run re-encoded 9 of the ten 307d PNGs (B_1-card always byte-identical); restored to the
   committed bytes before the merge commit (identical to HEAD and main).
3. Cross-lane note for the driver / the 817-818 claimers (I cannot edit their task files): 817
   (open on main) fixes the same maclauchlan red the other way - zero location_check.checked in
   _canon_norm, keep the live now() stamp; 818 is the horsley twin. My it.237 fix is the opposite
   interim (frozen CHECKED = "2026-10-14" in stage(); _canon_norm untouched). The two touch
   disjoint regions of fit/src_roman_maclauchlan.py, so when my branch lands and 817 is claimed
   on main, the module should 3-way auto-merge (both hunks survive). I did NOT add their side
   from my branch (their regression control lives in tests/test_src_roman_maclauchlan.py, which
   is 817's, not my, file; my constant alone keeps every suite green on any day). Recommendation
   for the claimer, recorded in the DECISIONS entry: after the zeroing, restore the live now()
   stamp (safe - the join ignores the date; better - honest provenance; 817's box 1 asks for it).
   The frozen constant stays a valid stopgap until then. Horsley: I touch nothing (818's lane).

**What happens next on this branch (the cycle comes back in chain order - each task file carries
its own hand-over with the exact build steps):**
1. 814 (in-progress, mine): its Depends (307d done, 816, 230) all satisfied in this branch - the
   settle+subpixel fix is ALREADY in tests/test_owner_check.py (verified byte-identical to the
   816 recipe in it.236). Remaining = verification only: two consecutive unflagged pair runs
   (A then B, ONE invocation), all ten 307d views stable run-to-run, then tick its boxes.
2. 812: add the in-run double-shot stability assert to tests/test_owner_check.py. The it.235 build
   survives verbatim at `git show 3579c22b:tests/test_owner_check.py` - rebase its double-shot part
   onto the current file (which is the 816 recipe), keeping c's settle/subpixel; verify additive
   by diff.
3. 813: the AW_OWNER_REFRESH refresh flag + write-surface + docstrings - also in the it.235 build;
   same rebase. (Until this lands, unflagged owner-check runs re-copy all ten 307d PNGs.)
4. 810: verification only (settle + double-shot + refresh in place; pair green; no new reds).
5. 811: the one-time flagged refresh run + pinned 307d PNGs + docs/site_flow.md note + the
   PITFALLS rewrite; then 242: final verification only (Depends 307d, 810, 811 - all met in the
   cycle).
6. 245 (mine, built in it.236 ab57da1b; Depends 815): the web/index.html fix is in the branch.
   Once 815 (agent c's page-side subpixel, open on main, Depends 814) lands, 245 is claimable:
   pair green + no new reds + the Marker-site audit note in its hand-over.

**Standing discipline (every owner-check work on this branch):** the pair runs in ONE invocation
(A then B - B cannot run alone); after ANY owner-check run restore the ten docs/site_flow/307d_*.png
to the committed bytes before committing (`git restore docs/site_flow/`; R5) - until 813's flag
lands, unflagged runs re-copy all ten (this run re-encoded 9; B_1-card always byte-identical);
NEVER `git add -A` over them. Probe logs die with the session - read them from
$TMPDIR/pytest-of-agent/pytest-<N>/owner{A,B}0/owner_probe.log with retention
(`-o tmp_path_retention_policy=all`; `--tmp-retention-policy` is NOT a valid pytest 9.1.1 CLI flag;
pytest.ini's retention_count=1 keeps only the latest run - copy a run's PNGs out first if a
cross-run compare is needed). If 230 is EVER reopened again: the reason is the driver's note in
DECISIONS.md; triage the reds by taxonomy: tier check = 245's defect, the q1/q2 ratio step = the
816 defect, a roman checked-date "differs" = check the stamped dates (maclauchlan = my constant,
horsley = 818's lane), anything batch5/207a = agent c's lane, anything else = cross-lane: log it,
do not absorb it, do not claim.
