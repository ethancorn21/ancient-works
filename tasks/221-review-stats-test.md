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
(2026-10-13, iteration 238, agent a - box 3 re-checked on the state after main's
77405cf merge: suite baseline unchanged (155/1/1, same placement red), pick still
marietta/1904-topo, 235 still open; gates 306e in-progress, 307d now unblocked.)

- What changed on main since 237: ONLY lead 77405cf - 13 matcher re-fits on 11 sites
  (212b sync) and review items for the 103 uncovered sites of 212c's report
  (web/data/review.json +5172 lines, new data/review/* items, fit_queue.json now 241
  entries, sites.json +102), plus a 4-line tweak in tests/test_batch_us.py. tests/
  test_review.py and tests/test_fit_queue.py UNCHANGED (diff 10f4683..d359be8) - the
  221 lane is untouched; boxes 1-2 stay green in the live suite.
- Suite this session: 155 passed / 1 skipped / 1 failed (340 s) - IDENTICAL to the
  236/237 baseline; the one failure is still
  tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser with the
  same failing seed-check label ("seed: the gestures own the mouse (map pan/zoom
  off), the earlier overlay hidden"). The 103 new review items created NO new failure
  (test_serve/test_review/test_fit_queue all green) - so nothing to file as a new task.
- Pick re-verified by running the test's own helper read-only (.venv python, `import
  test_fit_queue; _pick_place()`): still marietta - queue index 29, plan
  ancientmonuments00squi_n0169_1, single depiction ('topo', 1904) - unchanged by
  77405cf (fit_queue.json already had 241 entries at 237; the merge touched only 2 of
  its lines, and the first entry passing propose + _line_eligible + non-empty
  depictions is still marietta). 235's spec (the pick must mirror the page's
  surveyOldEnough 150-yr filter and its {plan,drawing,view}/last-'map' auto-select)
  is still accurate.
- Gates, re-checked in this checkout: 235 = `Status: open` (never started; fix not on
  main); 306e = in-progress (agent c's UK part 2; last hand-over: 14 of 17 lines,
  york x2 + windmill-hill x1 pending); 307d = open and NOW UNBLOCKED (its gate 307c is
  done) - awaiting a driver assignment; still a same-file gate for 235 (Touches:
  tests/); 309 = done/merged, inert. My `Depends on: 309, 235` already carries the
  live gate; nothing to add.
- NEXT (when the driver brings 221 back after 306e/307d/235 land): run the full suite
  (`.venv/bin/python -m pytest -q -p no:cacheprovider`); if 235's fix is on main and
  the suite is green, tick box 3 and set Status: done (the task is finished). If the
  placement-gesture failure still shows, keep box 3 unticked and end. If a DIFFERENT
  test fails, file a new task at the lowest free number in 200-499 (re-check `ls
  tasks/` then - as of this session the highest is 235, so 236 is the first
  candidate) with proper Depends on/Touches lines, and add it to this task's Depends
  on - do NOT fix it here (my Touches: tests/test_review.py and my files in tasks/).
- Re-read: tests/test_fit_queue.py::_pick_place + the PLACE_PROBE seed check (line
  ~1749) - only if 235 lands and its fix needs cross-checking against this task's
  suite run.
