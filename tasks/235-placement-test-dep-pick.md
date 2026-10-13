Status: open
Depends on: 306e, 307d
Touches: tests/test_fit_queue.py

# 235: The placement test's pick must mirror the page's depiction filter

## Goal
tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser (307bb box 3) fails
its seed check and has been red since ~iteration 199 (306d's run recorded `dep:null`; it is
in the driver's baseline, and 306e's iter-197 journal calls it "the 307bb gesture red, the
baseline from both parents"):

    RESULT FAIL: seed: the gestures own the mouse (map pan/zoom off), the earlier overlay hidden

The gestures part passes (all five map gestures report false); the failing sub-condition is
`dep === 'none'`, which sees `null`. The probe opens the picked queue site and reads
`map.getLayer('dep-<site>') ? visibility : null`. The pick `_pick_place()` (line ~1654) takes
the FIRST queue entry that has a propose, is line-eligible (`_line_eligible`: an unresolved
review item carrying the row, no docs yet) and has a NON-EMPTY RAW
`web/data/sites/<site>/depictions.json`. That pick is now `marietta` (queue entry 29, plan
ancientmonuments00squi_n0169_1), whose only depiction is a 1904 USGS topo quad - and the
page never shows it: `loadDeps` (web/index.html:~430) filters the fetched depictions with
`surveyOldEnough` (kinds {map, aerial, topo} only pass when `year` is present and
`year <= currentYear - 150`), and `select()`'s auto-select (web/index.html:~834) then takes
`ds.find(x => DRAWING.has(x.kind)) || ds.filter(x => x.kind === 'map').pop()` (DRAWING =
{plan, drawing, view}) - the 1904 topo fails the filter, so no depiction is selected, so the
`dep-marietta` layer is never created, so Cancel has nothing to bring back and the probe's
expectation fails. The pick checks what the SITE has; the test must check what the PAGE will
show.

Fix the test, not the page (the filter is deliberate: Ethan 2026-10-10, the comment at
web/index.html:~428 - USGS topographic quads "don't really ever show anything"):
`_pick_place` must apply the page's own two rules before accepting a site - (1) the
`surveyOldEnough` filter over the raw depictions (same kinds, same 150-year cutoff, missing
year excludes a survey kind; mirror it in stdlib, no copy of the JS needed: a small function
with the same boolean), and (2) the auto-select rule (a {plan, drawing, view} depiction, else
the last surviving 'map'). Only a site with at least one surviving depiction of one of those
kinds gets a page-created `dep-<site>` layer in a fresh browser, which is exactly what the
seed check (hidden during place mode) and the Cancel check (restored) need to be non-vacuous.
The pick stays DERIVED (first qualifying entry in file order), never pinned to a site.

## Acceptance criteria
- [ ] The test passes on this machine: `_pick_place` (tests/test_fit_queue.py) filters the
      picked site's raw depictions with the page's `surveyOldEnough` rule and its auto-select
      rule before accepting it (mirrored in stdlib, one small helper each, with a comment
      pointing at the web/index.html lines they mirror); `marietta` (only depiction: a 1904
      USGS topo, filtered out) is no longer picked; the pick is still derived, never pinned.
- [ ] The probe (PLACE_PROBE) and every other assertion in tests/test_fit_queue.py are
      unchanged; no page or server file is modified.
- [ ] The full suite has no failures (baseline: exactly this one test failing -
      306e's iter-197 run and the pre-236 driver baseline both record 154/155 passed,
      1 skipped, 1 failed).

## Notes
- Filed by agent a (221) iteration 236: 221's box 3 ("the full suite has no failures") waits
  on this task; 221's Depends on now carries 235.
- Depends on 306e (agent c is still re-exporting web/data/review.json and the data/review
  items, which drive `_line_eligible` - the pick's second gate - so verifying the new pick
  against moving data would be noise) and 307d (open, Touches: tests/ - same-file gate;
  307d's own test is a NEW file, but its broad tests/ claim is the safe gate).
- If the suite turns out to fail elsewhere once this one is green, that is a different task:
  file it, don't fix it here (one module per task).
