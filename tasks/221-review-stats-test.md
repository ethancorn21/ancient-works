Status: in-progress
Depends on: 309, 235
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
- [ ] The full suite has no failures (the driver's re-check baseline at filing: exactly
      these two failing).

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

## Hand-over
(2026-10-13, iteration 237, agent a - boxes 1+2 done (236); box 3 still blocked on 235,
re-verified this session: state unchanged since 236.)

- Re-verification this session (no code change; tests/test_review.py untouched again):
  (a) full suite `.venv/bin/python -m pytest -q -p no:cacheprovider` = 155 passed /
  1 skipped / 1 failed (325 s) - IDENTICAL to the 236 baseline; (b) the one failure is
  still tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser, same
  failing label as every prior red record ("seed: the gestures own the mouse (map
  pan/zoom off), the earlier overlay hidden") - no new failure mode, so nothing to file
  as a new task; (c) the pick is still `marietta` / plan ancientmonuments00squi_n0169_1
  with its single depiction `('topo', 1904)` - ran `_pick_place()` read-only
  (`import test_fit_queue; _pick_place()`): the exact un-pinnable state 235's spec
  fixes.
- Gates, re-checked: tasks/235 = `Status: open` (never started; its fix is not on main),
  its gate 306e = in-progress (agent c, UK part 2, still re-exporting web/data/review
  .json + data/review items that drive `_line_eligible`), 307d = open (Depends on: 307c).
  So box 3 cannot be settled yet; the `Depends on: 309, 235` line already carries the
  only live gate (309 is done/merged, inert - see Notes).
- NEXT (when the driver brings 221 back, i.e. after 235's gates 306e/307d merge and 235
  lands): run the full suite (`.venv/bin/python -m pytest -q -p no:cacheprovider`); if
  235's fix is on main and the suite is green, tick box 3 and set Status: done (this
  task is finished). If the placement-gesture failure still shows, keep box 3 unticked
  and end. If a DIFFERENT test fails, file a new task at the lowest free number in
  200-499 (re-check `ls tasks/` at that moment - as of this session the highest is 235,
  so 236 is the first candidate) with the proper Depends on/Touches lines, and add it to
  this task's Depends on - do NOT fix it here (my Touches is only tests/test_review.py
  and my files in tasks/).
- Re-read: tests/test_fit_queue.py::_pick_place + PLACE_PROBE seed check - only if 235
  comes back and its fix needs cross-checking against this task's suite run.
