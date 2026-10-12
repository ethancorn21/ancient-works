Status: open
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
- [ ] test_plan_lookup_is_keyed_by_id_and_site passes: the reqfail assertion excludes the
      page-caused aborts ('/tiles/' and 'arcgisonline'), with a comment naming the Esri
      host and the singular 'tile/' URL fact; no other assertion in the test is changed.
- [ ] test_page_shows_the_review_list passes: the stats-line filter accepts "built in all"
      OR "laid on today" (modelled on the page's own regex, web/review.js:74).
- [ ] The full suite has no failures (the driver's re-check baseline at filing: exactly
      these two failing).

## Notes
- Filed by agent a (307bb) iteration 129 after proving all four suite failures live on
  PRISTINE main (git archive main into a scratch copy, run 128): 2 in
  tests/test_fit_queue.py (card tests - 307bb's own file, fixed there) and these 2 in
  tests/test_review.py (307bb may not touch that file).
- `Depends on: 309` is a same-file race gate: agent c is editing tests/test_review.py
  right now; this task's fix lands on top of whatever 309 leaves in the file.
- Do not fix by deleting or loosening the assertions beyond the two documented
  page-caused/wording cases: the reqfail check stays strict for everything else, and the
  stats line must still be asserted present (both wordings).
