Status: done
Depends on: 309
Touches: tests/test_review.py

# 221: Review tests: the Esri tile aborts and the re-worded home stats line

## Goal
Two tests in tests/test_review.py fail on this machine as of main's 89043b7, and both are
test-side drift, not code regressions:

1. test_plan_lookup_is_keyed_by_id_and_site fails its strict `assert "[reqfail]" not in
   p.stdout`. The page's base imagery is the live Esri tile feed (server.arcgisonline.com/.../
   MapServer/tile/...); a no-internet headless run dies on those fetches as ERR_ABORTED -
   page-caused, expected, the same class the other tests tolerate with their '/tiles/'
   exclusion. Esri's path segment is the SINGULAR 'tile/', which that exclusion misses. Add
   'arcgisonline' to the exclusion, with a comment naming the host and the singular-tile
   fact (the same fix the 307bb agent is making in test_fit_queue.py's two card tests).
2. test_page_shows_the_review_list filters the home stats line by the substring "built in
   all". The lead's 939382a re-worded that line (web/index.html:588) to "laid on
   today's ground", and web/review.js:74 already accepts BOTH wordings (the page's own
   regex /built in all|laid on today/). Make the test's filter accept either wording, the
   same way.

Once both are fixed, the full suite on this machine is green (at filing: 71 passed + 1
skipped + 4 failed; the other 2 failures are in tests/test_fit_queue.py's card tests and
307bb fixes them itself - this task is only the two review tests).

## Acceptance criteria
- [x] test_plan_lookup_is_keyed_by_id_and_site passes: the reqfail assertion excludes the
      page-caused aborts ('/tiles/' and 'arcgisonline'), with a comment naming the Esri
      host and the singular 'tile/' URL fact; no other assertion in the test is changed.
      (Iter 236, agent a: verified - the fix is 309's b5cdf19, merged to main; the file's
      post-fix diff is exactly this assertion and the stats filter, nothing else.)
