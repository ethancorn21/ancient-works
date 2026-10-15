Status: done
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
- [x] The test passes on this machine: `_pick_place` (tests/test_fit_queue.py) filters the
      picked site's raw depictions with the page's `surveyOldEnough` rule and its auto-select
      rule before accepting it (mirrored in stdlib, one small helper each, with a comment
      pointing at the web/index.html lines they mirror); `marietta` (only depiction: a 1904
      USGS topo, filtered out) is no longer picked; the pick is still derived, never pinned.
- [x] The probe (PLACE_PROBE) and every other assertion in tests/test_fit_queue.py are
      unchanged; no page or server file is modified.
- [x] The full suite has no failures (baseline: exactly this one test failing -
      306e's iter-197 run and the pre-236 driver baseline both record 154/155 passed,
      1 skipped, 1 failed).

## Hand-over
(2026-10-14, iteration 197, agent a)

**DONE - all three boxes verified and ticked this session.** The whole fix is in
`tests/test_fit_queue.py` (the only non-memory file changed; `git diff main --name-only` is
the proof): two small stdlib helpers just above `_pick_place` and its gate 3 + docstring.

- `_survives_page_filter(dep)` mirrors web/index.html:444-445 (`surveyOldEnough`, applied by
  `loadDeps` at :449): {map, aerial, topo} pass only with a year (falsy year fails, as in the
  JS `x.year &&`) <= this year - 150; other kinds pass. The data's year is int or None (711/3
  across all 714 depictions - re-measured), so Python `and`/`<=` matches the JS exactly.
- `_page_auto_select(dep)` mirrors web/index.html:688 (`DRAWING` = {plan, drawing, view}) +
  `select()`'s auto-select at :866: first surviving drawing kind, else the last surviving
  'map'. Its comment records why only such a site gets a page-created `dep-<site>` layer
  (applyDep index.html:453 creates it only from the filtered list; startFit fitkit.js:575
  hides it in place mode only when it exists).
- Gate 3 is now `if _page_auto_select(json.loads(dep.read_text()) if dep.is_file() else None) is None: continue`.
  The pick stays DERIVED (first qualifying entry in file order); no site name anywhere.
  PLACE_PROBE, `_line_eligible`, `_pick_site`, `place_served` and every assertion are
  byte-identical to main's.

