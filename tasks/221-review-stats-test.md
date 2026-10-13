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
(2026-10-13, iteration 236, agent a - FIRST session on 221 since its 309 gate settled.
Boxes 1+2 VERIFIED and ticked; box 3 blocked on 235.)

- Verified, not fixed: the fix already landed on main in 309's lane (commit b5cdf19,
  merged via the lead; my branch carries it after 3ceb3a5). I did not touch the file this
  session. Verification: (a) `git diff b5cdf19^ HEAD -- tests/test_review.py` = 11+/2-
  and is EXACTLY the two documented changes (the stats filter at ~line 270 accepting
  "built in all" or "laid on today", modelled on web/review.js:74's /built in all|laid
  on today/ - still there; and the reqfail assertion at ~line 414 excluding '/tiles/' and
  'arcgisonline', commented with the Esri host and the SINGULAR 'tile/' fact) - no other
  assertion in either test changed; (b) web/review.js:74 regex intact; (c) both tests run
  green in the live suite: `.venv/bin/python -m pytest -q tests/test_review.py -k
  "plan_lookup_is_keyed or page_shows_the_review_list"` -> 2 passed.
- Box 3 is the only thing left, and it is NOT my code: full suite this session =
  155 passed / 1 skipped / 1 failed; the one failure is
  test_fit_queue.py::test_placement_gestures_and_save_in_the_browser, failing its seed
  check with `dep: null` (gestures all false) on the picked site `marietta` (only
  depiction: 1904 USGS topo -> filtered out by loadDeps' surveyOldEnough, so no
  dep-marietta layer is ever created). It is in the driver's test-baseline.txt (pre-
  existing, not a regression of this lane) and red since ~iter 199 (306d's journal).
- NEXT (after 306e and 307d merge, when the driver brings 221 back): run the full suite
  (`.venv/bin/python -m pytest -q -p no:cacheprovider`); if 235 landed and the suite is
  green, tick box 3, set Status: done, and this task is finished. If a placement-gesture
  failure still shows (235 not merged yet), keep box 3 unticked and end. If a DIFFERENT
  test fails, file a new task (lowest free number 200-499, then re-check the list) and
  add it to Depends on - do not fix outside this task's Touches (tests/test_review.py).
- Re-read: tests/test_fit_queue.py::_pick_place + PLACE_PROBE seed check - only if 235
  comes back and its fix needs cross-checking against this task's suite run.