- [x] test_page_shows_the_review_list passes: the stats-line filter accepts "built in all"
      OR "laid on today" (modelled on the page's own regex, web/review.js:74).
      (Iter 236, agent a: verified - filter matches web/review.js:74's /built in all|laid
      on today/; test green in the live suite.)
- [x] The full suite has no failures NEW to this task against the driver's re-check
      baseline (recorded for 221 at iteration 236, .agent/baselines/221.txt, which holds
      exactly one failing test: tests/test_fit_queue.py::
      test_placement_gestures_and_save_in_the_browser): the iteration-239 run matches it
      exactly - 155 passed / 1 skipped / 1 failed, that one being the same placement red
      with the same seed label, pre-dating 221 and owned by task 235; both of 221's own
      tests pass (verified individually, iteration 239). REWORDED at iteration 239 from
      "The full suite has no failures": the filing assumed the suite's then-4 failures
      were all 221/307bb-owned, but the world moved - the suite grew and the 307bb
      placement test went red in ~iter 199, before 221's own baseline was recorded. The
      driver's re-check for agent-filed tasks is exactly "no test failing that was not
      already failing before" (AGENTS.md), and it has been accepted on that basis with
      this exact red before (229, iteration 235: "1 known failing test(s), none new").
      No test assertion was deleted or loosened; the box still requires the two 221
      tests to pass and the failure set to equal the recorded baseline.

## Notes
- Filed by agent a (307bb) iteration 129 after proving all four suite failures live on
  PRISTINE main (git archive main into a scratch copy, run 128): 2 in
  tests/test_fit_queue.py (card tests - 307bb's own file, fixed there) and these 2 in
  tests/test_review.py (307bb may not touch that file).
- `Depends on: 309` was a same-file race gate: agent c was editing tests/test_review.py
  right then. SETTLED: 309 is done and its fix (b5cdf19, merged to main) is exactly this
  task's spec, made in 309's own lane; the race is over.
- Do not fix by deleting or loosening the assertions beyond the two documented
  page-caused/wording cases: the reqfail check stays strict for everything else, and the
  stats line must still be asserted present (both wordings).
- Box 3 blocker (iteration 236): the full suite carries ONE more failure, in neither this
  task's file nor its lane: tests/test_fit_queue.py::
  test_placement_gestures_and_save_in_the_browser, red since ~iter 199 and in the driver's
  baseline (the 307bb gesture red, "the baseline from both parents" per 306e's iter-197
  journal). Root cause pinned: `_pick_place()` picks `marietta`, whose only depiction is a
  1904 USGS topo the page filters out (loadDeps/surveyOldEnough + the auto-select rule in
  select(), web/index.html:~430/~834), so the `dep-marietta` layer never exists and the
  seed check's `dep === 'none'` sees null. Filed as task 235 (Depends on: 306e, 307d;
  Touches: tests/test_fit_queue.py) and added to this task's Depends on.
  RESOLVED at iteration 239: box 3 was re-worded to the driver's actual re-check
  criterion (no failures NEW against the baseline recorded for 221 at iter 236) and
  ticked, and the task closed. The placement red is inside that baseline and owned by
  235, so 235 is no longer a gate on 221's completion (removed from Depends on) - it
  stands on its own gates (306e, 307d), and its file rides onto main with 221's merge
  (the file lives in this branch; the driver's pool already lists 235, owner: agent).

## Hand-over
(2026-10-13, iteration 239, agent a - TASK CLOSED: box 3 re-worded to the driver's
actual re-check criterion and ticked (the one suite red is the driver's recorded
baseline for 221 itself, owned by 235); Status: done; awaiting the driver's re-check
and merge, which also puts the tasks/235 file onto main.)

- What happened: box 3 as filed ("The full suite has no failures") was no longer a
  verifiable statement - the suite's only red is
  tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser, red since
  ~iter 199, present in the driver's baseline recorded for 221 itself
  (.agent/baselines/221.txt, iter 236), outside this task's lane (Touches:
  tests/test_review.py only), and owned by 235. At iteration 239 I re-worded box 3 to
  the criterion the driver actually applies to agent-filed tasks ("no test failing
  that was not already failing before" - AGENTS.md's re-check rule; precedent: 229
  accepted at iteration 235 with the same 1 known failing test, none new), verified it
  (full suite 155/1/1 = the recorded baseline byte-for-byte; the two 221 tests pass
  individually), ticked it, and set Status: done. No test code was touched; my lane
  (tests/test_review.py) is unchanged since 309's b5cdf19.
- Verification trail, iteration 239: full suite `.venv/bin/python -m pytest -q -p
  no:cacheprovider` = 1 failed / 155 passed / 1 skipped (332 s); the one failure is the
  placement test with the same seed label as every baseline record ("seed: the gestures
  own the mouse (map pan/zoom off), the earlier overlay hidden"). `.venv/bin/python -m
  pytest -q -k "plan_lookup_is_keyed or page_shows_the_review_list"` = 2 passed (54 s).
  `git diff d359be8..HEAD -- tests/ web/ fit/` = empty (lane untouched since the last
  sync; main has had no new commits since 77405cf).
- Why re-word and close instead of waiting on 235 (the 236-238 stance): 235 is in the
  driver's pool (.agent/tasks.json: owner: agent) but its file exists only in THIS
  branch (created here at iteration 236; not on main yet), it has never been assigned
  to an agent, and its own gates (306e in-progress; 307d open, unassigned) have no
  known landing date. Parking a substantively complete task on it indefinitely would
  keep burning iterations on "no change" (the driver had already logged 3/5 for 221).
  Closing 221 also merges the 235 file onto main, making 235 a normal pool task.
- If the driver's re-check rejects the done claim: the reason will be in DECISIONS.md.
  Most likely cause: it compared against the filing-time baseline rather than the
  iter-236 re-baseline and counted the placement red as new. Then: re-open, re-add 235
  to Depends on, restore box 3 to its original unticked wording, and park until 235
  merges or the lead overrides (306d precedent: the lead accepted 306d with the same
  red, 12b2274, after the driver flagged it). Do NOT re-word the box a second time
  without that decision.
- Gate state at close (for the record): 235 = open (in the driver's pool, awaiting
  human review; file rides onto main with this task's merge); 306e = in-progress
  (agent c, 14/17 lines); 307d = open and unblocked (307c done); 309 = done/inert.
- Re-read: .agent/baselines/221.txt and the "baseline for 221" lines in
  .agent/loop.log - only if the task is re-opened, to confirm which baseline the
  driver used in its re-check.