**Verification (this session):**
- Pick simulation: pre-fix (main's code) = **marietta** (idx 1 of 180, 1904-topo-only);
  post-fix = **oswestry-castle-q20713795** (idx 3, plan earthworkenglan01allcgoog_n0119_1:
  1842 six-inch map survives, 1900 map filtered; auto-select = six-inch-1st.webp). marietta's
  auto-select = None.
- Placement test: PASS (65 s) on the oswestry pick; probe log (a retention=all run, keep at
  `/tmp/loop-ancient-works.a/pytest-of-agent/pytest-*/f4shot*/probe.log` until the driver
  cleans): every check [ok], incl. "place: the earlier overlay is hidden while placing"
  (now NON-vacuous: the layer existed before run 1) and "cancel: ... is back" ('none' ->
  'visible').
- Full suite (`.venv/bin/python -m pytest -q -p no:cacheprovider`): **177 passed, 1 skipped,
  0 failed** (508 s). vs the driver's 2026-10-13 baseline (159/1/1): the lone red is gone,
  zero failures; the count grew 161 -> 178 on main (236b/240/241, 221, ...) - prep's R3 was
  right, judge against the current tree, not the number in this file.

**Prep-note assumptions that were WRONG (tasks/prep/235.md, written 2026-10-13 17:09):**
1. **The test is NOT red on the current main** (the prep's whole premise). bba5961 (Oct 13
   22:17, the lead's port) rewrote the part-4 probe: the old strict seed check is gone
   (now `!before1.vis || vis === 'none'` - vacuous when no layer), and run 2's cancel check
   runs AFTER run 1's Save, which writes the saved fit's plan depiction into the TEMP tree's
   depictions.json, so run 2's page auto-selects it and the check passes even for a
   no-overlay pick. Proven twice today: main's pre-235 `_pick_place` (pick = marietta) PASSES
   the current test (saved doc `marietta.ancientmonuments00squi_n0169_1.json` `by: hand` in
   the temp tree; cancel check [ok]). The driver's 159/1/1 baseline quoting "seed: the
   gestures own the mouse ... dep:null" at line 1749/1755 was measured against the
   PRE-bba5961 file (same staleness as the PITFALLS entry on the cleared 307bb red). The fix
   still stands on its own merits: with the marietta pick the seed-time overlay checks are
   vacuous, and the pick now lands on a site whose overlay is visible from page load.
2. **All line numbers stale** (the file is ~137 lines shorter at main): `_pick_place`
   1654 -> 1517, `_line_eligible` 758 -> 764, PLACE_PROBE 1289 -> 1297, `place_served`
   1673 -> 1536, the test 1731 -> 1595; page 430-435/657/833-836 -> 444-445/449/688/866.
   The LOGIC the prep described is exactly right - the mirror is its sketch, split into the
   two helpers the box asks for.
3. **Queue indices stale**: bba5961 also re-exported `web/data/fit_queue.json` (Oct 13
   22:25, 241 -> 180 entries, "fit_queue drops dropped"): marietta is idx 1 (not 29),
   oswestry idx 3 (not 38). The prep's 241-entry skip-list is stale; the pick simulation was
   enough this session.

**Right in the prep:** deps 306e + 307d done (no Depends-on wait needed); the mirror logic;
falsy-year semantics; the post-fix pick = oswestry; the machine (headless Chrome +
playwright-core) working.

**Downstream:** 212 (in-progress, `Depends on: 235`) can re-claim done - the suite is fully
GREEN on this tree, which was its rejection reason (the driver re-runs against its 159/1/1
baseline and will see zero failures). 307bc (open, `Depends on: 235`) can re-run the
placement proof: with this pick (oswestry) it is green and non-vacuous, and closes 307b box 5.

**Environment notes for the next session:**
- The loop's temp base is `$TMPDIR=/tmp/loop-ancient-works.a` (pytest-of-agent there;
  `*current` entries are symlinks). pytest.ini retention = failed/1, so a PASSING run's
  probe.log is deleted - add `-o tmp_path_retention_policy=all` to keep it (PYTEST_ADDOPTS
  cannot be overridden from the CLI for retention; the later `-o` wins in practice, but the
  passing-run directory is still swept - grab it during the run or right after).
- Re-verify the derived pick before any re-run (seconds; store state moves under doc
  deletions/queue re-exports): `cd tests && .venv/bin/python -c "import test_fit_queue as T; e, done = T._pick_place(); print(e and (e['site'], e['best']['plan'], len(done)))"`.
- Worktree has 8 modified `docs/site_flow/307d_*.png`: machine-noise re-renders written by
  `tests/test_owner_check.py` on every full-suite run (PITFALLS: the test never compares
  them; PNG encoding is not run-to-run deterministic). They were dirty before this session
  too (the driver's a502a2b committed one re-rendered set). NOT committed by me (307d's
  files, outside my Touches); left for the driver's bookkeeping capture.
- If a re-run is needed: the placement test alone is ~70 s; the full suite ~8.5 min on this
  machine.

## Notes
- Filed by agent a (221) iteration 236: 221's box 3 ("the full suite has no failures") waits
  on this task; 221's Depends on now carries 235.
- Depends on 306e (agent c is still re-exporting web/data/review.json and the data/review
  items, which drive `_line_eligible` - the pick's second gate - so verifying the new pick
  against moving data would be noise) and 307d (open, Touches: tests/ - same-file gate;
  307d's own test is a NEW file, but its broad tests/ claim is the safe gate).
- If the suite turns out to fail elsewhere once this one is green, that is a different task:
  file it, don't fix it here (one module per task).
